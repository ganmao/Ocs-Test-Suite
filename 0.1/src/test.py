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
import time

class Test_PyDccAvp(unittest.TestCase):
    '''测试Dcc模块'''
    def setUp(self):
        self.dcc_cfg = PyDccLib.DCF.DccConfig()
    
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
        #my_avp_packer.print_avp()
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
        avp_cfg = self.dcc_cfg.CCR
        my_avp_packer_grouped = PyDccLib.Grouped(456)
        
        my_avp_packer = PyDccLib.Integer32(278, 456)
        my_avp_packer_grouped.append(my_avp_packer)
        
        my_avp_packer = PyDccLib.Integer64(447, 8589934591, 4006, 1)
        my_avp_packer_grouped.append(my_avp_packer)
        
        my_avp_packer = PyDccLib.OctetString(2, "abcdefghi", 10415, 1)
        my_avp_packer_grouped.append(my_avp_packer)
        
        p_grouped = my_avp_packer_grouped.encode()
        #pprint.pprint(my_avp_packer_grouped.avp)
        #print binascii.b2a_hex(p_grouped)
        #my_avp_packer_grouped.pa()
        #my_avp_packer_grouped.print_avp()
        self.assertEqual(binascii.b2a_hex(p_grouped), 
                         '000001c800000040000001160000000c000001c8000001bfc000001400000fa600000001ffffffff00000002c0000018000028af616263646566676869000000')
        
        # 解包
        my_avp_unpacker_group = PyDccLib.Grouped(decode_buf=p_grouped, avp_config_instance=avp_cfg)
        my_avp_unpacker_group.decode()
        #pprint.pprint(my_avp_unpacker_group.avp)
        #my_avp_unpacker_group.print_avp()
        #my_avp_unpacker_group.pa()
        
class Test_PyDccLibCfg(unittest.TestCase):
    '''测试Dcc模块加载配置文件'''
    def test_cfg(self):
        '测试配置文件加载'
        cfg = PyDccLib.DCF.DccConfig()
        #pprint.pprint(cfg.Cmd2Code)
        #pprint.pprint(cfg.Code2Cmd)
        #pprint.pprint(cfg.CCA)
        #pprint.pprint(cfg.CCR)
        
class Test_DccMsg(unittest.TestCase):
    '''测试DCC消息 包
    [avp1={}, avp2={}, avp3={}, avp_group1=[sub_avp1={},subs_avp2={},...], avp4={},...]
    '''
    def setUp(self):
        self.dcc_cfg = PyDccLib.DCF.DccConfig()
        self.pack_buf = None
        self.msg = PyDccLib.DMSG(self.dcc_cfg)
        self.de = PyDccLib.DE()
        
    def _test_pack(self):
        '按照LIST传入数据'
        self.avp_list = []
        self.avp_list.append({'278':456})
        self.avp_list.append({'447':8589934591})
        self.avp_list.append({'2':"abcdefghi"})
        
        _dict = {}
        _dict['437']=[]
        _dict['437'].append({'420':180})
        _dict['437'].append({'421':200})
        
        self.avp_list.append(_dict)
        
        self.pack_buf = self.msg.pack("CCR", self.avp_list, 789)
        self.msg.print_dmsg()
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[:32], 
                         '010000688000011000000004075bcd16')
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[40:], 
                         '000001160000000c000001c8000001bf0000001000000001ffffffff0000000200000014616263646566676869000000000001a40000000c000000b4000001a50000001000000000000000c8000001b500000008')
        
    def test_pack_fromfile(self):
        '从文件读取需要pack的数据'
        fp = file("a.json", "r")
        line = fp.readline()
        fp.close()
        
        self.avp_list = self.de.loads_json(line)
        self.pack_buf = self.msg.pack("CCR", self.avp_list, 789)
        self.msg.print_dmsg()
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[:32], 
                         '010000688000011000000004075bcd16')
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[40:], 
                         '000001160000000c000001c8000001bf0000001000000001ffffffff0000000200000014616263646566676869000000000001a40000000c000000b4000001a50000001000000000000000c8000001b500000008')
        
        
class Test_Engine(unittest.TestCase):
    '从引擎开始测试DCC的使用'
    def test_e(self):
        '测试引擎初始化'
        de = PyDccLib.DE()
        #pprint.pprint(de.dcf.Cmd2Code)
        #pprint.pprint(de.dcf.Code2Cmd)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(Test_Engine)
    #unittest.TextTestRunner(verbosity=2).run(suite)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_DccMsg)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(Test_PyDccAvp)
    #unittest.TextTestRunner(verbosity=2).run(suite)
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(Test_PyDccLibCfg)
    #unittest.TextTestRunner(verbosity=2).run(suite)
