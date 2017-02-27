# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
# All rights reserved
#

from ppmessage.core.constant import OS
from ppmessage.core.constant import DIS_WHAT
from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import MESSAGE_TYPE
from ppmessage.core.constant import MESSAGE_SUBTYPE
from ppmessage.core.constant import WEBSOCKET_STATUS
from ppmessage.core.constant import PP_WEB_SERVICE

from ppmessage.db.models import DeviceInfo
from ppmessage.db.models import ApiTokenData

from .error import DIS_ERR
from .error import get_error_string

import uuid
import json
import logging
import datetime
import tornado.websocket

class WSHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super(WSHandler, self).__init__(*args, **kwargs)

        self.delegate = self.application.get_delegate(PP_WEB_SERVICE.PCSOCKET)
        self.redis = self.application.redis
        self.sockets = self.delegate.sockets
        
        # tracking this socket
        self.ws_uuid = str(uuid.uuid1())

        self.body = None
        
        self.device_uuid = None
        self.user_uuid = None
        self.api_token = None
        
        self.extra_data = None
        self.is_service_user = False
        self.is_mobile_device = False

        return
    
    def _on_auth(self, _body):
        self.api_token = _body.get("api_token")
        self.user_uuid = _body.get("user_uuid")
        self.device_uuid = _body.get("device_uuid")
        self.is_service_user = _body.get("is_service_user")
        self.extra_data = _body.get("extra_data")

        if self.api_token == None:
            self.send_ack({"code": DIS_ERR.NOTOKEN, "what": DIS_WHAT.AUTH})
            return

        _key = ApiTokenData.__tablename__ + ".api_token." + self.api_token
        _token = self.redis.get(_key)
        if _token == None or len(_token) == 0:
            self.send_ack({"code": DIS_ERR.NODBKEY, "what": DIS_WHAT.AUTH})
            return

        _key = ApiTokenData.__tablename__ + ".uuid." + _token
        _token = self.redis.hgetall(_key)
        
        _level = _token.get("api_level")
        if _level != API_LEVEL.PPCOM and _level != API_LEVEL.PPKEFU:
            self.send_ack({"code": DIS_ERR.WRLEVEL, "what": DIS_WHAT.AUTH})
            return
        
        if self.user_uuid == None or self.device_uuid == None:
            self.send_ack({"code": DIS_ERR.NOUUIDS, "what": DIS_WHAT.AUTH})
            return
        
        if self.is_service_user == None:
            self.send_ack({"code": DIS_ERR.NOSERVICE, "what": DIS_WHAT.AUTH})
            return

        if self.is_service_user == False and self.extra_data == None:
            self.send_ack({"code": DIS_ERR.NOEXTRA, "what": DIS_WHAT.AUTH})
            return

        self.send_ack({"code": DIS_ERR.NOERR, "what": DIS_WHAT.AUTH})

        self.delegate.save_extra(self.user_uuid, self.extra_data)
        self.delegate.map_device(self.device_uuid)
        self.delegate.device_online(self.device_uuid, True)

        self.sockets[self.device_uuid] = self
                    
        logging.info("AUTH DEVICE:%s USER:%s." % (self.device_uuid, self.user_uuid))
        return
    
    def _on_send(self, _body):
        _send = _body.get("send")
        if _send == None:
            send_ack({"code": DIS_ERR.PARAM, "what": DIS_WHAT.SEND})
            return
        logging.info("sending ..... %s" % _send)
        self.delegate.send_send(self.device_uuid, _send)
        return

    def _which(self, _type):
        _map = {
            DIS_WHAT.AUTH: self._on_auth,
            DIS_WHAT.SEND: self._on_send
        }
        return _map.get(_type)
        
    def open(self):
        logging.info("CLIENT OPEN.....")
        self.set_nodelay(True)
        return

    def on_message(self, message):
        """
        
        AUTH:
        from ppcom/ppkefu
        {
        "type": DIS_WHAT.AUTH,
        "device_uuid": string,
        "user_uuid": string,
        "extra_data": OBJECT,
        "is_service_user": True/False
        }
        
        ack back to ppcom/ppkefu
        {"type": DIS_WHAT.ACK, "what": DIS_WHAT_AUTH, "code": int, "reason": string}
        
        TYPING
        from ppcom/ppkefu
        TYPING_WATCH the client be interested in this conversation typing
        {
        "type": DIS_WHAT.TYPING_WATCH,
        "conversation_uuid": xxxx,
        }

        from ppcom/ppkefu
        TYPING_UNWATCH the client is no longer interested the conversation typing 
        {
        "type": DIS_WHAT.TYPING_UNWATCH
        "conversation_uuid": xxxx,
        }

        from ppcom/ppkefu
        TYPING means the client is typing (receive and send)
        {
        "type": DIS_WHAT.TYPING 
        }

        to ppcom/ppkefu
        ONLINE means the user is online or not, 
        if online then which device type is online(send only)
        {
        "type": DIS_WHAT.ONLINE,
        "mobile": ONLINE/OFFLINE/UNCHANGED
        "browser": ONLINE/OFFLINE/UNCHANGED
        "user_uuid": string,
        }

        from ppcom/ppkefu
        SEND message with websocket
        {
        "type": DIS_WHAT.SEND
        "send": string
        }
         
        to ppcom/ppkefu
        ACK
        {
        "type": DIS_WHAT.ACK
        "what": ack which DIS_WHAT 
        "code": DIS_ERR
        "reason": string
        }
        """
        logging.info("WS MESSAGE..... %s" % message)
        _body = None
        try:
            _body = json.loads(message)
        except:
            logging.error("failed parse %s" % message)
            self.send_ack({"code": DIS_ERR.JSON, "what": DIS_WHAT.WS})
            return
        
        if _body == None:
            return

        self.body = _body
        
        _type = _body.get("type")
        if _type == None:
            self.send_ack({"code": DIS_ERR.TYPE, "what": DIS_WHAT.WS})
            logging.error("can not handle message: %s" % message)
            return

        _type = _type.upper()
        _f = self._which(_type)
        if _f == None:
            logging.error("can not hanle message: %s" % message)
            self.send_ack({"code": DIS_ERR.TYPE, "what": DIS_WHAT.WS})
            return

        _f(_body)
        return
    
    def on_close(self):
        if self.device_uuid == None:
            logging.error("CLOSE websocket with device_uuid == None")
            return
        
        logging.info("CLOSE device_uuid:%s." % self.device_uuid)
        self.sockets[self.device_uuid] = None
        del self.sockets[self.device_uuid]

        self.delegate.unmap_device(self.device_uuid)
        self.delegate.device_online(self.device_uuid, False)
        return
    
    def send_ack(self, _body):
        _what = _body.get("what")
        _code = _body.get("code")
        _extra = _body.get("extra")

        if _what == None or _code == None:
            return
        
        _what = _what.upper()
        _str = get_error_string(_code)
        _d = {
            "type": DIS_WHAT.ACK,
            "what": _what,
            "code" : _code,
            "reason": _str,
            "extra": _extra
        }
        self.write_message(_d)
            
        if _what != DIS_WHAT.AUTH:
            return

        # especially handle for auth
        if _code == DIS_ERR.NOERR:
            return
        
        self.device_uuid = None
        self.close()
        return

    def send_msg(self, _body):
        _d = {
            "type": DIS_WHAT.MSG,
            "msg": _body
        }
        self.write_message(_d)
        return

    def send_logout(self, _body):
        self._please_logout(self, _body.get("other_device"))
        return
    
    def check_origin(self, origin):
        return True
