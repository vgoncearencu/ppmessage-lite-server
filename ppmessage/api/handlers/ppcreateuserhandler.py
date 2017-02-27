# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.api.error import API_ERR

from ppmessage.db.models import DeviceUser

from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import USER_STATUS
from ppmessage.core.utils.randomidenticon import random_identicon
from ppmessage.core.utils.randomidenticon import download_random_identicon

import json
import uuid
import logging

from tornado.ioloop import IOLoop

def create_user(_redis, _request):
    
    _user_email = _request.get("user_email")
    _user_fullname = _request.get("user_fullname")
    _user_password = _request.get("user_password")
    _is_service_user = _request.get("is_service_user")
    
    if not all([_user_email, _user_fullname]):
        return None

    _key = DeviceUser.__tablename__ + ".user_email." + _user_email
    if _redis.exists(_key):
        return None
        
    if _is_service_user == None:
        _is_service_user = False

    _user_icon = random_identicon(_user_email)

    IOLoop.current().spawn_callback(download_random_identicon, _user_icon)
    
    _du_uuid = str(uuid.uuid1())
    
    _values = {
        "uuid": _du_uuid,
        "user_name": _user_fullname,
        "user_email": _user_email,
        "user_icon": _user_icon,
        "user_fullname": _user_fullname,
        "user_password": _user_password,
        "is_removed_user": False,
        "is_anonymous_user": False,
        "is_service_user": _is_service_user,
        "is_owner_user": False
    }
    
    _row = DeviceUser(**_values)
    _row.async_add(_redis)
    _row.create_redis_keys(_redis)
    _user_values = _values
    
    return _user_values

class PPCreateUserHandler(BaseHandler):
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        return

    def _Task(self):
        super(self.__class__, self)._Task()
        _request = json.loads(self.request.body)
        
        _user_email = _request.get("user_email")
        _user_fullname = _request.get("user_fullname")
        
        if not all([_user_email, _user_fullname]):
            self.setErrorCode(API_ERR.NO_PARA)
            return

        _key = DeviceUser.__tablename__ + ".user_email." + _user_email
        if self.application.redis.exists(_key):
            self.setErrorCode(API_ERR.EX_USER)
            return

        _rdata = create_user(self.application.redis, _request)
        if _rdata == None:
            self.setErrorCode(API_ERR.NO_PARA)
            return

        _r = self.getReturnData()
        _r.update(_rdata)
        return
