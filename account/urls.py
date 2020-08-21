# 这里将url进行统一的管理，每添加一个接口，只需要在urls中添加即可
from flask import Blueprint

from account.views.test.tests import Test

instance = Blueprint('even', __name__)

MODEL_NAME = "account"

urls = ()

routing_dict = dict()
v1_routing_dict = dict()

# login
v1_routing_dict["test"] = Test

for k, v in v1_routing_dict.items():
    routing_dict["/v1/{0}/".format(k)] = v
