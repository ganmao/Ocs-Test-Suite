#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-15

@author: zdl

使用说明：
    如果解码请传入需要解码的串
'''
from time import time
from struct import pack, unpack
from string import Template
import json

import avp_const_define as ACD
import avp_error as D_ERROR

class DMSG(object):
    '''
    Diameter 消息基类
    '''
    def __init__(self, config_instance):
        self.dcc_cfg = config_instance
        
        self.dmsg_head = {}
        self.dmsg_head['DCC_VERSION']      = ACD.const.DMSG_VERSION
        self.dmsg_head['DCC_LENGTH']       = 0x000000
        self.dmsg_head['DCC_FLAGS']        = 0x00
        self.dmsg_head['DCC_REQUEST']      = 0      #需要将读取配置文件中的对应摄者
        self.dmsg_head['DCC_PROXIABLE']    = 0
        self.dmsg_head['DCC_ERROR']        = 0
        self.dmsg_head['DCC_TPOTENTIALLY'] = 0
        self.dmsg_head['DCC_CODE']         = 0x000000
        self.dmsg_head['DCC_APP_ID']       = ACD.const.DMSG_APPLICATION_ID
        self.dmsg_head['DCC_HOPBYHOP']     = 0
        self.dmsg_head['DCC_ENDTOEND']     = 0
        self.dmsg_head['PIRNT_FMT']        = Template("\n\
+++++++++++++++++++++++++++++++\n\
${DCC_VERSION_HEX}\n\
\tDCC_VERSION = ${DCC_VERSION}\n\
${DCC_LENGTH_HEX}\n\
\tDCC_LENGTH  = ${DCC_LENGTH}\n\
${DCC_FLAGS_HEX}\n\
\tDCC_FLAGS   = ${DCC_FLAGS}\n\
${DCC_CODE_HEX}\n\
\tDCC_CODE    = ${DCC_CODE}\n\
${DCC_APP_ID_HEX}\n\
\tDCC_APP_ID  = ${DCC_APP_ID}\n\
${DCC_HOPBYHOP_HEX}\n\
\tHOP_BY_HOP  = ${DCC_HOPBYHOP}\n\
${DCC_ENDTOEND_HEX}\n\
\tEND_TO_END  = ${DCC_ENDTOEND}\n\
+++++++++++++++++++++++++++++++\n")
        
        self.dcc_cmd_name = None    # 存放传入的dcc_code_name
        
        self.dmsg_buf  = None # 存放打包好的数据BUF
        
        # 编码的时候存储编码/解码后的实例列表
        self.dmsg_list = []
        
        # 00-准备编码，01-消息头编码完成，02-消息整体编码完成
        # 10-准备解码，11-消息头解码完成，12-消息整体解码完成
        self.dmsg_state = None
        
    def __del__(self):
        del self.dmsg_head
        del self.dcc_cmd_name
        del self.dmsg_buf
        del self.dmsg_list
        del self.dmsg_state
        
    def set_flags_proxiable(self):
        '''P(roxiable) –如果设置，表明该消息可以被Proxy、中继或者复位向。
                     如果清零，该消息必须在本地处理。
        '''
        # 预留，如果需要修改的时候使用
        return ACD.const.DMSG_FLAGS_PROXIABLE
        
    def set_flags_error(self):
        '''E(rror) -如果设置，表明该消息包含一个协议差错，
                    且该消息与ABNF中描述的该命令不一致。
        “E”比特设置的消息一般当作差错消息。在请求消息中不能设置该比特。
        '''
        # 预留，如果需要修改的时候使用
        return ACD.const.DMSG_FLAGS_ERROR
        
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
        # 预留，如果需要修改的时候使用
        return ACD.const.DMSG_FLAGS_TPOTENTIALLY
    
    def set_hop_by_hop(self, dcc_code_name):
        '''Hop-by-Hop Identifier：Hop-by-Hop标识符为一个无符号32比特整数字段
                    （按网络字节顺序），用来帮助匹配请求和响应。发送者必须保证请求中的
        Hop-by-Hop标识符在特定的连接上在任何特定的时间是唯一的，
                    并且保证该数字在经过重启动后仍然唯一。应答消息的发送者必须确保Hop-by-Hop
                    标识符字段维持与相应的请求相同的值。Hop-by-Hop标识符通常是单调升序的数字，
                    其开始值是随机生成的。一个带有未知Hop-by-Hop标识符的应答消息必须被丢弃。
                    
        TODO: 具体实现：从DccCmdCode.ini配置文件中获取最后一次的值，并且需要在组包完成时写回文件
        '''
        return int(self.dcc_cfg.Cmd2Code[dcc_code_name][5]) + 1
    
    def set_end_by_end(self, range_number):
        '''End-to-End Identifier：端到端标识符是一个无符号32比特整数字段（按
                    网络字节顺序），用来检测重复消息。重启动时可以设置高位12比特为包含当
                    前时间的低位12比特，低位20比特为随机值。请求消息的发送者必须为每一个
                    消息插入一个唯一的标识符。该标识符必须维持本地唯一至少4分钟，即使经过
                    重启动。应答消息的生成者必须确保该端到端标识符字段包含与相应的请求相同
                    的值。端到端标识符不可以被Diameter代理以任何原因修改。源主机AVP和该
                    字段的结合可以用于检测重复。重复请求会造成相同应答的传输，并且不可以
                    影响任何状态的设置，当处理原始请求时。应当在本地被消除的重复的应答消
                    息将会被忽略。
                    
        TODO: 具体实现：调用的引擎传入具体的随机数，并且调用引擎需要保证在至少4分钟内没有重复
        '''
        now_stamp = int(time())
        
        stamp_lower_12bytes = now_stamp & 0x0FFF
        
        new_end_by_end = stamp_lower_12bytes << 20 | range_number
        
        return new_end_by_end
        
    def _pack_init(self, dcc_code_name, end_by_end_rang_number):
        '''在编码前赋值基本信息'''
        self.dmsg_state = "00"
        
        # 根据DccCmdCode.ini中定义给赋值DCC消息头
        self.dmsg_head['DCC_FLAGS']    = int(self.dcc_cfg.Cmd2Code[dcc_code_name][1], 2)
        
        # TODO: 重新设定FLAGS, 暂时先不考虑
#        self.set_flags_proxiable()
#        self.set_flags_tpotentially()
#        
#        # 生成最终FLAGS
#        self.dmsg_head['DCC_FLAGS'] = self.dmsg_head['DCC_PROXIABLE'] | \
#                                      self.dmsg_head['DCC_TPOTENTIALLY']
                                      
        # 设定Coommand_code
        self.dmsg_head['DCC_CODE']     = int(self.dcc_cfg.Cmd2Code[dcc_code_name][0])
        
        self.dmsg_head['DCC_APP_ID']   = int(self.dcc_cfg.Cmd2Code[dcc_code_name][4])
        
        self.dmsg_head['DCC_HOPBYHOP'] = self.set_hop_by_hop(dcc_code_name)
        
        self.dmsg_head['DCC_ENDTOEND'] = self.set_end_by_end(end_by_end_rang_number)
        
        return True
        
    def pack_head(self, dcc_code_name, end_by_end_rang_number):
        '''编码消息头'''
        pack_buf = ""
        
        self._pack_init(dcc_code_name, end_by_end_rang_number)
        
        ver_and_len = self.dmsg_head['DCC_VERSION'] << 24 | self.dmsg_head['DCC_LENGTH']
        pack_buf += pack("!i", ver_and_len)
        
        flags_and_code = self.dmsg_head['DCC_FLAGS'] << 24 | self.dmsg_head['DCC_CODE']
        pack_buf += pack("!i", flags_and_code)
        
        pack_buf += pack("!i", self.dmsg_head['DCC_APP_ID'])
        
        pack_buf += pack("!i", self.dmsg_head['DCC_HOPBYHOP'])
        
        pack_buf += pack("!i", self.dmsg_head['DCC_ENDTOEND'])
        
        self.dmsg_state = "01"
        
        return pack_buf
    
    def _find_etc(self, dcc_code_name):
        '''根据dcc_code_name返回对应配置实例'''
        if dcc_code_name == "CCR":
            return self.dcc_cfg.CCR
        elif dcc_code_name == "CCA":
            return self.dcc_cfg.CCA
        elif dcc_code_name == "RAR":
            return self.dcc_cfg.RAR
        elif dcc_code_name == "RAA":
            return self.dcc_cfg.RAA
        elif dcc_code_name == "ASR":
            return self.dcc_cfg.ASR
        elif dcc_code_name == "ASA":
            return self.dcc_cfg.ASA
        elif dcc_code_name == "DWR":
            return self.dcc_cfg.DWR
        elif dcc_code_name == "DWA":
            return self.dcc_cfg.DWA
        elif dcc_code_name == "DPR":
            return self.dcc_cfg.DPR
        elif dcc_code_name == "DPA":
            return self.dcc_cfg.DPA
        elif dcc_code_name == "CER":
            return self.dcc_cfg.CER
        elif dcc_code_name == "CEA":
            return self.dcc_cfg.CEA
        else:
            raise D_ERROR.DccE_InvalidDccType, \
                    "返回配置实例错误，不支持的类型[%s]" % dcc_code_name
    
    def _create_avp_factory_pack(self, dcc_code_name, avp_code, avp_data):
        '''根据AVP_CODE创建不同的AVP实例'''
        # 根据dcc_code_name获取对应的配置实例
        my_etc = self._find_etc(dcc_code_name)
        
        # 根据AVP_CODE获取具体的数据类型
        if avp_code in my_etc:
            avp_type_etc = my_etc[avp_code]
        else:
            raise D_ERROR.AvpE_InvalidEtcParam, \
                    "没有匹配到相应的AVP_CODE： [%s]" % avp_code
        
        from avp_integer32 import Integer32
        from avp_integer64 import Integer64
        from avp_unsigned32 import Unsigned32
        from avp_unsigned64 import Unsigned64
        from avp_octetstring import OctetString
        from avp_float32 import Float32
        from avp_float64 import Float64
        from avp_grouped import Grouped
        
        # TODO: 添加新的数据类型修改-1
        if avp_type_etc[4] == "Integer32":
            my_avp = Integer32(avp_code, avp_data, 
                               level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "Integer64":
            my_avp = Integer64(avp_code, avp_data, 
                               level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "Unsigned32":
            my_avp = Unsigned32(avp_code, avp_data, 
                                level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "Unsigned64":
            my_avp = Unsigned64(avp_code, avp_data, 
                                level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "OctetString":
            my_avp = OctetString(avp_code, avp_data, 
                                 level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "Float32":
            my_avp = Float32(avp_code, avp_data, 
                             level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "Float64":
            my_avp = Float64(avp_code, avp_data, 
                             level=(int(avp_type_etc[1])-1))
        elif avp_type_etc[4] == "Grouped":
            my_avp = Grouped(avp_code, level=(int(avp_type_etc[1])-1), 
                              avp_config_instance=my_etc)
        else:
            raise D_ERROR.AvpE_InvalidAvpDataType, \
                  "错误的数据类型，无法解析：[%s]" % avp_type_etc[4]
                
        return my_avp

    def pack_AVP(self, dcc_code_name, avp_list):
        '''将AVP都编码打包到一起'''
        pack_buf = ""
        for a_avp_dict in avp_list:
            # 根据AVP获取具体的类型
            (avp_code, avp_data) = a_avp_dict.items()[0]
            
            my_avp =  self._create_avp_factory_pack(dcc_code_name, avp_code, avp_data)
            self.dmsg_list.append(my_avp)
            
            # 如果是Grouped递归调用这个函数
            if my_avp.avp['AVP_DATA_TYPE'] == 'Grouped':
                pack_buf += self.pack_AVP(dcc_code_name, avp_data)
                
            pack_buf += my_avp.encode()
            
        return pack_buf
        
    def pack(self, dcc_code_name, avp_list, end_by_end_rang_number):
        '''对于传入的AVP字典进行编码
        dcc_code_name            需要对其进行编码的类型，如：CCR,CCA,DWA,DWR
        avp_dict                 需要编码的数据
        end_by_end_rang_number   随机数，具体第一请参看end_by_end说明
        
        avp_dict说明：
            avp_dict的KEY应该是AVP_CODE
            avp_dict的内容应该是AVP_DATA
            
        首先根据avp_dict先添加AVP，之后再编码消息头
        '''
        self.dcc_cmd_name = dcc_code_name
        
        self.dmsg_buf = self.pack_AVP(self.dcc_cmd_name, avp_list)
        
        length = len(self.dmsg_buf)
        
        # 20为消息包头的长度，是固定的
        self.dmsg_head['DCC_LENGTH'] = 20 + length
        
        self.dmsg_buf = self.pack_head(dcc_code_name, end_by_end_rang_number) +\
                                    self.dmsg_buf
                                    
        self.dmsg_state = "02"
        return self.dmsg_buf
    
    def unpack_head(self):
        '''解码包头内容'''
        pass
    
    def unpack(self, pack_buf):
        '''解包DCC消息，返回解包后的一个字典
                    首先解析包头，再解析具体包体
        '''
        pass
    
    def unpack_to_file(self, writefile):
        '''将解包后的结果输出到writefile'''
        pass
    
    def print_dmsg(self):
        '''按照格式打印消息包的信息'''
        if self.dmsg_state in ["02", "12"]:
            # 打印包头内容
            self.dmsg_head['DCC_VERSION_HEX']  = "0x" + ("%02X" % self.dmsg_head['DCC_VERSION'])
            self.dmsg_head['DCC_LENGTH_HEX']   = "0x" + ("%06X" % self.dmsg_head['DCC_LENGTH'])
            self.dmsg_head['DCC_FLAGS_HEX']    = "0x" + ("%02X" % self.dmsg_head['DCC_FLAGS'])
            self.dmsg_head['DCC_CODE_HEX']     = "0x" + ("%06X" % self.dmsg_head['DCC_CODE'])
            self.dmsg_head['DCC_APP_ID_HEX']   = "0x" + ("%08X" % self.dmsg_head['DCC_APP_ID'])
            self.dmsg_head['DCC_HOPBYHOP_HEX'] = "0x" + ("%08X" % self.dmsg_head['DCC_HOPBYHOP'])
            self.dmsg_head['DCC_ENDTOEND_HEX'] = "0x" + ("%08X" % self.dmsg_head['DCC_ENDTOEND'])
            print self.dmsg_head['PIRNT_FMT'].safe_substitute(self.dmsg_head)
            
            # 打印包体内容
            for avp in self.dmsg_list:
                avp.print_avp()
        else:
            raise D_ERROR.DccE_InvalidDccstate, \
                    "DCC消息状态错误[%s]！不能打印详细信息" % self.dmsg_state
    
    def fmt_hex(self, buf):
        '''将16进制的字符串格式化输出'''
        char_num = 1
        pstr = ""
        for char in buf:
            if char_num % 2 != 0:
                pstr += char
            else:
                pstr += char
                print pstr,
                pstr = ""
                
            if char_num % 32 == 0: print "\n",
            char_num += 1
    