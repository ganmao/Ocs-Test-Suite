#!/usr/bin/env python
#coding:utf-8

import wx

import mainFrame

modules ={u'mainFrame': [1, 'Main frame of Application', u'mainFrame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = mainFrame.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
    
