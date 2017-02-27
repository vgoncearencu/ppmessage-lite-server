# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
# All rights reserved
#
# db/dbinstance.py
#

from ppmessage.core.constant import SQL
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()

import logging

def _get_instance(_config=None):
    from .sqlsqlite import SqlInstance
    return SqlInstance()

def getDBSessionClass():
    db = _get_instance()
    if db == None:
        return None    
    db.createEngine()
    return db.getSessionClass()

def getDatabaseEngine(config=None):
    db = _get_instance(config)
    if db == None:
        return None
    return db.createEngine()

