# 这里将url进行统一的管理，每添加一个接口，只需要在urls中添加即可
from flask import Blueprint

from account.views.test.tests import Test

instance = Blueprint('even', __name__)

urls = ()

version = "v1"

# login
urls += (
    ('/{0}/{1}/'.format(version, "test"), Test.as_view("test")),
)

methods = ['GET', 'POST', 'PUT', 'DELETE']
for path, view in urls:
    instance.add_url_rule(path, view_func=view, methods=methods)
