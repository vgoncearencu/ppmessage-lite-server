# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 .
# Guijin Ding, dingguijin@gmail.com
#
#
# ppgetdefaultconversationhandler.py
# PPCOM get default conversation
# and the conversation users except himself
#

from .basehandler import BaseHandler

from ppmessage.db.models import AppInfo
from ppmessage.db.models import DeviceUser
from ppmessage.db.models import ConversationInfo
from ppmessage.db.models import ConversationUserData

from ppmessage.core.redis import redis_hash_to_dict

from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import PPCOM_WELCOME
from ppmessage.core.constant import DATETIME_FORMAT
from ppmessage.core.constant import CONVERSATION_TYPE
from ppmessage.core.constant import CONVERSATION_STATUS

from ppmessage.core.constant import REDIS_AMD_KEY

from ppmessage.core.utils.config import _get_config

from ppmessage.core.utils.datetimeencoder import DateTimeEncoder

from ppmessage.api.error import API_ERR

from operator import attrgetter
from operator import itemgetter

import json
import time
import uuid
import logging
import hashlib
import datetime

class PPComGetDefaultConversationHandler(BaseHandler):

    def _return_conversation(self, _user_uuid, _conversation_uuid):
        _redis = self.application.redis
        _conversation = redis_hash_to_dict(_redis, ConversationInfo, _conversation_uuid)

        if _conversation == None:
            logging.error("no such conversation info: %s" % _conversation_uuid)
            return None

        _key = ConversationUserData.__tablename__ + \
               ".user_uuid." + _user_uuid + \
               ".conversation_uuid." + _conversation_uuid
        _data_uuid = _redis.get(_key)
        if _data_uuid != None:
            _key = ConversationUserData.__tablename__ + ".uuid." + _data_uuid
            _data = _redis.hmget(_key, ["conversation_name", "conversation_icon"])
            _conversation["conversation_name"] = _data[0]
            _conversation["conversation_icon"] = _data[1]
        else:
            logging.error("no conversation data for conversation_uuid: %s" % _conversation_uuid)

        _conversation.update({"conversation_uuid": _conversation.get("uuid")})
        return _conversation

    def _get_users(self, _users):
        if _users == None:
            return None
        
        _redis = self.application.redis
        _pi = _redis.pipeline()
        _pre = DeviceUser.__tablename__ + ".uuid."
        for _user_uuid in _users:
            _key = _pre + _user_uuid
            _pi.hgetall(_key)
        _unsort = _pi.execute()

        _return_datas = []
        for _user in _unsort:
            if len(_user) == 0:
                continue
            _return_datas.append(_user)

        return _return_datas

    def _sort_users(self, _users):
        _redis = self.application.redis
        for _user in _users:
            _updatetime = datetime.datetime.strptime(_user["updatetime"], DATETIME_FORMAT["extra"])
            _user["updatetime"] = int(time.mktime(_updatetime.timetuple()))
        _sorted = sorted(_users, key=itemgetter("updatetime"), reverse=True)
        _return = []

        for _user in _sorted:
            _return.append(_user)        
        return _return
    
    def _get_app_welcome(self, _r):
        _app_uuid = _get_config().get("team").get("app_uuid")
        _key = AppInfo.__tablename__ + ".uuid." + _app_uuid

        _language = self.application.redis.hget(_key, "app_language")
        if not _language:
            _language = "zh_cn"
        
        _welcome = self.application.redis.hget(_key, "welcome_message")
        if not _welcome:
            _welcome = PPCOM_WELCOME.get(_language)

        _r["app_language"] = _language
        _r["app_welcome"] = _welcome
        _r["app_name"] = self.application.redis.hget(_key, "app_name")
        return _r
       
    def _user_conversations(self, _user_uuid):
        _key = ConversationUserData.__tablename__ + \
               ".user_uuid." + _user_uuid
        _conversations = self.application.redis.smembers(_key)
        return _conversations

    def _conversation_users(self, _conversation):
        _key = ConversationUserData.__tablename__ + \
               ".conversation_uuid." + _conversation.get("uuid")
        return self.application.redis.smembers(_key)
    
    def _latest_conversation(self, _conversations):
        _pi = self.application.redis.pipeline()
        _pre = ConversationInfo.__tablename__ + ".uuid."
        for _conversation in _conversations:
            _key = _pre + _conversation
            _pi.hgetall(_key)
        _unsorted = _pi.execute()
        _sorted = sorted(_unsorted, key=itemgetter("updatetime"), reverse=True)
        return _sorted[0]

    
    def _new_conversation(self):
        _service_users = DeviceUser.__tablename__ + ".is_service_user.True"
        _service_users = self.application.redis.smembers(_service_users)

        if not _service_users:
            logging.error("no service user ???????")
            return

        _service_users = list(_service_users)
        _peer_uuid = _service_users[0]
        if len(_service_users) != 1:
            _peer_uuid = None

        _key = DeviceUser.__tablename__ + ".uuid." + self._user_uuid
        _portal_user_name = self.application.redis.hget(_key, "user_fullname")
        _portal_user_icon = self.application.redis.hget(_key, "user_icon")

        _conversation_uuid = str(uuid.uuid1())
        _row = ConversationInfo(
            uuid=_conversation_uuid,
            user_uuid=self._user_uuid
        )
        _row.async_add(self.application.redis)
        _row.create_redis_keys(self.application.redis)
        
        _conversation_name = []
        for _user in _service_users:
            _key = DeviceUser.__tablename__ + ".uuid." + _user
            _name = self.application.redis.hget(_key, "user_fullname")
            if not _name:
                continue
            _conversation_name.append(_name)
        _conversation_name = ",".join(_conversation_name)

        _row = ConversationUserData(uuid=str(uuid.uuid1()),
                                    user_uuid=self._user_uuid,
                                    peer_uuid=_peer_uuid,
                                    conversation_uuid=_conversation_uuid,
                                    conversation_name=_conversation_name,
                                    conversation_type=CONVERSATION_TYPE.P2S,
                                    conversation_status=CONVERSATION_STATUS.NEW)
        _row.async_add(self.application.redis)
        _row.create_redis_keys(self.application.redis)

        
        for _user in _service_users:
            _row = ConversationUserData(uuid=str(uuid.uuid1()),
                                        user_uuid=_user,
                                        peer_uuid=self._user_uuid,
                                        conversation_uuid=_conversation_uuid,
                                        conversation_name=_portal_user_name,
                                        conversation_icon=_portal_user_icon,
                                        conversation_type=CONVERSATION_TYPE.S2P,
                                        conversation_status=CONVERSATION_STATUS.NEW)
            _row.async_add(self.application.redis)
            _row.create_redis_keys(self.application.redis)
        return

    
    def _exist_conversation(self, _conversations):
        
        _conversation_uuid = self._latest_conversation(_conversations).get('uuid')
        _conversation = self._return_conversation(self._user_uuid, _conversation_uuid)
        if not _conversation:
            self.setErrorCode(API_ERR.NO_CONVERSATION)
            logging.error("No conversation: %s" % _conversation_uuid)
            return

        _users = self._conversation_users(_conversation)
        if not _users:
            self.setErrorCode(API_ERR.NO_CONVERSATION_MEMBER)
            logging.error("Existed conversation but no users: %s" % str(_conversation_uuid))
            return

        _users.remove(self._user_uuid)
        _users = self._get_users(_users)
        _users = self._sort_users(_users)

        _r = self.getReturnData()
        self._get_app_welcome(_r)
        _r.update(_conversation)
        _r["user_list"] = _users
        
        return
        
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        return


    def _Task(self):
        super(self.__class__, self)._Task()
        _request = json.loads(self.request.body)
        self._user_uuid = _request.get("user_uuid")
        
        if not self._user_uuid:
            self.setErrorCode(API_ERR.NO_PARA)
            return
        
        _conversations = self._user_conversations(self._user_uuid)
        # no conversation then queue to AMD create
        # client check uuid field to check
        if not _conversations:
            # TODO CREATE CONVERSATION FOR THIS USER
            return self._new_conversation()

        return self._exist_conversation(_conversations)
