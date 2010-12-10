#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-11-24

@author: zdl
'''
from avp_integer32 import Integer32
from avp_integer64 import Integer64
from avp_unsigned32 import Unsigned32
from avp_unsigned64 import Unsigned64
from avp_octetstring import OctetString
from avp_float32 import Float32
from avp_float64 import Float64
from avp_grouped import Grouped

from avp_address import Address
from avp_time import Time
from avp_utf8string import UTF8String
from avp_diameteridentity import DiameterIdentity
from avp_enumerated import Enumerated

import dcc_error

def create_avp(  cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
    '''根据传入的AVP_CODE或者AVP_BUF创建解析出AVP_CODE创建对应的AVP
    '''
    # 判断传入BUF则认为需要解码
    if decode_buf:
        __my_avp_code = decode_avp_code(decode_buf, dcc_instance)
    else:
        __my_avp_code = avp_code
    
    # 获取对应AVP_CODE的配置
    __my_avp_cfg = dcc_instance.dcc_cfg.get_config(cmd_code,
                                                   __my_avp_code
                                                   )
    
    # 创建对应的AVP实例
    if __my_avp_cfg[4] == 'Integer32':
        return Integer32(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Integer64':
        return Integer64(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Float32':
        return Float32(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Float64':
        return Float64(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Unsigned32':
        return Unsigned32(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Unsigned64':
        return Unsigned64(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'OctetString':
        return OctetString(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Grouped':
        return Grouped(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Address':
        return Address(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Time':
        return Time(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'UTF8String':
        return UTF8String(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'DiameterIdentity':
        return DiameterIdentity(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    elif __my_avp_cfg[4] == 'Enumerated':
        return Enumerated(cmd_code,
                         __my_avp_code,
                         avp_data,
                         decode_buf,
                         dcc_instance)
    else:
        raise dcc_error.AvpE_InvalidAvpDataType, \
                "unknown avp[%s] data type[%s]!" % (__my_avp_cfg[2], __my_avp_cfg[4])
    
def decode_avp_code(avp_buf, dcc_instance):
    '''从AVP_BUF中解析出来头部的AVP_CODE
    '''
    (__my_avp_code,) = dcc_instance.unpack_from_bin("!I", avp_buf)
    
    return str(__my_avp_code)