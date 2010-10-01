#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl

使用说明：
～～～～～～～～～～～～～～～～～～～～～～～～～
AVP初始化参数说明：
===============================================
    avp_code            AVP编码（编码时必传）
    avp_data            AVP数据（编码时必传）
    vendor_id
    mandatory 
    private 
    level               AVP等级，主要在打印时用到
    decode_buf          需要解包的AVP二进制数据(解码时必填)
    
    如果decode_buf被赋值，则认为是需要进行解码，否则认为需要进行编码
    
    编码：
    avp_packer = PyDccLib.Integer32(avp_code, avp_data)
    解码：
    avp_unpacker = PyDccLib.Integer32(decode_buf=BUF)
    
    
其他方法说明：
    print_avp()    打印详细的解码或者编码后结果
    pa()            打印简单的解码或编码后结果
===============================================
'''

from struct import pack, unpack_from
from string import Template
from binascii import b2a_hex
from time import strftime, strptime, mktime, localtime
from codecs import getencoder, getdecoder

import avp_const_define as ACD
import avp_error as D_ERROR
import dcc_msg

class AVP(object):
    '''
    AVP的基类，其他所有Dcc的数据类型都从这里继承
    '''
    
    def __init__(self, avp_code=0, avp_data=None, vendor_id=0, 
                 mandatory=0, private=0, level=0, decode_buf = None,
                 cmd_etc_instance=None):
        '''
        cmd_etc_instance    对应需编码的实例字典（编码时必填）
        
        '''
        self.err = D_ERROR
        self.const = ACD
        self.seconds_between_1900_and_1970 = ((70*365)+17)*86400
        
        self.COMPACTTIMEFORMAT = '%Y%m%d%H%M%S'       #例:20090313102835
        self.ISOTIMEFORMAT = '%Y-%m-%d %X'            #例:2009-03-13 10:28:35
        self.TIMEFORMAT=self.COMPACTTIMEFORMAT
        
        self.avp = {}
        if decode_buf:  # 认定为需要解码
            self.avp['AVP_CODE']       = 0x00
            self.avp['AVP_FLAG']       = 0x00
            self.avp['AVP_LENGTH']     = 0x00
            self.avp['AVP_DATA']       = ""
            self.avp['AVP_VENDOR_ID']  = 0x00
            self.avp['AVP_MANDATORY']  = 0x00
            self.avp['AVP_PRIVATE']    = 0x00
            
            self.avp['AVP_BUF']        = decode_buf
            
            # 00-准备编码，01-已编码头，02-已编码完毕
            # 10-准备解码，11-已解码头，12-已解码完毕
            self.avp['AVP_CODE_STATE'] = "10"
        else:           #认定为需要编码
            self.avp['AVP_CODE']       = avp_code
            self.avp['AVP_FLAG']       = 0x00
            self.avp['AVP_LENGTH']     = 0x00
            self.avp['AVP_DATA']       = avp_data
            self.avp['AVP_VENDOR_ID']  = vendor_id
            self.avp['AVP_MANDATORY']  = mandatory
            self.avp['AVP_PRIVATE']    = private
            
            self.avp['AVP_BUF']        = ""
            self.avp['AVP_CODE_STATE'] = "00"
            
            if (self.avp['AVP_CODE'] == 0x00):
                raise self.err.AvpE_InvalidInitParam, \
                    "初始化参数错误，请检查！\n\tAVP_CODE=0x00"
        
        self.avp['AVP_LEVEL']          = int(level)
        self.avp['AVP_CODE_OPERATOR']  = "!i"
        self.avp['AVP_DATA_TYPE']      = "Integer32"
        self.avp['L']                  = self.avp['AVP_LEVEL'] * "\t"
        
        self.avp['AVP_CODE_HEX']       = 0x00
        self.avp['AVP_FLAGS_HEX']      = 0x00
        self.avp['AVP_LENGTH_HEX']     = 0x00
        self.avp['AVP_VONDER_HEX']     = 0x00
        self.avp['AVP_DATA_HEX']       = 0x00
        
        self.cmd_etc = cmd_etc_instance
        
        # 可读格式输出模板
        self.print_template = self.make_template("\
${L}AVP_CODE      = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}AVP_FLAG      = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}AVP_LENGTH    = [${AVP_LENGTH}] \n\
${L}AVP_VENDOR_ID = [${AVP_VENDOR_ID}] \n\
${L}AVP_DATA      = [${AVP_DATA}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.print_detail_template = self.make_template("\
${L}${AVP_CODE_HEX}\n${L}\tAVP_CODE      = [${AVP_CODE}] - ${AVP_NAME} - ${AVP_DATA_TYPE}(\"${AVP_CODE_OPERATOR}\") \n\
${L}${AVP_FLAGS_HEX}\n${L}\tAVP_FLAG      = [${AVP_FLAG}] (VENDOR_ID(${AVP_VENDOR_ID})|MANDATORY(${AVP_MANDATORY})|PRIVATE(${AVP_PRIVATE}) \n\
${L}${AVP_LENGTH_HEX}\n${L}\tAVP_LENGTH    = [${AVP_LENGTH}] \n\
${L}${AVP_VONDER_HEX}\n${L}\tAVP_VENDOR_ID = [${AVP_VENDOR_ID}] \n\
${L}${AVP_DATA_HEX}\n${L}\tAVP_DATA      = [${AVP_DATA}]\n\
${L}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        self.simple_print_template = self.make_template("${L}${AVP_NAME}(${AVP_CODE}) = [${AVP_DATA}]")
        
    def __del__(self):
        del self.avp
        del self.print_template
        del self.simple_print_template
        del self.cmd_etc 
        
    def __repr__(self):
        if (self.avp['AVP_CODE_STATE'][1:] == "2"):
            return repr(self.avp['AVP_DATA'])
        else:
            raise self.err.AvpE_InvalidCodeState, "编码/解码还未完成，当前不能输出结果"
        
    def __str__(self):
        return self.__repr__()
    
    def make_template(self, tmp_str):
        '重载string.Template函数'
        return Template(tmp_str)
    
    def pack_bin(self, fmt, *pack_data):
        '重载struct.pack函数,但是只支持同时两个类型进行压缩'
        if len(pack_data) == 2:
            return pack(fmt, pack_data[0], pack_data[1])
        else:
            return pack(fmt, pack_data[0])
        
    def unpack_from_bin(self, fmt, buf, offset=0):
        '重载struct.unpack_from函数'
        return unpack_from(fmt, buf, offset)
    
    def bin2ascii_hex(self, buf):
        '重载binascii.b2a_hex函数'
        return b2a_hex(buf)
    
    def NTPStamp2Time(self, stamp_int):
        '将NTP时间戳转换为年月日的时间格式'
        #stamp_int = float(repr(stamp_int))
        myUTCTime = stamp_int - self.seconds_between_1900_and_1970
        return strftime(self.TIMEFORMAT, localtime(myUTCTime))
        
    def UTCStamp2Time(self, stamp_int):
        '将UTC时间戳转换为年月日的时间格式'
        return strftime(self.TIMEFORMAT, localtime(stamp_int))
        
    def Time2NTPStamp(self, time_str):
        '将年月日的时间格式转换为NTP时间戳,'
        # TIMEFORMAT = '2009-03-13 10:28:35'
        if len(time_str) == 19 and time_str[4] == '-' and time_str[7] == '-' \
           and time_str[10] == ' ' and time_str[13] == ':' and time_str[16] == ':':
            myFormat = strptime(time_str, self.ISOTIMEFORMAT)
            outStamp = mktime(myFormat)
            outStamp = outStamp + self.seconds_between_1900_and_1970
            return str(outStamp)
        # TIMEFORMAT = '20090313102835'
        elif len(time_str) == 14:
            myFormat = strptime(time_str, self.COMPACTTIMEFORMAT)
            outStamp = mktime(myFormat)
            outStamp = outStamp + self.seconds_between_1900_and_1970
            return str(outStamp)
        else:
            raise self.err.AvpE_InvalidInitParam,\
                        "传入的时间格式错误！[%s][%s]" % (self.TIMEFORMAT, time_str)
        
    def Time2TUCStamp(self, time_str):
        '将年月日的时间格式转换为UTC时间戳'
        # TIMEFORMAT = '2009-03-13 10:28:35'
        if len(time_str) == 19 and time_str[4] == '-' and time_str[7] == '-' \
           and time_str[10] == ' ' and time_str[13] == ':' and time_str[16] == ':':
            myFormat = strptime(time_str, self.ISOTIMEFORMAT)
            return mktime(myFormat)
        # TIMEFORMAT = '20090313102835'
        elif len(time_str) == 14:
            myFormat = strptime(time_str, self.COMPACTTIMEFORMAT)
            return mktime(myFormat)
        else:
            raise self.err.AvpE_InvalidInitParam,\
                        "传入的时间格式错误！[%s][%s]" % (self.TIMEFORMAT, time_str)
    
    def utf8encoder(self, notu8str):
        '将unicode编码为UTF8格式'
        u8encoder = getencoder("utf_8")
        return u8encoder(notu8str)[0]
    
    def utf8decoder(self, u8str):
        '将UTF8编码为unicode格式'
        u8decoder = getdecoder("utf_8")
        return u8decoder(u8str)[0]
    
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
        avp_head_buf = self.pack_bin("!I", self.avp['AVP_CODE'])
        
        # 编码AVP_FLAG 和 AVP_LENGTH
        if self.avp['AVP_VENDOR_ID'] != 0:       # 如果含有Vendor_id则长度增加4
            self.avp['AVP_LENGTH'] += 4

        self.avp['AVP_LENGTH'] += len(self.avp['AVP_BUF'])
        
        # 确定AVP_FLAG
        # Vendor_id != 0 则需要添加FLAG标志和
        if self.avp['AVP_VENDOR_ID'] != 0:
            self.avp['AVP_FLAG'] |= self.const.const.AVP_FLAG_VENDOR
        if self.avp['AVP_MANDATORY'] != 0:
            self.avp['AVP_FLAG'] |= self.const.const.AVP_FLAG_MANDATORY
        if self.avp['AVP_PRIVATE'] != 0:
            self.avp['AVP_FLAG'] |= self.const.const.AVP_FLAG_PRIVATE
            
        # 编码AVP_FLAG 和 AVP_LENGTH
        flag_and_length = ( (self.avp['AVP_FLAG']<<24) \
                            | self.avp['AVP_LENGTH'])
        
        avp_head_buf += self.pack_bin("!I", flag_and_length)
        
        # 编码VENDOR_ID
        if self.avp['AVP_VENDOR_ID'] != 0:
            avp_head_buf += self.pack_bin("!I", self.avp['AVP_VENDOR_ID'])
        
        self.avp['AVP_CODE_STATE'] = "01"
        return avp_head_buf
    
    def encde_data(self):
        '''编码AVP_DATA'''
        # 因为json的字符串编码采用UNICODE，所以在这里进行一下转换
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
            
        return self.pack_bin(self.avp['AVP_CODE_OPERATOR'], self.avp['AVP_DATA'])
        
    def encode(self):
        '''编码整个AVP包，返回编码后的PACK_BUF'''
        if self.avp['AVP_CODE_STATE'] != "00":
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的状态[%s]，当前无法继续编码！" % \
                     self.avp['AVP_CODE_STATE']
                     
        self.avp['AVP_CODE'] = int(self.avp['AVP_CODE'])
        
        self.avp['AVP_BUF'] = self.encde_data()
        
        self.avp['AVP_DATA_HEX'] = self.avp['AVP_BUF']
        
        self.avp['AVP_BUF'] = self.encode_head() + self.avp['AVP_BUF']
        
        self.avp['AVP_CODE_STATE'] = "02"
            
        return self.avp['AVP_BUF']
    
    def decode_head(self, offset=0):
        '''解码AVP头
                     返回包头的总长度位置
        '''
        offset_ = offset
        
        # 解码AVP_CODE
        (self.avp['AVP_CODE'],) = self.unpack_from_bin("!I", 
                                              self.avp['AVP_BUF'], 
                                              offset_)
        offset_                   += 4
        
        # 解码AVP_FLAG 和 AVP_LENGTH
        (flags_and_length,)       = self.unpack_from_bin("!I", 
                                                self.avp['AVP_BUF'], 
                                                offset_)
        self.avp['AVP_FLAG']      = (flags_and_length >> 24)
        self.avp['AVP_LENGTH']    = (flags_and_length & 0x00FFFFFF)
        offset_                  += 4
        
        # 解析 VENDOR_ID
        if (self.avp['AVP_FLAG'] & self.const.const.AVP_FLAG_VENDOR) \
                == self.const.const.AVP_FLAG_VENDOR:       # 说明存在VONDER_ID
            if self.avp['AVP_LENGTH'] < 12:
                raise self.err.AvpE_InvalidAvpLength, "AVP的长度定义错误！"
            
            (self.avp['AVP_VENDOR_ID'],) = \
                                self.unpack_from_bin("!I",
                                            self.avp['AVP_BUF'], 
                                            offset_)
            offset_ += 4
        else:
            if self.avp['AVP_LENGTH'] < 8:
                raise self.err.AvpE_InvalidAvpLength, "AVP的长度定义错误！"
            self.avp['AVP_VENDOR_ID'] = 0x00
            
        # 解析 MANDATORY
        if (self.avp['AVP_FLAG'] & self.const.const.AVP_FLAG_MANDATORY) \
                == self.const.const.AVP_FLAG_MANDATORY:
            self.avp['AVP_MANDATORY'] = self.const.const.AVP_FLAG_MANDATORY
        
        # 解析 PRIVATE
        if (self.avp['AVP_FLAG'] & self.const.const.AVP_FLAG_PRIVATE) \
                == self.const.const.AVP_FLAG_PRIVATE:
            self.avp['AVP_PRIVATE'] = self.const.const.AVP_FLAG_PRIVATE
        
        self.avp['AVP_CODE_STATE'] = "11"
        
        return offset_
    
    def decode_data(self, offset=8):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self._reset_operator_type()
        
        (self.avp['AVP_DATA'],) = self.unpack_from_bin(self.avp['AVP_CODE_OPERATOR'], 
                                                 self.avp['AVP_BUF'], 
                                                 offset)
#        self.avp['AVP_DATA_HEX'] = self.pack_bin(self.avp['AVP_CODE_OPERATOR'], 
#                                        self.avp['AVP_DATA'])
        self.avp['AVP_DATA_HEX'] = self.avp['AVP_BUF'][offset:]

        return self.avp['AVP_LENGTH']
    
    def decode(self, offset=0):
        '''解码AVP包, 返回所解码包的PACK_BUF'''
        if self.avp['AVP_CODE_STATE'] != "10":
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的状态[%s]，请检查实例化的参数是否错误！" % \
                     self.avp['AVP_CODE_STATE']
        
        offset_ = offset
        offset_ = self.decode_head(offset_)
        
        if len(self.avp['AVP_BUF']) < self.avp['AVP_LENGTH']:
            raise self.err.AvpE_InvalidAvpLength, \
                    "传入的avp长度错误！"
        
        self.decode_data(offset_)
        
        self._fmt_avp_data()
        self.avp['AVP_CODE_STATE'] = "12"
        
        return self.avp
    
    def _reset_operator_type(self):
        '''重置一下operator_type，因为一些string类型的长度不定'''
        pass
    
    def _fmt_avp_data(self):
        '''对于已经解码的数据进行格式化，等待具体类型重载'''
        pass
    
    def create_avp_instance(self, 
                            avp_etc_instances, 
                            encode_data=None, 
                            decode_buf=None):
        '''根据传入的avp类型配置列表，返回对应AVP数据类型的实例
        avp_etc_list说明：
        index        
        0            avp_name
        1            AVP_LEVEL
        2            AVP_CODE
        4            DATA_TYPE
        '''
        return dcc_msg.create_avp_factory(avp_etc_instances, 
                                          encode_data, 
                                          decode_buf,
                                          self.cmd_etc)
        
    def get_avp_code(self, pack_buf, offset=0):
        '获取AVP的 AVP_CODE'
        if self.avp['AVP_CODE_STATE'] == "10":
            (avp_code,) = self.unpack_from_bin("!I", pack_buf, offset)
            return avp_code
        else:
            return self.avp['AVP_CODE']
    
    def get_avp_flags(self, pack_buf, offset=4):
        '获取FLAGS标识'
        if self.avp['AVP_CODE_STATE'] == "10":
            (flags_and_length,) = self.unpack_from_bin("!I", pack_buf, offset)
            return flags_and_length >> 24
        else:
            return self.avp['AVP_FLAG']
        
    def get_avp_length(self, pack_buf, offset=4):
        '获取AVP长度'
        if self.avp['AVP_CODE_STATE'] == "10":
            (flags_and_length,) = self.unpack_from_bin("!I", pack_buf, offset)
            return flags_and_length & 0x00FFFFFF
        else:
            return self.avp['AVP_LENGTH']
        
    def set_avp_data(self, avp_data):
        '设置AVP数据内容'
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_DATA'] = avp_data
        else:
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_DATA！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_level(self, level):
        '''重设具体的self.avp['AVP_LEVEL']值,重新计算self.avp['L']'''
        self.avp['AVP_LEVEL'] = level
        self.avp['L'] = self.avp['AVP_LEVEL'] * "\t"
    
    def set_avp_vonder_id(self, vendor_id):
        '设置AVP的VONDER ID'
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_VENDOR_ID'] = vendor_id
        else:
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_VENDOR_ID！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_mandatory(self, mandatory):
        '设置 flags的 mandatory'
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_MANDATORY'] = mandatory
        else:
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_MANDATORY！" % \
                    self.avp['AVP_CODE_STATE']
    
    def set_avp_private(self, private):
        '设置 flags的private'
        if self.avp['AVP_CODE_STATE'] == "00":
            self.avp['AVP_PRIVATE'] = private
        else:
            raise self.err.AvpE_InvalidCodeState, \
                    "错误的编码状态[%s]，当前不能设置AVP_PRIVATE！" % \
                    self.avp['AVP_CODE_STATE']
        
    def print_avp(self, d_print=1):
        '''按照规定格式输出数据'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            print_buf = ""
            
            if self.const.const.DEBUG_LEVEL == "DEBUG":
                self.avp['AVP_CODE_HEX']   = "0x" + ("%08X" % self.avp['AVP_CODE'])
                self.avp['AVP_FLAGS_HEX']  = "0x" + ("%02X" % self.avp['AVP_FLAG'])
                self.avp['AVP_LENGTH_HEX'] = "0x" + ("%06X" % self.avp['AVP_LENGTH'])
                if self.avp['AVP_VENDOR_ID']:
                    self.avp['AVP_VONDER_HEX'] = "0x" + ("%08X" % self.avp['AVP_VENDOR_ID'])
                self.avp['AVP_DATA_HEX']   = "0x" + self.bin2ascii_hex(self.avp['AVP_DATA_HEX']).upper()
                if d_print == 1:
                    print self.print_detail_template.safe_substitute(self.avp)
                else:
                    print_buf += self.print_detail_template.safe_substitute(self.avp)
            else:
                print self.print_template.safe_substitute(self.avp)
        else:
            raise self.err.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
                  
        return print_buf
        
    def sprint(self, d_print=1):
        '''简单输出格式'''
        if (self.avp['AVP_CODE_STATE'] == "02" 
            or self.avp['AVP_CODE_STATE'] == "12"):
            if d_print == 1:
                print self.simple_print_template.safe_substitute(self.avp)
            else:
                return self.simple_print_template.safe_substitute(self.avp)
        else:
            raise self.err.AvpE_InvalidCodeState, \
                  '解码/编码状态错误： %s' % self.avp['AVP_CODE_STATE']
