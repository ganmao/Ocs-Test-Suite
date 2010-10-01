#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-9-13

@author: zdl

TODO: 完善解包的测试用例
'''
import unittest
import PyDccLib
import binascii
import pprint
import struct

class Test_PyDccAvp(unittest.TestCase):
    '''测试Dcc模块'''
    def setUp(self):
        self.dcc_cfg = PyDccLib.DCF.DccConfig()
        self.cmd_cfg = self.dcc_cfg.CCR
    
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
        
        my_avp_unpacker = PyDccLib.Integer32(decode_buf=p, level=1)
        my_avp_unpacker.decode()
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], 456)
        
    def test_Integer64(self):
        '测试Integer64数据类型'
        my_avp_packer = PyDccLib.Integer64(123, 8589934591, 4006, 1)
        p = my_avp_packer.encode()
        #my_avp_packer.print_avp()
        self.assertEqual(binascii.b2a_hex(p), 
                         '0000007bc000001400000fa600000001ffffffff')
        #my_avp_packer.print_avp()
        self.assertEqual(repr(my_avp_packer), repr(8589934591))
        
        my_avp_unpacker = PyDccLib.Integer64(decode_buf=p, level=1)
        my_avp_unpacker.decode()
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], 8589934591)
        
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
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], "abcdefghi")
        
    def test_Grouped(self):
        '测试Grouped数据类型'
        my_avp_packer_grouped = PyDccLib.Grouped(456)
        
        my_avp_packer = PyDccLib.Integer32('278', 456)
        my_avp_packer_grouped.append(my_avp_packer)
        
        my_avp_packer = PyDccLib.Integer64('447', 8589934591, 4006, 1)
        my_avp_packer_grouped.append(my_avp_packer)
        
        my_avp_packer = PyDccLib.OctetString('2', "abcdefghi", 10415, 1)
        my_avp_packer_grouped.append(my_avp_packer)
        
        p_grouped = my_avp_packer_grouped.encode()
        #pprint.pprint(my_avp_packer_grouped.avp)
        #print binascii.b2a_hex(p_grouped)
        #my_avp_packer_grouped.sprint()
        #my_avp_packer_grouped.print_avp()
        self.assertEqual(binascii.b2a_hex(p_grouped), 
                         '000001c800000040000001160000000c000001c8000001bfc000001400000fa600000001ffffffff00000002c0000018000028af616263646566676869000000')
        
        # 解包
        my_avp_unpacker_group = PyDccLib.Grouped(decode_buf=p_grouped, cmd_etc_instance=self.cmd_cfg)
        my_avp_unpacker_group.decode()
        #pprint.pprint(my_avp_unpacker_group.avp)
        #my_avp_unpacker_group.print_avp()
        #my_avp_unpacker_group.sprint()
        
    def test_deep_Grouped(self):
        '测试多层嵌套的Grouped类型'
        my_avp_packer_grouped1 = PyDccLib.Grouped(456)
        
        my_avp_packer1 = PyDccLib.Integer32('278', 456)
        my_avp_packer_grouped1.append(my_avp_packer1)
        
        my_avp_packer1 = PyDccLib.Integer64('447', 8589934591, 4006, 1)
        my_avp_packer_grouped1.append(my_avp_packer1)
        
        my_avp_packer1 = PyDccLib.OctetString('2', "abcdefghi", 10415, 1)
        my_avp_packer_grouped1.append(my_avp_packer1)
        
        my_avp_packer_grouped2 = PyDccLib.Grouped(443)
        my_avp_packer_grouped2.append(my_avp_packer_grouped1)
        
        my_avp_packer1 = PyDccLib.Unsigned32('439', 200)
        my_avp_packer_grouped2.append(my_avp_packer1)
        
        my_avp_packer_grouped3 = PyDccLib.Grouped(413)
        my_avp_packer_grouped3.append(my_avp_packer_grouped2)
        p_grouped3 = my_avp_packer_grouped3.encode()
        
        #print binascii.b2a_hex(p_grouped3)
        self.assertEqual(binascii.b2a_hex(p_grouped3), 
                         '0000019d0000005c000001bb00000054000001c800000040000001160000000c000001c8000001bfc000001400000fa600000001ffffffff00000002c0000018000028af616263646566676869000000000001b70000000c000000c8')
        
        '''
00 00 01 9d --413
00 
00 00 5c 
    00 00 01 bb --443
    00 
    00 00 54 
        00 00 01 c8 --456
        00 
        00 00 40 
            00 00 01 16 --278
            00 
            00 00 0c 
            00 00 01 c8 
            00 00 01 bf --447
            c0 
            00 00 14 
            00 00 0f a6 
            00 00 00 01 ff ff ff ff 
            00 00 00 02 --2
            c0 
            00 00 18 
            00 00 28 af 
            61 62 63 64 65 66 67 68 69 00 00 00 
        00 00 01 b7 --439
        00 
        00 00 0c 
        00 00 00 c8 
        '''
        
        # 解包
        my_avp_unpacker_group = PyDccLib.Grouped(decode_buf=p_grouped3, cmd_etc_instance=self.cmd_cfg)
        my_avp_unpacker_group.decode()
        #pprint.pprint(my_avp_unpacker_group.avp['GROUPED_SUBS_AVP'])
        #my_avp_unpacker_group.print_avp()
        #my_avp_unpacker_group.sprint()
        #pprint.pprint(my_avp_unpacker_group.avp)
        
    def test_Address(self):
        '测试Address数据类型'
        my_avp_packer = PyDccLib.Address(1227, "127.0.0.1")
        p = my_avp_packer.encode()
        #print "test_Address=", binascii.b2a_hex(p)
        #my_avp_packer.print_avp()
        #my_avp_packer.sprint()
        self.assertEqual(binascii.b2a_hex(p), 
                         '000004cb0000001000017f0000010000')
        
        my_avp_unpacker = PyDccLib.Address(decode_buf=p, level=1)
        my_avp_unpacker.decode()
        #my_avp_unpacker.print_avp()
        #my_avp_unpacker.sprint()
        #print repr(my_avp_unpacker.avp)
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], "127.0.0.1")
        
    def test_Time(self):
        '测试Time数据类型'
        my_avp_packer = PyDccLib.Time(20386, "20101001000000")
        p = my_avp_packer.encode()
        #print "test_Address=", binascii.b2a_hex(p)
        #my_avp_packer.print_avp()
        #my_avp_packer.sprint()
        self.assertEqual(binascii.b2a_hex(p), 
                         '00004fa200000014333439343835313230302e30')
        
        my_avp_unpacker = PyDccLib.Time(decode_buf=p)
        my_avp_unpacker.decode()
        #my_avp_unpacker.print_avp()
        #my_avp_unpacker.sprint()
        #print repr(my_avp_unpacker.avp)
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], "20101001000000")
        
    def test_UTF8String(self):
        '测试UTF8String数据类型'
        my_avp_packer = PyDccLib.UTF8String(263, "zdl0812@163.com", 10415, 1)
        p = my_avp_packer.encode()
        #print "test_Address=", binascii.b2a_hex(p)
        #my_avp_packer.print_avp()
        #my_avp_packer.sprint()
        self.assertEqual(binascii.b2a_hex(p), 
                         '00000107c000001c000028af7a646c30383132403136332e636f6d00')
        
        my_avp_unpacker = PyDccLib.UTF8String(decode_buf=p)
        my_avp_unpacker.decode()
        #my_avp_unpacker.print_avp()
        #my_avp_unpacker.sprint()
        #print repr(my_avp_unpacker.avp)
        self.assertEqual(my_avp_unpacker.avp['AVP_DATA'], "zdl0812@163.com")
        
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
        self.de.InitConfig()
        self.pack_buf_hex = ""
        self.avp_list = []
        self.avp_list.append({'278':456})
        self.avp_list.append({'447':8589934591})
        self.avp_list.append({'2':"abcdefghi"})
        
        _dict = {}
        _dict['437']=[]
        _dict['437'].append({'420':180})
        _dict['437'].append({'421':200})
        
        self.avp_list.append(_dict)
        
    def test_unpack(self):
        '测试解包 DCC 消息'
        pb = binascii.a2b_hex("010000688000011000000004075bcd16d0a00315000001160000000c000001c8000001bf0000001000000001ffffffff0000000200000014616263646566676869000000000001b500000024000001a40000000c000000b4000001a50000001000000000000000c8")
        unp = self.msg.unpack(pb)
        #pprint.pprint(self.msg.dmsg['DCC_AVP_LIST'])
        #print repr(self.msg)
        #self.msg.print_dmsg()
        #pprint.pprint(unp)
        self.assertEqual(repr(self.msg),self.de.dumps_json(self.avp_list))
        
    def test_pack(self):
        '按照LIST传入数据,进行DCC消息编码'
        self.pack_buf = self.msg.pack("CCR", self.avp_list, 789)
        #print repr(self.msg)
        #self.msg.print_dmsg()
        #pprint.pprint(repr(self.msg))
        #print binascii.b2a_hex(self.pack_buf)
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[:32], 
                         '010000688000011000000004075bcd16')
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[40:], 
                         '000001160000000c000001c8000001bf0000001000000001ffffffff0000000200000014616263646566676869000000000001b500000024000001a40000000c000000b4000001a50000001000000000000000c8')
        
    def test_pack_fromfile(self):
        '从文件读取需要pack的数据'
        fp = file("a.json", "r")
        lines = fp.readlines()
        fp.close()
        
        self.avp_list = self.de.loads_json("".join(lines).replace('\n', ''))
        self.pack_buf = self.msg.pack("CCR", self.avp_list, 789)
        #self.msg.print_dmsg()
        self.pack_buf_hex = binascii.b2a_hex(self.pack_buf)
        #print self.pack_buf_hex
        #pprint.pprint(repr(self.msg))
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[:32], 
                         '010000688000011000000004075bcd16')
        self.assertEqual(binascii.b2a_hex(self.pack_buf)[40:], 
                         '000001160000000c000001c8000001bf0000001000000001ffffffff0000000200000014616263646566676869000000000001b500000024000001a40000000c000000b4000001a50000001000000000000000c8')
        
class Test_Engine(unittest.TestCase):
    '从引擎开始测试DCC的使用'
    def setUp(self):
        '初始化'
        self.de = PyDccLib.DE()
        self.de.InitConfig()
        self.avp_list = []
        self.avp_list.append({'278':456})
        self.avp_list.append({'447':8589934591})
        self.avp_list.append({'2':"abcdefghi"})
        
        _dict = {}
        _dict['437']=[]
        _dict['437'].append({'420':180})
        _dict['437'].append({'421':200})
        
        self.avp_list.append(_dict)
        
        self.json_str = '''[{"278": 456}, {"447": 8589934591}, {"2": "abcdefghi"}, {"437": [{"420": 180}, {"421": 200}]}]'''
    
    def test_loadini(self):
        '测试引擎初始化'
        #pprint.pprint(de.dcf.Cmd2Code)
        #pprint.pprint(de.dcf.Code2Cmd)
        
    def test_loads_json(self):
        '测试解析json字符串为python对象'
        json_obj = self.de.loads_json(self.json_str)
        #pprint.pprint(json_obj)
        self.assertEqual(json_obj, self.avp_list)
        
    def test_dumps_json(self):
        '测试将python对象转为json字符串'
        json_str = self.de.dumps_json(self.avp_list)
        #pprint.pprint(json_obj)
        self.assertEqual(json_str, self.json_str)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Engine)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#    
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_DccMsg)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#    
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_PyDccAvp)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#    
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_PyDccLibCfg)
#    unittest.TextTestRunner(verbosity=2).run(suite)
