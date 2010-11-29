# coding:utf-8
'''
Created on 2010-11-28

@author: zdl

调用dcc协议编码解码

从JSON文件中读取需要编码的内容
将编码后的信息输出到屏幕上

从文件读取需要解码的16进制数据
将解码后的内容写到屏幕上

Usage:
Call_PyDccCore [-e JSON_FILE|-d HEX_FILE] [-o OUT_FILE]

-e 需要编码的JSON文件
-d 需要解码的HEX文件
-o 输出文件，可选，不添加则输出到屏幕
'''

from getopt import getopt
from sys import argv
from random import randint
from binascii import a2b_hex, b2a_hex

import pprint

from PyDccCore import MSG, DCC

param = {}
json_str = None
hex_str = None

def pack_json(cmd_code, json_str, rand_num):
    '编码JSON数据'
    my_dcc = DCC()
    my_msg = MSG(my_dcc)
    
    my_msg.pack_json(cmd_code, json_str, rand_num)
    my_msg.pmsg(3)
    return b2a_hex(my_msg.dmsg['DCC_BUF'])
    
def unpack_hex(pack_buf):
    '解码HEX数据'
    my_dcc = DCC()
    my_msg = MSG(my_dcc)
    
    my_msg.unpack_json(pack_buf)
    #my_msg.pmsg()
    return my_msg.dmsg['DCC_JSON']
    
if __name__ == '__main__':
    opts, args = getopt(argv[1:], "e:d:o:")
    
    for (o, a) in opts:
        param[o] = a
    
    # 打开需要读取的文件
    if '-e' in param:
        encode_file = open(param['-e'], 'r')
        json_str = encode_file.readline()
        encode_file.close()
        
        out_buf = pack_json((272, 1), json_str, randint(0, 2097151))
        print out_buf
        
    elif '-d' in param:
        encode_file = open(param['-d'], 'r')
        hex_str = encode_file.readline()
        encode_file.close()
        
        out_json = unpack_hex(a2b_hex(hex_str))
        
        print out_json
    else:
        print 'plase use param: -e or -d!'
        
    
        