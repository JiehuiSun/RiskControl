#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-09-08 15:06:21
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: rule_conf.py


from .models.base_models import SourceDataByContractSignModel


class Rule(object):
    """
    规则

    TODO 该类为配置类，可以提取后台配置
    """
    rule_dict = {
        1001: "contract_sign_user"
    }

    rule_params = {
        1001: (("idcard", "name"), ("phone",)),
    }

    rule_sql = {
        1001: "query_contract_sign_user_data"
    }

    def query_contract_sign_user_data(self):
        """
        获取合同签署用户数据

        TODO 目前先只返回计数
        """
        query_list = SourceDataByContractSignModel.query.filter_by(status=1)
        query_list = query_list.filter_by(name=self.params["name"])
        query_list = query_list.filter_by(identity_no=self.params["idcard"])
        # query_list = query_list.filter_by(name=self.params["name"])

        ret = {
            "count": query_list.count()
        }

        return ret
