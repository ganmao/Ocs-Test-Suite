#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-15

@author: zdl

DiameterEngine
'''

from dcc_config import DccConfig

class DiameterEngine(object):
    '''
    Diameter 协议解码/编码引擎
    '''
    def __init__(self):
        # 引擎初始化
        
        # 初始化配置文件
        self.dcf = DccConfig()
        
    def __del__(self):
        del self.dcf