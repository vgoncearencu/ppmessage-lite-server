# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.db.models import ApiInfo
from ppmessage.api.error import API_ERR
from ppmessage.core.constant import API_LEVEL

import json
import logging

class PPGetApiInfoHandler(BaseHandler):

    def _get(self):
        _redis = self.application.redis
        _user_uuid = self.user_uuid

        _r = self.getReturnData()

        _key = ApiInfo.__tablename__ + \
               ".user_uuid." + _user_uuid + \
               ".api_level." + API_LEVEL.PPCOM
        _d = _redis.get(_key)
        if not _d:
            self.setErrorCode(API_ERR.WR_PARA)
            return

        _a = json.loads(_d)
        _ppcom = {
            "api_uuid": _a[0],
            "api_level": _a[1],
            "api_key": _a[2],
            "api_secret": _a[3]
        }
        _r["ppcom"] = _ppcom

        return
        
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        return

    def _Task(self):
        super(PPGetApiInfoHandler, self)._Task()
        _user_uuid = json.loads(self.request.body).get("user_uuid")
        if _user_uuid == None:
            self.setErrorCode(API_ERR.NO_PARA)
            return
        self.user_uuid = _user_uuid
        self._get()
        return
