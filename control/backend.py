#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-08-30 10:59:42
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: backend.py


from base import errors
from base import redis
from utils import hash_md5
from utils.time_utils import datetime_2_str_by_format
from .models.base_models import (RuleModel, ExpireModel, TriggerModel,
                                 StrategyModel, AlreadyTriggerModel, ReqLogsModel)

class Rule(object):
    """
    规则

    TODO 该类为配置类，可以提取后台配置
    """
    rule_dict = {
        1: "contract_sign_user"
    }

    rule_params = {
        1: (("idcard", "name"), ("phone",)),
    }


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

    conn = redis.client

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

    def add(self):
        """
        添加
        """
        # 取该规则的数据
        rule_data = self.query_data()
        if rule_data:
            if rule_data["is_trigger"]:
                # 如果已经触发规则，则异步计算数据同时返回
                async_handle_data()
                return rule_data

        # TODO 计算规则数据
        tmp_data = self.compute_data()

        # TODO 写数据
        ret = self.write_data()

        # TODO 写日志(异步)
        self.write_log()

        return ret

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

        # TODO 从数仓取数据
        big_data = self.big_query_data()
        if big_data:
            return
        return

    def compute_data(self):
        """
        计算数据
        """
        pass

    def write_data(self):
        """
        写数据
        """
        pass

    def write_log(self):
        """
        写日志
        """
        pass

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
        # 生成hash
        tmp_list = [self.rule.code]
        for i in self.need_params:
            tmp_list.append(self.params[i])
        tmp_str = "|".join(tmp_list)
        hash_code = hash_md5(tmp_str)

        # 获取数据
        cache_d = self.conn.get(hash_code)
        if not cache_d:
            return

        return cache_d


    def db_query_data(self):
        """
        本地库取数据
        """
        trigger = TriggerModel.query.filter_by(rule_id=self.rule.id).all()
        # 拿到所有触发ID，取所有触发的策略(数据正常情况，只会存在一个风险最高的一条策略)
        strategy = StrategyModel.query.filter(StrategyModel.trigger.in_(trigger)).one_or_none()
        if not strategy:
            return

        ret = dict()
        ret["rule"] = strategy.trigger.rule_id
        ret["strategy"] = strategy.id
        ret["is_trigger"] = False if strategy.count < strategy.trigger.count else True
        ret["dt"] = datetime_2_str_by_format(strategy.dt_dt_trigger)
        ret["info"] = strategy.trigger.return_info


    def big_query_data(self):
        """
        数仓取数据
        """
        pass
        return

    def async_handle_data(self):
        """
        异步处理数据
        """
        # TODO 计算规则数据
        tmp_data = self.compute_data()

        # TODO 写数据
        ret = self.write_data()

        # TODO 写日志(异步)
        self.write_log()
