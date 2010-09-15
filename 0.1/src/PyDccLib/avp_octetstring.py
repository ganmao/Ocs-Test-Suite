#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl
'''
from avp import AVP

class OctetString(AVP):
    '''
    该数据包含任意可变长的数据。除非另外注明，
    AVP长度字段必须至少设置为8（如果“V”比特有效，则为12）。
    这种类型的AVP值的长度如果不是4个八位组的倍数，应按照需要填充，
    这样下一个AVP（如果有）才能够在一个32比特边界开始。
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf = None):
        AVP.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf)
        self.avp['AVP_DATA_TYPE'] = "OctetString"
        
        if self.avp['AVP_CODE_STATE'] == "00":
            data_length = len(self.avp['AVP_DATA'])
            data_length = (data_length + 3) // 4 * 4
            self.avp['AVP_CODE_OPERATOR'] = "!" + str(data_length) + "s"
            
    def _reset_operator_type(self):
        if self.avp['AVP_CODE_STATE'][:1] == "1":
            if self.avp['AVP_VENDOR_ID'] == 0:
                self.avp['AVP_CODE_OPERATOR'] = "!" + str(self.avp['AVP_LENGTH'] - 8) + "s"
            else:
                self.avp['AVP_CODE_OPERATOR'] = "!" + str(self.avp['AVP_LENGTH'] - 12) + "s"
            
    def _fmt_avp_data(self):
        self.avp['AVP_DATA'] = self.avp['AVP_DATA'].rstrip('\x00')
        