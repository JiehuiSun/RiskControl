#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-08-30 21:58:29
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: urls.py


from .views.base_views import ConditionView


MODEL_NAME = "condition"

urls = ()

routing_dict = dict()
v1_routing_dict = dict()

#
v1_routing_dict["rule"] = ConditionView

for k, v in v1_routing_dict.items():
    routing_dict["/v1/{0}/".format(k)] = v
