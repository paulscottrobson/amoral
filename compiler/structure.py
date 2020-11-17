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
		self.name = name.lower()
		self.members = members
		self.zpRef = self.cb.allocateZeroPage()
		#
		self.useCode = self.createUse()
		self.createNew()
	#
	#		Create use method.
	#
	def createUse(self):
		code = self.createRoutine(self.name+".use")
		self.cb.append(Asm6502.STA_Z)		# sta zp
		self.cb.append(self.zpRef)
		self.cb.append(Asm6502.STX_Z)		# stx zp+1
		self.cb.append(self.zpRef+1)
		self.cb.append(Asm6502.RTS)			# rts
		self.cb.close()
		return code
	#
	#		Create new method.
	#
	def createNew(self):
		code = self.createRoutine(self.name+".new")
		self.cb.append(Asm6502.LDA_IM)		# lda #size
		self.cb.append(len(self.members)*2)
		self.cb.append(Asm6502.LDX_IM)		# ldx #0
		self.cb.append(0)
		self.branch(Asm6502.JSR_A,"alloc")	# jsr allocate function
		self.cb.append(Asm6502.JMP_A)		# jmp to use code.
		self.cb.append16(self.useCode)
		self.cb.close()
		return code
	#
	#		Create new routine
	#
	def createRoutine(self,name,hasParameter=False):
		self.cb.open(name)
		ident = Procedure(name,self.cb.getAddr())
		self.im.addGlobal(ident)
		if hasParameter:
			assert False
		return self.cb.getAddr()
	#
	#		Create JMP or JSR to a named routine
	#
	def branch(self,opcode,routine):
		ident = self.im.find(routine)
		assert ident is not None
		self.cb.append(opcode)
		self.cb.append16(ident.getValue())
		