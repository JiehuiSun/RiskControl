#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-08-30 10:59:42
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: backend.py


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


class BaseClass_(Rule):
    """
    基础类方法

    不建议直接引用
    """
    def __init__(self):
        self.model = None
        self.rule = None

        self.ver_params()
        self.init()


    def init(self):
        if not self.rule:
            raise "内部服务错误, 规则引用错误"
        if not self.rule_dict.get(self.rule):
            raise "内部服务错误, 规则CODE错误"

        self.need_params, self.other_params = self.rule_params[self.rule]
        self.all_params = self.need_params + self.other_params

        self.rule = RuleModel.query.filter_by(code=self.rule).one_or_none()
        if not self.rule:
            raise "内部服务器错误, 规则数据错误"

        # self.rule_func = getattr(self, self.rule)

    def ver_params(self):
        pass


class ConditionRule(BaseClass_):
    """
    条件规则
    """
    def __init__(self, rule_id, params):
        """
        TODO 其实校验参数可做有参装饰器
        """
        self.rule = rule_id
        self.ver_params()
        self.init()

    def add(self, params):
        """
        添加
        """
        pass

    def list(self, params):
        """
        详情
        """
        pass

