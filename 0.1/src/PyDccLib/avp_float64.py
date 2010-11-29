#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl
'''
from avp import AVP

class Float64(AVP):
    '''
    该类型表示双精度浮点值，遵循IEEE标准754-1985中关于浮点的描述。
    该64比特值按网络字节顺序传送。AVP长度字段必须设置为16（如果“V”比特有效，则为20）。
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        AVP.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        self.avp['AVP_CODE_OPERATOR']  = "!d"
        self.avp['AVP_DATA_TYPE']      = "Float64"
        