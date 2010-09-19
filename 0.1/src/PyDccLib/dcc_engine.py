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
        
    def loads_json(self, json_str):
        '将json的字符串，解析为列表'
        try:
            from json import loads, dumps
        except ImportError:
            '''由于py2.6以上才内置了JSON模块，
                                故如果没有内置则采用第三方模块：
            Contact mailto:patrickdlogan@stardecisions.com
            '''
            from sys import path
            path.insert(0, "json-py-3_4.zip")
            #from json import read as loads
            from minjson import read as loads
            
        return loads(json_str)
    
    def dumps_json(self, obj):
        '将列表，解析为json的字符串'
        try:
            from json import loads, dumps
        except SyntaxError:
            '''由于py2.6以上才内置了JSON模块，
                                故如果没有内置则采用第三方模块：
            Contact mailto:patrickdlogan@stardecisions.com
            '''
            from sys import path
            path.insert(0, "json-py-3_4.zip")
            #from json import write as dumps
            from minjson import write as dumps

        return dumps(obj)