#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
用来解包及编码DCC的库
'''

# TODO: 完善文档
# TODO: 对使用到的函数，注释，格式等，按照PyLint的标准进行完善
# TODO: 添加时间转换，字符转换的小工具

__version__ = "0.1"

import avp_const_define as ACD
import avp_error as D_ERROR
import dcc_config as DCF

from dcc_engine import DiameterEngine as DE
from dcc_msg import DMSG

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
from avp_address import Address
from avp_time import Time
from avp_utf8string import UTF8String
from avp_diameteridentity import DiameterIdentity
from avp_enumerated import Enumerated

# AVP的扩展数据类型

def version():
    '打印模块版本'
    print "version = __version__"
    