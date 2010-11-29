#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-10-1

@author: zdl
'''
from avp_octetstring import OctetString

class Time(OctetString):
    '''
            时间格式是从OctetString AVP基本格式导出的。该字符串必须包含4个八位组，
            与NTP时间戳格式的前4个字节格式相同。NTP时间戳在NTP协议规范［RFC2030］
            第3章中定义。本格式描述的时间，从通用协调时间（UTC）1900年1月1日0点
            开始。在UTC时间2036年二月7日6点28分16秒，时间值将溢出。SNTP规范中描述
            了将时间扩展到2104年的程序，所有DIAMETER节点都必须支持该程序。
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
        
    def _AVP__set_avp_operator_type(self):
        self.avp['AVP_CODE_OPERATOR'] = '!I'

    def _AVP__after_decode_data(self):
        self.avp['AVP_DATA'] = self.dcc.NTPStamp2Time(self.avp['AVP_DATA'])
        
    def _AVP__befor_encode_data(self):
        # 因为json的字符串编码采用UNICODE，所以在这里进行一下转换
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
        
        # 编码时根据传入的日期格式转化为NTP时间戳
        self.avp['AVP_DATA'] = int(self.dcc.Time2NTPStamp(self.avp['AVP_DATA']))