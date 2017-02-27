# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2017 PPMessage.
# Guijin Ding, dingguijin@gmail.com
#
# All rights reserved
#

from ppmessage.db.models import DeviceUser

from ppmessage.core.utils.randomidenticon import random_identicon
from ppmessage.core.utils.config import _get_config

import uuid
import logging
import datetime

def create_device_user(redis, request):
    _uuid = request.get("uuid")

    if not _uuid:
        logging.error("no uuid provided. %s" % request)
        return None
    
    _is_service_user = bool(request.get("is_service_user"))
    _is_anonymous_user = bool(request.get("is_anonymous_user"))
    _is_owner_user = bool(request.get("is_owner_user"))

    _user_email = request.get("user_email")
    if not _user_email:
        import strgen
        _user_email = strgen.StringGenerator("[\d\w]{10}").render() + "@" + strgen.StringGenerator("[\d\w]{10}").render()
        
    _user_icon = request.get("user_icon")
    if not _user_icon:
        if _user_email:
            _user_icon = random_identicon(_user_email)
        else:
            _user_icon = random_identicon(_uuid)

    _company_uuid = request.get("company_uuid")
    _user_name = request.get("user_name")
    _user_mobile = request.get("user_mobile")
    _user_fullname = request.get("user_fullname")
    _user_password = request.get("user_password")
    _user_language = request.get("user_language") or "cn"

    _ent_user_uuid = request.get("ent_user_uuid")
    _ent_user_createtime = request.get("ent_user_createtime")
    
    import pypinyin
    if not isinstance(_user_fullname, unicode):
        _user_fullname = _user_fullname.decode("utf-8")
    _user_pinyin = "".join(pypinyin.lazy_pinyin(_user_fullname))
    _user_py = "".join(pypinyin.lazy_pinyin(_user_fullname, style=pypinyin.FIRST_LETTER))

    _values = {
        "uuid": _uuid,
        "company_uuid": _company_uuid,
        "is_service_user": _is_service_user,
        "is_owner_user": _is_owner_user,
        "is_ppmessage_user": _is_ppmessage_user,
        "is_anonymous_user": _is_anonymous_user,
        "is_removed_user": False,
        "user_name": _user_name,
        "user_mobile": _user_mobile,
        "user_email": _user_email,
        "user_icon": _user_icon,
        "user_fullname": _user_fullname,
        "user_password": _user_password,
        "user_pinyin": _user_pinyin,
        "user_py": _user_py,
        "ent_user_uuid": _ent_user_uuid,
        "ent_user_createtime": _ent_user_createtime
    }
    
    _row = DeviceUser(**_values)
    _row.async_add(redis)
    _row.create_redis_keys(redis)
    return _values
