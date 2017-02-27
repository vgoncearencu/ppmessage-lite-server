# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.api.error import API_ERR
from ppmessage.db.models import AppInfo

from ppmessage.core.constant import API_LEVEL
from ppmessage.core.redis import redis_hash_to_dict
from ppmessage.core.genericupdate import generic_update

import json
import copy
import logging

class PPUpdateAppInfoHandler(BaseHandler):
    def _update(self, _request):
        _redis = self.application.redis
        _request = json.loads(self.request.body)

        _data = copy.deepcopy(_request)
        del _data["app_uuid"]

        if len(_data) > 0:
            _updated = generic_update(_redis, AppInfo, _app_uuid, _data)
            if not _updated:
                self.setErrorCode(API_ERR.GENERIC_UPDATE)
                return

        _app = redis_hash_to_dict(_redis, AppInfo, _app_uuid)
        _r = self.getReturnData()
        _r.update(_app)
        return

    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCONSOLE)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_CONSOLE)
        return
    
    def _Task(self):
        super(self.__class__, self)._Task()
        _request = json.loads(self.request.body)
        self._update(_request)
        return

