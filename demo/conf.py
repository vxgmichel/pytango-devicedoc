# -*- coding: utf-8 -*-

# Imports
import sys, os
# To find tangodoc extension
sys.path.insert(0, os.path.abspath('..'))
# To find powersupply module
sys.path.insert(0, os.path.abspath('.'))

# Configuration
extensions = ['sphinx.ext.autodoc', 'tangodoc']
master_doc = 'index'

# Data
project = u'tango-device-powersupply'
copyright = u'2014, Tango Controls'
release = '1.0'
