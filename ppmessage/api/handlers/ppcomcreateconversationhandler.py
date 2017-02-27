# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.db.models import AppInfo
from ppmessage.db.models import FileInfo
from ppmessage.db.models import DeviceUser
from ppmessage.db.models import ConversationInfo
from ppmessage.db.models import ConversationUserData

from ppmessage.core.redis import redis_hash_to_dict

from ppmessage.api.error import API_ERR

from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import CONVERSATION_TYPE
from ppmessage.core.constant import CONVERSATION_STATUS

import copy
import uuid
import json
import time
import hashlib
import logging
import datetime

class PPComCreateConversationHandler(BaseHandler):
    def _return(self, _conversation_uuid, _request):
        _redis = self.application.redis
        _user_uuid = _request.get("user_uuid")
        
        _conversation = redis_hash_to_dict(_redis, ConversationInfo, _conversation_uuid)
        if not _conversation:
            self.setErrorCode(API_ERR.NO_CONVERSATION)
            return False
        
        _r = self.getReturnData()
        _r.update(_conversation)
        
        _key = ConversationUserData.__tablename__ + \
               ".user_uuid." + _user_uuid + \
               ".conversation_uuid." + _conversation_uuid
        
        _data_uuid = _redis.get(_key)
        if not _data_uuid:
            self.setErrorCode(API_ERR.NO_CONVERSATION)
            return False
        
        _key = ConversationUserData.__tablename__ + ".uuid." + _data_uuid
        _data = _redis.hgetall(_key)
        _data.pop("uuid")
        _data.pop("createtime")
        _data.pop("updatetime")
        _r.update(_data)

        return True

    def _create(self, _member_uuid, _request):
        _user_uuid = _request.get("user_uuid")
        _redis = self.application.redis

        _key = DeviceUser.__tablename__ + ".uuid." + _user_uuid
        _portal_user_name = _redis.hget(_key, "user_fullname")
        _portal_user_icon = _redis.hget(_key, "user_icon")

        _key = DeviceUser.__tablename__ + ".uuid." + _member_uuid
        _member_user_name = _redis.hget(_key, "user_fullname")
        _member_user_icon = _redis.hget(_key, "user_icon")
        
        _conversation_uuid = str(uuid.uuid1())
        _values = {
            "uuid": _conversation_uuid,
            "user_uuid": _user_uuid
        }
        # create it
        _row = ConversationInfo(**_values)
        _row.async_add(_redis)
        _row.create_redis_keys(_redis)

        _row = ConversationUserData(uuid=str(uuid.uuid1()),
                                    user_uuid=_user_uuid,
                                    peer_uuid=_member_uuid,
                                    conversation_uuid=_conversation_uuid,
                                    conversation_type=CONVERSATION_TYPE.P2S,
                                    conversation_name=_member_user_name,
                                    conversation_icon=_member_user_icon,
                                    conversation_status=CONVERSATION_STATUS.NEW)
        _row.async_add(_redis)
        _row.create_redis_keys(_redis)

        _row = ConversationUserData(uuid=str(uuid.uuid1()),
                                    user_uuid=_member_uuid,
                                    peer_uuid=_user_uuid,
                                    conversation_uuid=_conversation_uuid,
                                    conversation_type=CONVERSATION_TYPE.S2P,
                                    conversation_name=_portal_user_name,
                                    conversation_icon=_portal_user_icon,
                                    conversation_status=CONVERSATION_STATUS.NEW)
        _row.async_add(_redis)
        _row.create_redis_keys(_redis)

        logging.info("return from new")
        return self._return(_conversation_uuid, _request)
    
    def _existed(self, _request):
        _user_uuid = _request.get("user_uuid")
        _member_list = _request.get("member_list")
        _redis = self.application.redis

        if not _member_list or not isinstance(_member_list, list) or len(_member_list) != 1:
            return False

        _peer_uuid = _member_list[0]
        if not _peer_uuid:
            return False
            
        _key = ConversationUserData.__tablename__ + \
               ".user_uuid." + _user_uuid + \
               ".peer_uuid." + _peer_uuid
        _conversation_data_uuid = _redis.get(_key)
        if not _conversation_data_uuid:
            return False
            
        _key = ConversationUserData.__tablename__ + \
               ".uuid." + _conversation_data_uuid

        _conversation_uuid = _redis.hget(_key, "conversation_uuid")
        if not _conversation_uuid:
            return False

        logging.info("return from existed")
        return self._return(_conversation_uuid, _request)


    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        return
    
    def _Task(self):
        super(PPComCreateConversationHandler, self)._Task()
        _request = json.loads(self.request.body)
        _user_uuid = _request.get("user_uuid")
        _member_list = _request.get("member_list")
        
        if not _user_uuid:
            self.setErrorCode(API_ERR.NO_PARA)
            return

        if self._existed(_request):
            return

        # assume ppcom only want to talk with only one
        if _member_list != None and isinstance(_member_list, list) == True and len(_member_list) == 1:
            return self._create(_member_list[0], _request)

        if len(_member_list) > 1:
            self.setErrorCode(API_ERR.WRONG_PARA)
            logging.error("NO SUPPORT MULTIPLE USERS")
            return
        
        return

