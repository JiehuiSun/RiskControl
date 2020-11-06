
import json
import mimetypes
import requests
import pymysql
from flask import current_app
from flask_mail import Message


class Requests(object):
    """
    封装requests模块
    """
    @classmethod
    def handle_req(self, method, url, **kwargs):
        req = getattr(requests, method)
        if not req:
            return json.dumps({"errcode": 10000, "errmsg": "不支持的请求"})
        headers_dict = kwargs.get("headers", dict())
        if not headers_dict.get("X-MUMWAY-TRACEID"):
            from datacenter import redis
            headers_dict["X-MUMWAY-TRACEID"] = redis.client.get("X-MUMWAY-TRACEID")

        kwargs["headers"] = headers_dict
        return req(url, **kwargs)

    @classmethod
    def get(self, url, params=None, **kwargs):
        return self.handle_req("get", url, params=params, **kwargs)

    @classmethod
    def post(self, url, data=None, json=None, **kwargs):
        return self.handle_req("post", url, data=data, json=json, **kwargs)

    @classmethod
    def put(self, url, data=None, **kwargs):
        return self.handle_req("put", url, data=data, **kwargs)

    @classmethod
    def delete(self, url, **kwargs):
        return self.handle_req("delete", url, **kwargs)

    @classmethod
    def options(self, url, **kwargs):
        return self.handle_req("delete", url, **kwargs)