#coding:utf-8
import wx
from wx.lib.anchors import LayoutAnchors
import wx.gizmos

from PyDccCore import MSG, DCC
from random import randint
from binascii import a2b_hex, b2a_hex

def create(parent):
    return mainFrame(parent)

[wxID_MAINFRAME, wxID_MAINFRAMEBNT_UNPACK, wxID_MAINFRAMEBTN_ASCII2BIN, 
 wxID_MAINFRAMEBTN_BIN2ASCII, wxID_MAINFRAMEBTN_CLEAR, 
 wxID_MAINFRAMEBTN_NTP2TIME, wxID_MAINFRAMEBTN_TIME2NTP, 
 wxID_MAINFRAMEBTN_UTF8DECODER, wxID_MAINFRAMEBTN_UTF8ENCODER, 
 wxID_MAINFRAMECHECKBOX_DEBUG, wxID_MAINFRAMED_PANEL, 
 wxID_MAINFRAMED_TREELISTCTRL, wxID_MAINFRAMEM_CHOICE, wxID_MAINFRAMEM_PANEL, 
 wxID_MAINFRAMENOTEBOOK, wxID_MAINFRAMETEXTCTRL, 
] = [wx.NewId() for _init_ctrls in range(16)]

class mainFrame(wx.Frame):
    def _init_coll_D_boxSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.D_treeListCtrl, 1, border=0, flag=wx.EXPAND)

    def _init_coll_M_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.textCtrl, 11, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.M_boxSizer2, 2, border=0, flag=0)

    def _init_coll_M_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.M_choice, 0, border=0, flag=0)
        parent.AddWindow(self.bnt_unpack, 0, border=0, flag=0)
        parent.AddWindow(self.btn_NTP2Time, 0, border=0, flag=0)
        parent.AddWindow(self.btn_Time2NTP, 0, border=0, flag=0)
        parent.AddWindow(self.btn_Ascii2Bin, 0, border=0, flag=0)
        parent.AddWindow(self.btn_Bin2Ascii, 0, border=0, flag=0)
        parent.AddWindow(self.btn_utf8decoder, 0, border=0, flag=0)
        parent.AddWindow(self.btn_utf8encoder, 0, border=0, flag=0)
        parent.AddWindow(self.checkbox_debug, 0, border=0,
              flag=wx.ALIGN_BOTTOM | wx.BOTTOM)
        parent.AddWindow(self.btn_clear, 0, border=0, flag=0)

    def _init_coll_notebook_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.M_panel, select=True,
              text='MixTools')
        parent.AddPage(imageId=-1, page=self.D_panel, select=False,
              text='Detail Info')

    def _init_coll_D_treeListCtrl_Columns(self, parent):
        # generated method, don't edit

        parent.AddColumn(text=u'Diameter Message Tree')
        parent.AddColumn(text=u'Detail')
        parent.AddColumn(text=u'Detail(HEX)')

    def _init_sizers(self):
        # generated method, don't edit
        self.M_boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.M_boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)

        self.D_boxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_M_boxSizer1_Items(self.M_boxSizer1)
        self._init_coll_M_boxSizer2_Items(self.M_boxSizer2)
        self._init_coll_D_boxSizer_Items(self.D_boxSizer)

        self.D_panel.SetSizer(self.D_boxSizer)
        self.M_panel.SetSizer(self.M_boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_MAINFRAME, name='mainFrame',
              parent=prnt, pos=wx.Point(566, 263), size=wx.Size(640, 480),
              style=wx.DEFAULT_FRAME_STYLE,
              title='Diameter Message HEX Translate Tools - 0027001941')
        self.SetClientSize(wx.Size(624, 442))
        self.SetToolTipString('Diameter Message HEX Translate Tools - 0027001941')

        self.notebook = wx.Notebook(id=wxID_MAINFRAMENOTEBOOK, name='notebook',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(624, 442), style=0)
        self.notebook.SetToolTipString('')
        self.notebook.Show(True)

        self.M_panel = wx.Panel(id=wxID_MAINFRAMEM_PANEL, name='M_panel',
              parent=self.notebook, pos=wx.Point(0, 0), size=wx.Size(616, 415),
              style=wx.TAB_TRAVERSAL)

        self.textCtrl = wx.TextCtrl(id=wxID_MAINFRAMETEXTCTRL, name='textCtrl',
              parent=self.M_panel, pos=wx.Point(0, 0), size=wx.Size(521, 415),
              style=wx.TE_MULTILINE | wx.ALWAYS_SHOW_SB | wx.CAPTION | wx.VSCROLL | wx.HSCROLL | wx.TR_MULTIPLE,
              value='')
        self.textCtrl.SetToolTipString('Please Input your data for translate')
        self.textCtrl.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL, False,
              'Courier New'))

        self.bnt_unpack = wx.Button(id=wxID_MAINFRAMEBNT_UNPACK,
              label='UNPACK HEX', name='bnt_unpack', parent=self.M_panel,
              pos=wx.Point(521, 25), size=wx.Size(87, 24), style=0)
        self.bnt_unpack.Bind(wx.EVT_BUTTON, self.OnBnt_unpackButton,
              id=wxID_MAINFRAMEBNT_UNPACK)
        self.bnt_unpack.SetToolTipString(u'UnPack String (HEX)')

        self.D_panel = wx.Panel(id=wxID_MAINFRAMED_PANEL, name='D_panel',
              parent=self.notebook, pos=wx.Point(0, 0), size=wx.Size(616, 415),
              style=wx.TAB_TRAVERSAL)

        self.D_treeListCtrl = wx.gizmos.TreeListCtrl(id=wxID_MAINFRAMED_TREELISTCTRL,
              name='D_treeListCtrl', parent=self.D_panel, pos=wx.Point(0, 0),
              size=wx.Size(616, 415),
              style=wx.TR_MULTIPLE | wx.HSCROLL | wx.VSCROLL | wx.TR_EXTENDED |
                    wx.TR_TWIST_BUTTONS | wx.TR_ROW_LINES | wx.TR_COLUMN_LINES | wx.TR_HIDE_ROOT |
                    wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_EDIT_LABELS | wx.TR_HAS_VARIABLE_ROW_HEIGHT )
        self.D_treeListCtrl.SetLineSpacing(8)
        self.D_treeListCtrl.SetToolTipString('Detail Diameter Message Info')
        self._init_coll_D_treeListCtrl_Columns(self.D_treeListCtrl)
        self.D_treeListCtrl.SetMainColumn(0)
        self.D_treeListCtrl.SetColumnWidth(0, 175)
        self.D_treeListCtrl.SetColumnWidth(1, 150)
        self.D_treeListCtrl.SetColumnWidth(2, 300)
        self.D_treeListCtrl_Root = self.D_treeListCtrl.AddRoot(u"Diameter Message Translation")
        self.D_treeListCtrl.SetItemTextColour(self.D_treeListCtrl_Root, wx.BLUE)
        #self.D_treeListCtrl.SetItemText(self.D_treeListCtrl_Root, "CCE", 1)
        #self.D_treeListCtrl.SetItemText(self.D_treeListCtrl_Root, "col 2 root", 2)
        self.D_treeListCtrl.ExpandAll(self.D_treeListCtrl_Root)

        self.btn_clear = wx.Button(id=wxID_MAINFRAMEBTN_CLEAR,
              label='CLEAR TEXT', name='btn_clear', parent=self.M_panel,
              pos=wx.Point(521, 207), size=wx.Size(87, 24), style=0)
        self.btn_clear.SetBackgroundColour(wx.Colour(0, 128, 255))
        self.btn_clear.SetBackgroundStyle(wx.BG_STYLE_COLOUR)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.OnBtn_clearButton,
              id=wxID_MAINFRAMEBTN_CLEAR)
        self.btn_clear.SetToolTipString(u'Clear Text')

        self.btn_NTP2Time = wx.Button(id=wxID_MAINFRAMEBTN_NTP2TIME,
              label='NTP2Time', name='btn_NTP2Time', parent=self.M_panel,
              pos=wx.Point(521, 49), size=wx.Size(87, 24), style=0)
        self.btn_NTP2Time.Bind(wx.EVT_BUTTON, self.OnBtn_NTP2TimeButton,
              id=wxID_MAINFRAMEBTN_NTP2TIME)
        self.btn_NTP2Time.SetToolTipString(u'Change Ntp Stamp To Time String (YYYYMMDDHH24MISS)')

        self.btn_Time2NTP = wx.Button(id=wxID_MAINFRAMEBTN_TIME2NTP,
              label='Time2NTP', name='btn_Time2NTP', parent=self.M_panel,
              pos=wx.Point(521, 73), size=wx.Size(87, 24), style=0)
        self.btn_Time2NTP.Bind(wx.EVT_BUTTON, self.OnBtn_Time2NTPButton,
              id=wxID_MAINFRAMEBTN_TIME2NTP)
        self.btn_Time2NTP.SetToolTipString(u'Change Time String (YYYYMMDDHH24MISS) To Ntp Stamp')

        self.btn_Ascii2Bin = wx.Button(id=wxID_MAINFRAMEBTN_ASCII2BIN,
              label='Ascii2Bin', name='btn_Ascii2Bin', parent=self.M_panel,
              pos=wx.Point(521, 97), size=wx.Size(87, 24), style=0)
        self.btn_Ascii2Bin.Bind(wx.EVT_BUTTON, self.OnBtn_Ascii2BinButton,
              id=wxID_MAINFRAMEBTN_ASCII2BIN)
        self.btn_Ascii2Bin.SetToolTipString(u'Change Ascii To Bin (HEX)')

        self.btn_Bin2Ascii = wx.Button(id=wxID_MAINFRAMEBTN_BIN2ASCII,
              label='Bin2Ascii', name='btn_Bin2Ascii', parent=self.M_panel,
              pos=wx.Point(521, 121), size=wx.Size(87, 24), style=0)
        self.btn_Bin2Ascii.Bind(wx.EVT_BUTTON, self.OnBtn_Bin2AsciiButton,
              id=wxID_MAINFRAMEBTN_BIN2ASCII)
        self.btn_Bin2Ascii.SetToolTipString(u'Change Bin (HEX) To Ascii')

        self.btn_utf8decoder = wx.Button(id=wxID_MAINFRAMEBTN_UTF8DECODER,
              label='utf8decoder', name='btn_utf8decoder', parent=self.M_panel,
              pos=wx.Point(521, 145), size=wx.Size(87, 24), style=0)
        self.btn_utf8decoder.Bind(wx.EVT_BUTTON, self.OnBtn_utf8decoderButton,
              id=wxID_MAINFRAMEBTN_UTF8DECODER)
        self.btn_utf8decoder.SetToolTipString(u'Change UTF-8 To Unicode')

        self.btn_utf8encoder = wx.Button(id=wxID_MAINFRAMEBTN_UTF8ENCODER,
              label='utf8encoder', name='btn_utf8encoder', parent=self.M_panel,
              pos=wx.Point(521, 169), size=wx.Size(87, 24), style=0)
        self.btn_utf8encoder.Bind(wx.EVT_BUTTON, self.OnBtn_utf8encoderButton,
              id=wxID_MAINFRAMEBTN_UTF8ENCODER)
        self.btn_utf8encoder.SetToolTipString(u'Change Unicode To UTF-8')

        self.checkbox_debug = wx.CheckBox(id=wxID_MAINFRAMECHECKBOX_DEBUG,
              label='DEBUG', name='checkbox_debug', parent=self.M_panel,
              pos=wx.Point(521, 193), size=wx.Size(87, 14), style=0)
        self.checkbox_debug.SetToolTipString(u'Is Use Debug Module')
        self.checkbox_debug.SetValue(False)

        self.M_choice = wx.Choice(choices=["P=>CCR", "P=>CCA",
              "P=>DPR", "P=>DPA", "P=>DWR", "P=>DWA", "P=>CER",
              "P=>CEA", "P=>ASR", "P=>ASA", "P=>RAR", "P=>RAA"],
              id=wxID_MAINFRAMEM_CHOICE, name='M_choice', parent=self.M_panel,
              pos=wx.Point(521, 0), size=wx.Size(87, 25),
              style=wx.DEFAULT_FRAME_STYLE)
        self.M_choice.SetBackgroundColour(wx.Colour(255, 255, 193))
        self.M_choice.SetToolTipString('Select DCC Type For pack')
        self.M_choice.SetHelpText('')
        self.M_choice.SetLabel('PACK TYPE')
        self.M_choice.SetAutoLayout(True)
        self.M_choice.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL, False,
              'Courier New'))
        self.M_choice.Bind(wx.EVT_CHOICE, self.OnM_choiceChoice,
              id=wxID_MAINFRAMEM_CHOICE)

        self._init_coll_notebook_Pages(self.notebook)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnM_choiceChoice(self, event):
        
        _select = self.change_choice2CmdCode(self.M_choice.GetCurrentSelection())
        
        if self.checkbox_debug.GetValue():
            json_str = self.textCtrl.GetValue()
            json_str = json_str.replace('\n', "")
            json_str = json_str.replace('\r', "")
            json_str = json_str.replace('},', "},\n")
            self.textCtrl.Clear()
            self.textCtrl.WriteText(json_str)
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(self.pack_json(_select, json_str))
            self.create_msg_tree(self.msg)
        else:
            try:
                #wx.MessageBox(u"开始将JSON数据编码为DCC消息", u"执行提示！", wx.OK|wx.ICON_QUESTION)
                json_str = self.textCtrl.GetValue()
                json_str = json_str.replace('\n', "")
                json_str = json_str.replace('\r', "")
                json_str = json_str.replace('},', "},\n")
                self.textCtrl.Clear()
                self.textCtrl.WriteText(json_str)
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(self.pack_json(_select, json_str))
                
                self.create_msg_tree(self.msg)
                
            except Exception, e:
                wx.MessageBox(u"错误！\n[%s]" % e, u"执行提示！", wx.OK|wx.ICON_ERROR) 
            
        event.Skip()
        
    def OnBtn_clearButton(self, event):
        self.textCtrl.Clear()
        event.Skip()
        
    def OnBnt_unpackButton(self, event):
        if self.checkbox_debug.GetValue():
            HEX_str = self.textCtrl.GetValue()
            HEX_str = HEX_str.replace('\n', "")
            HEX_str = HEX_str.replace('\r', "")
            HEX_str = HEX_str.replace(' ', "")
            self.textCtrl.Clear()
            self.textCtrl.WriteText(self.fmt_hex(HEX_str))
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(self.unpack_hex(HEX_str).replace('},', "},\n"))
            self.create_msg_tree(self.msg)
        else:
            try:
                #wx.MessageBox(u"开始将JSON数据编码为DCC消息", u"执行提示！", wx.OK|wx.ICON_QUESTION)
                HEX_str = self.textCtrl.GetValue()
                HEX_str = HEX_str.replace('\n', "")
                HEX_str = HEX_str.replace('\r', "")
                HEX_str = HEX_str.replace(' ', "")
                self.textCtrl.Clear()
                self.textCtrl.WriteText(self.fmt_hex(HEX_str))
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(self.unpack_hex(HEX_str).replace('},', "},\n"))
                
                self.create_msg_tree(self.msg)
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
                
        event.Skip()
        
    def OnBtn_NTP2TimeButton(self, event):
        if self.checkbox_debug.GetValue():
            _NTPStamp = self.textCtrl.GetValue()
            my_dcc = DCC()
            self.textCtrl.Clear()
            self.textCtrl.WriteText(_NTPStamp)
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(repr(my_dcc.NTPStamp2Time(float(_NTPStamp))))
        else:
            try:
                _NTPStamp = self.textCtrl.GetValue()
                my_dcc = DCC()
                self.textCtrl.Clear()
                self.textCtrl.WriteText(_NTPStamp)
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(repr(my_dcc.NTPStamp2Time(float(_NTPStamp))))
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
        event.Skip()

    def OnBtn_Time2NTPButton(self, event):
        if self.checkbox_debug.GetValue():
            _time_str = self.textCtrl.GetValue()
            my_dcc = DCC()
            self.textCtrl.Clear()
            self.textCtrl.WriteText(str(_time_str))
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(repr(my_dcc.Time2NTPStamp(_time_str)))
        else:
            try:
                _time_str = self.textCtrl.GetValue()
                my_dcc = DCC()
                self.textCtrl.Clear()
                self.textCtrl.WriteText(str(_time_str))
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(repr(my_dcc.Time2NTPStamp(_time_str)))
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
        event.Skip()

    def OnBtn_Ascii2BinButton(self, event):
        if self.checkbox_debug.GetValue():
            _ascii = self.textCtrl.GetValue()
            my_dcc = DCC()
            self.textCtrl.Clear()
            self.textCtrl.WriteText(_ascii)
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(repr(my_dcc.ascii2bin_hex(_ascii)))
        else:
            try:
                _ascii = self.textCtrl.GetValue()
                my_dcc = DCC()
                self.textCtrl.Clear()
                self.textCtrl.WriteText(_ascii)
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(repr(my_dcc.ascii2bin_hex(_ascii)))
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
        event.Skip()

    def OnBtn_Bin2AsciiButton(self, event):
        if self.checkbox_debug.GetValue():
            _bin = self.textCtrl.GetValue()
            my_dcc = DCC()
            self.textCtrl.Clear()
            self.textCtrl.WriteText(_bin)
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(repr(my_dcc.bin2ascii_hex(_bin)))
        else:
            try:
                _bin = self.textCtrl.GetValue()
                my_dcc = DCC()
                self.textCtrl.Clear()
                self.textCtrl.WriteText(_bin)
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(repr(my_dcc.bin2ascii_hex(_bin)))
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
                
        event.Skip()

    def OnBtn_utf8decoderButton(self, event):
        if self.checkbox_debug.GetValue():
            _utf8str = self.textCtrl.GetValue()
            my_dcc = DCC()
            self.textCtrl.Clear()
            self.textCtrl.WriteText(_utf8str)
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(repr(my_dcc.utf8decoder(_utf8str)))
        else:
            try:
                _utf8str = self.textCtrl.GetValue()
                my_dcc = DCC()
                self.textCtrl.Clear()
                self.textCtrl.WriteText(_utf8str)
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(repr(my_dcc.utf8decoder(_utf8str)))
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
                
        event.Skip()

    def OnBtn_utf8encoderButton(self, event):
        if self.checkbox_debug.GetValue():
            _unicode = self.textCtrl.GetValue()
            my_dcc = DCC()
            self.textCtrl.Clear()
            self.textCtrl.WriteText(_unicode)
            self.textCtrl.WriteText("\n==============================\n")
            self.textCtrl.WriteText(repr(my_dcc.utf8encoder(_unicode)))
        else:
            try:
                _unicode = self.textCtrl.GetValue()
                my_dcc = DCC()
                self.textCtrl.Clear()
                self.textCtrl.WriteText(_unicode)
                self.textCtrl.WriteText("\n==============================\n")
                self.textCtrl.WriteText(repr(my_dcc.utf8encoder(_unicode)))
            except Exception, e:
                wx.MessageBox(u"错误！\n%s" % e, u"执行提示！", wx.OK|wx.ICON_ERROR)
                
        event.Skip()
        
    #===================================================================
    #   业务数据处理函数
    #===================================================================
    def create_msg_tree(self, my_msg):
        '创建MSG的展示树'
        
        # 创建每个消息的根节点
        _message = self.D_treeListCtrl.AppendItem(self.D_treeListCtrl_Root, u"Dcc Message")
        self.D_treeListCtrl.SetItemText(_message, str(my_msg.dmsg['DCC_NAME']), 1)
        self.D_treeListCtrl.SetItemText(_message, "0x"+b2a_hex(my_msg.dmsg['DCC_BUF']), 2)
        
        # 创建MSG头信息节点
        _dcc_version = self.D_treeListCtrl.AppendItem(_message, u"Version")
        self.D_treeListCtrl.SetItemText(_dcc_version, str(my_msg.dmsg['DCC_VERSION']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_version, u"0x%02X" % my_msg.dmsg['DCC_VERSION'], 2)
        
        _dcc_length = self.D_treeListCtrl.AppendItem(_message, u"Message Length")
        self.D_treeListCtrl.SetItemText(_dcc_length, str(my_msg.dmsg['DCC_LENGTH']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_length, u"0x%06X" % my_msg.dmsg['DCC_LENGTH'], 2)
        
        _dcc_flags = self.D_treeListCtrl.AppendItem(_message, u"command flags")
        self.D_treeListCtrl.SetItemText(_dcc_flags, str(my_msg.dmsg['DCC_FLAGS']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_flags, u"0x%02X" % my_msg.dmsg['DCC_FLAGS'], 2)
        
        _dcc_code = self.D_treeListCtrl.AppendItem(_message, u"Command-Code")
        self.D_treeListCtrl.SetItemText(_dcc_code, str(my_msg.dmsg['DCC_CODE']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_code, u"0x%06X" % my_msg.dmsg['DCC_CODE'], 2)
        
        _dcc_app_id = self.D_treeListCtrl.AppendItem(_message, u"Application-ID")
        self.D_treeListCtrl.SetItemText(_dcc_app_id, str(my_msg.dmsg['DCC_APP_ID']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_app_id, u"0x%08X" % my_msg.dmsg['DCC_APP_ID'], 2)
        
        _dcc_hopbyhop = self.D_treeListCtrl.AppendItem(_message, u"Hop-by-Hop Identifier")
        self.D_treeListCtrl.SetItemText(_dcc_hopbyhop, str(my_msg.dmsg['DCC_HOPBYHOP']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_hopbyhop, u"0x%08X" % my_msg.dmsg['DCC_HOPBYHOP'], 2)
        
        _dcc_endtoend = self.D_treeListCtrl.AppendItem(_message, u"End-to-End Identifier")
        self.D_treeListCtrl.SetItemText(_dcc_endtoend, str(my_msg.dmsg['DCC_ENDTOEND']), 1)
        self.D_treeListCtrl.SetItemText(_dcc_endtoend, u"0x%08X" % my_msg.dmsg['DCC_ENDTOEND'], 2)
        
        # 创建消息体avp树
        for _avp in my_msg.dmsg['DCC_AVP_LIST']:
            self.create_avp_tree(_message, _avp)
            
    def create_avp_tree(self,parent_tree, avp):
        _has_err = False
        
        _avp_tree_root = self.D_treeListCtrl.AppendItem(parent_tree, u"AVP - " + str(avp.avp['AVP_CODE']))
        self.D_treeListCtrl.SetItemText(_avp_tree_root, avp.avp['AVP_NAME'], 1)
        self.D_treeListCtrl.SetItemText(_avp_tree_root, repr(avp.avp['AVP_DATA']), 2)
        
        _avp_code = self.D_treeListCtrl.AppendItem(_avp_tree_root, u"AVP Code")
        self.D_treeListCtrl.SetItemText(_avp_code, str(avp.avp['AVP_CODE']), 1)
        self.D_treeListCtrl.SetItemText(_avp_code, u"0x%08X" % avp.avp['AVP_CODE'], 2)
        
        avp_flag_bin = avp.dcc.bin(avp.avp['AVP_FLAG'])
        _avp_flags = self.D_treeListCtrl.AppendItem(_avp_tree_root, u"AVP Flags")
        self.D_treeListCtrl.SetItemText(_avp_flags, str(avp.avp['AVP_FLAG']), 1)
        self.D_treeListCtrl.SetItemText(_avp_flags, "0b"+avp_flag_bin, 2)
        
        # 对FLAG进行校验，如果不符合则设置背景色为黄色，并且添加具体问题的子节点
        if avp.avp['AVP_FLAG'] | 0x80 == avp.avp['AVP_FLAG'] and avp.my_avp_cfg[3] == '0':
            #消息中存在Vendor-ID，但是配置中没有
            _has_err = True
            self.D_treeListCtrl.SetItemBackgroundColour(_avp_flags, wx.Colour(255, 255, 128))
            _avp_flags_v = self.D_treeListCtrl.AppendItem(_avp_flags, u"WARN")
            self.D_treeListCtrl.SetItemText(_avp_flags_v, u"Vendor-ID WARN", 1)
            self.D_treeListCtrl.SetItemText(_avp_flags_v, u"解析包中含有Vendor-ID，但是配置中没有", 2)
        elif avp.avp['AVP_FLAG'] | 0x80 != avp.avp['AVP_FLAG'] and avp.my_avp_cfg[3] != '0':
            #消息中没有Vendor-ID标志位，但是配置文件中需要
            _has_err = True
            self.D_treeListCtrl.SetItemBackgroundColour(_avp_flags, wx.Colour(255, 255, 128))
            _avp_flags_v = self.D_treeListCtrl.AppendItem(_avp_flags, u"Vendor-ID WARN")
            self.D_treeListCtrl.SetItemText(_avp_flags_v, u"Vendor-ID WARN", 1)
            self.D_treeListCtrl.SetItemText(_avp_flags_v, u"解析包中没有Vendor-ID，但是配置中需要", 2)
        
        _avp_length = self.D_treeListCtrl.AppendItem(_avp_tree_root, u"AVP Length")
        self.D_treeListCtrl.SetItemText(_avp_length, str(avp.avp['AVP_LENGTH']), 1)
        self.D_treeListCtrl.SetItemText(_avp_length, u"0x%06X" % avp.avp['AVP_LENGTH'], 2)
        
        if avp.avp['AVP_FLAG'] | 0x80 == avp.avp['AVP_FLAG']:
            _avp_vendorid = self.D_treeListCtrl.AppendItem(_avp_tree_root, u"Vendor-ID")
            self.D_treeListCtrl.SetItemText(_avp_vendorid, str(avp.avp['AVP_VENDOR_ID']), 1)
            self.D_treeListCtrl.SetItemText(_avp_vendorid, u"0x%08X" % avp.avp['AVP_VENDOR_ID'], 2)
            
        _avp_data_type = self.D_treeListCtrl.AppendItem(_avp_tree_root, u"AVP Data Type")
        self.D_treeListCtrl.SetItemText(_avp_data_type, avp.avp['AVP_DATA_TYPE'], 1)
        
        if avp.avp['AVP_DATA_TYPE'] == 'Grouped':
            for _sub_avp in avp.avp['SUB_AVP']:
                self.create_avp_tree(_avp_tree_root, _sub_avp)
        else:
            _avp_data = self.D_treeListCtrl.AppendItem(_avp_tree_root, u"AVP Data")
            self.D_treeListCtrl.SetItemText(_avp_data, repr(avp), 1)
            self.D_treeListCtrl.SetItemText(_avp_data, u"%s" % repr(avp.avp['AVP_DATA']), 2)
            
        if _has_err == True:
            self.D_treeListCtrl.SetItemBackgroundColour(_avp_tree_root, wx.Colour(255, 255, 128))
        
    def pack_json(self, msg_code, json_str):
        '编码JSON数据'
        my_dcc = DCC()
        my_msg = MSG(my_dcc)
        my_msg.pack_json(msg_code, json_str, randint(0, 2097151))
        self.msg = my_msg
        return my_msg.fmt_hex(b2a_hex(my_msg.dmsg['DCC_BUF']))
        
    def unpack_hex(self, pack_buf):
        '解码HEX数据'
        my_dcc = DCC()
        my_msg = MSG(my_dcc)
        pack_buf = a2b_hex(pack_buf)
        my_msg.unpack_json(pack_buf)
        self.msg = my_msg
        #return my_msg.pmsg(0)
        return repr(my_msg)
        
    def fmt_hex(self, hex_buf):
        '''将16进制的字符串格式化输出'''
        char_num = 1
        pstr = ""
        out_str = ""
        for char in hex_buf:
            if char_num % 2 != 0:
                pstr += char
            else:
                pstr += char
                out_str = out_str + pstr + " "
                pstr = ""
                
            if char_num % 32 == 0:
                out_str += "\n"
                
            char_num += 1
            
        return out_str

    def change_choice2CmdCode(self, choice):
        '根据选择到的选项，转为对应的CmdCode'
        if choice == 0:         #CCR
            return (272, 1)
        elif choice == 1:       #CCA
            return (272, 0)
        elif choice == 2:       #DPR
            return (282, 1)
        elif choice == 3:       #DPA
            return (282, 0)
        elif choice == 4:       #DWR
            return (280, 1)
        elif choice == 5:       #DWA
            return (280, 0)
        elif choice == 6:       #CER
            return (257, 1)
        elif choice == 7:       #CEA
            return (257, 0)
        elif choice == 8:       #ASR
            return (274, 1)
        elif choice == 9:       #ASA
            return (274, 0)
        elif choice == 10:       #RAR
            return (258, 1)
        elif choice == 11:       #RAA
            return (258, 0)
        