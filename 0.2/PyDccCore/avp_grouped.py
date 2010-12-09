#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl

'''
from avp import AVP
import avp_factory

class Grouped(AVP):
    '''该数据字段定义为一个AVP序列。这些AVP按其定义的顺序排列，
            每一个都包括它们的头和填充位。AVP长度字段值设置为8（如果“V”比特有效，则为12），
            加上所有序列内的AVP的长度总和。因此Grouped类型的AVP的AVP长度字段总是4的倍数。
    '''
    def __init__(self,
                 cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
        AVP.__init__(self, cmd_code, avp_code, avp_data, decode_buf, dcc_instance)
        
    def _AVP__set_avp_operator_type(self):
        pass
        
    def _AVP__encode_data(self):
        '''生成子avp的实例，递归编码'''
        self.avp['AVP_BUF'] = ''
        # 遍历传入的列表，生成实例，进行编码
        for sub_avp_obj_ in self.avp['AVP_DATA']:
            avp_instance = avp_factory.create_avp(self.my_cmd_code,
                                                  sub_avp_obj_.keys()[0],
                                                  sub_avp_obj_.values()[0],
                                                  None,
                                                  self.dcc)
            avp_instance.encode()
            self.avp['SUB_AVP'].append(avp_instance)
            self.avp['AVP_BUF'] += avp_instance.avp['AVP_BUF']
            
        return self.avp['AVP_BUF']
            
    def _AVP__encode_avp_flag_and_length(self):
        '重载，调用子avp的长度之和为长度'
        # AVP_CODE + AVP_FLAG + AVP_LENGTH的长度
        self.avp['AVP_LENGTH'] += 4 + 4
        
        # 如果含有Vendor_id则长度增加4
        if self.avp['AVP_VENDOR_ID'] != 0:
            self.avp['AVP_LENGTH'] += 4
            
        # 如果是Grouped类型，遍历SUBS_AVP，累加AVP_LENGTH
        for sub_avp_obj_ in self.avp['SUB_AVP']:
            self.avp['AVP_LENGTH'] += len(sub_avp_obj_.avp['AVP_BUF'])
        
        # 编码 AVP_FLAG 和 AVP_LENGTH
        flag_and_length = ( (self.avp['AVP_FLAG']<<24) \
                            | self.avp['AVP_LENGTH'])
        
        return self.dcc.pack_data2bin("!I", flag_and_length)
        
    def _AVP__decode_data(self, offset):
        '''重载，将AVP_BUF多次进行解析'''
        offset_ = offset
        self.avp['AVP_DATA'] = []
        while offset_ < self.avp['AVP_LENGTH']:
            sub_buf_ = self.avp['AVP_BUF'][offset_:]
            avp_instance = avp_factory.create_avp(self.my_cmd_code,
                                                  None,
                                                  None,
                                                  sub_buf_,
                                                  self.dcc)
            avp_instance.decode()
            self.avp['SUB_AVP'].append(avp_instance)
            self.avp['AVP_DATA'].append(repr({repr(avp_instance.avp['AVP_CODE']):avp_instance.avp['AVP_DATA']}))
            
            # avp['AVP_LENGTH'] 因为是标明的长度，但是dcc要求是4的倍数，所以在这里进行修正
            lengthset = (avp_instance.avp['AVP_LENGTH'] + 3) // 4 * 4
            
            offset_ += lengthset
            