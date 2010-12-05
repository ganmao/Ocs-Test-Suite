#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-14

@author: zdl

首先读取  etc 目录下的 DccCmdCode.ini 配置文件，
根据其中定义再去去读目录下的其他配置文件

最终初始化后的参数都保存在AvpConfig类中

CmdCode字典保存  DccCmdCode.ini 配置的内容
CCR,CCA,...等数组分别保存对应的配置文件信息
每一个配置数据的结构都是数据组成的字典

配置文件格式说明：
    配置文件各个列的间隔可以采用<TAB>或者空格
    
    配置文件第一行为标题，会第一个读入数据的TITLE
    CmdCode的KEY是 CODE与FLAGS的组合
    CCR,CCA,...等的KEY就是AVP_CODE
    
    配置文件都需要保存到etc目录下，否则请修改 avp_const_define.const.ETC_PATH
'''
import re
from os.path import sep

import dcc_defined as DCC_DEF
import dcc_error as DCC_ERR

class DCC_CFG(object):
    '''配置文件处理类'''
    def __init__(self):
        self.etc_path = DCC_DEF.const.ETC_PATH
        self.re_str_fmt = re.compile("\s+")
        self.re_ltrip_space = re.compile("^\s+")
        
        self.Code2Cmd = {}  # 以CODE为KEY
        #self.Cmd2Code = {}  # 以NAME为KEY
        self.CCR = {}
        self.CCA = {}
        self.RAR = {}
        self.RAA = {}
        self.ASR = {}
        self.ASA = {}
        self.DWR = {}
        self.DWA = {}
        self.DPR = {}
        self.DPA = {}
        self.CER = {}
        self.CEA = {}
        
        self.__read_CmdCode()
        
        for key in self.Code2Cmd.keys():
            if (key != "TITLE"):
                #self.__switch_file(self.Code2Cmd[key][2])
                self.__switch_file(int(self.Code2Cmd[key][0]),
                                   int(self.Code2Cmd[key][1]),
                                   self.Code2Cmd[key][2])
        
    def __read_CmdCode(self):
        '读取CmdCode配置文件'
        fh = open(self.etc_path + sep + "DccCmdCode.ini", "r")
        
        for eachline in fh:
            # 格式化行信息
            line_list = self.re_str_fmt.split(eachline)
            
            if line_list[0] == "CMD_CODE":
                self.Code2Cmd["TITLE"] = line_list
                #self.Cmd2Code["TITLE"] = line_list
                continue
            else:
                self.Code2Cmd[(int(line_list[0]), int(line_list[1]))] = line_list
                #self.Cmd2Code[line_list[2]] = line_list
            
        fh.close()
        
    def __read_AvpFile(self, CmdCodeStr):
        '''根据传入的CmdCodeStr到self.Code2Cmd中确定具体文件
                     之后初始化相应的配置
        '''
        fh = open(self.etc_path + sep + \
                  "avpfile-" + CmdCodeStr.lower() + ".ini", "r")
        
        my_dict = {}
        
        #line_num = 0
        for eachline in fh:
            # 删除配置文件左侧空白
            eachline = self.re_ltrip_space.sub("", eachline)
            
            # 根据空白将各个列存入数组
            line_list = self.re_str_fmt.split(eachline)
                
            if line_list[0] == "AVP_NAME":
                my_dict["TOTLE"] = line_list
            else:
                #my_dict[int(line_list[2])] = line_list
                my_dict[line_list[2]] = line_list
                
        fh.close()
        return my_dict
        
    def __switch_file(self, cmd_code, request_flag, cmd_name):
        '根据不同的CmdCodeStr返回应该复制的字段属性'
        if (cmd_code, request_flag) == DCC_DEF.const.CREDIT_CONTROL_REQUEST:
            self.CCR = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.CREDIT_CONTROL_ANSWER:
            self.CCA = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.RE_AUTH_REQUEST:
            self.RAR = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.RE_AUTH_ANSWER:
            self.RAA = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.ABORT_SESSION_REQUEST:
            self.ASR = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.ABORT_SESSION_ANSWER:
            self.ASA = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.DEVICE_WATCHDOG_REQUEST:
            self.DWR = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.DEVICE_WATCHDOG_ANSWER:
            self.DWA = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.DISCONNECT_PEER_REQUEST:
            self.DPR = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.DISCONNECT_PEER_ANSWER:
            self.DPA = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.CAPABILITIES_EXCHANGE_REQUEST:
            self.CER = self.__read_AvpFile(cmd_name)
        elif (cmd_code, request_flag) == DCC_DEF.const.CAPABILITIES_EXCHANGE_ANSWER:
            self.CEA = self.__read_AvpFile(cmd_name)
        else:
            raise DCC_ERR.AvpE_InvalidEtcParam, \
                    "Match CMD_CODE Error:(code=%s, flag=%s, name=%s)" % (cmd_code, request_flag, cmd_name)
                    
    def __del__(self):
        del self.etc_path
        del self.Code2Cmd
        #del self.Cmd2Code
        del self.CCR
        del self.CCA
        del self.RAR
        del self.RAA
        del self.ASR
        del self.ASA
        del self.DWR
        del self.DWA
        del self.DPR
        del self.DPA
        del self.CER
        del self.CEA 
        
    def get_config(self, cmd_code, avp_code=None):
        '''根据cmd_code与avp_code从相应配置文件中获取配置
        如果未传入avp_code则返回整个msg配置文件，如果传入avp_code则只返回对应avp配置
        '''
        try:
            if avp_code:
                avp_code = str(avp_code)
                
                if cmd_code == DCC_DEF.const.CREDIT_CONTROL_REQUEST:
                    return self.CCR[avp_code]
                elif cmd_code == DCC_DEF.const.CREDIT_CONTROL_ANSWER:
                    return self.CCA[avp_code]
                elif cmd_code == DCC_DEF.const.RE_AUTH_REQUEST:
                    return self.RAR[avp_code]
                elif cmd_code == DCC_DEF.const.RE_AUTH_ANSWER:
                    return self.RAA[avp_code]
                elif cmd_code == DCC_DEF.const.ABORT_SESSION_REQUEST:
                    return self.ASR[avp_code]
                elif cmd_code == DCC_DEF.const.ABORT_SESSION_ANSWER:
                    return self.ASA[avp_code]
                elif cmd_code == DCC_DEF.const.DEVICE_WATCHDOG_REQUEST:
                    return self.DWR[avp_code]
                elif cmd_code == DCC_DEF.const.DEVICE_WATCHDOG_ANSWER:
                    return self.DWA[avp_code]
                elif cmd_code == DCC_DEF.const.DISCONNECT_PEER_REQUEST:
                    return self.DPR[avp_code]
                elif cmd_code == DCC_DEF.const.DISCONNECT_PEER_ANSWER:
                    return self.DPA[avp_code]
                elif cmd_code == DCC_DEF.const.CAPABILITIES_EXCHANGE_REQUEST:
                    return self.CER[avp_code]
                elif cmd_code == DCC_DEF.const.CAPABILITIES_EXCHANGE_ANSWER:
                    return self.CEA[avp_code]
                else:
                    raise DCC_ERR.AvpE_InvalidEtcParam, \
                            "Match CMD_CODE Error: cmd_code=%s, acp_code=%s" % (cmd_code, avp_code)
            else:
                if cmd_code == DCC_DEF.const.CREDIT_CONTROL_REQUEST:
                    return self.CCR
                elif cmd_code == DCC_DEF.const.CREDIT_CONTROL_ANSWER:
                    return self.CCA
                elif cmd_code == DCC_DEF.const.RE_AUTH_REQUEST:
                    return self.RAR
                elif cmd_code == DCC_DEF.const.RE_AUTH_ANSWER:
                    return self.RAA
                elif cmd_code == DCC_DEF.const.ABORT_SESSION_REQUEST:
                    return self.ASR
                elif cmd_code == DCC_DEF.const.ABORT_SESSION_ANSWER:
                    return self.ASA
                elif cmd_code == DCC_DEF.const.DEVICE_WATCHDOG_REQUEST:
                    return self.DWR
                elif cmd_code == DCC_DEF.const.DEVICE_WATCHDOG_ANSWER:
                    return self.DWA
                elif cmd_code == DCC_DEF.const.DISCONNECT_PEER_REQUEST:
                    return self.DPR
                elif cmd_code == DCC_DEF.const.DISCONNECT_PEER_ANSWER:
                    return self.DPA
                elif cmd_code == DCC_DEF.const.CAPABILITIES_EXCHANGE_REQUEST:
                    return self.CER
                elif cmd_code == DCC_DEF.const.CAPABILITIES_EXCHANGE_ANSWER:
                    return self.CEA
                else:
                    raise DCC_ERR.AvpE_InvalidEtcParam, \
                            "Match CMD_CODE Error: cmd_code=%s, acp_code=%s" % (cmd_code, avp_code)
        except KeyError:
            raise DCC_ERR.AvpE_InvalidAvpCode, \
                            "Can Not Find The avp_code(%s) In avpfile(%s) Config File!" % (avp_code, cmd_code)
                            