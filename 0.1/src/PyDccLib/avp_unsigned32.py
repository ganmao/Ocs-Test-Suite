#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl
'''

from avp import AVP

class Unsigned32(AVP):
    '''
    32比特无符号整数，按照网络字节顺序。AVP长度字段必须设置为12（如果“V”比特有效，则为16）。
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 avp_config_instance=None):
        AVP.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     avp_config_instance)
        self.avp['AVP_CODE_OPERATOR']  = "!I"
        self.avp['AVP_DATA_TYPE']      = "Unsigned32"
        