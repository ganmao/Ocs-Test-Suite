#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
用来解包及编码DCC的核心库

        |--------------------------------------|
 O ---->|DCC.__init__()---> CFG.__init__()     |
 |=     |      \/                              |
/\ ---->|MSG(instance) --encode/decode--> AVP1 |
        |              --encode/decode--> AVP2 |
   <----|              ...                     |
        |--------------------------------------|
        |       ERR            DEF             |
        |--------------------------------------|

1，初始化DCC引擎，以便配置信息初始化
2，实例化MSG类，调用相应的encode/decode函数
3，根据需要价码与编码的AVP_CODE，实例化相应的类
4，调用实例化类的encode/decode函数

编码过程:

            DCC
JSON--->|        |--->DCC::init
        |        |
        |        |--->AVP(Class)
        |        |--->DCC::get_config
        |        |--->AVP::pack_avp(method)
        |        |
        |        |--->MSG(Class)
        |        |--->DCC::get_config
        |        |--->MSG::pack_dmsg_body(method)
        |        |--->MSG::pack_dmsg_head(method)
BIN <---|        |

解码过程:
            DCC
BIN --->|        |--->DCC::init
        |        |
        |        |--->MSG(Class)
        |        |--->DCC::get_config
        |        |--->MSG::unpack_dmsg_head(method)
        |        |--->MSG::unpack_dmsg_body(method)
        |        |
        |        |--->AVP(Class)
        |        |--->DCC::get_config
        |        |--->AVP::unpack_avp(method)
JSON<---|        |

编码中返回码定义，请参见dcc_defined

使用方法:
    1，实例化D_ENGINE类
    2，调用DCC::encode/DCC::decode
    
DCC::encode(json_string) return bin_buf
DCC::decode(bin_buf) return json_string

MSG::set_debug    设置调试等级(是否打印解码过程)
MSG::set_check    设置校验等级(是否完全根据配置文件校验)

MSG::get_flags_proxiable()
MSG::get_flags_error()
MSG::get_flags_tpotentially()

MSG::set_flags_proxiable()
MSG::set_flags_error()
MSG::set_flags_tpotentially()

MSG::set_hop_by_hop()    -- 程序默认从配置文件中读取，编码后写回文件
MSG::set_end_by_end()    -- 设置时需要传入一个随机数，按照协议规定，4分钟内保持不重复，可以采用de中的函数获取

MSG::get_hop_by_hop()
MSG::get_end_by_end()

DCC的一些小工具
进制转换
时间戳转换
解码
第三方包的调用，配置文件，错误码，常量的调用均通过DCC
'''

# 库版本
__version__ = "0.2"

# 常量定义
import dcc_defined as DCC_DEF

# 错误定义
import dcc_error as DCC_ERR

# 配置信息
from dcc_config import DCC_CFG

# 驱动引擎
from dcc_engine import DCC

from avp_factory import create_avp

# 消息包函数接口
from msg import MSG

# AVP基类
from avp import AVP

def version():
    '打印模块版本'
    print "version = __version__"
    