# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Jin He, jin.he@yvertical.com
#
#

from .basehandler import BaseHandler

from ppmessage.core.constant import API_LEVEL

from ppmessage.db.models import AppInfo
from ppmessage.api.error import API_ERR
from ppmessage.core.redis import redis_hash_to_dict
from ppmessage.core.constant import API_LEVEL

import json
import logging

class PPGetAppInfoHandler(BaseHandler):

    def _get(self):
        _redis = self.application.redis

        _request = json.loads(self.request.body)
        
        _app_uuid = _request.get("app_uuid")
        if not _app_uuid:
            self.setErrorCode(API_ERR.NO_PARA)
            return
        _data = redis_hash_to_dict(_redis, AppInfo, _app_uuid)
        if _data == None:
            self.setErrorCode(API_ERR.NO_APP)
            return
        
        _r = self.getReturnData()
        for _i in _data:
            _r[_i] = _data[_i]

        return

    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        self.addPermission(api_level=API_LEVEL.PPCONSOLE)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_KEFU)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_CONSOLE)
        return
        
    def _Task(self):
        super(PPGetAppInfoHandler, self)._Task()            
        self._get()
        return
