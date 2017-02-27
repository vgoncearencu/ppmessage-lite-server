# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler
from ppmessage.api.error import API_ERR

from ppmessage.db.models import DeviceUser
from ppmessage.core.redis import redis_hash_to_dict

from ppmessage.core.constant import API_LEVEL

import json
import logging
import time

class PPGetUserInfoHandler(BaseHandler):
    def _get(self, _user_uuid):
        _redis = self.application.redis
        _user = redis_hash_to_dict(_redis, DeviceUser, _user_uuid)
        if _user is None:
            self.setErrorCode(API_ERR.NO_USER)
            return
        _r = self.getReturnData()
        _r.update(_user)
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
        _request = json.loads(self.request.body)
        _user_uuid = _request.get("user_uuid")
        if not _user_uuid:
            self.setErrorCode(API_ERR.NO_PARA)
            return
        self._get(_user_uuid)
        return
