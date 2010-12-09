#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-15

@author: zdl

使用说明：
    如果解码请传入需要解码的串
'''
from time import time
import re

from avp_factory import create_avp

class MSG(object):
    '''
    Diameter 消息基类
    '''
    def __init__(self, dcc_instance):
        self.dcc = dcc_instance
        
        self.dmsg = {}
        self.dmsg['DCC_VERSION']      = self.dcc.dcc_def.const.DMSG_VERSION
        self.dmsg['DCC_LENGTH']       = 0x00
        self.dmsg['DCC_FLAGS']        = 0x00
        self.dmsg['DCC_REQUEST']      = 0x00      #需要将读取配置文件中的对应设置
        self.dmsg['DCC_PROXIABLE']    = 0x00
        self.dmsg['DCC_ERROR']        = 0x00
        self.dmsg['DCC_TPOTENTIALLY'] = 0x00
        self.dmsg['DCC_CODE']         = 0x00
        self.dmsg['DCC_NAME']         = ""
        self.dmsg['DCC_APP_ID']       = self.dcc.dcc_def.const.DMSG_APPLICATION_ID
        self.dmsg['DCC_HOPBYHOP']     = 0x00
        self.dmsg['DCC_ENDTOEND']     = 0x00
        
        # 存放打包好的数据BUF
        self.dmsg['DCC_BUF']          = None
        
        # 编码的时候存储实例列表
        self.dmsg['DCC_AVP_LIST']     = []
        
        # 详见dcc_defined.py
        self.dmsg['DCC_STAT']         = None
        
        self.dmsg['DCC_JSON']         = None
        
    def __del__(self):
        del self.dmsg
        del self.dcc
        
    def __repr__(self):
        '输出具体需要解包的json或者已经解包后的json'
        if self.dmsg['DCC_STAT'] in (self.dcc.dcc_def.const.ENCODE_DCC_MSG_END,
                                     self.dcc.dcc_def.const.DECODE_DCC_MSG_END):
            return self.dmsg['DCC_JSON']
        else:
            raise self.dcc.dcc_err.DccE_InvalidDccstate, \
                        "The Incorrect Status[%s], Can Not Use repr!" % self.dmsg['DCC_STAT']
        
    def __str__(self):
        return self.__repr__()
        
    def __set_flags_proxiable(self):
        '''P(roxiable) –如果设置，表明该消息可以被Proxy、中继或者复位向。
                     如果清零，该消息必须在本地处理。
        '''
        # 预留，定义在dcc_defined
        self.dmsg['DCC_FLAGS'] |= self.dcc.dcc_def.const.DMSG_FLAGS_PROXIABLE
        
    def set_flags_error(self, cmd_code):
        '''E(rror) -如果设置，表明该消息包含一个协议差错，
                    且该消息与ABNF中描述的该命令不一致。
        “E”比特设置的消息一般当作差错消息。在请求消息中不能设置该比特。
        '''
        # 预留，定义在dcc_defined
        # 对外开放接口，当是一个错误消息的时候，设置这个标记位
        if cmd_code[1] != 1 and \
           self.dmsg['DCC_STAT'] not in (self.dcc.dcc_def.const.ENCODE_DCC_MSG_HEAD_END,
                                         self.dcc.dcc_def.const.ENCODE_DCC_MSG_END):
            self.dmsg['DCC_FLAGS'] |= self.dcc.dcc_def.const.DMSG_FLAGS_ERROR
        else:
            raise self.dcc.dcc_err.DccE_InvalidMethod, \
                    "Call set_flags_error() Error:\n \
                     Can Not Set E(rror) Flag For Request Msg or \
                     The Proc Status Type(%s) Error!" % self.dmsg['DCC_STAT']
        
    def set_flags_tpotentially(self):
        '''T(Potentially re-transmitted message)-该标记在链路失败过程后被设置，
                    以帮助去除重复的请求。当重发请求还没有被确认时，需要设置该比特，
                    以作为链路失败而造成的可能的重复包的指示。当第一次发送一个请求时，
                    该比特必须被清零，否则发送者必须设置该比特。
        Diameter代理仅需要关心它们发送的同一请求消息的遍数；
                    其它实体进行的重传不须考虑。Diameter代理接收到一个T比特设置为1的请求，
                    必须在前转该请求时保持T标记的设置。如果接收到一个以前消息的差错消息（例如协议差错），
                    则不可以设置该标记。该标记只有在没有接收到任何来自服务器的该请求的应答、
                    且该请求再次被发送的情况下，才能被设置。该标记不能在应答消息中设置。
        '''
        # 预留，定义在dcc_defined
        # 对外接口,当重复发送消息时需要设置此标记
        if self.dmsg['DCC_STAT'] not in (self.dcc.dcc_def.const.ENCODE_DCC_MSG_HEAD_END,
                                         self.dcc.dcc_def.const.ENCODE_DCC_MSG_END):
            self.dmsg['DCC_FLAGS'] |= self.dcc.dcc_def.const.DMSG_FLAGS_TPOTENTIALLY
        else:
            raise self.dcc.dcc_err.DccE_InvalidMethod, \
                    "The Proc Status Type Error! Call set_flags_tpotentially() Error:\n \
                     [%s]" % self.dmsg['DCC_STAT']
                    
    def __set_hop_by_hop(self, cmd_code):
        '''Hop-by-Hop Identifier：Hop-by-Hop标识符为一个无符号32比特整数字段
                    （按网络字节顺序），用来帮助匹配请求和响应。发送者必须保证请求中的
        Hop-by-Hop标识符在特定的连接上在任何特定的时间是唯一的，
                    并且保证该数字在经过重启动后仍然唯一。应答消息的发送者必须确保Hop-by-Hop
                    标识符字段维持与相应的请求相同的值。Hop-by-Hop标识符通常是单调升序的数字，
                    其开始值是随机生成的。一个带有未知Hop-by-Hop标识符的应答消息必须被丢弃。
                    
        具体实现：从DccCmdCode.ini配置文件中获取最后一次的值，并且需要在组包完成时写回文件
        '''
        return int(self.dcc.dcc_cfg.Code2Cmd[cmd_code][5]) + 1
    
    def __set_end_by_end(self, range_number):
        '''End-to-End Identifier：端到端标识符是一个无符号32比特整数字段（按
                    网络字节顺序），用来检测重复消息。重启动时可以设置高位12比特为包含当
                    前时间的低位12比特，低位20比特为随机值。请求消息的发送者必须为每一个
                    消息插入一个唯一的标识符。该标识符必须维持本地唯一至少4分钟，即使经过
                    重启动。应答消息的生成者必须确保该端到端标识符字段包含与相应的请求相同
                    的值。端到端标识符不可以被Diameter代理以任何原因修改。源主机AVP和该
                    字段的结合可以用于检测重复。重复请求会造成相同应答的传输，并且不可以
                    影响任何状态的设置，当处理原始请求时。应当在本地被消除的重复的应答消
                    息将会被忽略。
                    
        具体实现：调用的引擎传入具体的随机数，并且调用引擎需要保证在至少4分钟内没有重复
        '''
        now_stamp = int(time())
        
        stamp_lower_12bytes = now_stamp & 0x0FFF
        
        new_end_by_end = stamp_lower_12bytes << 20 | range_number
        
        return new_end_by_end
    
    def __set_cmd_flags(self, cmd_code):
        '设置msg CMD FLAG'
        
        # 设置 R(equest)
        if cmd_code[1] == 1:
            self.dmsg['DCC_FLAGS'] |= self.dcc.dcc_def.const.DMSG_FLAGS_REQUEST
            
        # 设置 P(roxiable)
        self.__set_flags_proxiable()
        
        # 设置  E(rror),根据需要外部直接调用吧
        #self.set_flags_error()
        
        # 设置  T(Potentially re-transmitted message)
        # 根据需要外部直接调用吧
        #self.set_flags_tpotentially()
        
    def __set_head_info(self, cmd_code, end_by_end_random_number):
        '''在编码前赋值基本信息'''
        # Version 已经在初始化类的时候赋值
        
        # Message Length 已经在pack中编码包体后确定
        
        # 设置 command flags
        self.__set_cmd_flags(cmd_code)
        
        # 设置 Command-Code
        self.dmsg['DCC_CODE'] = int(self.dcc.dcc_cfg.Code2Cmd[cmd_code][0])
        
        # 设置 Application-ID
        self.dmsg['DCC_APP_ID'] = int(self.dcc.dcc_cfg.Code2Cmd[cmd_code][4])
        
        # 设置 Hop-by-Hop Identifier
        self.dmsg['DCC_HOPBYHOP'] = self.__set_hop_by_hop(cmd_code)
        
        # 设置 End-to-End Identifier
        self.dmsg['DCC_ENDTOEND'] = self.__set_end_by_end(end_by_end_random_number)
        
        return True
        
    def __pack_head(self, cmd_code, end_by_end_random_number):
        '''编码消息头'''
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_HEAD_BEGIN
        pack_buf = ""
        
        self.__set_head_info(cmd_code, end_by_end_random_number)
        
        ver_and_len = self.dmsg['DCC_VERSION'] << 24 | self.dmsg['DCC_LENGTH']
        pack_buf += self.dcc.pack_data2bin("!I", ver_and_len)
        
        flags_and_code = self.dmsg['DCC_FLAGS'] << 24 | self.dmsg['DCC_CODE']
        pack_buf += self.dcc.pack_data2bin("!I", flags_and_code)
        
        pack_buf += self.dcc.pack_data2bin("!I", self.dmsg['DCC_APP_ID'])
        
        pack_buf += self.dcc.pack_data2bin("!I", self.dmsg['DCC_HOPBYHOP'])
        
        pack_buf += self.dcc.pack_data2bin("!I", self.dmsg['DCC_ENDTOEND'])
        
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_HEAD_END
        
        return pack_buf

    def __pack_AVP(self, cmd_code, avp_list):
        '''将AVP都编码打包到一起'''
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_BODY_BEGIN
        pack_buf = ""
        
        for decode_avp_dict in avp_list:
            avp_instance = create_avp(cmd_code,
                                      decode_avp_dict.keys()[0],
                                      decode_avp_dict.values()[0],
                                      None,
                                      self.dcc
                                      )
            
            avp_instance.encode()
            
            # 将创建的AVP添加入DCC_AVP_LIST
            self.dmsg['DCC_AVP_LIST'].append(avp_instance)
                
            # 将所有编码后的数据整合到一起
            pack_buf += avp_instance.avp['AVP_BUF']
            
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_BODY_END
        return pack_buf

    def pack_json(self, cmd_code, json_str, end_by_end_random_number):
        '对传入的json字符串进行编码'
        avp_list = self.dcc.loads_json(json_str)
        return self.pack(cmd_code, avp_list, end_by_end_random_number)

    def pack(self, cmd_code, avp_list, end_by_end_random_number):
        '''对于传入的AVP字典进行编码
        dcc_code_name            需要对其进行编码的类型，如：(272, 1)
        avp_list                 需要编码的数据列表，采用列表方式传入
        end_by_end_rand_number   随机数，具体定义请参看end_by_end说明
        
        avp_list的元素均为dict，包含{'AVP_CODE':AVP_DATA}
            
                    编码过程：
                        首先根据avp_list先添加AVP，之后再编码消息头
                        
        编码avp的列表，输出编码后的BUF
        '''
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_BEGIN
        
        # 根据 cmd_code 获取 DCC_NAME
        self.dmsg['DCC_NAME'] = self.dcc.dcc_cfg.Code2Cmd[cmd_code][2]
        
        # 对AVP的内容进行编码
        dcc_avp_buf = self.__pack_AVP(cmd_code, avp_list)
        
        # 计算编码后AVP的长度,20为消息包头的长度，是固定的
        length = len(dcc_avp_buf)
        self.dmsg['DCC_LENGTH'] = 20 + length
        
        # 编码包头
        dcc_head_buf = self.__pack_head(cmd_code, end_by_end_random_number)
        
        # 将包体与包头组合
        self.dmsg['DCC_BUF'] = dcc_head_buf + dcc_avp_buf
        
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.ENCODE_DCC_MSG_END
        return self.dmsg['DCC_BUF']
        
    def unpack_json(self, pack_buf):
        '解压传入的buf，返回json串'
        self.unpack(pack_buf)
        return self.dmsg['DCC_JSON']
    
    def __unpack_head(self, pack_buf):
        '''解码包头内容'''
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.DECODE_DCC_MSG_HEAD_BEGIN
        offset_ = 0
        (ver_and_len,) = self.dcc.unpack_from_bin("!I", pack_buf, offset_)
        offset_ += 4
        self.dmsg['DCC_VERSION'] = ver_and_len >> 24
        
        self.dmsg['DCC_LENGTH']  = ver_and_len & 0x00FFFFFF
        
        if len(pack_buf) != self.dmsg['DCC_LENGTH']:
            raise self.dcc.dcc_err.DccE_InvalidLength, \
                    "The Length Wrong In Msg Head!\n \
                    \tThe Real Length:[%d]\n \
                    \tThe Length In Msg Head:[%d]" \
                    % (len(pack_buf), self.dmsg['DCC_LENGTH'])
        
        (flags_and_code,)  = self.dcc.unpack_from_bin("!I", pack_buf, offset_)
        offset_ += 4
        self.dmsg['DCC_FLAGS'] = flags_and_code >> 24
        self.dmsg['DCC_CODE']  = flags_and_code & 0x00FFFFFF
        
        if self.dmsg['DCC_FLAGS'] & self.dcc.dcc_def.const.DMSG_FLAGS_REQUEST \
            == self.dcc.dcc_def.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_REQUEST'] = '1'
        else:
            self.dmsg['DCC_REQUEST'] = '0'
            
        if self.dmsg['DCC_FLAGS'] & self.dcc.dcc_def.const.DMSG_FLAGS_PROXIABLE \
            == self.dcc.dcc_def.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_PROXIABLE'] = '1'
        else:
            self.dmsg['DCC_PROXIABLE'] = '0'
            
        if self.dmsg['DCC_FLAGS'] & self.dcc.dcc_def.const.DMSG_FLAGS_ERROR \
            == self.dcc.dcc_def.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_ERROR'] = '1'
        else:
            self.dmsg['DCC_ERROR'] = '0'
            
        if self.dmsg['DCC_FLAGS'] & self.dcc.dcc_def.const.DMSG_FLAGS_TPOTENTIALLY \
            == self.dcc.dcc_def.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_TPOTENTIALLY'] = '1'
        else:
            self.dmsg['DCC_TPOTENTIALLY'] = '0'
            
        (self.dmsg['DCC_APP_ID'],)   = self.dcc.unpack_from_bin("!I", pack_buf, offset_)
        offset_ += 4
        (self.dmsg['DCC_HOPBYHOP'],) = self.dcc.unpack_from_bin("!I", pack_buf, offset_)
        offset_ += 4
        (self.dmsg['DCC_ENDTOEND'],) = self.dcc.unpack_from_bin("!I", pack_buf, offset_)
        offset_ += 4
        
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.DECODE_DCC_MSG_HEAD_END
        return offset_
    
    def unpack(self, pack_buf):
        '''解包DCC消息，返回解包后的一个字典
                    首先解析包头，再解析具体包体
                    
        解码BUF，输出解码后的实例
        '''
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.DECODE_DCC_AVP_BEGIN
        self.dmsg['DCC_BUF'] = pack_buf
        avp_pack_buf = ""
        
        # 解析包头
        offset = self.__unpack_head(self.dmsg['DCC_BUF'])
        
        # 根据 cmd_code 获取 DCC_NAME
        _cmd_code = (int(self.dmsg['DCC_CODE']), int(self.dmsg['DCC_REQUEST']))
        self.dmsg['DCC_NAME'] = self.dcc.dcc_cfg.Code2Cmd[_cmd_code][2]
        
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.DECODE_DCC_MSG_BODY_BEGIN
        while offset != self.dmsg['DCC_LENGTH']:
            # 确定具体需要解包的AVP BUF
            avp_pack_buf = self.dmsg['DCC_BUF'][offset:]
            
            try:
                # 返回需要解析AVP的AVP_INSTANCE
                avp_instance = create_avp(cmd_code = _cmd_code,
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = avp_pack_buf,
                                        dcc_instance = self.dcc
                                        )
            except Exception, e:
                raise self.dcc.dcc_err.DccE_CreateAvpError, \
                        "Create Avp Instance Error: %s" % e
            
            # AVP解包，并且将解包后结果添加到self.dmsg['DCC_AVP_LIST']
            avp_instance.decode()
            self.dmsg['DCC_AVP_LIST'].append(avp_instance)
            
            # avp['AVP_LENGTH'] 因为是标明的长度，但是dcc要求是4的倍数，所以在这里进行修正
            lengthset = (avp_instance.avp['AVP_LENGTH'] + 3) // 4 * 4
            
            offset += lengthset
            
        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.DECODE_DCC_MSG_BODY_END
        
        # 将AVP组合为需要返回的数据类型，之后装为json
        self.dmsg['DCC_JSON'] = self.dcc.dumps_json(
                                    self.__compress_json_obj(self.dmsg['DCC_AVP_LIST'])
                                    )

        self.dmsg['DCC_STAT'] = self.dcc.dcc_def.const.DECODE_DCC_MSG_END
        return self.dmsg
    
    def __compress_json_obj(self, avp_instance_list):
        '将实例列表转为json可以编辑的数据对象'
        _json_obj = []
        for avp in avp_instance_list:
            if avp.avp['AVP_DATA_TYPE'] == 'Grouped':
                _json_obj.append({repr(avp.avp['AVP_CODE']):self.__compress_json_obj(avp.avp['SUB_AVP'])})
            else:
                _json_obj.append({repr(avp.avp['AVP_CODE']):avp.avp['AVP_DATA']})
                
        return _json_obj
    
    def pmsg(self, level=1):
        '''按照格式打印消息包的信息'''
        if self.dmsg['DCC_STAT'] in (self.dcc.dcc_def.const.ENCODE_DCC_MSG_END,
                                     self.dcc.dcc_def.const.DECODE_DCC_MSG_END):
            if level == 0:
                msg_txt = ""
                bin_flags = self.dcc.bin(self.dmsg['DCC_FLAGS'])
                
                msg_txt += 'Version               = 0x%02X(%d)\n' % (self.dmsg['DCC_VERSION'], self.dmsg['DCC_VERSION'])
                msg_txt += 'Message Length        = 0x%06X(%d)\n' % (self.dmsg['DCC_LENGTH'], self.dmsg['DCC_LENGTH'])
                msg_txt += 'command flags         = 0x%02X(%s)\n' % (self.dmsg['DCC_FLAGS'], bin_flags)
                msg_txt += 'Command-Code          = 0x%06X(%d)\n' % (self.dmsg['DCC_CODE'], self.dmsg['DCC_CODE'])
                msg_txt += 'Application-ID        = 0x%08X(%d)\n' % (self.dmsg['DCC_APP_ID'], self.dmsg['DCC_APP_ID'])
                msg_txt += 'Hop-by-Hop Identifier = 0x%08X(%d)\n' % (self.dmsg['DCC_HOPBYHOP'], self.dmsg['DCC_HOPBYHOP'])
                msg_txt += 'End-to-End Identifier = 0x%08X(%d)\n' % (self.dmsg['DCC_ENDTOEND'], self.dmsg['DCC_ENDTOEND'])
                msg_txt += "..................................\n"
                for avp in self.dmsg['DCC_AVP_LIST']:
                    msg_txt += avp.pavp(level)
                    
                return msg_txt
            else:
                bin_flags = self.dcc.bin(self.dmsg['DCC_FLAGS'])
                
                print 'Version               = 0x%02X(%d)' % (self.dmsg['DCC_VERSION'], self.dmsg['DCC_VERSION'])
                print 'Message Length        = 0x%06X(%d)' % (self.dmsg['DCC_LENGTH'], self.dmsg['DCC_LENGTH'])
                print 'command flags         = 0x%02X(%s)' % (self.dmsg['DCC_FLAGS'], bin_flags)
                print 'Command-Code          = 0x%06X(%d)' % (self.dmsg['DCC_CODE'], self.dmsg['DCC_CODE'])
                print 'Application-ID        = 0x%08X(%d)' % (self.dmsg['DCC_APP_ID'], self.dmsg['DCC_APP_ID'])
                print 'Hop-by-Hop Identifier = 0x%08X(%d)' % (self.dmsg['DCC_HOPBYHOP'], self.dmsg['DCC_HOPBYHOP'])
                print 'End-to-End Identifier = 0x%08X(%d)' % (self.dmsg['DCC_ENDTOEND'], self.dmsg['DCC_ENDTOEND'])
                print "=================================="
                for avp in self.dmsg['DCC_AVP_LIST']:
                    avp.pavp(level)
                        
                print "=================================="
        else:
            raise self.dcc.dcc_err.DccE_InvalidDccstate, \
                    "Can Not Print Detail Info, Ten Wrong DCC Msg Status:[%s]!" % self.dmsg['DCC_STAT']
        
    def fmt_hex(self, hex_buf):
        '''将16进制的字符串格式化输出'''
        char_num = 1
        pstr = ""
        out_str = ""
        for char in hex_buf:
            if char_num % 2 != 0:
                pstr += char
            else:
                pstr += char
                out_str = out_str + pstr + " "
                pstr = ""
                
            if char_num % 32 == 0:
                out_str += "\n"
                
            char_num += 1
            
        return out_str
    
