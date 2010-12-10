# coding:utf-8
'''
Created on 2010-11-28

@author: zdl
'''

from distutils.core import setup
import py2exe
import glob
import time

options = {"py2exe":
           {"compressed": True,
            "optimize": 2,
            "bundle_files": 1,
            #"dll_excludes" : ['msvcr71.dll'],
            "excludes" : ['_ssl', 'doctest', 'pdb', 'unittest', 'difflib',
                          'optparse', 'pickle', 'calebdar', 'inspect']
            }
           }

setup(version = "0.2 ",
      description = "Build From: " + time.ctime(),
      name = "Diameter Message Tools",
      author = "zhang.dongliang",
      author_email = "zhang.dongliang@zte.com.cn",
      options = options,
      zipfile=None,
      windows=[{"script":"DccTranslate.pyw",
                "icon_resources":[(1, "kachi.ico")]}
              ],
      data_files=[("etc", glob.glob("etc/*.ini")),
                 ]) 
