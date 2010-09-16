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

import avp_const_define as ACD


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
        
        self.dmsg_head['DCC_BUF']       = None
        
        self.dmsg_list = {}
        self.cmd_code = None     # 定义当前解包的类型
        
        # 00-准备编码，01-消息头编码完成，02-消息整体编码完成
        # 10-准备解码，11-消息头解码完成，12-消息整体解码完成
        self.dmsg_state = None
        
    def _set_flags_proxiable(self):
        '''P(roxiable) –如果设置，表明该消息可以被Proxy、中继或者复位向。
                     如果清零，该消息必须在本地处理。
        '''
        # 预留，如果需要修改的时候使用
        return ACD.const.DMSG_FLAGS_PROXIABLE
        
    def _set_flags_error(self):
        '''E(rror) -如果设置，表明该消息包含一个协议差错，
                    且该消息与ABNF中描述的该命令不一致。
        “E”比特设置的消息一般当作差错消息。在请求消息中不能设置该比特。
        '''
        # 预留，如果需要修改的时候使用
        return ACD.const.DMSG_FLAGS_ERROR
        
    def _set_flags_tpotentially(self):
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
    
    def _set_hop_by_hop(self):
        '''Hop-by-Hop Identifier：Hop-by-Hop标识符为一个无符号32比特整数字段
                    （按网络字节顺序），用来帮助匹配请求和响应。发送者必须保证请求中的
        Hop-by-Hop标识符在特定的连接上在任何特定的时间是唯一的，
                    并且保证该数字在经过重启动后仍然唯一。应答消息的发送者必须确保Hop-by-Hop
                    标识符字段维持与相应的请求相同的值。Hop-by-Hop标识符通常是单调升序的数字，
                    其开始值是随机生成的。一个带有未知Hop-by-Hop标识符的应答消息必须被丢弃。
                    
        TODO: 具体实现：从DccCmdCode.ini配置文件中获取最后一次的值，并且需要在组包完成时写回文件
        '''
        return self.dcc_cfg.Cmd2Code[dcc_code_name][5] + 1
    
    def _set_end_by_end(self, range_number):
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
        self.dmsg_head['DCC_FLAGS']        = self.dcc_cfg.Cmd2Code[dcc_code_name][1]
        
        # 重新设定FLAGS, 暂时先不考虑
#        self._set_flags_proxiable()
#        self._set_flags_tpotentially()
#        
#        # 生成最终FLAGS
#        self.dmsg_head['DCC_FLAGS'] = self.dmsg_head['DCC_PROXIABLE'] | \
#                                      self.dmsg_head['DCC_TPOTENTIALLY']
                                      
        # 设定Coommand_code
        self.dmsg_head['DCC_CODE']         = self.dcc_cfg.Cmd2Code[dcc_code_name][2]
        
        self.dmsg_head['DCC_HOPBYHOP']     = self._set_hop_by_hop()
        
        self.dmsg_head['DCC_ENDTOEND']     = self._set_end_by_end(end_by_end_rang_number)
        
        return True
        
    def pack_head(self, dcc_code_name, end_by_end_rang_number):
        '''编码消息头'''
        self._pack_init(dcc_code_name, end_by_end_rang_number)
        
        ver_and_len = self.dmsg_head['DCC_VERSION'] << 24 | self.dmsg_head['DCC_LENGTH']
        self.dmsg_head['DCC_BUF'] = pack("!I", ver_and_len)
        
        flags_and_code = self.dmsg_head['DCC_FLAGS'] << 24 | self.dmsg_head['DCC_CODE']
        self.dmsg_head['DCC_BUF'] += pack("!I", flags_and_code)
        
        self.dmsg_head['DCC_BUF'] += pack("!I", self.dmsg_head['DCC_APP_ID'])
        
        self.dmsg_head['DCC_BUF'] += pack("!I", self.dmsg_head['DCC_HOPBYHOP'])
        
        self.dmsg_head['DCC_BUF'] += pack("!I", self.dmsg_head['DCC_ENDTOEND'])
        
        self.dmsg_state = "01"
        
        return self.dmsg_head['DCC_BUF']
    
    def _create_avp_factory_pack(self, avp_code):
        '''根据AVP_CODE创建不同的AVP实例'''
    
    def pack_AVP(self, avp_dict):
        '''将AVP都编码打包到一起'''
        for avp_code in avp_dict.keys:
            MyAvp =  self._create_avp_factory_pack(avp_code)
            
            MyAvp.encode()
        
    def pack(self, dcc_code_name, avp_dict, end_by_end_rang_number):
        '''对于传入的AVP字典进行编码
        CmdCode          需要对其进行编码的类型，也就是DCC中的COMMAND-CODE
        avp_dict         需要编码的数据
        end_by_end_rang_number    随机数，具体第一请参看end_by_end说明
        
        avp_dict说明：
            avp_dict的KEY应该是AVP_CODE
            avp_dict的内容应该是AVP_DATA
            
        首先根据avp_dict先添加AVP，之后再编码消息头
        '''
        length = self.pack_AVP(avp_dict)
        
        # 20为消息包头的长度，是固定的
        self.dmsg_head['DCC_LENGTH'] = 20 + length
        
        self.pack_head(dcc_code_name, end_by_end_rang_number)
    
    def pack_from_file(self, readfile):
        '''根据从文件中读取出来的数据进行编码
        readfile        需要读取的文件
        
        readfile格式说明：
            AVP_CODE:AVP_DATA
        '''
        pass
    
    def unpack_head(self):
        '''解码包头内容'''
        pass
    
    def unpack(self):
        '''解包DCC消息，返回解包后的一个字典'''
        pass
    
    def unpack_to_file(self, writefile):
        '''将解包后的结果输出到writefile'''
        pass
    