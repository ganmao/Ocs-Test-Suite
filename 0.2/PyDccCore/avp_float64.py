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
    def __init__(self,
                 cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
        AVP.__init__(self, cmd_code, avp_code, avp_data, decode_buf, dcc_instance)
        
    def _AVP__set_avp_operator_type(self):
        self.avp['AVP_CODE_OPERATOR']  = "!d"
        