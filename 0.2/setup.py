# coding:utf-8
'''
Created on 2010-11-28

@author: zdl
'''

from distutils.core import setup
import py2exe
import glob

options = {"py2exe":
           {"compressed": 1, #压缩
            "optimize": 2,
            "bundle_files": 1 #所有文件打包成一个exe文件 
            }
           }

setup(options = options,
      zipfile=None,
      console=["Call_PyDccCore.py", "test.py"],
      data_files=[("etc", glob.glob("etc/*.ini")),
                  ("plugins", glob.glob("plugins/*.py"))]) 
