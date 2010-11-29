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
    def __init__(self,
                 cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
        AVP.__init__(self, cmd_code, avp_code, avp_data, decode_buf, dcc_instance)
        
    def _AVP__set_avp_operator_type(self):
        # 认为正在编码
        if self.avp['AVP_CODE_STATE'] == self.dcc.dcc_def.const.ENCODE_DCC_AVP_BEGIN:
            self.avp['AVP_LENGTH'] = len(self.avp['AVP_DATA'])
            __data_length = (self.avp['AVP_LENGTH'] + 3) // 4 * 4
            self.avp['AVP_CODE_OPERATOR'] = "!" + str(__data_length) + "s"
        # 认为正在解码
        elif self.avp['AVP_CODE_STATE'] == self.dcc.dcc_def.const.DECODE_DCC_AVP_HEAD_END:
            # 根据self.avp['AVP_LENGTH']进行判断
            if self.avp['AVP_VENDOR_ID'] == 0x00:
                __data_length = self.avp['AVP_LENGTH'] - 8
            else:
                __data_length = self.avp['AVP_LENGTH'] - 12
                
            self.avp['AVP_CODE_OPERATOR'] = "!" + str(__data_length) + "s"
        
    def _AVP__after_decode_data(self):
        self.avp['AVP_DATA'] = self.avp['AVP_DATA'].rstrip('\x00')
        