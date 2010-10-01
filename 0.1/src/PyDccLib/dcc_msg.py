#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-15

@author: zdl

使用说明：
    如果解码请传入需要解码的串
'''
from time import time
from struct import pack, unpack_from
from string import Template

import avp_const_define as ACD
import avp_error as D_ERROR
from dcc_engine import DiameterEngine as DE

# TODO: 添加新的数据类型需修改
from avp_integer32 import Integer32
from avp_integer64 import Integer64
from avp_unsigned32 import Unsigned32
from avp_unsigned64 import Unsigned64
from avp_octetstring import OctetString
from avp_float32 import Float32
from avp_float64 import Float64
from avp_grouped import Grouped

class DMSG(object):
    '''
    Diameter 消息基类
    '''
    def __init__(self, config_instance):
        self.dcc_cfg = config_instance
        self.de = DE()
        
        self.dmsg = {}
        self.dmsg['DCC_VERSION']      = ACD.const.DMSG_VERSION
        self.dmsg['DCC_LENGTH']       = 0x00
        self.dmsg['DCC_FLAGS']        = 0x00
        self.dmsg['DCC_REQUEST']      = 0x00      #需要将读取配置文件中的对应摄者
        self.dmsg['DCC_PROXIABLE']    = 0x00
        self.dmsg['DCC_ERROR']        = 0x00
        self.dmsg['DCC_TPOTENTIALLY'] = 0x00
        self.dmsg['DCC_CODE']         = 0x00
        self.dmsg['DCC_NAME']         = ""
        self.dmsg['DCC_APP_ID']       = ACD.const.DMSG_APPLICATION_ID
        self.dmsg['DCC_HOPBYHOP']     = 0x00
        self.dmsg['DCC_ENDTOEND']     = 0x00
        
        # 存放打包好的数据BUF
        self.dmsg['DCC_BUF']          = None 
        
        # 编码的时候存储实例列表
        self.dmsg['DCC_AVP_LIST']     = []
        
        # 编码时存放需要编码的JSON串，解码后存放需要输出的JSON串
        self.dmsg['DCC_JSON']         = ""
        
        # 00-准备编码，01-消息头编码完成，02-消息整体编码完成
        # 10-准备解码，11-消息头解码完成，12-消息整体解码完成
        self.dmsg['DCC_STAT']         = None
        
        self.dmsg['PIRNT_FMT']        = Template("\n\
+++++++++++++++++++++++++++++++\n\
\t${DCC_NAME}\n\
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
        
    def __del__(self):
        del self.dmsg
        
    def __repr__(self):
        '输出具体需要解包的json或者已经解包后的json'
        if self.dmsg['DCC_STAT'] in ["01", "02", "12"]:
            return self.dmsg['DCC_JSON']
        else:
            raise D_ERROR.DccE_InvalidDccstate, \
                        "错误的状态[%s]！当前状态不能使用repr" % self.dmsg['DCC_STAT']
        
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
    
    def find_cmd_name_by_code(self, dcc_cmd_code, dcc_request_flag):
        '''根据cmd_code与REQUEST标志获取name'''
        find_tulp = (str(dcc_cmd_code), bin(dcc_request_flag)[2:])
        dcc_cmd_name = self.dcc_cfg.Code2Cmd[find_tulp][2]
        return dcc_cmd_name
        
    def find_avp_etc(self, dcc_cmd_name):
        '''根据cmd_name返回具体的AVP配置实例'''
        if dcc_cmd_name == "CCR":
            return self.dcc_cfg.CCR
        elif dcc_cmd_name == "CCA":
            return self.dcc_cfg.CCA
        elif dcc_cmd_name == "RAR":
            return self.dcc_cfg.RAR
        elif dcc_cmd_name == "RAA":
            return self.dcc_cfg.RAA
        elif dcc_cmd_name == "ASR":
            return self.dcc_cfg.ASR
        elif dcc_cmd_name == "ASA":
            return self.dcc_cfg.ASA
        elif dcc_cmd_name == "DWR":
            return self.dcc_cfg.DWR
        elif dcc_cmd_name == "DWA":
            return self.dcc_cfg.DWA
        elif dcc_cmd_name == "DPR":
            return self.dcc_cfg.DPR
        elif dcc_cmd_name == "DPA":
            return self.dcc_cfg.DPA
        elif dcc_cmd_name == "CER":
            return self.dcc_cfg.CER
        elif dcc_cmd_name == "CEA":
            return self.dcc_cfg.CEA
        else:
            raise D_ERROR.DccE_InvalidDccType, \
                    "返回配置实例错误，不支持的类型[%s]" % dcc_cmd_name
        
    def decode_avp_code_from_buf(self, decode_buf):
        '''根据传入的buf UNPACK avp_code'''
        (avp_code,) = unpack_from("!I", decode_buf)
        return str(avp_code)
        
    def get_avp_etc_by_code(self, avp_code, cmd_etc_instances):
        '''根据AVP_CODE，从avp_etc_instance中查找具体的数据配置'''
        if avp_code in cmd_etc_instances:
            avp_etc = cmd_etc_instances[avp_code]
        else:
            raise D_ERROR.AvpE_InvalidEtcParam, \
                    "没有匹配到相应的AVP_CODE： [%s]" % avp_code
                    
        return avp_etc
        
    def _pack_init(self, dcc_code_name, end_by_end_rang_number):
        '''在编码前赋值基本信息'''
        self.dmsg['DCC_STAT'] = "00"
        
        # 根据DccCmdCode.ini中定义给赋值DCC消息头
        self.dmsg['DCC_FLAGS']    = int(self.dcc_cfg.Cmd2Code[dcc_code_name][1], 2)
        
        # TODO: 重新设定FLAGS, 暂时先不考虑
#        self.set_flags_proxiable()
#        self.set_flags_tpotentially()
#        
#        # 生成最终FLAGS
#        self.dmsg['DCC_FLAGS'] = self.dmsg['DCC_PROXIABLE'] | \
#                                      self.dmsg['DCC_TPOTENTIALLY']
                                      
        # 设定Coommand_code
        self.dmsg['DCC_CODE']     = int(self.dcc_cfg.Cmd2Code[dcc_code_name][0])
        
        self.dmsg['DCC_APP_ID']   = int(self.dcc_cfg.Cmd2Code[dcc_code_name][4])
        
        self.dmsg['DCC_HOPBYHOP'] = self.set_hop_by_hop(dcc_code_name)
        
        self.dmsg['DCC_ENDTOEND'] = self.set_end_by_end(end_by_end_rang_number)
        
        return True
        
    def pack_head(self, dcc_code_name, end_by_end_rang_number):
        '''编码消息头'''
        pack_buf = ""
        
        self._pack_init(dcc_code_name, end_by_end_rang_number)
        
        ver_and_len = self.dmsg['DCC_VERSION'] << 24 | self.dmsg['DCC_LENGTH']
        pack_buf += pack("!I", ver_and_len)
        
        flags_and_code = self.dmsg['DCC_FLAGS'] << 24 | self.dmsg['DCC_CODE']
        pack_buf += pack("!I", flags_and_code)
        
        pack_buf += pack("!I", self.dmsg['DCC_APP_ID'])
        
        pack_buf += pack("!I", self.dmsg['DCC_HOPBYHOP'])
        
        pack_buf += pack("!I", self.dmsg['DCC_ENDTOEND'])
        
        self.dmsg['DCC_STAT'] = "01"
        
        return pack_buf
    
    def _create_avp_instance(self, cmd_etc_instance, avp_dict):
        '创建AVP实例'
        # 从列表中获取需要编码的AVP_CODE和AVP_DATA
        (avp_code, avp_data) = avp_dict.items()[0]
            
        # 根据AVP_CODE获取具体的AVP配置列表
        avp_etc = self.get_avp_etc_by_code(avp_code, cmd_etc_instance)
            
        # 根据avp_etc中的配置类型，创建具体的AVP实例
        avp_instance = create_avp_factory(avp_etc, avp_data)
            
        return avp_instance
    
    def _create_group_sub_instance(self, cmd_etc_instance, group_instance, sub_avp_list):
        'Grouped需要递归调用以将子AVP添加到Grouped中'
        for sub_dict in sub_avp_list:
            sub_instance = self._create_avp_instance(cmd_etc_instance, sub_dict)
            
            if sub_instance.avp['AVP_DATA_TYPE'] == 'Grouped':
                sub_group = self._create_group_sub_instance(cmd_etc_instance, sub_instance, sub_dict)
            
            group_instance.append(sub_instance)

    def pack_AVP(self, dcc_code_name, avp_list):
        '''将AVP都编码打包到一起'''
        pack_buf = ""
        
        # 根据DCC_NAME获取到相应的配置文件实例
        cmd_etc_instance = self.find_avp_etc(self.dmsg['DCC_NAME'])
        
        for decode_avp_dict in avp_list:
            avp_instance = self._create_avp_instance(cmd_etc_instance, decode_avp_dict)
            
            # 将创建的AVP添加入DCC_AVP_LIST
            self.dmsg['DCC_AVP_LIST'].append(avp_instance)
            
            # 如果是Grouped递归调用这个函数
            if avp_instance.avp['AVP_DATA_TYPE'] == 'Grouped':
                self._create_group_sub_instance(cmd_etc_instance, 
                                                avp_instance, 
                                                decode_avp_dict.items()[0][1])
                
            # 将所有编码后的数据整合到一起
            pack_buf += avp_instance.encode()
            
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
        self.dmsg['DCC_STAT'] = "00"
        self.dmsg['DCC_NAME'] = dcc_code_name
        self.dmsg['DCC_JSON'] = self.de.dumps_json(avp_list)
        
        # 对AVP的内容进行编码
        dcc_avp_buf = self.pack_AVP(self.dmsg['DCC_NAME'], avp_list)
        
        # 计算编码后AVP的长度,20为消息包头的长度，是固定的
        length = len(dcc_avp_buf)
        self.dmsg['DCC_LENGTH'] = 20 + length
        
        # 编码包头
        dcc_head_buf = self.pack_head(dcc_code_name, end_by_end_rang_number)
        
        # 将包体与包头组合
        self.dmsg['DCC_BUF'] = dcc_head_buf + dcc_avp_buf
        
        self.dmsg['DCC_STAT'] = "02"
        return self.dmsg['DCC_BUF']
    
    def unpack_head(self, pack_buf):
        '''解码包头内容'''
        offset_ = 0
        (ver_and_len,) = unpack_from("!I", pack_buf, offset_)
        offset_ += 4
        self.dmsg['DCC_VERSION'] = ver_and_len >> 24
        
        self.dmsg['DCC_LENGTH']  = ver_and_len & 0x00FFFFFF
        
        if len(pack_buf) != self.dmsg['DCC_LENGTH']:
            raise D_ERROR.DccE_InvalidLength, \
                    "传入需解码包长度与包头中标识长度不符！\n\t传入包长度：[%d]\n\t包头中标明长度：[%d]" \
                    % (len(pack_buf), self.dmsg['DCC_LENGTH'])
        
        (flags_and_code,)  = unpack_from("!I", pack_buf, offset_)
        offset_ += 4
        self.dmsg['DCC_FLAGS'] = flags_and_code >> 24
        self.dmsg['DCC_CODE']  = flags_and_code & 0x00FFFFFF
        
        if self.dmsg['DCC_FLAGS'] | ACD.const.DMSG_FLAGS_REQUEST \
            == ACD.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_REQUEST'] = ACD.const.DMSG_FLAGS_REQUEST
        else:
            self.dmsg['DCC_REQUEST'] = ACD.const.DMSG_FLAGS_ANSWER
            
        if self.dmsg['DCC_FLAGS'] | ACD.const.DMSG_FLAGS_PROXIABLE \
            == ACD.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_PROXIABLE'] = ACD.const.DMSG_FLAGS_PROXIABLE
            
        if self.dmsg['DCC_FLAGS'] | ACD.const.DMSG_FLAGS_ERROR \
            == ACD.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_ERROR'] = ACD.const.DMSG_FLAGS_ERROR
            
        if self.dmsg['DCC_FLAGS'] | ACD.const.DMSG_FLAGS_TPOTENTIALLY \
            == ACD.const.DMSG_FLAGS_REQUEST:
            self.dmsg['DCC_TPOTENTIALLY'] = ACD.const.DMSG_FLAGS_TPOTENTIALLY
            
        (self.dmsg['DCC_APP_ID'],)   = unpack_from("!I", pack_buf, offset_)
        offset_ += 4
        (self.dmsg['DCC_HOPBYHOP'],) = unpack_from("!I", pack_buf, offset_)
        offset_ += 4
        (self.dmsg['DCC_ENDTOEND'],) = unpack_from("!I", pack_buf, offset_)
        offset_ += 4
        
        self.dmsg['DCC_STAT'] = "11"
        return offset_
    
    def _find_avp_config_by_code(self, cmd_code, request_flag):
        '根据传入的CMD-CODE与请求标志，确定具体解码的消息类型'
        find_tulp = (str(cmd_code), bin(request_flag)[2:])
        
        self.dmsg['DCC_NAME'] = self.dcc_cfg.Code2Cmd[find_tulp][2]
        
        if self.dmsg['DCC_NAME'] == "CCR":
            return self.dcc_cfg.CCR
        elif self.dmsg['DCC_NAME'] == "CCA":
            return self.dcc_cfg.CCA
        elif self.dmsg['DCC_NAME'] == "RAR":
            return self.dcc_cfg.RAR
        elif self.dmsg['DCC_NAME'] == "RAA":
            return self.dcc_cfg.RAA
        elif self.dmsg['DCC_NAME'] == "ASR":
            return self.dcc_cfg.ASR
        elif self.dmsg['DCC_NAME'] == "ASA":
            return self.dcc_cfg.ASA
        elif self.dmsg['DCC_NAME'] == "DWR":
            return self.dcc_cfg.DWR
        elif self.dmsg['DCC_NAME'] == "DWA":
            return self.dcc_cfg.DWA
        elif self.dmsg['DCC_NAME'] == "DPR":
            return self.dcc_cfg.DPR
        elif self.dmsg['DCC_NAME'] == "DPA":
            return self.dcc_cfg.DPA
        elif self.dmsg['DCC_NAME'] == "CER":
            return self.dcc_cfg.CER
        elif self.dmsg['DCC_NAME'] == "CEA":
            return self.dcc_cfg.CEA
        else:
            raise D_ERROR.DccE_InvalidDccType, \
                    "返回配置实例错误，不支持的类型[%s, %s]" % self.dmsg['DCC_NAME']
            
    def unpack(self, pack_buf):
        '''解包DCC消息，返回解包后的一个字典
                    首先解析包头，再解析具体包体
        '''
        self.dmsg['DCC_STAT'] = "10"
        self.dmsg['DCC_BUF'] = pack_buf
        avp_pack_buf = ""
        
        # 解析包头
        offset = self.unpack_head(self.dmsg['DCC_BUF'])

        # 根据CMD_CODE查找CMD_NAME
        self.dmsg['DCC_NAME'] = self.find_cmd_name_by_code(self.dmsg['DCC_CODE'], 
                                                           self.dmsg['DCC_REQUEST'])
        
        # 根据DCC_NAME获取到相应的配置文件实例
        cmd_etc_instance = self.find_avp_etc(self.dmsg['DCC_NAME'])
        
        while offset != self.dmsg['DCC_LENGTH']:
            # 确定具体需要解包的AVP BUF
            avp_pack_buf = self.dmsg['DCC_BUF'][offset:]
            
            # 返回需要解析AVP的AVP_CODE
            avp_code = self.decode_avp_code_from_buf(avp_pack_buf)
            
            # 根据AVP_CODE获取具体的AVP配置列表
            avp_etc = self.get_avp_etc_by_code(avp_code, cmd_etc_instance)
            
            # 根据AVP配置列表中的类型返回实例
            #my_avp = create_avp_factory(avp_etc, decode_buf=avp_pack_buf, msg_etc=self.dmsg)
            my_avp = create_avp_factory(avp_etc, decode_buf=avp_pack_buf, msg_etc=cmd_etc_instance)
            
            # AVP解包，并且将解包后结果添加到self.dmsg['DCC_AVP_LIST']
            my_avp.decode()
            self.dmsg['DCC_AVP_LIST'].append(my_avp.avp)
            
            offset += my_avp.avp['AVP_LENGTH']

        
        self.dmsg['DCC_JSON'] = self.de.dumps_json( \
                                      self._create_unpack_json_list( \
                                                self.dmsg['DCC_AVP_LIST'] \
                                            ) \
                                      )
        self.dmsg['DCC_STAT'] = "12"
        return self.dmsg
    
    def _create_unpack_json_list(self, avp_list):
        '创建解包时的json串'
        json_list = []
        for avp in avp_list:
            if avp['AVP_DATA_TYPE'] == 'Grouped':
                json_list.append({str(avp['AVP_CODE']): self._create_unpack_json_list(avp['GROUPED_SUBS_AVP'])})
            else:
                json_list.append({str(avp['AVP_CODE']): avp['AVP_DATA']})
                
        return json_list
    
    def print_dmsg(self):
        '''按照格式打印消息包的信息'''
        if self.dmsg['DCC_STAT'] in ["02", "12"]:
            # 打印包头内容
            self.dmsg['DCC_VERSION_HEX']  = "0x" + ("%02X" % self.dmsg['DCC_VERSION'])
            self.dmsg['DCC_LENGTH_HEX']   = "0x" + ("%06X" % self.dmsg['DCC_LENGTH'])
            self.dmsg['DCC_FLAGS_HEX']    = "0x" + ("%02X" % self.dmsg['DCC_FLAGS'])
            self.dmsg['DCC_CODE_HEX']     = "0x" + ("%06X" % self.dmsg['DCC_CODE'])
            self.dmsg['DCC_APP_ID_HEX']   = "0x" + ("%08X" % self.dmsg['DCC_APP_ID'])
            self.dmsg['DCC_HOPBYHOP_HEX'] = "0x" + ("%08X" % self.dmsg['DCC_HOPBYHOP'])
            self.dmsg['DCC_ENDTOEND_HEX'] = "0x" + ("%08X" % self.dmsg['DCC_ENDTOEND'])
            print self.dmsg['PIRNT_FMT'].safe_substitute(self.dmsg)
            
            # 打印包体内容
            for avp in self.dmsg['DCC_AVP_LIST']:
                avp.print_avp()
        else:
            raise D_ERROR.DccE_InvalidDccstate, \
                    "DCC消息状态错误[%s]！不能打印详细信息" % self.dmsg['DCC_STAT']
    
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
    
def create_avp_factory(avp_etc, encode_data=None, decode_buf=None, msg_etc=None):
    '''根据传入的avp类型配置列表，返回对应AVP数据类型的实例
    avp_etc        单条Avp的配置list
    encode_data    需要编码的avp_code
    decode_buf    需要解码的buf
    msg_etc        解码时Greouped类型需要用到全部的配置实例
    '''
    # TODO: 添加新的数据类型需修改
    if avp_etc[4] == "Integer32":
        my_avp = Integer32(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "Integer64":
        my_avp = Integer64(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "Unsigned32":
        my_avp = Unsigned32(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "Unsigned64":
        my_avp = Unsigned64(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "OctetString":
        my_avp = OctetString(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "Float32":
        my_avp = Float32(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "Float64":
        my_avp = Float64(avp_etc[2],
                           avp_data=encode_data,
                           decode_buf=decode_buf,
                           level=(int(avp_etc[1])-1),
                           cmd_etc_instance=avp_etc)
    elif avp_etc[4] == "Grouped":
        my_avp = Grouped(avp_etc[2],
                            avp_data=encode_data,
                            decode_buf=decode_buf,
                            level=(int(avp_etc[1])-1),
                            cmd_etc_instance=msg_etc)
    else:
        raise D_ERROR.AvpE_InvalidAvpDataType, \
              "错误的数据类型，无法解析：[%s]" % avp_etc[4]
              
    return my_avp

