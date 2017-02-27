# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2017 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
#

from .basehandler import BaseHandler

from ppmessage.api.error import API_ERR

from ppmessage.db.models import CompanyInfo
from ppmessage.db.models import DeviceUser

from ppmessage.core.constant import API_LEVEL
from ppmessage.core.db.deviceuser import create_device_user


import json
import uuid
import logging
import datetime

class PPComGetUserUUIDHandler(BaseHandler):
    def _new_user(self):
        _du_uuid = str(uuid.uuid1())
        _user = create_device_user(self.application.redis, {
            "uuid": _du_uuid,
            "company_uuid": self._company_uuid,
            "user_name": self._user_fullname,
            "user_fullname": self._user_fullname,
            "user_email": self._user_email,
            "user_mobile": self._user_mobile,
            "user_icon": self._user_icon,
            "ent_user_uuid": self._ent_user_uuid,
            "ent_user_createtime": datetime.datetime.utcfromtimestamp(self._ent_user_createtime/1000),
            "is_anonymous_user": False,
            "is_service_user": False,
            "is_owner_user": False
        })
        _r = self.getReturnData()
        _r["user_fullname"] = _user_name
        _r["user_uuid"] = _du_uuid
        _r["uuid"] = _du_uuid
        return

    def _exist_user(self, _user_uuid):
        _update = {"uuid": _user_uuid}
        if self._user_email:
            _update.update({"user_email": self._user_email})
        if self._user_icon:
            _update.update({"user_icon": self._user_icon})
        if self._user_mobile:
            _update.update({"user_mobile": self._user_mobile})
        if self._user_name:
            _update.update({"user_fullname": self._user_fullname})

        if _update:
            _row = DeviceUser(**_update) 
            _row.update_redis_keys(self.application.redis)
            _row.async_update(self.application.redis)

        _key = DeviceUser.__tablename__ + ".uuid." + _user_uuid        
        _r = self.getReturnData()
        _r.update(self.application.redis.hgetall(_key))
        return

    def _new_company(self):
        self._company_uuid = str(uuid.uuid1())
        _row = CompanyInfo(uuid=self._company_uuid,
                           ent_company_uuid=self._ent_company_uuid,
                           ent_company_createtime=datetime.datetime.utcfromtimestamp(self._ent_company_createtime/1000),
                           company_name=self._company_name,
                           company_fullname=self._company_fullname)
        _row.async_add(self.application.redis)
        _row.create_redis_keys(self.application.redis)
        return

    def _exist_company(self):
        _key = CompanyInfo.__tablename__ + ".uuid." + self._company_uuid
        _update = {"uuid": self._company_uuid}
        if self._company_name:
            _update.update({"company_name": self._company_name})
        if self._company_fullname:
            _update.update({"company_fullname": self._company_fullname})
        _row = CompanyInfo(**_update)
        _row.async_update(self.application.redis)
        _row.update_redis_keys(self.application.redis)
        return
    
    def initialize(self):
        self.addPermission(api_level=API_LEVEL.PPCOM)
        return

    def _Task(self):
        super(self.__class__, self)._Task()
        _request = json.loads(self.request.body)

        # TODO: use this to merge messages 
        self._ppcom_trace_uuid = _request.get("ppcom_trace_uuid")
        
                
        # time.time() * 1000
        self._ent_user_createtime = _request.get("user_createtime")
        self._ent_user_uuid = str(_request.get("user_id"))
        
        self._user_fullname = _request.get("user_name")
        self._user_email = _request.get("user_email")
        self._user_mobile = _request.get("user_mobile")
        self._user_icon = _request.get("user_icon")

        # TODO: create company info db
        self._ent_company_uuid = str(_request.get("company_id"))
        self._ent_company_createtime = _request.get("company_createtime")
        self._company_name = _request.get("company_name")
        self._company_fullname = _request.get("company_fullname")

        if not all([self._ppcom_trace_uuid, self._ent_user_uuid, self._ent_user_createtime]):
            logging.error("wrong parameters %s" % _request)
            self.setErrorCode(API_ERR.NO_PARA)
            return

        if self._ent_company_uuid and self._ent_company_createtime:
            _key = CompanyInfo.__tablename__ + ".ent_company_uuid." + self._ent_company_uuid
            self._company_uuid = self.application.redis.get(_key)
            if not self._company_uuid:
                logging.info("new company")
                self._new_company()
            else:
                logging.info("exist company")
                self._exist_company()
        
        _key = DeviceUser.__tablename__ + ".ent_user_uuid." + self._ent_user_uuid
        _user_uuid = self.application.redis.get(_key)

        if not _user_uuid:
            logging.info("new ent user")
            return self._new_user(_request)

        logging.info("existed ent user, try update")
        return self._exist_user(_user_uuid)

