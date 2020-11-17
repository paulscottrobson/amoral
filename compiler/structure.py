# *******************************************************************************************
# *******************************************************************************************
#
#       File:           structure.py
#       Date:           17th November 2020
#       Purpose:        Structure generator worker
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import sys
from asm6502 import *
from codemanager import *
from exception import *

# *******************************************************************************************
#
#								Class structure helper
#
#	This is implemented as a worker class to keep down the complexity of compiler.py and
#	block.py
#
# *******************************************************************************************

class StructureHelper(object):
	#
	#		Set up
	#
	def __init__(self,identMgr,codeBlock):
		self.im = identMgr
		self.cb = codeBlock 
	#
	#		Generate one structure
	#
	def create(self,name,members):
		print(name,members)

		