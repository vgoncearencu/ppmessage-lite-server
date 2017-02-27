# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.db.models import ConversationUserData
from ppmessage.db.models import ConversationInfo
from ppmessage.db.models import DeviceUser

from ppmessage.api.error import API_ERR
from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import CONVERSATION_TYPE

import json
import logging

class PPGetConversationUserListHandler(BaseHandler):
    """
    """
    def _get(self, _conversation_uuid):
        _redis = self.application.redis
        _key = ConversationUserData.__tablename__ + \
               ".conversation_uuid." + _conversation_uuid
        _uuids = _redis.smembers(_key)

        _users = []
        for _user_uuid in _uuids:
            _key = DeviceUser.__tablename__ + ".uuid." + _user_uuid
            _users.append(_redis.hgetall(_key))            
        _r = self.getReturnData()
        _r["list"] = _users
        return

    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        self.addPermission(api_level=API_LEVEL.PPCONSOLE)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_KEFU)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_CONSOLE)
        return

    def _Task(self):
        super(PPGetConversationUserListHandler, self)._Task()
        _request = json.loads(self.request.body)
        _conversation_uuid = _request.get("conversation_uuid")
        if not _conversation_uuid:
            self.setErrorCode(API_ERR.NO_PARA)
            return
        self._get(_conversation_uuid)
        return

