#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl

'''
from string import Template
import binascii
from struct import unpack_from

import avp_error as D_ERROR

from avp import AVP

class Grouped(AVP):
    '''该数据字段定义为一个AVP序列。这些AVP按其定义的顺序排列，
            每一个都包括它们的头和填充位。AVP长度字段值设置为8（如果“V”比特有效，则为12），
            加上所有序列内的AVP的长度总和。因此Grouped类型的AVP的AVP长度字段总是4的倍数。
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 avp_config_instance=None):
        AVP.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     avp_config_instance)
        
        if (self.avp_cfg == None and self.avp['AVP_CODE_STATE'] == "10"):
            raise D_ERROR.AvpE_InvalidInitParam, \
                    "编码Grouped类型必须传入avp_config_instance！"
        
        self.avp['AVP_DATA_TYPE']    = "Grouped"
        
        self.avp['GROUP_SUB_BUF']    = "" # 用来保存Grouped内部子AVP_BUF
        self.avp['GROUPED_SUBS_AVP'] = []
        self.avp['AVP_CODE_OPERATOR'] = None
        
        self.print_template_group = Template("\
${L}AVP_CODE=${AVP_CODE} - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}AVP_FLAG=${AVP_FLAG} (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}AVP_LENGTH=${AVP_LENGTH} \n\
${L}AVP_VENDOR_ID=${AVP_VENDOR_ID} \n\
${L}AVP_DATA=${AVP_BUF}\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
    def encde_data(self):
        '''重载改变用途,直接返回已经打包好的PAVK_BUF'''
        self.avp['AVP_DATA'] = binascii.b2a_hex(self.avp['GROUP_SUB_BUF'])
        return self.avp['GROUP_SUB_BUF']
    
    def append(self, pack_buf):
        '''Grouped专用来给其添加子AVP'''
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['GROUP_SUB_BUF'] += pack_buf
        
    def decode_data(self, offset=0):
        '''重载，需要根据不同的类型进行解码
                     每次解码一个AVP,将解码结果存储在self.avp['GROUPED_SUBS_AVP']的字典组成的数据中
                     返回本次解码AVP包的长度
        '''
        (sub_avp_code,) = unpack_from("!I", self.avp['AVP_BUF'], offset)
        
        sub_avp_data_type = self._find_avp_data_type(sub_avp_code)
        
        sub_avp = self.create_avp_factory(sub_avp_data_type)
                  
        sub_avp.decode(offset)
        
        self.avp['GROUPED_SUBS_AVP'].append(sub_avp.avp)
        return sub_avp.avp['AVP_LENGTH']
    
    def _calc_encode_size(self, data_type):
        '''因为Greoup类型的包长是等具体子AVP确定后才能确定，
                                     通过_reset_avp_length进行设置的，所以这里返回0
        '''
        return 0
    
    def _find_avp_data_type(self, avp_code):
        '''根据传入的AVP_CODE查找到对应的类型
                      需要加载配置文件后定义
        '''
        if avp_code in self.avp_cfg:
            return self.avp_cfg[avp_code][4]
        else:
            raise D_ERROR.AvpE_InvalidEtcParam, \
                    "没有匹配到相应的AVP_CODE： [%s]" % avp_code
        
    def decode(self, offset=0):
        '''重载改变用途
                     用来从Greoped解析AVP包
                     每次根据包定义的长度，解析出来一个包的BUF返回
                     将解析中的offset记录在变量self.avp['GROUP_DECODE_OFFSET']中
                     判断指针移动到 (初始位置+self.avp['AVP_LENGTH'])认为解码完成
                     返回所解码Grouped内包的PACK_BUF
        '''
        offset_ = offset
        offset_ += self.decode_head(offset_)
        
        self.avp['AVP_DATA'] = binascii.b2a_hex(self.avp['AVP_BUF'][offset_:])
        
        # 根据子AVP的总长度，循环解析子AVP
        while offset_ != (self.avp['AVP_LENGTH'] + offset):
            offset_ += self.decode_data(offset_)
            
        self.avp['AVP_CODE_STATE'] = "12"
        return self.avp['AVP_BUF']
        
    def print_avp(self):
        '''根据Grouped重载'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            print self.print_template_group.safe_substitute(self.avp)
            
            # 循环遍历self.avp['GROUPED_SUBS_AVP']，打印
            for sub_avp in self.avp['GROUPED_SUBS_AVP']:
                print self.print_template.safe_substitute(sub_avp)
                
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
        
    def pa(self):
        '''简单输出格式'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            print self.simple_print_template.safe_substitute(self.avp)
            
            # 循环遍历self.avp['GROUPED_SUBS_AVP']，打印
            for sub_avp in self.avp['GROUPED_SUBS_AVP']:
                print self.simple_print_template.safe_substitute(sub_avp)
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
