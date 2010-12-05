#!/usr/bin/evn python
#-*- coding:utf-8 -*-
'''
Created on 2010-11-20

@author: zdl
'''
import unittest
import pprint
import binascii

import PyDccCore

class Test_Dcc(unittest.TestCase):
    '''测试Dcc模块,通用引擎函数与功能'''
    def setUp(self):
        '测试环境预处理'
        self.dcc = PyDccCore.DCC()
        
        self.json_str = '''[{"278": 456}, {"447": 8589934591}, {"2": "abcdefghi"}, {"437": [{"420": 180}, {"421": 200}]}]'''
        
        self.py_obj = []
        self.py_obj.append({u'278': 456})
        self.py_obj.append({u'447': 8589934591L})
        self.py_obj.append({u'2': u'abcdefghi'})
        self.py_obj.append({u'437': [{u'420': 180}, {u'421': 200}]})
        
    def tearDown(self):
        del self.dcc
        del self.json_str
        del self.py_obj
        
    def test_const_define(self):
        '测试定义的常量是否加载正确' 
        self.assertEqual(self.dcc.dcc_def.const.AVP_FLAG_VENDOR, 0x80)
        self.assertEqual(self.dcc.dcc_def.const.AVP_FLAG_MANDATORY, 0x40)
        self.assertEqual(self.dcc.dcc_def.const.AVP_FLAG_PRIVATE, 0x20)
        
    def test_error(self):
        '测试定义的错误类型'
        def raiseError_AvpE_InvalidCodeState():
            "测试编码状态错误函数"
            raise PyDccCore.DCC_ERR.AvpE_InvalidCodeState, \
                  "错误的编码状态"
        
        self.assertRaises(PyDccCore.DCC_ERR.AvpE_InvalidCodeState, 
                          raiseError_AvpE_InvalidCodeState)
        
    def test_func_loads_json(self):
        '测试函数:loads_json'
        self.assertEqual(self.dcc.loads_json(self.json_str), self.py_obj)
        
    def test_func_dumps_json(self):
        '测试函数:dumps_json'
        self.assertEqual(self.dcc.dumps_json(self.py_obj), self.json_str)
        
    def test_func_Time2TUCStamp(self):
        '测试函数:Time2TUCStamp'
        self.assertEqual(self.dcc.Time2TUCStamp('20101120204950'), 1290257390)
        
    def test_func_Time2NTPStamp(self):
        '测试函数:Time2NTPStamp'
        self.assertEqual(self.dcc.Time2NTPStamp('20101120204950'), 3499246190)
        
    def test_func_UTCStamp2Time(self):
        '测试函数:UTCStamp2Time'
        self.assertEqual(self.dcc.UTCStamp2Time(1290257390), '20101120204950')
        
    def test_func_NTPStamp2Time(self):
        '测试函数:NTPStamp2Time'
        self.assertEqual(self.dcc.NTPStamp2Time(3499246190), '20101120204950')
        
    def test_func_utf8encoder(self):
        '测试函数:utf8encoder'
        self.assertEqual(self.dcc.utf8encoder('张栋梁'), '\xe5\xbc\xa0\xe6\xa0\x8b\xe6\xa2\x81')
        
    def test_func_utf8decoder(self):
        '测试函数:utf8decoder'
        self.assertEqual(self.dcc.utf8decoder('\xe5\xbc\xa0\xe6\xa0\x8b\xe6\xa2\x81'), '张栋梁')

    def test_func_bin2ascii_hex(self):
        '测试函数:bin2ascii_hex'
        self.assertEqual(self.dcc.bin2ascii_hex('zhang.dongliang@zte.com.cn'), '7a68616e672e646f6e676c69616e67407a74652e636f6d2e636e')

    def test_func_ascii2bin_hex(self):
        '测试函数:ascii2bin_hex'
        self.assertEqual(self.dcc.ascii2bin_hex('7a68616e672e646f6e676c69616e67407a74652e636f6d2e636e'), 'zhang.dongliang@zte.com.cn')

    def test_func_pack_data2bin(self):
        '测试函数:pack_data2bin'
        self.assertEqual(self.dcc.bin2ascii_hex(self.dcc.pack_data2bin('!II', 99, 88)), '0000006300000058')
        
    def test_func_unpack_from_bin(self):
        '测试函数:unpack_from_bin'
        self.assertEqual(self.dcc.unpack_from_bin('!II',self.dcc.ascii2bin_hex('0000006300000058')), (99, 88))
        
    def test_calc_pack_size(self):
        '测试函数:calc_pack_size'
        self.assertEqual(self.dcc.calc_pack_size('!I'), 4)
        
    def test_func_catch_cmd_code(self):
        '测试函数:catch_cmd_code'
        self.assertEqual(self.dcc.catch_cmd_code('CCR'), (272, 1))
        
    def test_func_bin(self):
        '测试函数:bin'
        self.assertEqual(self.dcc.bin(1), '00000001')
        
class Test_Config(unittest.TestCase):
    '''测试配置信息读取与调用'''
    def setUp(self):
        '测试环境预处理'
        self.dcc = PyDccCore.DCC()
        
    def tearDown(self):
        del self.dcc
        
    def test_cfg_cmdcode(self):
        '测试加载配置文件：DccCmdCode.ini'
        self.assertEqual(self.dcc.dcc_cfg.Code2Cmd["TITLE"][0], 'CMD_CODE')
        
    def test_cfg_avpfile_ccr(self):
        '测试加载配置文件：avpfile-ccr.ini'
        self.assertEqual(self.dcc.dcc_cfg.CCR['1'][2], '1')
        
    def test_cfg_func_get_config(self):
        '测试函数:get_config'
        self.assertEqual(
            self.dcc.dcc_cfg.get_config(
                self.dcc.dcc_def.const.CREDIT_CONTROL_REQUEST,'1')[2],
            '1')
        
        self.assertEqual(
            self.dcc.dcc_cfg.get_config(self.dcc.dcc_def.const.CREDIT_CONTROL_REQUEST)['1'][2], 
            '1')
        
class Test_AVP(unittest.TestCase):
    '''测试AVP的编码与解包'''
    def setUp(self):
        '测试环境预处理'
        self.dcc = PyDccCore.DCC()
        self.test_avp = {}
    
    def test_avp_base(self):
        '测试AVP的基类与抛出异常'
        self.test_avp['AVP_CODE'] = '872'
        self.test_avp['AVP_DATA'] = 123
        
        self.assertRaises(
            self.dcc.dcc_err.AvpE_InvalidAvpCode,
            PyDccCore.create_avp,
            cmd_code = (272, 0),
            avp_code = self.test_avp['AVP_CODE'],
            avp_data = self.test_avp['AVP_DATA'],
            decode_buf = None,
            dcc_instance = self.dcc
            )
        
    def test_avp_Integer32(self):
        '测试Integer32类型 '
        self.test_avp['AVP_CODE'] = '429'
        self.test_avp['AVP_DATA'] = -123
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001AD0000000CFFFFFF85'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001AD0000000CFFFFFF85')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], -123)
        
    def test_avp_Integer64(self):
        '测试Integer64类型 '
        self.test_avp['AVP_CODE'] = '30114'
        self.test_avp['AVP_DATA'] = -1234567890
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000075A28000001400000F3EFFFFFFFFB669FD2E'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000075A28000001400000F3EFFFFFFFFB669FD2E')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], -1234567890)
        
    def test_avp_Unsigned32(self):
        '测试Unsigned32类型 '
        self.test_avp['AVP_CODE'] = '268'
        self.test_avp['AVP_DATA'] = 12345
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('0000010C0000000C00003039'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('0000010C0000000C00003039')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 12345)
        
    def test_avp_Unsigned64(self):
        '测试Unsigned64类型 '
        self.test_avp['AVP_CODE'] = '421'
        self.test_avp['AVP_DATA'] = 123456789999
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001A5000000100000001CBE991DEF'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001A5000000100000001CBE991DEF')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 123456789999)
        
    def test_avp_OctetString(self):
        '测试OctetString类型 '
        self.test_avp['AVP_CODE'] = '11'
        self.test_avp['AVP_DATA'] = 'zhang.dongliang'
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp(3)
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('0000000B000000177A68616E672E646F6E676C69616E6700'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('0000000B000000177A68616E672E646F6E676C69616E6700')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 'zhang.dongliang')
        
    def test_avp_Grouped(self):
        '测试Grouped类型 '
        self.test_avp['445'] =[]
        self.test_avp['445'].append({'447':200})
        self.test_avp['445'].append({'429':300})
        
        #pprint.pprint(self.test_avp)
        
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = '445',
                                        avp_data = self.test_avp['445'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001BD00000024000001BF0000001000000000000000C8000001AD0000000C0000012C'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001BD00000024000001BF0000001000000000000000C8000001AD0000000C0000012C')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], [{447: 200}, {429: 300}])
        
    def _test_avp_Float32(self):
        '测试Float32类型 '
        self.test_avp['AVP_CODE'] = '429'
        self.test_avp['AVP_DATA'] = 123
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001AD0000000C0000007B'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001AD0000000C0000007B')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 123)
        
    def _test_avp_Float64(self):
        '测试Float64类型 '
        self.test_avp['AVP_CODE'] = '429'
        self.test_avp['AVP_DATA'] = 123
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001AD0000000C0000007B'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001AD0000000C0000007B')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 0),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 123)
        
    def test_avp_Address(self):
        '测试Address类型 '
        self.test_avp['AVP_CODE'] = '1227'
        self.test_avp['AVP_DATA'] = '127.0.0.1'
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp(3)
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000004CB80000012000028AF00017F0000010000'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000004CB80000012000028AF00017F0000010000')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], '127.0.0.1')
        
    def test_avp_Time(self):
        '测试Time类型 '
        self.test_avp['AVP_CODE'] = '55'
        self.test_avp['AVP_DATA'] = '20101017215500'
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000000370000000CD0657EB4'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000000370000000CD0657EB4')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], '20101017215500')
        
    def test_avp_UTF8String(self):
        '测试UTF8String类型 '
        self.test_avp['AVP_CODE'] = '444'
        self.test_avp['AVP_DATA'] = '张栋梁'
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp(3)
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001BC00000011E5BCA0E6A08BE6A281000000'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001BC00000011E5BCA0E6A08BE6A281000000')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], '张栋梁')
        
    def test_avp_DiameterIdentity(self):
        '测试DiameterIdentity类型 '
        self.test_avp['AVP_CODE'] = '293'
        self.test_avp['AVP_DATA'] = 'www.zhangdl.com'
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp(3)
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('00000125000000177777772E7A68616E67646C2E636F6D00'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('00000125000000177777772E7A68616E67646C2E636F6D00')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 'www.zhangdl.com')
        
    def test_avp_Enumerated(self):
        '测试Enumerated类型 '
        self.test_avp['AVP_CODE'] = '416'
        self.test_avp['AVP_DATA'] = 1
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = self.test_avp['AVP_CODE'],
                                        avp_data = self.test_avp['AVP_DATA'],
                                        decode_buf = None,
                                        dcc_instance = self.dcc
                                        )
        self.avp.encode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp(3)
        self.assertEqual(self.avp.avp['AVP_BUF'], binascii.a2b_hex('000001A04000000C00000001'))
        
        self.test_avp['AVP_BUF'] = self.dcc.ascii2bin_hex('000001A04000000C00000001')
        self.avp = PyDccCore.create_avp(cmd_code = (272, 1),
                                        avp_code = None,
                                        avp_data = None,
                                        decode_buf = self.test_avp['AVP_BUF'],
                                        dcc_instance = self.dcc
                                        )
        self.avp.decode()
        
        #pprint.pprint(self.avp.avp)
        #self.avp.pavp()
        self.assertEqual(self.avp.avp['AVP_DATA'], 1)

class Test_MSG(unittest.TestCase):
    '测试消息的解包，打包'
    def setUp(self):
        '测试环境预处理'
        self.dcc = PyDccCore.DCC()
        self.msg = PyDccCore.MSG(self.dcc)
        
        self.avp_list = [{'263': 'SCP_008.zte.com.cn;3492837433;377231'}, {'264': 'SCP_008.zte.com.cn'}, {'296': 'cu.com'}, {'283': 'chinatelecom.com'}, {'258': 1}, {'461': 'data@cu.com'}, {'416': 1}, {'415': 0}, {'55': '20100907163714'}, {'443': [{'450': 0}, {'444': '8613256717239'}]}, {'443': [{'450': 1}, {'444': '8613256717239'}]}, {'456': [{'432': 0}, {'872': 1}, {'437': [{'413': [{'445': [{'447': 0}, {'429': 0}]}]}]}, {'1264': []}]}, {'873': [{'874': [{'2': '8613256717239'}, {'1228': '220.206.177.1'}]}]}]
        self.json_str = '[{"263": "SCP_008.zte.com.cn;3492837433;377231"}, {"264": "SCP_008.zte.com.cn"}, {"296": "cu.com"}, {"283": "chinatelecom.com"}, {"258": 1}, {"461": "data@cu.com"}, {"416": 1}, {"415": 0}, {"55": "20100907163714"}, {"443": [{"450": 0}, {"444": "8613256717239"}]}, {"443": [{"450": 1}, {"444": "8613256717239"}]}, {"456": [{"432": 0}, {"872": 1}, {"437": [{"413": [{"445": [{"447": 0}, {"429": 0}]}]}]}, {"1264": []}]}, {"873": [{"874": [{"2": "8613256717239"}, {"1228": "220.206.177.1"}]}]}]'
        self.buf = '010001cc80000110000000040005c1cd0005c1cd000001074000002c5343505f3030382e7a74652e636f6d2e636e3b333439323833373433333b333737323331000001084000001a5343505f3030382e7a74652e636f6d2e636e0000000001284000000e63752e636f6d00000000011b400000186368696e6174656c65636f6d2e636f6d000001024000000c00000001000001cd00000013646174614063752e636f6d00000001a00000000c000000010000019f0000000c00000000000000374000000cd030783a000001bb0000002c000001c20000000c00000000000001bc0000001538363133323536373137323339000000000001bb0000002c000001c20000000c00000001000001bc0000001538363133323536373137323339000000000001c800000064000001b00000000c000000000000036880000010000028af00000001000001b5000000340000019d0000002c000001bd00000024000001bf000000100000000000000000000001ad0000000c00000000000004f08000000c000028af0000036980000048000028af0000036a8000003c000028af0000000280000019000028af38363133323536373137323339000000000004cc80000012000028af0001dcceb1010000'
        
    def test_pack(self):
        '测试DCC消息编码'
        self.msg.pack((272, 1), self.avp_list, 123)
        #self.msg.pmsg(5)
        #print "pack_json_str=", self.msg
        #print "pack_buf_hex=", self.dcc.bin2ascii_hex(self.msg.dmsg['DCC_BUF'])
        
    def test_unpack(self):
        '测试DCC消息解码'
        self.msg.unpack(self.dcc.ascii2bin_hex(self.buf))
        #self.msg.pmsg(5)
        
        #print "pack_json_str=", self.msg
        
    def test_unpack_json(self):
        '测试unpack_json'
        json_str = self.msg.unpack_json(self.dcc.ascii2bin_hex(self.buf))
        #print "pack_json_str=", self.msg
        #print "json_str=", json_str
        #print self.msg.pmsg(99)
        
        
    def test_pack_json(self):
        '测试pack_json'
        self.msg.pack_json((272, 1), self.json_str, 123)
        #self.msg.pmsg(3)
        
        #print self.msg.fmt_hex(self.dcc.bin2ascii_hex(self.msg.dmsg['DCC_BUF']))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test']
    #unittest.main()
    
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Dcc)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#    
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Config)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#
#    suite = unittest.TestLoader().loadTestsFromTestCase(Test_AVP)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_MSG)
    unittest.TextTestRunner(verbosity=2).run(suite)
    