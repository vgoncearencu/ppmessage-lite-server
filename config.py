#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
# config.py
#

from ppmessage.core.constant import SQL
from ppmessage.core.constant import API_LEVEL
from ppmessage.core.constant import REDIS_HOST
from ppmessage.core.constant import REDIS_PORT
from ppmessage.core.constant import USER_STATUS
from ppmessage.core.constant import CONFIG_STATUS
from ppmessage.core.constant import PP_WEB_SERVICE

from ppmessage.core.utils.config import _get_config
from ppmessage.core.utils.config import _dump_config
from ppmessage.core.utils.getipaddress import get_ip_address
from ppmessage.core.utils.randomidenticon import random_identicon

from ppmessage.db.create import create_pgsql_db
from ppmessage.db.create import create_mysql_db
from ppmessage.db.create import create_mysql_tables
from ppmessage.db.create import create_pgsql_tables
from ppmessage.db.create import create_sqlite_tables

import os
import json
import uuid
import redis
import errno    
import logging
import traceback

import tornado.ioloop
import tornado.options
import tornado.web


_redis = redis.Redis(db=1)

def _insert_into(_row):
    from ppmessage.db.dbinstance import getDBSessionClass
    _class = getDBSessionClass()
    _session = _class()
    try:
        _session.add(_row)
        _session.commit()
    except:
        _session.rollback()
        traceback.print_exc()
    finally:
        _class.remove()
    return


def _mkdir_p(_path):
    try:
        os.makedirs(_path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(_path):
            pass
        else:
            raise
    return

def _cur_dir():
    return os.path.abspath(os.path.dirname(__file__))

class ServerHandler():    
    def _dump_server_config(self, _server_config):
        """
        server config is first
        """

        _url = _server_config.get("url")
        _server_config.update({"ssl":"off"})
        if _url.startswith("https"):
            _server_config.update({"ssl":"on"})

        _host = _url[_url.index("//")+2:]
        _host = _host.split(":")

        if len(_host) == 1:
            _server_config.update({"name": _host[0]})
            if _servcer_config.get("ssl") == "on":
                _server_config.update({"port": 443})
            else:
                _server_config.update({"port": 80})
                
        if len(_host) == 2:
            _server_config.update({"name": _host[0], "port": int(_host[1])})
        
        _config = {
            "config_status": CONFIG_STATUS.SERVER,
            "server": _server_config
        }
        _dump_config(_config)
        return

    def _create_server_stores(self, _server):
        try:
            _mkdir_p(_server.get("generic_store"))
            _mkdir_p(_server.get("identicon_store"))
        except:
            return False
        return True
    
    def post(self):
        _cur = _cur_dir()
        _generic_store = _cur + "/ppmessage/resource/data/generic"
        _identicon_store = _cur + "/ppmessage/resource/data/identicon"            

        _server = {
            "url": "http://127.0.0.1:8945",
            "generic_store": _generic_store,
            "identicon_store": _identicon_store
        }
        
        if not self._create_server_stores(_server):
            logging.error("config server not run for wrong request: %s." % _server)
            return False
        
        self._dump_server_config(_server)
        return True

class DatabaseHandler():
    
    def _dump_db_config(self, _db_config):
        _config = _get_config()
        _config["config_status"] = CONFIG_STATUS.DATABASE
        _config["db"] = _db_config
        _dump_config(_config)
        return
    
    def _sqlite(self):
        _cur = _cur_dir()
        _db_file_path = _cur + "/ppmessage/resource/data/db/ppmessage.db"
        
        try:
            _dir = os.path.dirname(_db_file_path)
            _mkdir_p(_dir)
            open(_db_file_path, "w").close()
        except:
            logging.error("sqlite: can not create %s" % _db_file_path)
            return False
        
        _config = {
            "type": SQL.SQLITE.lower(),
            "sqlite": {
                "db_file_path": _db_file_path
            }
        }

        if create_sqlite_tables(_config):
            self._dump_db_config(_config)
            return True
        return False
    
    def post(self):        
        return self._sqlite()
        

class FirstHandler():
    def __init__(self, *args, **kwargs):
        self._user_uuid = str(uuid.uuid1())
        self._app_uuid = str(uuid.uuid1())
        
    def _create_user(self, _request):
        from ppmessage.db.models import DeviceUser
        
        _user_email = _request.get("user_email")
        _user_fullname = _request.get("user_fullname")
        _user_password = _request.get("user_password")
        _user_icon = random_identicon(_user_email)
        
        _row = DeviceUser(
            uuid=self._user_uuid,
            user_email=_user_email,
            user_icon=_user_icon,
            user_status=USER_STATUS.OWNER_2,
            user_fullname=_user_fullname,
            user_password=_user_password,
            is_removed_user=False,
            is_owner_user=True,
            is_service_user=True,
            is_anonymous_user=False
        )
        
        _row.create_redis_keys(_redis)
        _insert_into(_row)
        self._user_fullname = _user_fullname
        return True

    def _create_team(self, _request):
        from ppmessage.db.models import AppInfo
        
        _app_name = "PPMessage Lite Test Team"
        _app_uuid = self._app_uuid
        _app_key = str(uuid.uuid1())
        _app_secret = str(uuid.uuid1())

        _row = AppInfo(uuid=_app_uuid, 
                       app_name=_app_name,
                       app_key=_app_key,
                       app_secret=_app_secret)
        _row.create_redis_keys(_redis)
        _insert_into(_row)
        return True

    def _create_api(self, _request):
        from ppmessage.db.models import ApiInfo
        import hashlib
        import base64
        _user_uuid = self._user_uuid

        def _encode(_key):
            _key = hashlib.sha1(_key.encode("utf-8")).hexdigest()
            _key = base64.b64encode(_key.encode("utf-8"))
            _key = _key.decode("utf-8")
            return _key

        def _info(_type):
            _uuid = str(uuid.uuid1())
            _key = _encode(str(uuid.uuid1()))
            _secret = _encode(str(uuid.uuid1()))
            _row = ApiInfo(uuid=_uuid,
                           user_uuid=_user_uuid,
                           api_level=_type,
                           api_key=_key,
                           api_secret=_secret)
            _row.create_redis_keys(_redis)
            _insert_into(_row)
            return {"uuid":_uuid, "key":_key, "secret":_secret}

        _config = {
            API_LEVEL.PPCOM.lower(): _info(API_LEVEL.PPCOM),
            API_LEVEL.PPKEFU.lower(): _info(API_LEVEL.PPKEFU),
            API_LEVEL.PPCONSOLE.lower(): _info(API_LEVEL.PPCONSOLE),
            API_LEVEL.PPCONSOLE_BEFORE_LOGIN.lower(): _info(API_LEVEL.PPCONSOLE_BEFORE_LOGIN),
            API_LEVEL.THIRD_PARTY_KEFU.lower(): _info(API_LEVEL.THIRD_PARTY_KEFU),
            API_LEVEL.THIRD_PARTY_CONSOLE.lower(): _info(API_LEVEL.THIRD_PARTY_CONSOLE)
        }
        self._api = _config
        return True
    
    def _dist_ppcom(self, _request):
        from ppmessage.ppconfig.config.ppcom.config import config
        _d = {
            "ssl": _get_config().get("server").get("ssl"),
            "server_name": _get_config().get("server").get("name"),
            "server_port": _get_config().get("server").get("port"),
            "key": self._api.get(API_LEVEL.PPCOM.lower()).get("key"),
            "secret": self._api.get(API_LEVEL.PPCOM.lower()).get("secret"),
        }
        config(_d)
        return True

    def _dist_ppkefu(self, _request):
        from ppmessage.ppconfig.config.ppkefu.config import config
        _d = {
            "key": self._api.get(API_LEVEL.PPKEFU.lower()).get("key"),
            "server_url": _get_config().get("server").get("url")
        }
        config(_d)
        return True

    def _dist(self, _request):
        if not self._dist_ppcom(_request):
            return False
        if not self._dist_ppkefu(_request):
            return False
        return True

    def _dump_config(self, _request):
        _config = _get_config()
        _config["config_status"] = CONFIG_STATUS.FIRST
        _config["api"] = self._api
        _config["team"] = {
            "app_uuid": self._app_uuid,
            "name": "Test PPMessage Lite Server"
        }
        _config["user"] = {
            "user_uuid": self._user_uuid,
            "user_email": _request.get("user_email"),
            "user_fullname": _request.get("user_fullname"),
            "user_password": _request.get("user_password")
        }
        _config["configed"] = True
        _dump_config(_config)
        return True

    def post(self, _request):

        logging.info("firstrequest: %s" % _request)
        
        if not self._create_user(_request):
            return False

        if not self._create_team(_request):
            return False

        if not self._create_api(_request):
            return False

        if not self._dist(_request):
            return False

        self._dump_config(_request)

        return True

    
def _main():
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    tornado.options.define("email", default=None, help="", type=str)
    tornado.options.define("password", default=None, help="", type=str)
    
    tornado.options.parse_command_line()

    _user_email = tornado.options.options.email
    _user_password = tornado.options.options.password

    if not _user_email or not _user_password:
        logging.error("run config with --email=your_email_address --password=initial_password_you_want_set")
        return
    
    if _get_config() != None and _get_config().get("config_status") == CONFIG_STATUS.FIRST:
        logging.error("PPMessage Lite Server alreay configed, run lite.py to start server. Or remove ppmessage/bootstrap/config.json and run config.py again")
        return

    ServerHandler().post()
    DatabaseHandler().post()
    FirstHandler().post({
        "user_email": _user_email,
        "user_password": _user_password,
        "user_fullname": _user_email
    })
    
    return

if __name__ == "__main__":
    _main()
