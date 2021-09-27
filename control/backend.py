#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-08-30 10:59:42
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: backend.py


import json
import time
import datetime
from base import errors
from base import redis, db, apscheduler
from utils import hash_md5
from utils.time_utils import datetime_2_str_by_format, now_dt, str_2_datetime_by_format
from .rule_conf import Rule
from .models.base_models import (RuleModel, ExpireModel, TriggerModel,
                                 StrategyModel, AlreadyTriggerModel, ReqLogsModel,
                                 SourceDataByContractSignModel)


class BaseClass(Rule):
    """
    基础类方法

    不建议直接引用
    """
    # def __init__(self):
    #     self.model = None
    #     self.rule = None
    #
    #     self.ver_params()
    #     self.init()


    def init(self):
        if not self.rule:
            raise errors.ParamsError("内部服务错误, 规则引用错误")
        if not self.rule_dict.get(self.rule):
            raise errors.ParamsError("内部服务错误, 规则CODE错误")

        self.need_params, self.other_params = self.rule_params[self.rule]
        self.all_params = self.need_params + self.other_params

        self.rule = RuleModel.query.filter_by(code=self.rule).one_or_none()
        if not self.rule:
            raise errors.ParamsError("内部服务器错误, 规则数据错误")

        # self.rule_func = getattr(self, self.rule)
        self.conn = redis.client

    def ver_params(self):
        pass


class ConditionRule(BaseClass):
    """
    条件规则
    """
    def __init__(self, rule_id, params):
        """
        TODO 其实校验参数可做有参装饰器
        """
        self.params = params
        self.rule = rule_id

        self.ver_params()
        self.init()

        self.trigger = None
        self.strategy = None
        self.new_data = None
        self.is_upgrade = False
        self.count = 0
        self.expire_dt = None

        # 生成hash
        tmp_list = [str(self.rule.code)]
        for i in self.need_params:
            tmp_list.append(self.params[i])
        tmp_str = "|".join(tmp_list)
        self.hash_code = hash_md5(tmp_str)

    def add(self):
        """
        添加
        """
        # 取该规则的数据
        rule_data = self.query_data()
        self.rule_data = rule_data
        if rule_data:
            if rule_data["is_trigger"]:
                # 如果已经触发规则，则异步计算数据同时返回
                self.async_handle_data()
                rule_data["level"] = self.strategy.trigger.level
                return rule_data

        # 计算规则数据
        tmp_data = self.compute_data()

        # 写数据
        ret = self.write_data()

        # 写日志(异步)
        self.write_log()

        # 定时
        self.task_clean_data()

        ret_data = self.new_data
        ret_data["level"] = self.strategy.trigger.level

        return ret_data

    def list(self, params):
        """
        详情
        """
        pass

    def query_data(self):
        """
        数据详情
        """
        # 从缓存取数据
        cache_data = self.cache_query_data()
        if cache_data:
            return cache_data

        # 从数据库取数据
        db_data = self.db_query_data()
        if db_data:
            return db_data

        # 从数仓取数据
        big_data = self.big_query_data()
        if big_data:
            self.count = big_data["count"]
            big_data["is_trigger"] = False
            return big_data
        return

    def compute_data(self):
        """
        计算数据
        """
        trigger = TriggerModel.query.filter_by(rule_id=self.rule.id) \
            .order_by(TriggerModel.level).all()
        if not trigger:
            raise errors.ParamsError("触发配置错误")
        t_ids = [i.id for i in trigger]
        # 拿到所有触发ID，取所有触发的策略(数据正常情况，只会存在一个风险最高的一条策略)
        strategy = StrategyModel.query.filter(StrategyModel.trigger_id.in_(t_ids)) \
            .filter_by(need_code=self.hash_code,
                       is_deleted=False).one_or_none()
        if not strategy:
            # 第一次请求进来
            s_params = {
                "trigger_id": trigger[0].id,
                "trigger": trigger[0],
                "count": 1 if not self.count else self.count,
                "need_code": self.hash_code,
                "req_code": self.gen_req_code(),
                "dt_trigger": now_dt()
            }
            strategy = StrategyModel(**s_params)
            db.session.add(strategy)
            db.session.commit()

            self.new_data = {
                "rule": self.rule.code,
                "strategy": strategy.id,
                "is_trigger": False if strategy.count < strategy.trigger.count else True,
                "count": 1,
                "info": strategy.trigger.return_info,
                "dt": datetime_2_str_by_format(now_dt())
            }
            self.strategy = strategy
            self.trigger = trigger[0]
            if self.new_data["is_trigger"]:
                self.is_upgrade = True
            return self.new_data

        old_trigger = strategy.trigger
        new_trigger = None
        for i in trigger:
            if i.id == old_trigger.id:
                tmp_index = trigger.index(i) + 1
                if tmp_index + 1 <= len(trigger):
                    _new_trigger = trigger[tmp_index]
                    if self.rule_data["count"] + 1 >= _new_trigger.count:
                        new_trigger = _new_trigger
                        break

        ret = self.rule_data
        ret["count"] += 1
        if not new_trigger:
            self.trigger = old_trigger
            # 未触发更高风险或已经最高风险
            if not ret["is_trigger"]:
                if ret["count"] >= self.trigger.count:
                    ret["is_trigger"] = True
                    self.is_upgrade = True
        else:
            # 触发下一等级的风险
            self.trigger = new_trigger
            self.is_upgrade = True
            ret["strategy"] = strategy.id
            ret["info"] = self.trigger.return_info
            ret["is_trigger"] = True

        self.strategy = strategy
        self.new_data = ret
        return ret

    def write_data(self):
        """
        写数据
        """
        self._write_db_data()
        self._write_cache_data()

        return True

    def write_log(self):
        """
        写日志
        """

        log_params = {
            "strategy_id": self.strategy.id,
            "strategy": self.strategy,
            "info": json.dumps(self.rule.code, ensure_ascii=False),
            "rule": self.rule.code
        }

        req_log = ReqLogsModel(**log_params)
        db.session.add(req_log)
        db.session.commit()


    def cache_query_data(self):
        """
        缓存取数据

        return: dict
        {
            rule: 1,
            strategy: 1,
            is_trigger: True,
            count: 1,
            info: 触发规则的信息,
            dt: 2021-01-01 00:00:00
        }
        """

        # 获取数据
        cache_d = self.conn.get(self.hash_code)
        if not cache_d:
            return

        cache_d = json.loads(cache_d)
        return cache_d


    def db_query_data(self):
        """
        本地库取数据
        """
        trigger = TriggerModel.query.filter_by(rule_id=self.rule.id).all()
        # 拿到所有触发ID，取所有触发的策略(数据正常情况，只会存在一个风险最高的一条策略)
        t_ids = [i.id for i in trigger]
        strategy = StrategyModel.query.filter(StrategyModel.trigger_id.in_(t_ids)) \
            .filter_by(need_code=self.hash_code,
                       is_deleted=False).one_or_none()
        if not strategy:
            return

        ret = dict()
        ret["rule"] = strategy.trigger.rule_id
        ret["strategy"] = strategy.id
        ret["is_trigger"] = False if strategy.count < strategy.trigger.count else True
        ret["dt"] = datetime_2_str_by_format(strategy.dt_trigger)
        ret["info"] = strategy.trigger.return_info
        ret["count"] = strategy.count

        return ret


    def big_query_data(self):
        """
        数仓取数据

        TODO 这里应该用SQL获取数据，由于临时在本地数据库，所以先用ORM代替
        """
        query_data_func = getattr(self, self.rule_sql[self.rule.code])
        if not query_data_func:
            return
        return query_data_func()

    def async_handle_data(self):
        """
        异步处理数据
        TODO
        """
        # 计算规则数据
        tmp_data = self.compute_data()

        # 写数据
        ret = self.write_data()

        # 写日志(异步)
        self.write_log()

        # 定时
        self.task_clean_data()

    def _write_db_data(self):
        """
        数据写入数据库
        """
        self.strategy.count = self.new_data["count"]
        if not self.is_upgrade:
            # 风险未提升
            pass
        else:
            # 风险提升或触发一级风险
            self.strategy.trigger_id = self.trigger.id
            self.strategy.trigger = self.trigger
            self.strategy.trigger = self.trigger

            # 触发记录
            trigger_log_params = {
                "strategy_id": self.strategy.id,
                "strategy": self.strategy,
                "dt_trigger": now_dt(),
                "rule": self.rule.code
            }
            trigger_log = AlreadyTriggerModel(**trigger_log_params)
            db.session.add(trigger_log)
        db.session.commit()

    def _write_cache_data(self):
        """
        数据写入缓存
        """
        cache_data = self.cache_query_data()
        if not cache_data:
            self.conn.set(self.hash_code, json.dumps(self.new_data, ensure_ascii=False))
            if self.strategy.trigger.duration:
                duration = self.strategy.trigger.duration
            else:
                duration = 30
                # TODO 这里先预留，默认时效30秒，以做测试
                """
                思路： 根据'self.strategy.expire.expire_day'等数据直接计算应该时效的时间点，
                    比如：expire_day = 1, expire_month = 1
                    那么直接计算1个月后多1天的日期将设置为过期时间, 直接day+expire_day即可, 可扩展到时分秒
                """
            self.conn.expire(self.hash_code, duration)
            self.expire_dt = now_dt() + datetime.timedelta(seconds=duration)
        else:
            remaining_time = self.conn.ttl(self.hash_code)
            self.conn.set(self.hash_code, json.dumps(self.new_data, ensure_ascii=False))
            self.conn.expire(self.hash_code, remaining_time)


    def gen_req_code(self):
        # 生成请求hash
        tmp_list = [str(self.rule.code)]
        for i in self.all_params:
            tmp_list.append(self.params[i])
        tmp_str = "|".join(tmp_list)
        self.hash_req_code = hash_md5(tmp_str)
        return self.hash_req_code

    def task_clean_data(self):
        """
        定时任务清数据
        """
        if not self.expire_dt:
            return
        task_params = {
            "trigger": "date",
            "run_date": self.expire_dt
        }
        apscheduler.add_job(hash_md5(self.hash_code + str(time.time())),
                            func=self.del_data,
                            args=(self.strategy.id,),
                            **task_params)

    def del_data(self, strategy_id):
        """
        删除数据
        """
        from application import app
        with app.app_context():
            strategy = StrategyModel.query.filter_by(id=strategy_id).one_or_none()
            if strategy:
                strategy.is_deleted = True
                db.session.commit()
        return
