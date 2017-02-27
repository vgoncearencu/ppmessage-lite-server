# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from ppmessage.api.handlers.basehandler import BaseHandler

from ppmessage.db.models import AppInfo
from ppmessage.db.models import DeviceUser
from ppmessage.db.models import DeviceInfo
from ppmessage.db.models import PCSocketInfo
from ppmessage.db.models import MessagePushTask
from ppmessage.db.models import PCSocketDeviceData

from ppmessage.api.error import API_ERR

from ppmessage.core.constant import OS
from ppmessage.core.constant import YVOBJECT
from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import TASK_STATUS
from ppmessage.core.constant import MESSAGE_TYPE
from ppmessage.core.constant import MESSAGE_SUBTYPE
from ppmessage.core.constant import SERVICE_USER_STATUS

from ppmessage.core.utils.config import _get_config
from ppmessage.core.redis import redis_hash_to_dict

import traceback
import datetime
import logging
import hashlib
import json
import uuid
import time

class PPKefuLoginHandler(BaseHandler):
   
    def _create_device(self):
        _osmodel = self.input_data.get("osmodel")
        _osversion = self.input_data.get("osversion")
        _device_fullname = self.input_data.get("device_fullname")
        _device_uuid = str(uuid.uuid1())
        _values = {
            "uuid": _device_uuid,
            "terminal_uuid": self._terminal_uuid,
            "user_uuid": self.user.get("uuid"),
            "device_ostype": self._ostype,
            "device_ios_model": _osmodel,
            "device_osversion": _osversion,
            "device_fullname": _device_fullname        
        }
        _row = DeviceInfo(**_values)
        _row.create_redis_keys(self.application.redis)
        _row.async_add(self.application.redis)
        return _values

    def _user_with_email(self):
        _redis = self.application.redis
        _key = DeviceUser.__tablename__ + ".user_email." + self._user_email

        if not _redis.exists(_key):
            self.setErrorCode(API_ERR.NO_USER)
            return False
        
        _user_uuid = _redis.get(_key)
        _user = redis_hash_to_dict(_redis, DeviceUser, _user_uuid)

        if _user == None:
            self.setErrorCode(API_ERR.NO_USER)
            return False

        self.user = _user
        return True
    
    def _update_user_with_device(self, _user_uuid, _device_uuid):
        _values = {"uuid": _user_uuid}
        _values["ppkefu_browser_device_uuid"] = _device_uuid
        _row = DeviceUser(**_values)
        _row.async_update(self.application.redis)
        _row.update_redis_keys(self.application.redis)
        return

    def _update_device_with_user(self, _device_uuid, _user_uuid):
        _values = {
            "uuid": _device_uuid,
            "user_uuid": _user_uuid,
        }
        _row = DeviceInfo(**_values)
        _row.update_redis_keys(self.application.redis)
        _row.async_update(self.application.redis)
        return
        
    #L2=========================================

    def _parameter(self, _p):
        if _p == None or len(_p) == 0:
            self.setErrorCode(API_ERR.NO_PARA)
            return False
        return True
    
    def _check_input(self):
        self.input_data = json.loads(self.request.body)

        self._terminal_uuid = self.input_data.get("terminal")
        if not self._parameter(self._terminal_uuid):
            return False
        
        self._user_email = self.input_data.get("user_email")
        if not self._parameter(self._user_email):
            return False

        self._ostype = self.input_data.get("ostype")
        if not self._parameter(self._ostype):
            return False
        self._ostype = self._ostype[:3].upper()

        return True

    def _device(self):
        self._terminal_uuid = self.input_data["terminal"]
        
        _device = None
        _redis = self.application.redis
        _key = DeviceInfo.__tablename__ + ".terminal_uuid." + self._terminal_uuid
        _device = redis_hash_to_dict(_redis, DeviceInfo, _redis.get(_key))
        
        if _device == None:
            return self._create_device()
        
        return _device

    def _return(self):
        _redis = self.application.redis
        _user = redis_hash_to_dict(_redis, DeviceUser, self.user.get("uuid"))
        _r = self.getReturnData()
        _r.update(_user)

        _app_uuid = _get_config().get("team").get("app_uuid")
        _key = AppInfo.__tablename__ + ".uuid." + _app_uuid
        _r["app"] = _redis.hgetall(_key)

        logging.info("PPKEFULOGIN RETURN: %s" % _r)
        return


    #L1============================================
    def _login(self):
        self.input_data = None
        self.user = None
        self.device = None

        logging.info(self.request.body)
        if not self._check_input():
            self.setErrorCode(API_ERR.NO_PARA)
            return

        if not self._user_with_email():
            self.setErrorCode(API_ERR.NO_USER)
            return

        self.device = self._device()
        if not self.device:
            self.setErrorCode(API_ERR.NO_DEVICE)
            return

        self._update_device_with_user(self.device.get("uuid"), self.user.get("uuid"))        
        self._update_user_with_device(self.user.get("uuid"), self.device.get("uuid"))
        self._return()

        return

    #L0============================================
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        return

    def _Task(self):
        super(self.__class__, self)._Task()
        self._login()
        return
