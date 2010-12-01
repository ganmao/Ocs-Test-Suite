#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-15

@author: zdl

Diameter Engine , Dcc 的接入类
'''
from sys import path
from time import strftime, strptime, mktime, localtime
from codecs import getencoder, getdecoder
from string import Template
from struct import pack, unpack_from, calcsize
from binascii import b2a_hex, a2b_hex

import dcc_defined as DCC_DEF
import dcc_error as DCC_ERR

from dcc_config import DCC_CFG

class DCC(object):
    '''Diameter 协议解码/编码引擎
    '''
    def __init__(self):
        '引擎初始化'
        self.dcc_cfg = DCC_CFG()
        self.dcc_err = DCC_ERR
        self.dcc_def = DCC_DEF
        
        self.TIMEFORMAT=self.dcc_def.const.COMPACTTIMEFORMAT
        self.seconds_between_1900_and_1970 = ((70*365)+17)*86400
        
    def __del__(self):
        del self.dcc_cfg
        del self.dcc_err
        del self.dcc_def
        del self.TIMEFORMAT
        del self.seconds_between_1900_and_1970
        
    def loads_json(self, json_str):
        '将json的字符串，解析为列表'
        try:
            from json import loads
        except ImportError:
            '''由于py2.6以上才内置了JSON模块，
                                故如果没有内置则采用第三方模块：
            Contact mailto:patrickdlogan@stardecisions.com
            '''
            path.insert(0, self.dcc_def.const.PLUS_PATH)
            from minjson import read as loads
            
        return loads(json_str)
    
    def dumps_json(self, obj):
        '将列表，解析为json的字符串'
        try:
            from json import dumps
        except ImportError:
            '''由于py2.6以上才内置了JSON模块，
                                故如果没有内置则采用第三方模块：
            Contact mailto:patrickdlogan@stardecisions.com
            '''
            path.insert(0, self.dcc_def.const.PLUS_PATH)
            from minjson import write as dumps
            
        return dumps(obj)
    
    def NTPStamp2Time(self, stamp):
        '将NTP时间戳转换为年月日的时间格式'
        #stamp = float(repr(stamp))
        myUTCTime = stamp - self.seconds_between_1900_and_1970
        return strftime(self.TIMEFORMAT, localtime(myUTCTime))
    
    def UTCStamp2Time(self, stamp):
        '将UTC时间戳转换为年月日的时间格式'
        return strftime(self.TIMEFORMAT, localtime(stamp))
    
    def Time2NTPStamp(self, time_str):
        '将年月日的时间格式转换为NTP时间戳,'
        # TIMEFORMAT = '2009-03-13 10:28:35'
        if len(time_str) == 19:
            myFormat = strptime(time_str, self.dcc_def.const.ISOTIMEFORMAT)
            outStamp = mktime(myFormat)
            outStamp = outStamp + self.seconds_between_1900_and_1970
            return outStamp
        # TIMEFORMAT = '20090313102835'
        elif len(time_str) == 14:
            myFormat = strptime(time_str, self.dcc_def.const.COMPACTTIMEFORMAT)
            outStamp = mktime(myFormat)
            outStamp = outStamp + self.seconds_between_1900_and_1970
            return outStamp
        else:
            raise DCC_ERR.AvpE_InvalidInitParam,\
                        "The Time Format Error:\nfmt=%s, input=%s" % (self.TIMEFORMAT, time_str)
        
    def Time2TUCStamp(self, time_str):
        '将年月日的时间格式转换为UTC时间戳'
        # TIMEFORMAT = '2009-03-13 10:28:35'
        if len(time_str) == 19:
            myFormat = strptime(time_str, self.dcc_def.const.ISOTIMEFORMAT)
            return mktime(myFormat)
        # TIMEFORMAT = '20090313102835'
        elif len(time_str) == 14:
            myFormat = strptime(time_str, self.dcc_def.const.COMPACTTIMEFORMAT)
            return mktime(myFormat)
        else:
            raise DCC_ERR.AvpE_InvalidInitParam,\
                        "The Time Format Error:\nfmt=%s, input=%s" % (self.TIMEFORMAT, time_str)
    
    def utf8encoder(self, nonu8str):
        '将unicode编码为UTF8格式'
        u8encoder = getencoder("utf_8")
        return u8encoder(nonu8str)[0]
    
    def utf8decoder(self, u8str):
        '将UTF8编码为unicode格式'
        u8decoder = getdecoder("utf_8")
        return u8decoder(u8str)[0]
    
    def create_template(self, tmplate_str):
        '重载string.Template函数'
        return Template(tmplate_str)
    
    def pack_data2bin(self, fmt, *pack_data):
        '重载struct.pack函数'
        return pack(fmt, *pack_data)
    
    def unpack_from_bin(self, fmt, buf, offset=0):
        '重载struct.unpack_from函数'
        return unpack_from(fmt, buf, offset)
    
    def calc_pack_size(self, fmt):
        return calcsize(fmt)
    
    def bin2ascii_hex(self, bin_buf):
        '重载binascii.b2a_hex函数'
        return b2a_hex(bin_buf)
    
    def ascii2bin_hex(self, ascii_buf):
        '重载binascii.a2b_hex函数'
        return a2b_hex(ascii_buf)
    
    def catch_cmd_code(self, cmd_code_str):
        '根据传入的CMD_CODE描述串，获取系统自定义的常量'
        if cmd_code_str == 'CCR':
            return self.dcc_def.const.CREDIT_CONTROL_REQUEST
        elif cmd_code_str == 'CCA':
            return self.dcc_def.const.CREDIT_CONTROL_ANSWER
        elif cmd_code_str == 'RAR':
            return self.dcc_def.const.RE_AUTH_REQUEST
        elif cmd_code_str == 'RAA':
            return self.dcc_def.const.RE_AUTH_ANSWER
        elif cmd_code_str == 'ASR':
            return self.dcc_def.const.ABORT_SESSION_REQUEST
        elif cmd_code_str == 'ASA':
            return self.dcc_def.const.ABORT_SESSION_ANSWER
        elif cmd_code_str == 'DWR':
            return self.dcc_def.const.DEVICE_WATCHDOG_REQUEST
        elif cmd_code_str == 'DWA':
            return self.dcc_def.const.DEVICE_WATCHDOG_ANSWER
        elif cmd_code_str == 'DPR':
            return self.dcc_def.const.DISCONNECT_PEER_REQUEST
        elif cmd_code_str == 'DPA':
            return self.dcc_def.const.DISCONNECT_PEER_ANSWER
        elif cmd_code_str == 'CER':
            return self.dcc_def.const.CAPABILITIES_EXCHANGE_REQUEST
        elif cmd_code_str == 'CEA':
            return self.dcc_def.const.CAPABILITIES_EXCHANGE_ANSWER
        else:
            raise self.dcc_err.DccE_InvalidDccType, \
                        "The CMD_CODE Error:%s" % cmd_code_str
    
    def bin(self, num):
        '将数据转为二进制表示'
        b = lambda n : (n > 0) and (b(n/2) + str(n%2)) or ''
            
        out_str = "%8s" % b(num)
        out_str = out_str.replace(' ', '0')
        
        return out_str
    
    