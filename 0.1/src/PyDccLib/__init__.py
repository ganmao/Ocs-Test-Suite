#!/usr/bin/evn python
#-*- coding:utf-8 -*-
__doc__ = '''
用来解包及编码DCC的库

使用说明：
～～～～～～～～～～～～～～～～～～～～～～～～～
AVP初始化参数说明：
===============================================
    avp_code            AVP编码（编码时必传）
    avp_data            AVP数据（编码时必传）
    vendor_id
    mandatory 
    private 
    level               AVP等级，主要在打印时用到
    decode_buf          需要解包的AVP二进制数据(解码时必填)
    
    如果decode_buf被赋值，则认为是需要进行解码，否则认为需要进行编码
    
    编码：
    avp_packer = PyDccLib.Integer32(avp_code, avp_data)
    解码：
    avp_unpacker = PyDccLib.Integer32(decode_buf=BUF)
    
    
其他方法说明：
    print_avp()    打印详细的解码或者编码后结果
    pa()            打印简单的解码或编码后结果
===============================================
'''

# TODO: 增加模块管理引擎，进行管理
# TODO: 实现具体的消息包编码与解包
# TODO: 实现其他扩展的数据类型

__version__ = "0.1"

import avp_const_define as ACD
import avp_error as D_ERROR
import dcc_config as DCF

from dcc_engine import DiameterEngine as DE

# AVP基类
from avp import AVP

# AVP的基本数据类型
from avp_integer32 import Integer32
from avp_integer64 import Integer64
from avp_unsigned32 import Unsigned32
from avp_unsigned64 import Unsigned64
from avp_octetstring import OctetString
from avp_float32 import Float32
from avp_float64 import Float64
from avp_grouped import Grouped

# AVP的扩展数据类型

def version():
    '打印模块版本'
    print "version = __version__"
    