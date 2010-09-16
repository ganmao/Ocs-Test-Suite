#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-14

@author: zdl

首先读取 ../etc 目录下的 DccCmdCode.ini 配置文件，
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

import avp_const_define as ACD
import avp_error as D_ERROR

class DccConfig(object):
    '''配置文件处理类'''
    def __init__(self):
        self.etc_path = ACD.const.ETC_PATH
        self.re_str_fmt = re.compile("\s+")
        self.re_ltrip_space = re.compile("^\s+")
        
        self.Code2Cmd = {}  # 以CODE为KEY
        self.Cmd2Code = {}  # 以NAME为KEY
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
        
        self.read_CmdCode()
        
        for key in self.Code2Cmd.keys():
            if (key == "TOTLE" or self.Code2Cmd[key][3] == "-"): continue
            self.switch_code(self.Code2Cmd[key][2])
        
    def read_CmdCode(self):
        '读取CmdCode配置文件'
        fh = open(self.etc_path + sep + "DccCmdCode.ini", "r")
        
        for eachline in fh:
            # 格式化行信息
            line_list = self.re_str_fmt.split(eachline)
            
            if line_list[0] == "CMD_CODE":
                self.Code2Cmd["TOTLE"] = line_list
                self.Cmd2Code["TOTLE"] = line_list
                continue
            else:
                self.Code2Cmd[(line_list[0], line_list[1])] = line_list
                self.Cmd2Code[line_list[2]] = line_list
            
        fh.close()
        
    def read_AvpFile(self, CmdCodeStr):
        '''根据传入的CmdCodeStr到self.Code2Cmd中确定具体文件
                     之后初始化相应的配置
        '''
        fh = open(self.etc_path + sep + \
                  "avpfile-" + CmdCodeStr.lower() + ".ini", "r")
        
        my_dict = {}
        
        line_num = 0
        for eachline in fh:
            # 格式化行信息
            line_num += 1
            
            # 删除配置文件左侧空白
            eachline = self.re_ltrip_space.sub("", eachline)
            
            # 根据空白将各个列存入数组
            line_list = self.re_str_fmt.split(eachline)
                
            if line_list[0] == "AVP_NAME":
                my_dict["TOTLE"] = line_list
            else:
                my_dict[int(line_list[2])] = line_list
                
        fh.close()
        #print u"加载[%s],[%d]条" % (CmdCodeStr, line_num)
        #print u"实际存储[%s],[%d]条" % (CmdCodeStr, len(my_dict))
        return my_dict
        
    def switch_code(self, CmdCodeStr):
        '根据不同的CmdCodeStr返回应该复制的字段属性'
        if CmdCodeStr == "CCR":
            self.CCR = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "CCA":
            self.CCA = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "RAR":
            self.RAR = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "RAA":
            self.RAA = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "ASR":
            self.ASR = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "ASA":
            self.ASA = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "DWR":
            self.DWR = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "DWA":
            self.DWA = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "DPR":
            self.DPR = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "DPA":
            self.DPA = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "CER":
            self.CER = self.read_AvpFile(CmdCodeStr)
        elif CmdCodeStr == "CEA":
            self.CEA = self.read_AvpFile(CmdCodeStr)
        else:
            raise D_ERROR.AvpE_InvalidEtcParam, \
                    "匹配CmdCodeStr编码错误!"
        
    def __del__(self):
        del self.etc_path
        del self.Code2Cmd
        del self.Cmd2Code
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
        