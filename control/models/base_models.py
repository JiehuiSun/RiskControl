#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-08-27 16:26:11
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: base_models.py


from base import db
from utils import time_utils


class RuleModel(db.Model):
    """
    规则表
    """
    __tablename__ = "rule_model"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False, comment="规则CODE")
    contents = db.Column(db.Text, nullable=False, comment="规则信息")
    comments = db.Column(db.Text, nullable=False, comment="备注")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class ExpireModel(db.Model):
    """
    期效表
    """
    __tablename__ = "expire_model"

    id = db.Column(db.Integer, primary_key=True)
    expire_day = db.Column(db.Integer, nullable=False, comment="过期日")
    expire_week = db.Column(db.Integer, nullable=False, comment="过期周")
    expire_month = db.Column(db.Integer, nullable=False, comment="过期月")
    comments = db.Column(db.Text, nullable=False, comment="备注")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)


class TriggerModel(db.Model):
    """
    触发器表
    """
    __tablename__ = "trigger_model"

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.ForeignKey("rule_model.id"))
    rule = db.relationship('RuleModel', backref=db.backref('trigger_model', lazy='dynamic'))
    count = db.Column(db.Integer, nullable=False, comment="计数")
    duration = db.Column(db.Integer, nullable=False, comment="时效(s)")
    expire_id = db.Column(db.ForeignKey("expire_model.id"))
    expire = db.relationship('ExpireModel', backref=db.backref('trigger_model', lazy='dynamic'))
    level = db.Column(db.Integer, nullable=False, default=1, comment="风险等级")
    comments = db.Column(db.Text, nullable=False, comment="备注")
    return_info = db.Column(db.Text, nullable=False, comment="返回信息")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class StrategyModel(db.Model):
    """
    策略表
    """
    __tablename__ = "strategy_model"

    id = db.Column(db.Integer, primary_key=True)
    trigger_id = db.Column(db.ForeignKey("trigger_model.id"))
    trigger = db.relationship('TriggerModel', backref=db.backref('strategy_model', lazy='dynamic'))
    count = db.Column(db.Integer, nullable=False, comment="计数")
    need_code = db.Column(db.String(64), nullable=False, comment="需要的唯一码")
    req_code = db.Column(db.String(64), nullable=False, comment="请求的唯一码")
    dt_trigger = db.Column(db.DateTime, default=time_utils.now_dt, comment="第一次触发时间")
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class AlreadyTriggerModel(db.Model):
    """
    已经触发表
    """
    __tablename__ = "already_trigger_model"

    id = db.Column(db.Integer, primary_key=True)
    trigger_id = db.Column(db.ForeignKey("trigger_model.id"))
    trigger = db.relationship('TriggerModel', backref=db.backref('strategy_model', lazy='dynamic'))
    dt_trigger = db.Column(db.DateTime, default=time_utils.now_dt, comment="第一次触发时间")
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)


class ReqLogsModel(db.Model):
    """
    日志表
    """
    __tablename__ = "req_logs_model"

    id = db.Column(db.Integer, primary_key=True)
    trigger_id = db.Column(db.ForeignKey("trigger_model.id"))
    trigger = db.relationship('TriggerModel', backref=db.backref('strategy_model', lazy='dynamic'))
    info = db.Column(db.Text, comment="请求内容")
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
