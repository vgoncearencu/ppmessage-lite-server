# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler
from ppmessage.db.models import ConversationUserData
from ppmessage.api.error import API_ERR
from ppmessage.core.constant import API_LEVEL

import json
import logging

class PPOpenConversationHandler(BaseHandler):
    def _open(self, _user_uuid, _conversation_uuid):
        _redis = self.application.redis
        _key = ConversationUserData.__tablename__ + \
               ".user_uuid." + _user_uuid + \
               ".conversation_uuid." + _conversation_uuid
        _data_uuid = _redis.get(_key)
        if _data_uuid == None:
            self.setErrorCode(API_ERR.NO_CONVERSATION)
            return
        
        _row = ConversationUserData(uuid=_data_uuid, conversation_status=CONVERSATION_STATUS.OPEN)
        _row.async_update(_redis)
        _row.update_redis_keys(_redis)
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
        _conversation_uuid = _request.get("conversation_uuid")
        _user_uuid = _request.get("user_uuid")
        
        if not all([_conversation_uuid, _user_app]):
            self.setErrorCode(API_ERR.NO_PARA)
            return
        
        self._open(_user_uuid, _conversation_uuid)
        return

