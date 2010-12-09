#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl

AVP处理基类

编码：
dict_obj 一个字典类型的数据结构
            
    dict_obj--->|    |--->AVP::__init__()     --进行初始化
                |    |--->AVP::getConfig()    --根据传入的类型加载对应配置文件
                |    |--->AVP::encode()
                |    |--->AVP::encode_data()
                |    |--->AVP::encode_head()
   avp_class<---|    |
     
实例化avp,调用avp.encode()函数进行编码
如果传入类型为Grouped，则进行递归编码

解码：
dict_obj 一个字典类型的数据结构
            
     bin_buf--->|    |--->AVP::__init__()     --进行初始化
                |    |--->AVP::dncode()
                |    |--->AVP::decode_head()
                |    |--->AVP::getConfig()    --根据传入的类型加载对应配置文件
                |    |--->AVP::decode_data()
   avp_class<---|    |
    
实例化avp,调用avp.decode()函数进行解码
如果传入类型为Grouped，则进行递归解码

AVP类初始化变量说明：
avp_code
avp_data
decode_buf            判断当存在时，调用DecodeAvp,否则调用EncodeAvp
debug

get_avp_code
get_avp_flag
get_avp_data
get_avp_level
get_avp_length
get_avp_vonder_id
get_avp_mandatory
get_avp_private

set_avp_flag
set_avp_data
set_avp_level
set_avp_vonder_id
set_avp_mandatory
set_avp_private
'''

class AVP(object):
    '''
    AVP的基类，其他所有Dcc的数据类型都从这里继承
    '''
    
    def __init__(self,
                 cmd_code     = (),
                 avp_code     = 0x00,
                 avp_data     = "",
                 decode_buf   = None,
                 dcc_instance = None):
        '''avp_code    编码时必传
           avp_data    编码时必传
           decode_buf  解码时必传（用来判断是编码还是解码）
        '''
        self.dcc = dcc_instance
        self.my_cmd_code = cmd_code
        
        self.avp = {}
        self.avp['AVP_CODE']          = int(avp_code)
        self.avp['AVP_FLAG']          = 0x00
        self.avp['AVP_LENGTH']        = 0x00
        self.avp['AVP_DATA']          = avp_data
        self.avp['AVP_VENDOR_ID']     = 0x00
        self.avp['AVP_MANDATORY']     = 0x00
        self.avp['AVP_PRIVATE']       = 0x00
        self.avp['AVP_BUF']           = decode_buf
        self.avp['AVP_DATA_TYPE']     = ""
        self.avp['AVP_CODE_OPERATOR'] = ""
        self.avp['SUB_AVP']           = []
        self.avp['AVP_NAME']          = ""
        
        if decode_buf:  # 认定为需要解码
            # 详细定义见 dcc_defined
            self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_BEGIN
            
        else:           #认定为需要编码
            self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.ENCODE_DCC_AVP_BEGIN
        
        # 根据传入的 AVP_CODE 获取相应的配置信息
        self.my_avp_cfg = self.__get_avp_config()
        self.avp['AVP_NAME'] = self.my_avp_cfg[0]
        
    def __del__(self):
        del self.avp
        del self.dcc
        del self.my_cmd_code
        del self.my_avp_cfg
        
    def __repr__(self):
        if (self.avp['AVP_CODE_STATE'] in (self.dcc.dcc_def.const.ENCODE_DCC_AVP_END,
                                           self.dcc.dcc_def.const.DECODE_DCC_AVP_END)):
            return repr({repr(self.avp['AVP_CODE']):self.avp['AVP_DATA']})
        else:
            raise self.dcc.dcc_err.AvpE_InvalidCodeState, \
                    "The Incorrect Status[%s], Can Not Use repr!" % self.avp['AVP_CODE_STATE']
        
    def __str__(self):
        return self.__repr__()
    
    def __get_avp_config(self):
        '''根据AVP_CODE获取AVP的配置
        '''
        return self.dcc.dcc_cfg.get_config(
                                self.my_cmd_code,
                                self.avp['AVP_CODE']
                                )
    
    def __set_avp_type(self):
        '设置AVP的数据类型'
        self.avp['AVP_DATA_TYPE'] = self.my_avp_cfg[4]
        
    def __set_avp_operator_type(self):
        '设置编码时指定的编码方式，根据不同的数据类型，在子类中重载'
        raise self.dcc.dcc_err.AvpE_InvalidMethod, \
                    "Unknow AVP Type, Can Not Use set_avp_operator_type!"
    
    def __set_avp_vonder_id(self):
        '根据配置文件设置AVP的VONDER ID'
        if self.my_avp_cfg[3] != '0':
            self.avp['AVP_VENDOR_ID'] = int(self.my_avp_cfg[3])
    
    def __set_avp_mandatory(self):
        '''设置 flags的 mandatory
        从配置文件中获取M_FLAG列
        M    必选
        C    条件可选
        OM    运行商定义的必选项
        OC    运营商定义的条件可选项
        '''
        if self.my_avp_cfg[8] == 'M' or self.my_avp_cfg[8] == 'OM':
            self.avp['AVP_MANDATORY'] = 0x40
    
    def __set_avp_private(self):
        '设置 flags的private'
        pass
        
    def __set_avp_flag(self):
        '编码AVP_FLAG'
        if self.avp['AVP_VENDOR_ID'] != 0x00:
            self.avp['AVP_FLAG'] |= self.dcc.dcc_def.const.AVP_FLAG_VENDOR
        if self.avp['AVP_MANDATORY'] != 0x00:
            self.avp['AVP_FLAG'] |= self.dcc.dcc_def.const.AVP_FLAG_MANDATORY
        if self.avp['AVP_PRIVATE'] != 0x00:
            self.avp['AVP_FLAG'] |= self.dcc.dcc_def.const.AVP_FLAG_PRIVATE
    
    def encode(self):
        '''对传入的对象进行编码
        前提条件：
        AVP类已经被初始化
    返回编码的状态信息
        '''
        # 根据配置信息，实例化对应的数据类型
        self.__set_avp_type()
        
        # 根据配置信息，设置编码类型格式
        self.__set_avp_operator_type()
        
        self.__befor_encode_data()
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_BODY_BEGIN
        
        # 进行数据编码
        try:
            self.avp['AVP_BUF'] = self.__encode_data()
        except Exception, e:
            raise self.dcc.dcc_err.AvpE_DecodAvpError, \
                    "encode [%d] error!\n%s" % (self.avp['AVP_CODE'], e)
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_BODY_END
        
        # 对AVP进行整理打包
        self.avp['AVP_BUF'] = self.__encode_head() + self.avp['AVP_BUF']
        
        # 设置编码状态信息
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.ENCODE_DCC_AVP_END
            
        return self.avp['AVP_CODE_STATE']
    
    def __encode_data(self):
        '''编码AVP_DATA'''
        return self.dcc.pack_data2bin(self.avp['AVP_CODE_OPERATOR'],
                                      self.avp['AVP_DATA'])
        
    def __encode_avp_flag_and_length(self):
        '编码AVP_LENGTH'
        # 因为部分类型（octetstring）的DATA长度已经赋值，所以在这里被赋值过得不再累加
        if self.avp['AVP_LENGTH'] == 0:
            self.avp['AVP_LENGTH'] = \
                self.dcc.calc_pack_size(self.avp['AVP_CODE_OPERATOR'])
        
        self.avp['AVP_LENGTH'] += 4 + 4   # AVP_CODE + AVP_FLAG + AVP_LENGTH的长度
        
        # 如果含有Vendor_id则长度增加4
        if self.avp['AVP_VENDOR_ID'] != 0:
            self.avp['AVP_LENGTH'] += 4
        
        # 编码 AVP_FLAG 和 AVP_LENGTH
        flag_and_length = ( (self.avp['AVP_FLAG']<<24) \
                            | self.avp['AVP_LENGTH'])
        
        return self.dcc.pack_data2bin("!I", flag_and_length)
        
    def __encode_avp_vandor_id(self):
        '编码AVP_VANDOR_ID'
        # 编码VENDOR_ID
        if self.avp['AVP_VENDOR_ID'] != 0:
            return self.dcc.pack_data2bin("!I", self.avp['AVP_VENDOR_ID'])
        else:
            return ''
    
    def __encode_head(self):
        '''编码AVP包头'''
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.ENCODE_DCC_AVP_BODY_BEGIN
        
        # 编码AVP_CODE
        avp_head_buf = self.dcc.pack_data2bin("!I", self.avp['AVP_CODE'])
        
        # 设置vandor_id 值与vandor_id标志
        self.__set_avp_vonder_id()
        
        # 设置M标记位
        self.__set_avp_mandatory()
        
        # 设置P标记位
        self.__set_avp_private()
        
        # 编码avp_flag
        self.__set_avp_flag()
        
        # 编码avp_length
        avp_head_buf += self.__encode_avp_flag_and_length()
        
        # 编码vandor_id
        avp_head_buf += self.__encode_avp_vandor_id()
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.ENCODE_DCC_AVP_BODY_END
        
        return avp_head_buf
    
    def decode(self, offset=0):
        '''解码AVP包, 返回所解码包的PACK_BUF'''
        offset_ = offset
        offset_ += self.__decode_head(offset_)
        
        # 校验AVP_LENGTH是否合法
        if len(self.avp['AVP_BUF']) < self.avp['AVP_LENGTH']:
            raise self.dcc.dcc_err.AvpE_InvalidAvpLength, \
                    "Decode AVP_CODE[%s] Error: The Length In BUF Is Wrong!\nReal Length:[%d]\nPack BUF Length:[%d]" % \
                    (self.avp['AVP_CODE'], len(self.avp['AVP_BUF']), self.avp['AVP_LENGTH'])
        
        
        # 根据包中定义长度，截取实际的BUF，
        # [WARN]实际解码中用户不大，效率优化时可以注释掉这里
        buf_length = (self.avp['AVP_LENGTH'] + 3) // 4* 4
        self.avp['AVP_BUF'] = self.avp['AVP_BUF'][offset:buf_length]
        
        # 设置解析数据类型
        self.__set_avp_type()
        
        # 设置解析操作类型
        self.__set_avp_operator_type()
        
        # 对数据进行解码
        try:
            self.__decode_data(offset_)
        except Exception, e:
            raise self.dcc.dcc_err.AvpE_DecodAvpError, \
                    "decode [%d] error!\n%s" % (self.avp['AVP_CODE'], e)
                
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_END
        
        return self.avp
    
    def __decode_head(self, offset=0):
        '''解码AVP头
                     返回包头的总长度位置
        '''
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_HEAD_BEGIN
        # 解码AVP_CODE, 因为已经在上层解析完毕，故当前不再解析
        offset_ = offset + 4 # 偏移 AVP_CODE 的位置

        # 解析AVP_LENGTH AND AVP_FLAG
        self.__decode_avp_flag_and_length(offset_)
        offset_ += 4 # 偏移 avp_length_flag 的位置
        
        # 解析校验设置AVP_FLAG
        self.__decode_avp_flag()
        
        # 解析AVP_vendor_ID
        if self.avp['AVP_VENDOR_ID'] == self.dcc.dcc_def.const.AVP_FLAG_VENDOR:
            self.__decode_avp_vonder_id(offset_)
            offset_ += 4 # 偏移 AVP_VANDOR_ID 的位置
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_HEAD_END
        
        return offset_
    
    def __decode_avp_flag_and_length(self, offset):
        '解析avp leng and flag'
        (__flags_and_length,)  = self.dcc.unpack_from_bin("!I", 
                                            self.avp['AVP_BUF'], 
                                            offset)
        
        self.avp['AVP_FLAG']      = (__flags_and_length >> 24)
        self.avp['AVP_LENGTH']    = (__flags_and_length & 0x00FFFFFF)
        
    def __decode_avp_flag(self):
        '从AVP_FLAG中解析AVP_FLAG的各个属性'
        # 解析 VENDOR_ID
        if (self.avp['AVP_FLAG'] & self.dcc.dcc_def.const.AVP_FLAG_VENDOR) \
                == self.dcc.dcc_def.const.AVP_FLAG_VENDOR:       # 说明存在VONDER_ID
            if self.avp['AVP_LENGTH'] < 12:
                raise self.dcc.dcc_err.AvpE_InvalidAvpLength, "The AVP Length less for min Len: 12!"
            
            self.avp['AVP_VENDOR_ID'] = self.dcc.dcc_def.const.AVP_FLAG_VENDOR
        else:
            if self.avp['AVP_LENGTH'] < 8:
                raise self.dcc.dcc_err.AvpE_InvalidAvpLength, "The AVP Length less for min Len: 8!"
            
        # 解析 MANDATORY
        if (self.avp['AVP_FLAG'] & self.dcc.dcc_def.const.AVP_FLAG_MANDATORY) \
                == self.dcc.dcc_def.const.AVP_FLAG_MANDATORY:
            self.avp['AVP_MANDATORY'] = self.dcc.dcc_def.const.AVP_FLAG_MANDATORY
        
        # 解析 PRIVATE
        if (self.avp['AVP_FLAG'] & self.dcc.dcc_def.const.AVP_FLAG_PRIVATE) \
                == self.dcc.dcc_def.const.AVP_FLAG_PRIVATE:
            self.avp['AVP_PRIVATE'] = self.dcc.dcc_def.const.AVP_FLAG_PRIVATE
        
    def __decode_avp_vonder_id(self, offset):
        '解析AVP_VENDOR_ID'
        (self.avp['AVP_VENDOR_ID'],) = self.dcc.unpack_from_bin("!I", 
                                            self.avp['AVP_BUF'], 
                                            offset)
    
    def __decode_data(self, offset):
        '''解码AVP包体数据
                     返回本次解码AVP包的总长度
        '''
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_BODY_BEGIN
        
        try:
            (self.avp['AVP_DATA'],) = self.dcc.unpack_from_bin(self.avp['AVP_CODE_OPERATOR'], 
                                                           self.avp['AVP_BUF'], 
                                                           offset)
        except Exception, e:
            raise self.dcc.dcc_err.AvpE_DecodAvpError, \
                    "Decode AVP Error:\n%s\ncode=%s\nfmt=%s\nbuf=%s" % (e,
                                            self.avp['AVP_CODE'],
                                            self.avp['AVP_CODE_OPERATOR'],
                                            self.dcc.bin2ascii_hex(self.avp['AVP_BUF'])
                                            )
        
        # 解码数据类型后进行一些后续处理
        self.__after_decode_data()
        
        self.avp['AVP_CODE_STATE'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_BODY_END
        return self.avp['AVP_LENGTH']
    
    def __after_decode_data(self):
        '解码后进行后续处理'
        pass
    
    def __befor_encode_data(self):
        '编码前对数据进行处理'
        # 因为json的字符串编码采用UNICODE，所以在这里进行一下转换
        if type(self.avp['AVP_DATA']) == type(u"a"):
            self.avp['AVP_DATA'] = str(self.avp['AVP_DATA'])
    
    def pavp(self, level=1):
        '打印编码过程信息'
        if self.avp['AVP_CODE_STATE'] in (self.dcc.dcc_def.const.ENCODE_DCC_AVP_END,
                                          self.dcc.dcc_def.const.DECODE_DCC_AVP_END):
            
            avp_flag_bin = self.dcc.bin(self.avp['AVP_FLAG'])
            
            if level == 0:
                avp_txt = ""
                tab_space = "\t" * (int(self.my_avp_cfg[1]) - 1)
#                if self.avp['AVP_DATA_TYPE'] == 'Grouped':
#                    self.avp['AVP_DATA'] = self.avp['AVP_DATA_TYPE']
                avp_txt = '%s%s(%s)=[%s]\n' % (tab_space,
                                       self.my_avp_cfg[0],
                                       self.avp['AVP_CODE'],
                                       repr(self.avp['AVP_DATA']))
                if self.avp['AVP_DATA_TYPE'] == 'Grouped':
                    for avp_instance in self.avp['SUB_AVP']:
                        avp_txt += avp_instance.pavp(level)
                        
                return avp_txt
            elif level >= 5:
                from pprint import pprint
                pprint(self.avp)
            elif level >= 3:
                print '''AVP_CODE      = 0x%08X(%s|%d)
AVP_FLAG      = 0x%02X(%8s)
AVP_LENGTH    = 0x%06X(%d)
AVP_VENDOR_ID = 0x%08X(%d)
AVP_DATA      = %s
AVP_BUF       = %s
AVP_BUF_BIN   = 0x%s
----------------------''' % (self.avp['AVP_CODE'],
            self.my_avp_cfg[0],
            self.avp['AVP_CODE'],
            self.avp['AVP_FLAG'],
            avp_flag_bin,
            self.avp['AVP_LENGTH'],
            self.avp['AVP_LENGTH'],
            self.avp['AVP_VENDOR_ID'],
            self.avp['AVP_VENDOR_ID'],
            repr(self.avp['AVP_DATA']),
            repr(self.avp['AVP_BUF']),
            self.dcc.bin2ascii_hex(self.avp['AVP_BUF']).upper()
            )
                if self.avp['AVP_DATA_TYPE'] == 'Grouped':
                    for avp_instance in self.avp['SUB_AVP']:
                        avp_instance.pavp(3)
            elif level >= 1:
                tab_space = "\t" * (int(self.my_avp_cfg[1]) - 1)
                if self.avp['AVP_DATA_TYPE'] == 'Grouped':
                    self.avp['AVP_DATA'] = self.avp['AVP_DATA_TYPE']
                print '%s%s(%s)=[%s]' % (tab_space,
                                       self.my_avp_cfg[0],
                                       self.avp['AVP_CODE'],
                                       repr(self.avp['AVP_DATA']))
                if self.avp['AVP_DATA_TYPE'] == 'Grouped':
                    for avp_instance in self.avp['SUB_AVP']:
                        avp_instance.pavp(1)
            else:
                pass
