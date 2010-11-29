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
        
        # 编码时根据传入的IP字符串判断地址族
        self.__addr_info = getaddrinfo(self.avp['AVP_DATA'],
                                self.dcc.dcc_def.const.DIAMETE_ADDRESS_PORT)
        
        if self.__addr_info[0][0] == AF_INET:
            self.avp['AVP_ADDR_FAMILY'] = 1
        elif self.__addr_info[0][0] == AF_INET6:
            self.avp['AVP_ADDR_FAMILY'] = 2
            
            
    def _AVP__set_avp_operator_type(self):
        '''需要根据不同的数据长度来设置解码格式'''
        # 认为正在编码
        if self.avp['AVP_CODE_STATE'] == self.dcc.dcc_def.const.ENCODE_DCC_AVP_BEGIN:
            if self.avp['AVP_ADDR_FAMILY'] == 1:
                self.avp['AVP_CODE_OPERATOR'] = "!h6s"
                # 数据长度=地址族标志(2)+地址编码(4)
                self.avp['AVP_LENGTH'] = 6
            elif self.avp['AVP_ADDR_FAMILY'] == 2:
                self.avp['AVP_CODE_OPERATOR'] = "!h18s"
                # 数据长度=地址族标志(2)+地址编码(16)
                # IPv6的没有实际编辑过，需要在unix上试一下再完善
                self.avp['AVP_LENGTH'] = 18
        # 认为正在解码
        elif self.avp['AVP_CODE_STATE'] == self.dcc.dcc_def.const.DECODE_DCC_AVP_HEAD_END:
            # 根据self.avp['AVP_LENGTH']进行判断
            if self.avp['AVP_VENDOR_ID'] == 0x00:
                __data_length = self.avp['AVP_LENGTH'] - 10
            else:
                __data_length = self.avp['AVP_LENGTH'] - 14
                
            self.avp['AVP_CODE_OPERATOR'] = "!h" + str(__data_length) + "s"
            
    def _AVP__encode_data(self):
        '''编码AVP_DATA'''
        return self.dcc.pack_data2bin(self.avp['AVP_CODE_OPERATOR'],
                                      self.avp['AVP_ADDR_FAMILY'],
                                      self.avp['AVP_DATA'])
        
    def _AVP__decode_data(self, offset):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_BODY_BEGIN
        
        (self.avp['AVP_ADDR_FAMILY'], self.avp['AVP_DATA']) \
            = self.dcc.unpack_from_bin(self.avp['AVP_CODE_OPERATOR'], 
                                       self.avp['AVP_BUF'], 
                                       offset)
        
        # 解码数据类型后进行一些后续处理
        self._AVP__after_decode_data()
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_BODY_END
        return self.avp['AVP_LENGTH']
    
    def _AVP__after_decode_data(self):
        if self.avp['AVP_ADDR_FAMILY'] == 1:
            self.avp['AVP_DATA'] = self.avp['AVP_DATA'][:4]
        elif self.avp['AVP_ADDR_FAMILY'] == 2:
            self.avp['AVP_DATA'] = self.avp['AVP_DATA'][:16]
        
        # 如果编译时支持IPv6，则可以使用 inet_ntop 函数解码
        self.avp['AVP_DATA'] = inet_ntoa(self.avp['AVP_DATA'])
        
    def _AVP__befor_encode_data(self):
        # 因为json的字符串编码采用UNICODE，所以在这里进行一下转换
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
        
        # 如果编译时添加了IPv6支持，可以调用 inet_pton 函数进行打包
        self.avp['AVP_DATA'] = inet_aton(self.avp['AVP_DATA'])