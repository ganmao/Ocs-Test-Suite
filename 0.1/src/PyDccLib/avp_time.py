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
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        OctetString.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        
        self.avp['AVP_DATA_TYPE'] = "Time"
        
        self.avp['AVP_TIME_STAMP'] = None
        self.avp['AVP_TIME_STR'] = None
        
        
        # 编码时根据传入的日期格式转化为NTP时间戳
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_TIME_STR']   = self.avp['AVP_DATA']
            self.avp['AVP_DATA']       = self.Time2NTPStamp(self.avp['AVP_DATA'])
            self.avp['AVP_TIME_STAMP'] = self.avp['AVP_DATA']
            
            data_length = len(self.avp['AVP_DATA'])
            data_length = (data_length + 3) // 4 * 4
            self.avp['AVP_CODE_OPERATOR'] = "!" + str(data_length) + "s"
            
        # 可读格式输出模板
        self.print_template = self.make_template("\
${L}AVP_CODE       = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}AVP_FLAG       = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}AVP_LENGTH     = [${AVP_LENGTH}] \n\
${L}AVP_VENDOR_ID  = [${AVP_VENDOR_ID}] \n\
${L}AVP_TIME_STAMP = [${AVP_TIME_STAMP}]\n\
${L}AVP_TIME_STR   = [${AVP_TIME_STR}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.print_detail_template = self.make_template("\
${L}${AVP_CODE_HEX}\n${L}\tAVP_CODE       = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}${AVP_FLAGS_HEX}\n${L}\tAVP_FLAG       = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}${AVP_LENGTH_HEX}\n${L}\tAVP_LENGTH     = [${AVP_LENGTH}] \n\
${L}${AVP_VONDER_HEX}\n${L}\tAVP_VENDOR_ID  = [${AVP_VENDOR_ID}] \n\
${L}${AVP_DATA_HEX}\n\
${L}\tAVP_TIME_STAMP = [${AVP_TIME_STAMP}]\n\
${L}\tAVP_TIME_STR   = [${AVP_TIME_STR}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.simple_print_template = self.make_template("${L}${AVP_NAME}(${AVP_CODE}) = [${AVP_DATA}]")
        
    def decode_data(self, offset=8):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self._reset_operator_type()
        
        (self.avp['AVP_DATA'],) = self.unpack_from_bin(self.avp['AVP_CODE_OPERATOR'], 
                                                 self.avp['AVP_BUF'], 
                                                 offset)
        
        self.avp['AVP_DATA_HEX'] = self.avp['AVP_BUF'][offset:]
        
        self.avp['AVP_TIME_STAMP'] = float(self.avp['AVP_DATA'])
        
        # Time类型需要将时间戳转为可读格式
        self.avp['AVP_DATA']     = self.NTPStamp2Time(self.avp['AVP_TIME_STAMP'])
        self.avp['AVP_TIME_STR'] = self.avp['AVP_DATA']
        
        return self.avp['AVP_LENGTH']
        