#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-08-30 21:53:04
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: base_views.py


from api import Api
from ..backend import ConditionRule


class ConditionView(Api):
    """
    条件规则视图
    """
    NEED_LOGIN = False

    def post(self):
        self.params_dict = {
            "rule": "required int",
            "data": "required dict"
        }

        self.ver_params()

        condition = ConditionRule(self.data["rule"], self.data["data"])
        ret_data = condition.add()
        print(ret_data)
        ret = {
            "pass": 1 - ret_data["is_trigger"],
            "dt": ret_data["dt"],
            "message": ret_data["info"],
            "level": ret_data["level"]
        }

        return self.ret(data=ret)
