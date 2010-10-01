#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl

'''
from avp import AVP

class Grouped(AVP):
    '''该数据字段定义为一个AVP序列。这些AVP按其定义的顺序排列，
            每一个都包括它们的头和填充位。AVP长度字段值设置为8（如果“V”比特有效，则为12），
            加上所有序列内的AVP的长度总和。因此Grouped类型的AVP的AVP长度字段总是4的倍数。
    '''
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf=None,
                 cmd_etc_instance=None):
        AVP.__init__(self, avp_code, avp_data, vendor_id, 
                     mandatory, private, level, decode_buf,
                     cmd_etc_instance)
        
        if (self.cmd_etc == None and self.avp['AVP_CODE_STATE'] == "10"):
            raise self.err.AvpE_InvalidInitParam, \
                    "编码Grouped类型必须传入cmd_etc_instance！"
        
        self.avp['AVP_DATA_TYPE']    = "Grouped"
        
        self.avp['GROUPED_SUBS_BUF']    = "" # 用来保存Grouped内部子AVP_BUF
        self.avp['GROUPED_SUBS_AVP'] = [] # 保存解码或者加密后的avp实例
        
        self.print_template_group = self.make_template("\
${L}AVP_CODE      = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}AVP_FLAG      = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}AVP_LENGTH    = [${AVP_LENGTH}] \n\
${L}AVP_VENDOR_ID = [${AVP_VENDOR_ID}] \n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.print_detail_template_group = self.make_template("\
${L}${AVP_CODE_HEX}\n${L}\tAVP_CODE      = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}${AVP_FLAGS_HEX}\n${L}\tAVP_FLAG      = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}${AVP_LENGTH_HEX}\n${L}\tAVP_LENGTH    = [${AVP_LENGTH}] \n\
${L}${AVP_VONDER_HEX}\n${L}\tAVP_VENDOR_ID = [${AVP_VENDOR_ID}] \n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
    def encde_data(self):
        '''重载改变用途,直接返回已经打包好的PAVK_BUF'''
        self.avp['AVP_DATA'] = self.bin2ascii_hex(self.avp['GROUPED_SUBS_BUF'])
        return self.avp['GROUPED_SUBS_BUF']
            
    def append(self, avp_instance):
        '''接受传入的AVP实例，之后进行编码，将编码后的结果放入self.avp['GROUPED_SUBS_BUF']'''
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['GROUPED_SUBS_BUF'] += avp_instance.encode()
            avp_instance.set_avp_level(avp_instance.avp['AVP_LEVEL'] + 1)
            self.avp['GROUPED_SUBS_AVP'].append(avp_instance.avp)
        else:
            raise self.err.AvpE_InvalidCodeState, \
                    "状态错误[%s]！不能添加新的子AVP" % self.avp['AVP_CODE_STATE']
        
    def decode_data(self, offset=0):
        '''重载，需要根据不同的类型进行解码
                     每次解码一个AVP,将解码结果存储在self.avp['GROUPED_SUBS_AVP']的字典组成的数据中
                     此函数是为了解析Grouped中每一个avp
                     返回本次解码AVP包的长度
        '''
        (sub_avp_code,) = self.unpack_from_bin("!I", self.avp['AVP_BUF'], offset)
        #print "begin unpack:", sub_avp_code
        
        # 根据AVP_CODE 获取具体的AVP配置实例列表
        sub_avp_cfg = self.cmd_etc[str(sub_avp_code)]
        
        # 根据具体的avp配置实例列表，创建相应的AVP实例
        sub_avp = self.create_avp_instance(sub_avp_cfg,
                                           decode_buf=self.avp['AVP_BUF'])
        # 解析子AVP
        sub_avp.decode(offset)
        
        # 添加解析的子avp到GROUPED_SUBS_AVP
        self.avp['GROUPED_SUBS_AVP'].append(sub_avp.avp)
        
        return sub_avp.avp['AVP_LENGTH']
        
    def decode(self, offset=0):
        '''重载改变用途
                     用来从Greoped解析AVP包
                     每次根据包定义的长度，解析出来一个包的BUF返回
                     将解析中的offset记录在变量self.avp['GROUP_DECODE_OFFSET']中
                     判断指针移动到 (初始位置+self.avp['AVP_LENGTH'])认为解码完成
                     返回所解码Grouped内包的PACK_BUF
        '''
        offset_ = offset
        offset_ = self.decode_head(offset_)
        
        self.avp['AVP_DATA'] = self.bin2ascii_hex(self.avp['AVP_BUF'][offset_:])
        
        # 根据子AVP的总长度，循环解析子AVP_BUF
        while offset_ != (self.avp['AVP_LENGTH'] + offset):
            offset_ += self.decode_data(offset_)
            
        self.avp['AVP_CODE_STATE'] = "12"
        return self.avp
    
    def print_sub_avp(self, avp_dict, d_print=1):
        '打印Grouped的子avp'
        print_buf = ""
        avp_dict['AVP_CODE_HEX']   = "0x" + ("%08X" % avp_dict['AVP_CODE'])
        avp_dict['AVP_FLAGS_HEX']  = "0x" + ("%02X" % avp_dict['AVP_FLAG'])
        avp_dict['AVP_LENGTH_HEX'] = "0x" + ("%06X" % avp_dict['AVP_LENGTH'])
        if avp_dict['AVP_VENDOR_ID']:
            avp_dict['AVP_VONDER_HEX'] = "0x" + ("%08X" % avp_dict['AVP_VENDOR_ID'])
        avp_dict['AVP_DATA_HEX']   = "0x" + self.bin2ascii_hex(str(avp_dict['AVP_DATA_HEX'])).upper()
        
        if d_print == 1:
            print self.print_detail_template.safe_substitute(avp_dict)
        else:
            print_buf += self.print_detail_template.safe_substitute(avp_dict)
            
        if avp_dict['AVP_DATA_TYPE'] == 'Grouped':
            for sub_avp in avp_dict['GROUPED_SUBS_AVP']:
                self.print_sub_avp(sub_avp)
            
        return print_buf
        
    def print_avp(self, d_print=1):
        '''根据Grouped重载'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            print_buf = ""

            self.avp['AVP_CODE_HEX']   = "0x" + ("%08X" % self.avp['AVP_CODE'])
            self.avp['AVP_FLAGS_HEX']  = "0x" + ("%02X" % self.avp['AVP_FLAG'])
            self.avp['AVP_LENGTH_HEX'] = "0x" + ("%06X" % self.avp['AVP_LENGTH'])
            if self.avp['AVP_VENDOR_ID']:
                self.avp['AVP_VONDER_HEX'] = "0x" + ("%08X" % self.avp['AVP_VENDOR_ID'])
            else:
                self.avp['AVP_VONDER_HEX'] = "None"
            
            if d_print == 1:
                print self.print_detail_template_group.safe_substitute(self.avp)
            else:
                print_buf += self.print_detail_template_group.safe_substitute(self.avp)
                
            # 循环遍历self.avp['GROUPED_SUBS_AVP']，打印
            for sub_avp in self.avp['GROUPED_SUBS_AVP']:
                print_buf += self.print_sub_avp(sub_avp)
            
        else:
            raise self.err.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
        
        return print_buf
    
    def sprint_sub_avp(self, avp_dict, d_print=1):
        '打印Grouped的子avp'
        print_buf = ""

        if d_print == 1:
            print self.simple_print_template.safe_substitute(avp_dict)
        else:
            print_buf = self.simple_print_template.safe_substitute(avp_dict) + print_buf
            
        if avp_dict['AVP_DATA_TYPE'] == 'Grouped':
            for sub_avp in avp_dict['GROUPED_SUBS_AVP']:
                self.sprint_sub_avp(sub_avp)
            
        return print_buf
        
    def sprint(self, d_print=1):
        '''简单输出格式'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            print_buf = ""
            
            if d_print == 1:
                print self.simple_print_template.safe_substitute(self.avp)
            else:
                print_buf += self.simple_print_template.safe_substitute(self.avp)
                
            # 循环遍历self.avp['GROUPED_SUBS_AVP']，打印
            for sub_avp in self.avp['GROUPED_SUBS_AVP']:
                print_buf += self.sprint_sub_avp(sub_avp)
        else:
            raise self.err.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
                  
        return print_buf
    
    