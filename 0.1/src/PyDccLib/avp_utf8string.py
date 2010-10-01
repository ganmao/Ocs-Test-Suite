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
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        OctetString.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        
        self.avp['AVP_DATA_TYPE'] = "UTF8String"
        
        # 编码时将传入的数据编码为UTF-8格式
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_DATA'] = str(self.utf8encoder(self.avp['AVP_DATA']))
            
            data_length = len(self.avp['AVP_DATA'])
            data_length = (data_length + 3) // 4 * 4
            self.avp['AVP_CODE_OPERATOR'] = "!" + str(data_length) + "s"
            
    def decode_data(self, offset=8):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self._reset_operator_type()
        
        (self.avp['AVP_DATA'],) = self.unpack_from_bin(self.avp['AVP_CODE_OPERATOR'], 
                                                 self.avp['AVP_BUF'], 
                                                 offset)
        
        self.avp['AVP_DATA_HEX'] = self.avp['AVP_BUF'][offset:]
        
        # 将解码后的内容按照UTF8解码
        self.avp['AVP_DATA'] = self.utf8decoder(self.avp['AVP_DATA'])
        
        return self.avp['AVP_LENGTH']
            