# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.db.models import AppInfo
from ppmessage.db.models import DeviceUser

from ppmessage.api.error import API_ERR
from ppmessage.core.constant import API_LEVEL

from ppmessage.core.utils.config import _get_config

from ppmessage.core.redis import redis_hash_to_dict

import pypinyin
from pypinyin import lazy_pinyin
from pypinyin import pinyin

import base64
import os
import json
import time
import datetime
import itertools
import logging

class PPGetUserDetailHandler(BaseHandler):

    def _du(self):

        _request = json.loads(self.request.body)

        _user_uuid = _request.get("user_uuid")
        if not _user_uuid:
            self.setErrorCode(API_ERR.NO_PARA)
            return

        _o = redis_hash_to_dict(self.application.redis, DeviceUser, _user_uuid)
        if not _o:
            self.setErrorCode(API_ERR.NO_OBJECT)
            return

        # not return the password default
        return_password = False
        if "return_password" in _request:
            return_password = _request["return_password"]
        if not return_password:
            del _o["user_password"]
        
        _fn = _o.get("user_fullname")
        if _fn != None and not isinstance(_fn, unicode):
            _fn = _fn.decode("utf-8")

        _rdata = self.getReturnData()
        _rdata.update(_o)
        _rdata["pinyinname0"] = "".join(lazy_pinyin(_fn))
        _rdata["pinyinname1"] = "".join(list(itertools.chain.from_iterable(pinyin(_fn, style=pypinyin.INITIALS))))

        _app_uuid = _get_config().get("team").get("app_uuid")
        _o = redis_hash_to_dict(self.application.redis, AppInfo, _app_uuid)
        _rdata.update({"team": _o});
        return
    
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        self.addPermission(api_level=API_LEVEL.PPCONSOLE)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_KEFU)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_CONSOLE)
        return

    def _Task(self):
        super(self.__class__, self)._Task()
        self._du()


