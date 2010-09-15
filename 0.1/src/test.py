#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl
'''
import unittest
import PyDccLib
import binascii
import pprint

class Test_PyDccLib(unittest.TestCase):
    '''测试Dcc模块'''
    def test_const_define(self):
        '测试定义的常量'
        self.assertEqual(PyDccLib.ACD.const.AVP_FLAG_VENDOR, 0x80)
        self.assertEqual(PyDccLib.ACD.const.AVP_FLAG_MANDATORY, 0x40)
        self.assertEqual(PyDccLib.ACD.const.AVP_FLAG_PRIVATE, 0x20)
        
    def test_error(self):
        '测试定义的错误类型'
        def raiseError_AvpE_InvalidCodeState():
            "测试编码状态错误函数"
            raise PyDccLib.D_ERROR.AvpE_InvalidCodeState, \
                  "错误的编码状态"
        
        self.assertRaises(PyDccLib.D_ERROR.AvpE_InvalidCodeState, 
                          raiseError_AvpE_InvalidCodeState)
        
    def test_avp(self):
        '测试AVP基类的默认数据类型 int'
        
        # 编码，并且输出
        my_avp_packer = PyDccLib.AVP(123, 456, 4006, 1)
        p = my_avp_packer.encode()
        self.assertEqual(binascii.b2a_hex(p), 
                         '0000007bc000001000000fa6000001c8')
        
        # 解码，并且比对
        my_avp_unpacker = PyDccLib.AVP(decode_buf=p, level=1)
        my_avp_unpacker.decode()
        #my_avp_unpacker.print_avp()
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], 456)
        
    def test_Integer32(self):
        '测试Integer32数据类型'
        my_avp_packer = PyDccLib.Integer32(123, 456, 1, 1)
        p = my_avp_packer.encode()
        self.assertEqual(binascii.b2a_hex(p), 
                         '0000007bc000001000000001000001c8')
        
    def test_Integer64(self):
        '测试Integer64数据类型'
        my_avp_packer = PyDccLib.Integer64(123, 8589934591, 4006, 1)
        p = my_avp_packer.encode()
        self.assertEqual(binascii.b2a_hex(p), 
                         '0000007bc000001400000fa600000001ffffffff')
        #my_avp_packer.print_avp()
        self.assertEqual(repr(my_avp_packer), repr(8589934591))
        
    def test_OctetString(self):
        '测试OctetString数据类型'
        my_avp_packer = PyDccLib.OctetString(234, "abcdefghi", 4006, 1)
        p = my_avp_packer.encode()
        #print "test_OctetString=", binascii.b2a_hex(p)
        #my_avp_packer.print_avp()
        self.assertEqual(binascii.b2a_hex(p), 
                         '000000eac000001800000fa6616263646566676869000000')
        
        my_avp_unpacker = PyDccLib.OctetString(decode_buf=p, level=1)
        my_avp_unpacker.decode()
        #my_avp_unpacker.print_avp()
        #print repr(my_avp_unpacker.avp)
        
    def test_Grouped(self):
        '测试Grouped数据类型'
        my_avp_packer_grouped = PyDccLib.Grouped(456)
        
        my_avp_packer = PyDccLib.Integer32(123, 456, 1, 1)
        p = my_avp_packer.encode()
        my_avp_packer_grouped.append(p)
        
        my_avp_packer = PyDccLib.Integer64(321, 8589934591, 4006, 1)
        p = my_avp_packer.encode()
        my_avp_packer_grouped.append(p)
        
        my_avp_packer = PyDccLib.OctetString(234, "abcdefghi", 4006, 1)
        p = my_avp_packer.encode()
        my_avp_packer_grouped.append(p)
        
        p_grouped = my_avp_packer_grouped.encode()
        #print binascii.b2a_hex(p_grouped)
        self.assertEqual(binascii.b2a_hex(p_grouped), 
                         '000001c8000000440000007bc000001000000001000001c800000141c000001400000fa600000001ffffffff000000eac000001800000fa6616263646566676869000000')
        
        # 解包
        my_avp_unpacker_group = PyDccLib.Grouped(decode_buf=p_grouped)
        my_avp_unpacker_group.decode()
        #pprint.pprint(my_avp_unpacker_group.avp)
        #my_avp_unpacker_group.print_avp()
        my_avp_unpacker_group.pa()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(Test_PyDccLib)
    #unittest.TextTestRunner(verbosity=2).run(suite)
