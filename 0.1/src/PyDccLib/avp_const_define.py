#-*- coding:utf-8 -*-
'''
Created on 2010-9-4

@author: zdl

定义AVP的各种常量
'''

import const

# 配置文件路径
const.ETC_PATH = "./etc"

# AVP_FLAGS中的定义
const.AVP_FLAG_VENDOR    = 0x80
const.AVP_FLAG_MANDATORY = 0x40
const.AVP_FLAG_PRIVATE   = 0x20

# 消息头信息
const.DMSG_VERSION            = 0x01
const.DMSG_FLAGS_REQUEST      = 0x80
const.DMSG_FLAGS_ANSWER       = 0x00
const.DMSG_FLAGS_PROXIABLE    = 0x40
const.DMSG_FLAGS_ERROR        = 0x20
const.DMSG_FLAGS_TPOTENTIALLY = 0x10
const.DMSG_APPLICATION_ID     = 0x40

# Command-Code定义
const.CC_Credit_Control        = 272
const.CC_Re_Auth               = 258
const.CC_Abort_Session         = 274
const.CC_Device_Watchdog       = 280
const.CC_Disconnect_Peer       = 282
const.CC_Capabilities_Exchange = 257


