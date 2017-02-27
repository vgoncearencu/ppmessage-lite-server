# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
# 
#

from .basehandler import BaseHandler

from ppmessage.db.models import DeviceInfo
from ppmessage.db.models import DeviceUser
from ppmessage.db.models import ApiTokenData

from ppmessage.api.error import API_ERR

from ppmessage.core.constant import API_LEVEL

from ppmessage.core.redis import redis_hash_to_dict

import datetime
import logging
import json
import uuid

class PPKefuLogoutHandler(BaseHandler):

    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        return
    
    def _delete_auth_token(self):
        _key = ApiTokenData.__tablename__ + \
               ".api_token." + self.api_token
        _uuid = self.application.redis.get(_key)
        if not _uuid:
            return
        _row = ApiTokenData(uuid=_uuid)
        _row.delete_redis_keys(self.application.redis)
        _row.async_delete(self.application.redis)
        return
    
    def _Task(self):    
        super(PPKefuLogoutHandler, self)._Task()
        _input = json.loads(self.request.body)

        _user_uuid = _input.get("user_uuid")
        _device_uuid = _input.get("device_uuid")
    
        if not all([_user_uuid, _device_uuid]):
            self.setErrorCode(API_ERR.NO_PARA)
            return False

        self.user_uuid = _user_uuid
        self.device_uuid = _device_uuid
        
        logging.info("DEVICEUSERLOGOUT with: %s." % str(self.request_body))
        self._delete_auth_token()
        return
