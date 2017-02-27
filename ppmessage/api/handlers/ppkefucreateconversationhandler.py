# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
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

from ppmessage.dispatcher.policy import BroadcastPolicy

from ppmessage.core.utils.createicon import create_group_icon
from ppmessage.core.utils.datetimestring import datetime_to_microsecond_timestamp

import copy
import uuid
import json
import time
import logging
import datetime

class Conversation():
    def _result_data(self, _conversation):
        _now = datetime.datetime.now()
        _rdata = {}
        _rdata["user_list"] = [self._peer_uuid]        
        _rdata["uuid"] = _conversation["uuid"]
        _rdata["user_uuid"] = self._user_uuid
        _rdata["peer_uuid"] = self._peer_uuid
        _rdata["status"] = CONVERSATION_STATUS.NEW
        _rdata["conversation_name"] = self._peer_name
        _rdata["conversation_icon"] = self._peer_icon
        _rdata["updatetime"] = _now
        _rdata["createtime"] = _now
        return _rdata
        
    def _userdata(self, _conversation):
        _redis = self._redis
        _conversation_uuid = _conversation["uuid"]
        
        _values = {
            "uuid": str(uuid.uuid1()),
            "user_uuid": self._user_uuid,
            "peer_uuid": self._peer_uuid,
            "conversation_uuid": _conversation_uuid,
            "conversation_name": self._peer_name,
            "conversation_icon": self._peer_icon,
            "conversation_status": CONVERSATION_STATUS.NEW,
        }
        
        _row = ConversationUserData(**_values)
        _row.async_add(self._redis)
        _row.create_redis_keys(self._redis)

        _values = {
            "uuid": str(uuid.uuid1()),
            "user_uuid": self._peer_uuid,
            "peer_uuid": self._user_uuid,
            "conversation_uuid": _conversation_uuid,
            "conversation_name": self._user_name,
            "conversation_icon": self._user_icon,
            "conversation_status": CONVERSATION_STATUS.NEW,
        }
        
        _row = ConversationUserData(**_values)
        _row.async_add(self._redis)
        _row.create_redis_keys(self._redis)

        return

    def _create(self):
        _key = DeviceUser.__tablename__ + ".uuid." + self._user_uuid
        _user = self._redis.hmget(_key, ["user_icon", "user_fullname"])
        self._user_icon = _user[0]
        self._user_name = _user[1]

        self._peer_uuid = self._member_list[0]
        _key = DeviceUser.__tablename__ + ".uuid." + self._peer_uuid
        
        self._peer_icon = self._redis.hget(_key, "user_icon")
        self._peer_name = self._redis.hget(_key, "user_fullname")
    
        _conv_uuid = str(uuid.uuid1())
        _values = {
            "uuid": _conv_uuid,
            "user_uuid": self._user_uuid,
        }
        # create it
        _row = ConversationInfo(**_values)
        _row.async_add(self._redis)
        _row.create_redis_keys(self._redis)

        self._userdata(_values)

        return self._result_data(_values)

    def create(self, _handler, _request):
        self._handler = _handler
        self._redis = _handler.application.redis
        
        self._user_uuid = _request.get("user_uuid")
        self._member_list = _request.get("member_list")
        
        if self._member_list != None and isinstance(self._member_list, list) == True:
            self._member_list = list(set(self._member_list))

        if len(self._member_list) != 1:
            logging.error("NOT SUPPORT MULTIPLE USER")
            return False
        
        return self._create()
        

class PPKefuCreateConversationHandler(BaseHandler):
    """
    For the member_list length == 1, if the conversation has been created 
    return the existed conversation

    For the group_uuid != None, if the conversation has been created
    return the existed conversation
    
    """
    def _return(self, _conversation_uuid):
        _conversation = redis_hash_to_dict(self.application.redis, ConversationInfo, _conversation_uuid)
        if _conversation == None:
            self.setErrorCode(API_ERR.NO_CONVERSATION)
            return
        _r = self.getReturnData()
        _r.update(_conversation)
        return
    
    def _existed(self, _request):
        _user_uuid = _request.get("user_uuid")
        _member_list = _request.get("member_list")
        _redis = self.application.redis
                
        if _member_list != None and isinstance(_member_list, list) == True and len(_member_list) == 1:
            _peer_uuid = _member_list[0]
            if not _peer_uuid:
                return False
            
            _key = ConversationUserData.__tablename__ + \
                   ".user_uuid." + _user_uuid + \
                   ".peer_uuid." + _peer_uuid
            _conversation_data_uuid = _redis.get(_key)

            if not _conversation_data_uuid:
                return False

            _key = ConversationUserData.__tablename__ + ".uuid." + _conversation_data_uuid
            _conversation_data = _redis.hgetall(_key)
            _key = ConversationInfo.__tablename__ + ".uuid." + _conversation_data.get("conversation_uuid")
            _conversation = _redis.hgetall(_key)
            _conversation_data.pop("uuid")
            _r = self.getReturnData()
            _r.update(_conversation)
            _r.update(_conversation_data)
            return True

        if _member_list != None and isinstance(_member_list, list) == True and len(_member_list) > 1:
            logging.error("NO SUPPORT MULTIPLE USER")
            return False

        return False

    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPKEFU)
        return
    
    def _Task(self):
        super(self.__class__, self)._Task()
        _request = json.loads(self.request.body)

        _user_uuid = _request.get("user_uuid")        
        _member_list = _request.get("member_list")
        
        if not _user_uuid or not _member_list:
            self.setErrorCode(API_ERR.NO_PARA)
            return

        if self._existed(_request):
            return

        _conv = Conversation()
        _r = _conv.create(self, _request)
        if _r != None:
            _res = self.getReturnData()
            _res.update(_r)
        return

