#!/usr/bin/python
# -*- coding: utf-8 -*-


# from __future__ import generators

# from gi.repository import GObject, Gtk #, GdkPixbuf, Gdk

# from __future__ import generators
# from gi.repository import GObject
# from gi.repository import Gtk
import os, sys, copy


print("ABC")


#os.environ['PYTHONPATH'] = '/usr/local/lib/python2.7/dist-packages/libsbml'
os.environ['PYTHONPATH'] = '/usr/local/lib64/python2.7/site-packages/libsbml'

#export PYTHONPATH=/usr/local/lib/python2.7/dist-packages/libsbml

missing_modules = []


# try:
# 	from __future__ import generators
# except ImportError:
# 	missing_modules.append("generators from __future__")

# try:
# 	from gi.repository import GObject
# except ImportError:
# 	missing_modules.append("GObject from gi.repository")

# try:
# 	from gi.repository import Gtk
# except ImportError:
# 	missing_modules.append("Gtk from gi.repository")


try:
	import string
except ImportError:
	missing_modules.append("string")

try:
	import re
except ImportError:
	missing_modules.append("re")

try:
	import sys
except ImportError:
	missing_modules.append("sys")

try:
	import xlrd
except ImportError:
	missing_modules.append("xlrd		MS Excel support")

libsbml_error=0
try:
	import libsbml
except ImportError:
	libsbml_error+=1
try:
	import _libsbml
except ImportError:
	libsbml_error+=1
if libsbml_error>1:
	missing_modules.append("libsbml	SBML support")

try:
	import networkx
except ImportError:
	missing_modules.append("networkx	Graph analysis")


#try:
#	import SOAPpy
#except ImportError:
#	missing_modules.append("SOAPpy	Connection to web services")

try:
	import itertools
except ImportError:
	missing_modules.append("itertools")

try:
	import difflib
except ImportError:
	missing_modules.append("difflib")

try:
	import subprocess
except ImportError:
	missing_modules.append("subprocess")

try:
	import math
except ImportError:
	missing_modules.append("math")

try:
	import matplotlib.pyplot
except ImportError:
	missing_modules.append("matplotlib.pyplot")

try:
	import pickle
except ImportError:
	missing_modules.append("pickle")

try:
	import pyparsing
except ImportError:
	missing_modules.append("pyparsing")


if (len(missing_modules) > 0):
	if (len(missing_modules) == 1):
		print("There is one missing module: ")
	else:
		print("There are "+str(len(missing_modules))+" missing modules: ")
	for a in missing_modules:
		print("* "+str(a))

	#user_answer = raw_input("Do you want to download and install missing modules? [y/n] \n")
	#print(user_answer)
	print("\nPlease install all missing modules manually and then run setup.py again.")

else:
	print("Everything is OK. Run ModeRator \"./modcm.py -help\"")


