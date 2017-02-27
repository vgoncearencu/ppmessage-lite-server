# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
# db/sqlsqlite.py
#

from .sqlnone import SqlNone

from ppmessage.core.constant import SQL
from ppmessage.core.singleton import singleton

from ppmessage.core.utils.config import _get_config

from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite

import os
import logging
import traceback

def _cur_dir():
    return os.path.abspath(os.path.dirname(__file__))

class SqlInstance(SqlNone):

    def __init__(self):

        _cur = _cur_dir()
        _db_file_path = _cur + "/../resource/data/db/ppmessage.db"

        _db = _get_config()
        if _db:
            _db = _db.get("db")
            if _db:
                _db = _db.get("db_file_path")
                if _db:
                    _db_file_path = _db
                
        self.db_file_path = _db_file_path
        super(self.__class__, self).__init__()
        return

    def name(self):
        return SQL.SQLITE
    
    def createEngine(self):
        _dbstring = "sqlite+pysqlite:///%s" % self.db_file_path
        if self.dbengine == None:
            _engine = create_engine(_dbstring, module=sqlite)
            self.dbengine = _engine
        return self.dbengine
