#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-10-1

@author: zdl
'''
from avp_octetstring import OctetString

class Enumerated(OctetString):
    '''
    Enumerated是从Integer32 AVP基本格式导出的。该定义包含一个有效值的列表
        及相关解释，并在引入该AVP的Diameter应用中有所描述。
        
    TODO: 需要校验一下Enumerated数据的合法性，是否是已经定义的值
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        OctetString.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        
        self.avp['AVP_DATA_TYPE'] = "Enumerated"
        