#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-30

@author: zdl
'''
from socket import AF_INET, AF_INET6, getaddrinfo, inet_aton, inet_ntoa#, inet_pton, inet_ntop

from avp_octetstring import OctetString

class Address(OctetString):
    '''
            地址格式是从OctetString AVP基本格式导出的。它与其它数据格式不同，例如需要
            区分32比特（IPV4）或128比特（IPV6）地址。地址AVP的头两个八位组为AddressType，
            其包含一个在［IANA的“地址簇号码”］中定义的地址簇。AddressType用来区别剩下
            八位组的内容和格式。
    IANA的“地址簇号码”的定义参见:
    http://www.iana.org/assignments/address-family-numbers/address-family-numbers.xml
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        OctetString.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        
        self.avp['AVP_DATA_TYPE'] = "Address"
        
        # 编码时根据传入的IP字符串判断地址族
        if self.avp['AVP_CODE_STATE'] == "00":
            addr_info = getaddrinfo(self.avp['AVP_DATA'], 3868)
            if addr_info[0][0] == AF_INET:
                self.avp['AVP_ADDR_FAMILY'] = 1
            elif addr_info[0][0] == AF_INET6:
                self.avp['AVP_ADDR_FAMILY'] = 2
                
            if self.avp['AVP_ADDR_FAMILY'] == 1:
                self.avp['AVP_CODE_OPERATOR'] = "!h6s"
            elif self.avp['AVP_ADDR_FAMILY'] == 2:
                self.avp['AVP_CODE_OPERATOR'] = "!h18s"
                
            self.avp['AVP_DATA'] = inet_aton(self.avp['AVP_DATA'])
            
        # 可读格式输出模板
        self.print_template = self.make_template("\
${L}AVP_CODE        = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}AVP_FLAG        = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}AVP_LENGTH      = [${AVP_LENGTH}] \n\
${L}AVP_VENDOR_ID   = [${AVP_VENDOR_ID}] \n\
${L}AVP_ADDR_FAMILY = [${AVP_ADDR_FAMILY}] \n\
${L}AVP_DATA        = [${AVP_DATA}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.print_detail_template = self.make_template("\
${L}${AVP_CODE_HEX}\n${L}\tAVP_CODE        = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}${AVP_FLAGS_HEX}\n${L}\tAVP_FLAG        = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}${AVP_LENGTH_HEX}\n${L}\tAVP_LENGTH      = [${AVP_LENGTH}] \n\
${L}${AVP_VONDER_HEX}\n${L}\tAVP_VENDOR_ID   = [${AVP_VENDOR_ID}] \n\
${L}${AVP_DATA_HEX} \n\
${L}\tAVP_ADDR_FAMILY = [${AVP_ADDR_FAMILY}] \n\
${L}\tAVP_DATA        = [${AVP_DATA}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.simple_print_template = self.make_template("${L}${AVP_NAME}(${AVP_CODE}) = [${AVP_ADDR_FAMILY}][${AVP_DATA}]")
            
    def _reset_operator_type(self):
        '''需要根据不同的数据长度来设置解码格式'''
        if self.avp['AVP_CODE_STATE'] in ["10", "11"]:
            if self.avp['AVP_VENDOR_ID'] == 0:
                self.avp['AVP_CODE_OPERATOR'] = "!h" + str(self.avp['AVP_LENGTH'] - 10) + "s"
            else:
                self.avp['AVP_CODE_OPERATOR'] = "!h" + str(self.avp['AVP_LENGTH'] - 14) + "s"
        else:
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的状态[%s]，当前不能重置操作类型！" % \
                     self.avp['AVP_CODE_STATE']
            
    def encde_data(self):
        '''编码AVP_DATA'''
        # 因为json的字符串编码采用UNICODE，所以在这里进行一下转换
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
            
        return self.pack_bin(self.avp['AVP_CODE_OPERATOR'], 
                             self.avp['AVP_ADDR_FAMILY'], 
                             self.avp['AVP_DATA'])
        
    def decode_data(self, offset=8):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self._reset_operator_type()
        
        (self.avp['AVP_ADDR_FAMILY'], self.avp['AVP_DATA']) = \
                            self.unpack_from_bin(self.avp['AVP_CODE_OPERATOR'], 
                                                 self.avp['AVP_BUF'], 
                                                 offset)
                            
        self.avp['AVP_DATA_HEX'] = self.avp['AVP_DATA']
        
        self.avp['AVP_DATA'] = inet_ntoa(self.avp['AVP_DATA'][:4])
        
        return self.avp['AVP_LENGTH']