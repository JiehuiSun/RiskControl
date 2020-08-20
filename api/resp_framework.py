#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-08-20 15:59:01
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: resp_framework.py


class _EvenException(Exception):
    _errcode_dict = {
        0: 'OK',
    }

    def __init__(self, errcode, errmsg=None, data=None):
        # print('dict: ', self._errcode_dict)
        # print('errcode', type(errcode), errcode)
        # print('errmsg', type(errmsg), errmsg)
        if not self._check_errcode(errcode):
            raise NotImplementedError(
                'errcode {0} is not implemented'.format(errcode))
        self.errcode = errcode
        self.errmsg = errmsg if errmsg else self.err_code_dict[errcode]
        self.data = data

    def _check_errcode(self, errcode):
        if errcode in self.err_code_dict:
            return True
        return False


class Resp(_EvenException):
    """
    返回封装
    每个模块的开头两位数不一样
    """
    err_code_dict = {
        # 其他
        10999: "其他错误",  # 找不到错误码使用(正常不会出现)

        # 参数
        10101: "参数不完整",
        10102: "参数错误",
        10103: "上传失败, 不支持的文件格式",

        # 数据库
        10901: "数据不存在或已被删除",
        10902: "未知的数据库错误",
        10903: "其他模块的数据库错误",
        10907: "操作失败",

        # 文案
        10201: "",

        # 第三方
    }

    @classmethod
    def ret(cls, errcode=0, errmsg="", data={}):
        ret = {
            "errcode": errcode,
            "errmsg": "OK",
            "data": data
        }

        if ret["errcode"] == 0:
            return ret

        if errcode not in cls.err_code_dict:
            ret["errcode"] = 10399
        if errmsg:
            ret["errmsg"] = "{0}({1})".format(cls.err_code_dict[ret["errcode"]], errmsg)
        else:
            ret["errmsg"] = cls.err_code_dict[ret["errcode"]]

        return ret
