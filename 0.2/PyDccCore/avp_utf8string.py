#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-10-1

@author: zdl
'''
from avp_octetstring import OctetString

class UTF8String(OctetString):
    '''
    UTF8String格式是从OctetString AVP基本格式导出的。
            该格式是使用ISO/IEC IS 10646－1字符集表示的可读的字符串，
            使用RFC 2279中描述的UTF-8转换格式，编码为一个OctetString。
    '''
    def __init__(self,
                 cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
        OctetString.__init__(self,
                             cmd_code,
                             avp_code,
                             avp_data,
                             decode_buf,
                             dcc_instance)
            
    def _AVP__befor_encode_data(self):
        # 因为json的字符串编码采用UNICODE，所以在这里进行一下转换
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
        
        # 编码时将传入的数据编码为UTF-8格式
        self.avp['AVP_DATA'] = str(self.dcc.utf8encoder(self.avp['AVP_DATA']))
        
    def _AVP__after_decode_data(self):
        self.avp['AVP_DATA'] = self.avp['AVP_DATA'].rstrip('\x00')
        
        # 编码时将传入的数据编码为UTF-8格式
        self.avp['AVP_DATA'] = self.dcc.utf8decoder(self.avp['AVP_DATA'])
        
        # 将UTF-8编码转为本地编码
        self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])