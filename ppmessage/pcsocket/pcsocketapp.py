# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com.
# All rights are reserved.
#

from .wshandler import WSHandler

from ppmessage.core.constant import REDIS_HOST
from ppmessage.core.constant import REDIS_PORT

from ppmessage.core.constant import PCSOCKET_SRV

from ppmessage.core.constant import REDIS_ACK_NOTIFICATION_KEY
from ppmessage.core.constant import REDIS_PUSH_NOTIFICATION_KEY
from ppmessage.core.constant import REDIS_SEND_NOTIFICATION_KEY

from ppmessage.core.constant import DIS_WHAT
from ppmessage.core.constant import PP_WEB_SERVICE
from ppmessage.core.constant import DATETIME_FORMAT

from ppmessage.core.singleton import singleton
from ppmessage.core.main import AbstractWebService

from ppmessage.core.utils.getipaddress import get_ip_address
from ppmessage.core.utils.datetimestring import now_to_string

from ppmessage.db.models import AppInfo
from ppmessage.db.models import DeviceInfo
from ppmessage.db.models import PCSocketInfo
from ppmessage.db.models import PCSocketDeviceData
from ppmessage.db.models import ConversationUserData
from ppmessage.db.models import UserNavigationData

from ppmessage.dispatcher.policy import BroadcastPolicy

from .error import DIS_ERR

import tornado.options
from tornado.options import options
from tornado.web import Application
from tornado.ioloop import PeriodicCallback

import datetime
import logging
import redis
import uuid
import time
import json
import copy


@singleton
class PCSocketDelegate():
    def __init__(self, app):
        self.app = app
        self.redis = app.redis
        self.sockets = {}
        self.register = {"uuid": None, "host": None, "port": None}
        return
    
    def _remove_device_data_by_pattern(self, _pattern):
        _keys = self.redis.keys(_pattern)
        for _i in _keys:
            _row = PCSocketDeviceData(uuid=self.redis.get(_i))
            _row.delete_redis_keys(self.redis)
            _row.async_delete(self.redis)
        return

    def _remove_device_data_by_uuid(self, _uuid):
        if _uuid == None:
            return
        _row = PCSocketDeviceData(uuid=_uuid)
        _row.delete_redis_keys(self.redis)
        _row.async_delete(self.redis)
        return

    def register_service(self, _port):
        _ip = get_ip_address()
        self.register.update({"host": _ip, "port": _port})
        
        _key = PCSocketInfo.__tablename__ + \
               ".host." + _ip + \
               ".port." + _port
        # existed
        if self.redis.exists(_key):
            _row = PCSocketInfo(uuid=self.redis.get(_key),
                                latest_register_time=datetime.datetime.now())
            _row.update_redis_keys(self.redis)
            _row.async_update(self.redis)
            _key = PCSocketDeviceData.__tablename__ + \
               ".pc_socket_uuid." + _row.uuid + \
               ".device_uuid.*"
            self._remove_device_data_by_pattern(_key)
            self.register["uuid"] = _row.uuid
            return

        # first time run
        _row = PCSocketInfo(uuid=str(uuid.uuid1()),
                            host=_ip,
                            port=_port,
                            latest_register_time=datetime.datetime.now())
        _row.async_add(self.redis)
        _row.create_redis_keys(self.redis)
        self.register["uuid"] = _row.uuid
        return

    def map_device(self, _device_uuid):
        if _device_uuid == None:
            return
        
        _table = PCSocketDeviceData.__tablename__
        
        _key_0 = _table + ".pc_socket_uuid." + self.register["uuid"] + \
               ".device_uuid." + _device_uuid
        _key_1 = _table + ".device_uuid." + _device_uuid
        
        # the same host
        if self.redis.exists(_key_0):
            return

        # not the same host
        _host = self.redis.get(_key_1)
        # still the same, but no key????
        if _host != None and _host == self.register["uuid"]:
            logging.error("should not be here, two keys not consistent")
            return

        # remove the previous
        if _host != None and _host != self.register["uuid"]:
            _key_2 = _table + ".pc_socket_uuid." + _host + ".device_uuid." + _device_uuid
            _data = self.redis.get(_key_2)
            self._remove_device_data_by_uuid(_data)

        # create it
        _row = PCSocketDeviceData(uuid=str(uuid.uuid1()),
                                  pc_socket_uuid=self.register["uuid"],
                                  device_uuid=_device_uuid)
        _row.create_redis_keys(self.redis)
        _row.async_add(self.redis)
        return

    def unmap_device(self, _device_uuid):
        if _device_uuid == None:
            return
        _key = PCSocketDeviceData.__tablename__ + \
               ".pc_socket_uuid." + self.register["uuid"] + \
               ".device_uuid." + _device_uuid
        _data = self.redis.get(_key)
        self._remove_device_data_by_uuid(_data)
        return
    
    def device_online(self, _device_uuid, _is_online=True):
        _row = DeviceInfo(uuid=_device_uuid, device_is_online=_is_online)
        _row.async_update(self.redis)
        _row.update_redis_keys(self.redis)
        return
        
    def send_send(self, _device_uuid, _body):
        _body["pcsocket"] = {
            "host": self.register["host"],
            "port": self.register["port"],
            "device_uuid": _device_uuid
        }
        _key = REDIS_SEND_NOTIFICATION_KEY
        self.redis.rpush(_key, json.dumps(_body))
        return
    
    def save_extra(self, _user_uuid, _extra_data):
        if _extra_data == None:
            return

        _visit_page_url = None
        if isinstance(_extra_data, dict):
            _visit_page_url = _extra_data.get("href")
            _extra_data = json.dumps(_extra_data)
            
        _row = UserNavigationData(uuid=str(uuid.uuid1()),
                                  user_uuid=_user_uuid,
                                  visit_page_url=_visit_page_url,
                                  navigation_data=_extra_data)
        _row.async_add(self.redis)
        _row.create_redis_keys(self.redis)
        return
    
    def ack_loop(self):
        """
        every 100ms check ack notification
        """
        _host = str(self.register.get("host"))
        _port = str(self.register.get("port"))
        
        key = REDIS_ACK_NOTIFICATION_KEY + ".host." + _host + ".port." + _port
        while True:
            noti = self.redis.lpop(key)
            if noti == None:
                # no message
                return
            body = json.loads(noti)
            ws = self.sockets.get(body.get("device_uuid"))
            if ws == None:
                logging.error("No WS to handle ack body: %s" % body) 
                continue
            ws.send_ack(body)
        return

    def push_loop(self):
        """
        every 50ms check push notification
        """
        _host = str(self.register.get("host"))
        _port = str(self.register.get("port"))
        
        key = REDIS_PUSH_NOTIFICATION_KEY + ".host." + _host + ".port." + _port
        
        while True:
            noti = self.redis.lpop(key)
            if noti == None:
                return

            body = json.loads(noti)
            logging.info("WS will send: %s" % body)
            pcsocket = body.get("pcsocket") 
            if pcsocket == None:
                logging.error("no pcsocket in push: %s" % (body))
                continue
            device_uuid = pcsocket.get("device_uuid")
            ws = self.sockets.get(device_uuid)
            if ws == None:
                logging.error("No WS handle push: %s" % body)
                continue
            ws.send_msg(body["body"])

        return

    def run_periodic(self):
        tornado.options.parse_command_line()
        try:
            self.register_service(str(options.port))
        except:
            self.register_service(str(options.main_port))

        # set the periodic check ack every 100 ms
        PeriodicCallback(self.ack_loop, 100).start()

        # set the periodic check push every 50 ms
        PeriodicCallback(self.push_loop, 50).start()
        return

class PCSocketWebService(AbstractWebService):
    @classmethod
    def name(cls):
        return PP_WEB_SERVICE.PCSOCKET

    @classmethod
    def get_handlers(cls):
        return [("/"+PCSOCKET_SRV.WS, WSHandler)]

    @classmethod
    def get_delegate(cls, app):
        return PCSocketDelegate(app)

class PCSocketApp(Application):
    
    def __init__(self):
        self.redis = redis.Redis(REDIS_HOST, REDIS_PORT, db=1)
        settings = {}
        settings["debug"] = True
        Application.__init__(self, PCSocketWebService.get_handlers(), **settings)
        return

    def get_delegate(self, name):
        return PCSocketDelegate(self)
    

