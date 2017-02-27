# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.api.error import API_ERR
from ppmessage.core.constant import API_LEVEL

import json
import uuid
import logging


class PPComTrackEventHandler(BaseHandler):

    def _get(self):
        _request = json.loads(self.request.body)
        _user_uuid = _request.get("user_uuid")
        _device_uuid = _request.get("device_uuid")
        _event_name = _request.get("event_name")
        _event_data = _request.get("event_data")

        if not all([_user_uuid, _device_uuid, _event_name, _event_data]):
            self.setErrorCode(API_ERR.NO_PARA)
            return
        
        logging.info("trackevent: name: %s, data: %s" % (_event_name, _event_data))
        return
    
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        return

    def _Task(self):
        super(self.__class__, self)._Task()
        self._get()
        return

