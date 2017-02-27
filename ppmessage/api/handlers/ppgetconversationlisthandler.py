# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
# kun.zhao@yvertical.com
#
#

from .basehandler import BaseHandler

from ppmessage.api.error import API_ERR
from ppmessage.db.models import ConversationInfo
from ppmessage.core.redis import redis_hash_to_dict

from ppmessage.core.constant import API_LEVEL

from ppmessage.core.utils.deviceuserinfoutils import get_device_user_info
from ppmessage.core.utils.messageutils import get_message_info
from ppmessage.core.utils.messageutils import get_message_count
from ppmessage.core.utils.messageutils import get_app_conversations

import json
import logging

class PPGetConversationListHandler(BaseHandler):
    def _get(self):
        _redis = self.application.redis
        _conversations = self._get_app_conversations(_redis)
        _l = []
        for _conversation_uuid in _conversations:
            if _conversation_uuid == None:
                continue
            
            _data = redis_hash_to_dict(_redis, ConversationInfo, _conversation_uuid)
            if _data == None or _data.get("latest_task") == None:
                continue

            # we add user_info here for convenient client to use
            _data['create_user'] = self._get_user_info(_redis, _data['user_uuid'])

            # we add latest message info here for convenient client to use
            _data['latest_message'] = self._get_latest_message(_redis, _data['latest_task'])

            # add message total count
            _data['message_total_count'] = self._get_message_count(_redis, _data['uuid'])
                
            _l.append(_data)

        _r = self.getReturnData()
        _r["list"] = _l
        return

    def _get_app_conversations(self, redis):
        return get_app_conversations(redis)
    
    def _get_user_info(self, redis, user_uuid):
        return get_device_user_info(redis, user_uuid)

    def _get_latest_message(self, redis, task_uuid):
        return get_message_info(redis, task_uuid)

    def _get_message_count(self, redis, conversation_uuid):
        return get_message_count(redis, conversation_uuid)

    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)        
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        self.addPermission(api_level=API_LEVEL.PPCONSOLE)        
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_KEFU)
        self.addPermission(api_level=API_LEVEL.THIRD_PARTY_CONSOLE)
        return
    
    def _Task(self):
        super(self.__class__, self)._Task()
        self._get()
        return

        
