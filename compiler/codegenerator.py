# *******************************************************************************************
# *******************************************************************************************
#
#       File:           codegenerator.py
#       Date:           15th November 2020
#       Purpose:        Code Generator (Runtime/Base)
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

from runtime import *
from codemanager import *

# *******************************************************************************************
#
#										Base Class
#
# *******************************************************************************************

class BaseCodeGenerator(object):
	pass

# *******************************************************************************************
#
#									Runtime Code Generator
#
# *******************************************************************************************

class RuntimeCodeGenerator(object):
	def __init__(self,codeBlock):
		self.cb = codeBlock
	#
	#		Compile an variable access command. e.g. add [4] add [2004]
	#
	def cmdVar(self,baseCmd,address):
		if address < 256:
			self.cb.append(baseCmd+RTOpcodes.VARSHORT)
			self.cb.append(address)
		else:
			self.cb.append(baseCmd+RTOpcodes.VARLONG)
			self.cb.append16(address)
	#
	#		Compile an immediate command. e.g. add #4 add #2004
	#
	def cmdImm(self,baseCmd,const):
		if const < 256:
			self.cb.append(baseCmd+RTOpcodes.IMMSHORT)
			self.cb.append(const)
		else:
			self.cb.append(baseCmd+RTOpcodes.IMMLONG)
			self.cb.append16(const)
	#
	#		Compile a unary function INC/DEC/RTN etc.
	#
	def unary(self,cmd):
		self.cb.append(cmd)
	#
	#		Compile a call to the given addres
	#
	def call(self,target):
		assert target % 2 == 0
		self.cb.append16(RTOpcodes.JSR + (target >> 1))
	#
	#		Compile a branch to an absolute address. Returns a 'patch' address that
	#		can be updated.
	#
	def branch(self,cmd,target = 0):
		self.cb.append(cmd+RTOpcodes.ABS)
		self.cb.append16(target)
		return self.cb.getAddr()-2
	#
	#		Patch a branch
	#
	def patchBranch(self,patchAddr,patchTarget):
		self.cb.write(patchAddr,patchTarget & 0xFF)
		self.cb.write(patchAddr+1,patchTarget >> 8)


if __name__ == "__main__":
	cb = CodeBlock()
	im = IdentifierManager()
	cb.importRuntime(im)
	rt = RuntimeCodeGenerator(cb)
	#
	rt.cmdVar(RTOpcodes.ADD,7)
	rt.cmdVar(RTOpcodes.ADD,518)
	print("=============================")
	#	
	rt.cmdImm(RTOpcodes.ADD,7)
	rt.cmdImm(RTOpcodes.ADD,518)
	print("=============================")
	#
	rt.unary(RTOpcodes.INC)
	print("=============================")
	#
	rt.branch(RTOpcodes.BEQ,0x127A)	
	patch = rt.branch(RTOpcodes.BMI)
	rt.patchBranch(patch,0xCDEF)
	print("=============================")
	#
	rt.call(0x2308)	