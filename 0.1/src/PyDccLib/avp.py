#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl
'''

from struct import pack, unpack_from, calcsize
from string import Template

import avp_const_define as ACD
import avp_error as D_ERROR

class AVP(object):
    '''
    AVP的基类，其他所有Dcc的数据类型都从这里继承
    '''
    
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf = None,
                 avp_config_instance=None):
        '''
        avp_config_instance    对应需编码的实例字典（编码时必填）
        
        '''
        
        # 可读格式输出模板
        self.print_template = Template("\
${L}AVP_CODE      = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}AVP_FLAG      = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}AVP_LENGTH    = [${AVP_LENGTH}] \n\
${L}AVP_VENDOR_ID = [${AVP_VENDOR_ID}] \n\
${L}AVP_DATA      = [${AVP_DATA}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.print_detail_template = Template("\
${L}${AVP_CODE_HEX}\n${L}\tAVP_CODE      = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}${AVP_FLAGS_HEX}\n${L}\tAVP_FLAG      = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}${AVP_LENGTH_HEX}\n${L}\tAVP_LENGTH    = [${AVP_LENGTH}] \n\
${L}${AVP_VONDER_HEX}\n${L}\tAVP_VENDOR_ID = [${AVP_VENDOR_ID}] \n\
${L}${AVP_DATA_HEX}\n${L}\tAVP_DATA      = [${AVP_DATA}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.simple_print_template = Template("${L}${AVP_NAME}(${AVP_CODE}) = [${AVP_DATA}]")
        
        self.avp_cfg = avp_config_instance
        
        self.avp                   = {}
        if decode_buf:  # 认定为需要解码
            self.avp['AVP_CODE']       = None
            self.avp['AVP_FLAG']       = None
            self.avp['AVP_LENGTH']     = None
            self.avp['AVP_DATA']       = None
            self.avp['AVP_VENDOR_ID']  = None
            self.avp['AVP_MANDATORY']  = None
            self.avp['AVP_PRIVATE']    = None
            
            self.avp['AVP_BUF']        = decode_buf
            
            # 00-准备编码，01-已解码头，02-已解码完毕
            # 10-准备解码，11-已编码头，12-已编码完毕
            self.avp['AVP_CODE_STATE'] = "10"
        else:           #认定为需要编码
            self.avp['AVP_CODE']       = avp_code
            self.avp['AVP_FLAG']       = 0
            self.avp['AVP_LENGTH']     = 0
            self.avp['AVP_DATA']       = avp_data
            self.avp['AVP_VENDOR_ID']  = vendor_id
            self.avp['AVP_MANDATORY']  = mandatory
            self.avp['AVP_PRIVATE']    = private
            
            self.avp['AVP_BUF']        = None
            self.avp['AVP_CODE_STATE'] = "00"
            
            if (self.avp['AVP_CODE'] == 0):
                raise D_ERROR.AvpE_InvalidInitParam, \
                    "初始化参数错误，请检查！\n\tAVP_CODE=0"
        
        self.avp['AVP_LEVEL']          = int(level)
        self.avp['AVP_CODE_OPERATOR']  = "!i"
        self.avp['AVP_DATA_TYPE']      = "Integer32"
        self.avp['L']                  = self.avp['AVP_LEVEL'] * "\t"
        
        self.avp['AVP_CODE_HEX']       = None
        self.avp['AVP_FLAGS_HEX']      = None
        self.avp['AVP_LENGTH_HEX']     = None
        self.avp['AVP_VONDER_HEX']     = None
        self.avp['AVP_DATA_HEX']       = None
        self.avp['AVP_ORDER']          = 0
        
    def __del__(self):
        del self.avp
        del self.print_template
        del self.simple_print_template
        del self.avp_cfg 
        
    def __repr__(self):
        if (self.avp['AVP_CODE_STATE'][1:] == "2"):
            return repr(self.avp['AVP_DATA'])
        else:
            raise D_ERROR.AvpE_InvalidCodeState, "编码/解码还未完成，当前不能输出结果"
        
    def __str__(self):
        return self.__repr__()
    
    def encode_head(self):
        '''编码AVP包头'''
        self.avp['AVP_LENGTH'] = 4 + 4   # AVP_CODE + AVP_FLAG + AVP_LENGTH的长度
        
        # 集中设置AVP的各个属性
#        self.set_avp_data()
#        self.set_avp_vonder_id()
#        self.set_avp_mandatory()
#        self.set_avp_proxy()
#        self.set_avp_level()
        
        # 编码AVP_CODE
        avp_head_buf = pack("!I", self.avp['AVP_CODE'])
        
        # 编码AVP_FLAG 和 AVP_LENGTH
        if self.avp['AVP_VENDOR_ID'] != 0:       # 如果含有Vendor_id则长度增加4
            self.avp['AVP_LENGTH'] += 4

        self.avp['AVP_LENGTH'] += len(self.avp['AVP_BUF'])
        
        # 确定AVP_FLAG
        # Vendor_id != 0 则需要添加FLAG标志和
        if self.avp['AVP_VENDOR_ID'] != 0:
            self.avp['AVP_FLAG'] |= ACD.const.AVP_FLAG_VENDOR
        if self.avp['AVP_MANDATORY'] != 0:
            self.avp['AVP_FLAG'] |= ACD.const.AVP_FLAG_MANDATORY
        if self.avp['AVP_PRIVATE'] != 0:
            self.avp['AVP_FLAG'] |= ACD.const.AVP_FLAG_PRIVATE
            
        # 编码AVP_FLAG 和 AVP_LENGTH
        flag_and_length = ( (self.avp['AVP_FLAG']<<24) \
                            | self.avp['AVP_LENGTH'])
        
        avp_head_buf += pack("!I", flag_and_length)
        
        # 编码VENDOR_ID
        if self.avp['AVP_VENDOR_ID'] != 0:
            avp_head_buf += pack("!I", self.avp['AVP_VENDOR_ID'])
        
        self.avp['AVP_CODE_STATE'] = "01"
        return avp_head_buf
    
    def encde_data(self):
        '''编码AVP_DATA'''
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
            
        return pack(self.avp['AVP_CODE_OPERATOR'], self.avp['AVP_DATA'])
        
    def encode(self):
        '''编码整个AVP包，返回编码后的PACK_BUF'''
        if self.avp['AVP_CODE_STATE'] != "00":
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的状态[%s]，当前无法继续编码！" % \
                     self.avp['AVP_CODE_STATE']
                     
        self.avp['AVP_CODE'] = int(self.avp['AVP_CODE'])
                     
        self.avp['AVP_BUF'] = self.encde_data()
        self.avp['AVP_DATA_HEX'] = "0x" + self.avp['AVP_BUF']
        
        self.avp['AVP_BUF'] = self.encode_head() + self.avp['AVP_BUF']
        
        self.avp['AVP_CODE_STATE'] = "02"
            
        return self.avp['AVP_BUF']
    
    def decode_head(self, offset=0):
        '''解码AVP头
                     返回包头的总长度位置
        '''
        offset_ = offset
        
        # 解码AVP_CODE
        
        (self.avp['AVP_CODE'],) = unpack_from("!I", 
                                                 self.avp['AVP_BUF'], 
                                                 offset_)
        offset_                   += 4
        
        # 解码AVP_FLAG 和 AVP_LENGTH
        (flags_and_length,)       = unpack_from("!I", 
                                                self.avp['AVP_BUF'], 
                                                offset_)
        self.avp['AVP_FLAG']      = (flags_and_length >> 24)
        self.avp['AVP_LENGTH']    = (flags_and_length & 0x00FFFFFF)
        offset_                  += 4
        
        # 解析 VENDOR_ID
        if (self.avp['AVP_FLAG'] & ACD.const.AVP_FLAG_VENDOR) \
                == ACD.const.AVP_FLAG_VENDOR:       # 说明存在VONDER_ID
            if self.avp['AVP_LENGTH'] < 12:
                raise D_ERROR.AvpE_InvalidAvpLength, "AVP的长度定义错误！"
            
            (self.avp['AVP_VENDOR_ID'],) = \
                                unpack_from("!I",
                                            self.avp['AVP_BUF'], 
                                            offset_)
            offset_ += 4
        else:
            if self.avp['AVP_LENGTH'] < 8:
                raise D_ERROR.AvpE_InvalidAvpLength, "AVP的长度定义错误！"
            self.avp['AVP_VENDOR_ID'] = 0
            
        # 解析 MANDATORY
        if (self.avp['AVP_FLAG'] & ACD.const.AVP_FLAG_MANDATORY) \
                == ACD.const.AVP_FLAG_MANDATORY:
            self.avp['AVP_MANDATORY'] = 1
        else:
            self.avp['AVP_MANDATORY'] = 0
        
        # 解析 PRIVATE
        if (self.avp['AVP_FLAG'] & ACD.const.AVP_FLAG_PRIVATE) \
                == ACD.const.AVP_FLAG_PRIVATE:
            self.avp['AVP_PRIVATE'] = 1
        else:
            self.avp['AVP_PRIVATE'] = 0
        
        self.avp['AVP_CODE_STATE'] = "11"
        return offset_
    
    def decode_data(self, offset=8):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self._reset_operator_type()
        
        (self.avp['AVP_DATA'],) = unpack_from(self.avp['AVP_CODE_OPERATOR'], 
                                                 self.avp['AVP_BUF'], 
                                                 offset)
        self.avp['AVP_DATA_HEX'] = pack(self.avp['AVP_CODE_OPERATOR'], 
                                        self.avp['AVP_DATA'])
        return self.avp['AVP_LENGTH']
    
    def decode(self, offset=0):
        '''解码AVP包, 返回所解码包的PACK_BUF'''
        if self.avp['AVP_CODE_STATE'] != "10":
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的状态[%s]，请检查实例化的参数是否错误！" % \
                     self.avp['AVP_CODE_STATE']
        
        offset_ = offset
        offset_ = self.decode_head(offset_)
        self.decode_data(offset_)
        
        self._fmt_avp_data()
        self.avp['AVP_CODE_STATE'] = "12"
        
        return self.avp['AVP_BUF']
    
    def _reset_operator_type(self):
        '''重置一下operator_type，因为一些string类型的长度不定'''
        pass
    
    def _fmt_avp_data(self):
        '''对于已经解码的数据进行格式化，等待具体类型重载'''
        pass
                    
    def create_avp_factory(self, sub_avp_data_type):
        '''根据不同的数据类型创建不同的数据实例'''
        from avp_integer32 import Integer32
        from avp_integer64 import Integer64
        from avp_unsigned32 import Unsigned32
        from avp_unsigned64 import Unsigned64
        from avp_octetstring import OctetString
        from avp_float32 import Float32
        from avp_float64 import Float64
        
        if sub_avp_data_type == "Integer32":
            sub_avp = Integer32(decode_buf=self.avp['AVP_BUF'],
                                level=self.avp['AVP_LEVEL'] + 1)
        elif sub_avp_data_type == "Integer64":
            sub_avp = Integer64(decode_buf=self.avp['AVP_BUF'],
                                level=self.avp['AVP_LEVEL'] + 1)
        elif sub_avp_data_type == "Unsigned32":
            sub_avp = Unsigned32(decode_buf=self.avp['AVP_BUF'],
                                 level=self.avp['AVP_LEVEL'] + 1)
        elif sub_avp_data_type == "Unsigned64":
            sub_avp = Unsigned64(decode_buf=self.avp['AVP_BUF'],
                                 level=self.avp['AVP_LEVEL'] + 1)
        elif sub_avp_data_type == "OctetString":
            sub_avp = OctetString(decode_buf=self.avp['AVP_BUF'],
                                  level=self.avp['AVP_LEVEL'] + 1)
        elif sub_avp_data_type == "Float32":
            sub_avp = Float32(decode_buf=self.avp['AVP_BUF'],
                                  level=self.avp['AVP_LEVEL'] + 1)
        elif sub_avp_data_type == "Float64":
            sub_avp = Float64(decode_buf=self.avp['AVP_BUF'],
                                  level=self.avp['AVP_LEVEL'] + 1)
        else:
            raise D_ERROR.AvpE_InvalidAvpDataType, \
                  "错误的数据类型，无法解析：[%s]" % sub_avp_data_type
                
        return sub_avp
        
    def get_avp_code(self, pack_buf, offset=0):
        (avp_code,) = unpack_from("!I", pack_buf, offset)
        return avp_code
    
    def get_avp_flags(self, pack_buf, offset=4):
        (flags_and_length,) = unpack_from("!I", pack_buf, offset)
        return flags_and_length >> 24
    
    def get_avp_length(self, pack_buf, offset=4):
        (flags_and_length,) = unpack_from("!I", pack_buf, offset)
        return flags_and_length & 0x00FFFFFF
    
    def set_avp_data(self, avp_data):
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_DATA'] = avp_data
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_DATA！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_level(self, level):
        '''重设具体的self.avp['AVP_LEVEL']值,重新计算self.avp['L']'''
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_LEVEL'] = level
            self.avp['L'] = self.avp['AVP_LEVEL'] * "\t"
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_LEVEL！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_vonder_id(self, vendor_id):
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_VENDOR_ID'] = vendor_id
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_VENDOR_ID！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_mandatory(self, mandatory):
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_MANDATORY'] = mandatory
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_MANDATORY！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_private(self, private):
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_PRIVATE'] = private
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_PRIVATE！" % \
                    self.avp['AVP_CODE_STATE']
        
    def print_avp(self, d_print=1):
        '''按照规定格式输出数据'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            print_buf = ""
            
            if ACD.const.DEBUG_LEVEL == "DEBUG":
                from binascii import b2a_hex
                self.avp['AVP_CODE_HEX']   = "0x" + ("%08X" % self.avp['AVP_CODE'])
                self.avp['AVP_FLAGS_HEX']  = "0x" + ("%02X" % self.avp['AVP_FLAG'])
                self.avp['AVP_LENGTH_HEX'] = "0x" + ("%06X" % self.avp['AVP_LENGTH'])
                if self.avp['AVP_VENDOR_ID'] is not None:
                    self.avp['AVP_VONDER_HEX'] = "0x" + ("%08X" % self.avp['AVP_VENDOR_ID'])
                self.avp['AVP_DATA_HEX']   = "0x" + b2a_hex(self.avp['AVP_DATA_HEX']).upper()
                if d_print == 1:
                    print self.print_detail_template.safe_substitute(self.avp)
                else:
                    print_buf += self.print_detail_template.safe_substitute(self.avp)
            else:
                print self.print_template.safe_substitute(self.avp)
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
                  
        return print_buf
        
    def pa(self, d_print=1):
        '''简单输出格式'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            if d_print == 1:
                print self.simple_print_template.safe_substitute(self.avp)
            else:
                return self.simple_print_template.safe_substitute(self.avp)
        else:
            raise D_ERROR.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
