# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#

from .getyvobjectdetailhandler import GetYVObjectDetailHandler

from .ackmessagehandler import AckMessageHandler
from .setdeviceinfohandler import SetDeviceInfoHandler

from .ppcreateuserhandler import PPCreateUserHandler
from .ppremoveuserhandler import PPRemoveUserHandler
from .ppupdateuserhandler import PPUpdateUserHandler

from .ppcomcreatedevicehandler import PPComCreateDeviceHandler
from .ppupdatedevicehandler import PPUpdateDeviceHandler

from .ppkefucreateconversationhandler import PPKefuCreateConversationHandler
from .ppupdateconversationhandler import PPUpdateConversationHandler
from .ppgetconversationinfohandler import PPGetConversationInfoHandler

from .ppgetconversationlisthandler import PPGetConversationListHandler
from .ppgetuserconversationlisthandler import PPGetUserConversationListHandler

from .ppopenconversationhandler import PPOpenConversationHandler
from .ppcloseconversationhandler import PPCloseConversationHandler

from .ppgetappinfohandler import PPGetAppInfoHandler
from .ppgetserviceuserlisthandler import PPGetServiceUserListHandler

from .ppsendmessagehandler import PPSendMessageHandler
from .ppcomgetuseruuidhandler import PPComGetUserUUIDHandler
from .ppgetuserinfohandler import PPGetUserInfoHandler

from .ppupdateconversationmemberhandler import PPUpdateConversationMemberHandler

from .ppupdateappinfohandler import PPUpdateAppInfoHandler
from .ppisemailvalidhandler import PPIsEmailValidHandler

from .ppgetconversationuserlisthandler import PPGetConversationUserListHandler

from .pppageuserconversationhandler import PPPageUserConversationHandler
from .pppageunackedmessagehandler import PPPageUnackedMessageHandler
from .pppagehistorymessagehandler import PPPageHistoryMessageHandler

from .ppkefuloginhandler import PPKefuLoginHandler
from .ppkefulogouthandler import PPKefuLogoutHandler

from .ppgetuserdetailhandler import PPGetUserDetailHandler

from .ppgetapiinfohandler import PPGetApiInfoHandler

from .ppvalidateonlinedevicehandler import PPValidateOnlineDeviceHandler

from .ppcomcreateanonymoushandler import PPComCreateAnonymousHandler
from .ppcomgetdefaultconversationhandler import PPComGetDefaultConversationHandler
from .ppcomcreateconversationhandler import PPComCreateConversationHandler

from .ppgetipinfohandler import PPGetIPInfoHandler
from .ppcomtrackeventhandler import PPComTrackEventHandler

def getWebServiceHandlers():
    handler_list = []

    # ack the received message
    handler_list.append((r"/ACK_MESSAGE", AckMessageHandler))

    # get yvobject detail yvobject is the caller and callee
    handler_list.append((r"/GET_YVOBJECT_DETAIL", GetYVObjectDetailHandler))

    handler_list.append((r"/PPCOM_CREATE_DEVICE", PPComCreateDeviceHandler))
    handler_list.append((r"/PPCOM_CREATE_ANONYMOUS", PPComCreateAnonymousHandler))
    handler_list.append((r"/PPCOM_GET_DEFAULT_CONVERSATION", PPComGetDefaultConversationHandler))
    handler_list.append((r"/PPCOM_CREATE_CONVERSATION", PPComCreateConversationHandler))

    handler_list.append((r"/PPKEFU_LOGIN", PPKefuLoginHandler))
    handler_list.append((r"/PPKEFU_LOGOUT", PPKefuLogoutHandler))
    
    # set deviceinfo
    handler_list.append((r"/SET_DEVICE_INFO", SetDeviceInfoHandler))

    # PPMESSAGE
    handler_list.append((r"/PP_CREATE_USER", PPCreateUserHandler))
    handler_list.append((r"/PP_REMOVE_USER", PPRemoveUserHandler))
    handler_list.append((r"/PP_UPDATE_USER", PPUpdateUserHandler))
    
    handler_list.append((r"/PP_UPDATE_DEVICE", PPUpdateDeviceHandler))
        
    handler_list.append((r"/PPKEFU_CREATE_CONVERSATION", PPKefuCreateConversationHandler))
    handler_list.append((r"/PP_UPDATE_CONVERSATION", PPUpdateConversationHandler))
    handler_list.append((r"/PP_GET_CONVERSATION_INFO", PPGetConversationInfoHandler))
    
    handler_list.append((r"/PP_GET_CONVERSATION_LIST", PPGetConversationListHandler))
    handler_list.append((r"/PP_GET_USER_CONVERSATION_LIST", PPGetUserConversationListHandler))
    
    handler_list.append((r"/PP_OPEN_CONVERSATION", PPOpenConversationHandler))
    handler_list.append((r"/PP_CLOSE_CONVERSATION", PPCloseConversationHandler))

    handler_list.append((r"/PP_GET_APP_INFO", PPGetAppInfoHandler))
    handler_list.append((r"/PP_GET_SERVICE_USER_LIST", PPGetServiceUserListHandler))

    handler_list.append((r"/PP_SEND_MESSAGE", PPSendMessageHandler))
    handler_list.append((r"/PP_GET_USER_INFO", PPGetUserInfoHandler))

    handler_list.append((r"/PP_UPDATE_CONVERSATION_MEMBER", PPUpdateConversationMemberHandler))

    handler_list.append((r"/PP_UPDATE_APP_INFO", PPUpdateAppInfoHandler))
    handler_list.append((r"/PP_IS_EMAIL_VALID", PPIsEmailValidHandler))

    handler_list.append((r"/PP_GET_CONVERSATION_USER_LIST", PPGetConversationUserListHandler))
    
    handler_list.append((r"/PP_PAGE_USER_CONVERSATION", PPPageUserConversationHandler))
    handler_list.append((r"/PP_PAGE_UNACKED_MESSAGE", PPPageUnackedMessageHandler))
    handler_list.append((r"/PP_PAGE_HISTORY_MESSAGE", PPPageHistoryMessageHandler))

    handler_list.append((r"/PP_GET_USER_DETAIL", PPGetUserDetailHandler))

    handler_list.append((r"/PP_GET_API_INFO", PPGetApiInfoHandler))

    handler_list.append((r"/PP_VALIDATE_ONLINE_DEVICE", PPValidateOnlineDeviceHandler))

    handler_list.append((r"/PP_GET_IP_INFO", PPGetIPInfoHandler))
    
    handler_list.append((r"/PPCOM_TRACK_EVENT", PPComTrackEventHandler))
    handler_list.append((r"/PPCOM_GET_USER_UUID", PPComGetUserUUIDHandler))
    
    return handler_list

