#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-10-1

@author: zdl
'''
from avp_octetstring import OctetString

class DiameterIdentity(OctetString):
    '''
    DiameterIdentity格式是从OctetString AVP基本格式导出的。
        DiameterIdentity = FQDN
    DiameterIdentity值唯一标识一个Diameter节点，以用于重复连接和路由环路检测。
            字符串的内容必须是Diameter节点的FQDN。如果多个Diameter节点在同一台主机上运行，
            每个Diameter节点必须分配一个唯一的DiameterIdentity。如果一个Diameter节点可以
            由若干个FQDN标识，其中一个FQDN应在启动时被挑选出来，并作为该节点唯一
            的DiameterIdentity。
        FQDN               = fully qualified domain name
        
    TODO: 源自OctetString,但是需要校验一下FQDN的正确性
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        OctetString.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        
        self.avp['AVP_DATA_TYPE'] = "DiameterIdentity"
        