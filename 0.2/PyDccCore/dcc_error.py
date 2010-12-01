#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-9

@author: zdl

定义Diameter库的异常类型
'''

class DCCException(Exception):
    '''Dcc 异常基类
    '''
    def __init__(self, msg=None):
        Exception.__init__(self)
        self.msg = msg
    
    def __name__(self):
        return "DCCException"
    
    def __repr__(self):
        return repr(self.msg)
    
    def __str__(self):
        return str(self.msg)
    
class DccE_InvalidDccType(DCCException):
    '''Dcc类型错误'''
    def __init__(self, msg=None):
        DCCException.__init__(self, msg)
    def __name__(self):
        return "DccE_InvalidDccType"
    
class DccE_InvalidDccstate(DCCException):
    '''Dcc状态错误'''
    def __init__(self, msg=None):
        DCCException.__init__(self, msg)
    def __name__(self):
        return "DccE_InvalidDccstate"
    
class DccE_InvalidLength(DCCException):
    '''Dcc长度错误'''
    def __init__(self, msg=None):
        DCCException.__init__(self, msg)
    def __name__(self):
        return "DccE_InvalidLength"
    
class DccE_InvalidMethod(DCCException):
    '''Dcc错误的方法'''
    def __init__(self, msg=None):
        DCCException.__init__(self, msg)
    def __name__(self):
        return "DccE_InvalidMethod"
    
class DccE_CreateAvpError(DCCException):
    '''创建AVP实例错误'''
    def __init__(self, msg=None):
        DCCException.__init__(self, msg)
    def __name__(self):
        return "DccE_CreateAvpError"
    
class AvpException(DCCException):
    '''
    AVP异常错误基类,继承自DCCException
    使用方法：
    except AvpError, var:
        #var是抛出异常的实例
    
    msg 记录具体的错误消息
    '''
    def __init__(self, msg=None):
        DCCException.__init__(self, msg)
    def __name__(self):
        return "AvpException"
        
        
class AvpE_InvalidAvpLength(AvpException):
    '''AVP长度错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidAvpLength"
        
        
class AvpE_InvalidCodeState(AvpException):
    '''编码状态错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidCodeState"
        
class AvpE_InvalidMethod(AvpException):
    '''编码状态错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidMethod"
    
class AvpE_InvalidAvpDataType(AvpException):
    '''编码状态错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidAvpDataType"
    
class AvpE_InvalidInitParam(AvpException):
    '''错误的初始化参数'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidInitParam"
    
class AvpE_InvalidEtcParam(AvpException):
    '''配置文件错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidEtcParam"
    
class AvpE_InvalidAvpCode(AvpException):
    '''配置文件错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_InvalidAvpCode"
    
class AvpE_DecodAvpError(AvpException):
    '''解析数据错误'''
    def __init__(self, msg=None):
        AvpException.__init__(self, msg)
    def __name__(self):
        return "AvpE_DecodAvpError"
    