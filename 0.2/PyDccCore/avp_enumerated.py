#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-10-1

@author: zdl
'''
from avp_integer32 import Integer32

class Enumerated(Integer32):
    '''
    Enumerated是从Integer32 AVP基本格式导出的。该定义包含一个有效值的列表
        及相关解释，并在引入该AVP的Diameter应用中有所描述。
    
    '''
    def __init__(self,
                 cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
        Integer32.__init__(self,
                             cmd_code,
                             avp_code,
                             avp_data,
                             decode_buf,
                             dcc_instance)
        