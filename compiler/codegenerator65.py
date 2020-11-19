# *******************************************************************************************
# *******************************************************************************************
#
#       File:           codegenerator65.py
#       Date:           19th November 2020
#       Purpose:        Code Generator (6502)
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

from asm6502 import *
from runtime import *
from codemanager import *
from codegenerator import *

# *******************************************************************************************
#
#									Runtime Code Generator
#
# *******************************************************************************************

class M6502CodeGenerator(BaseCodeGenerator):
	def __init__(self,codeBlock,identMgr):
		self.cb = codeBlock
		self.im = identMgr
		self.bin1 = { 	RTOpcodes.ADD:Asm6502.ADC_IM, RTOpcodes.SUB:Asm6502.SBC_IM, 
						RTOpcodes.AND:Asm6502.AND_IM, RTOpcodes.ORR:Asm6502.ORA_IM, 
						RTOpcodes.XOR:Asm6502.EOR_IM }
		#
		self.bin2 = { RTOpcodes.MLT:"multiply",RTOpcodes.DIV:"divide",RTOpcodes.MOD:"modulus"}
	#
	#		Compile an variable access command. e.g. add [4] add [2004]
	#
	def cmdVar(self,baseCmd,address):
		address = address * 2 + self.cb.getVariableBase()
		if baseCmd == RTOpcodes.LDR or baseCmd == RTOpcodes.STR:				# LDR/STR abs
			isLoad = (baseCmd == RTOpcodes.LDR)
			self.cb.append(Asm6502.LDA_A if isLoad else Asm6502.STA_A)
			self.cb.append16(address)
			self.cb.append(Asm6502.LDX_A if isLoad else Asm6502.STX_A)
			self.cb.append16(address+1)
			return
		#
		if baseCmd in self.bin1:												# Direct maps.
			if baseCmd == RTOpcodes.ADD or baseCmd == RTOpcodes.SUB:			# carry set/clear
				self.cb.append(Asm6502.CLC if baseCmd == RTOpcodes.ADD else Asm6502.SEC)
			#
			c65 = self.bin1[baseCmd] + (Asm6502.ADC_A-Asm6502.ADC_IM)			# 6502 orthogonality
			self.cb.append(c65) 												# ADC xxxx
			self.cb.append16(address)
			self.cb.append(Asm6502.TAY)											# TAY
			self.cb.append(Asm6502.TXA)											# TXA
			self.cb.append(c65)													# ADC xxxx+1
			self.cb.append16(address+1)
			self.cb.append(Asm6502.TAX)											# TAX
			self.cb.append(Asm6502.TYA)											# TYA
			return
		#
		if baseCmd in self.bin2:												# Helper functions
			self.cb.append(Asm6502.JSR_A)
			self.cb.append16(self.im.find(self.bin2[baseCmd]+".absolute").getValue())
			self.cb.append16(address)
			return
		#
		assert False
	#
	#		Compile an immediate command. e.g. add #4 add #2004
	#
	def cmdImm(self,baseCmd,const):
		if baseCmd == RTOpcodes.LDR:											# LDR Immediate code.
			self.cb.append(Asm6502.LDA_IM)
			self.cb.append(const & 0xFF)
			if (const & 0xFF) == (const >> 8):
				self.cb.append(Asm6502.TAX)
			else:
				self.cb.append(Asm6502.LDX_IM)
				self.cb.append(const >> 8)
			return
		#
		if baseCmd in self.bin1:												# Direct maps.
			if baseCmd == RTOpcodes.ADD or baseCmd == RTOpcodes.SUB:			# carry set/clear
				self.cb.append(Asm6502.CLC if baseCmd == RTOpcodes.ADD else Asm6502.SEC)
			c65 = self.bin1[baseCmd]
			self.cb.append(c65) 												# ADC# low
			self.cb.append(const & 0xFF)
			if (const >> 8) == 0 and self.canOptimiseShort(c65):				# 0-255 constants.
				return
			self.cb.append(Asm6502.TAY)											# TAY
			self.cb.append(Asm6502.TXA)											# TXA
			self.cb.append(c65)													# ADC# high
			self.cb.append(const >> 8)
			self.cb.append(Asm6502.TAX)											# TAX
			self.cb.append(Asm6502.TYA)											# TYA
			return
		#
		if baseCmd in self.bin2:												# Helper functions
			self.cb.append(Asm6502.JSR_A)
			self.cb.append16(self.im.find(self.bin2[baseCmd]+".immediate").getValue())
			self.cb.append16(const)
			return
		assert False
	#
	#		Can optimise short constants ?
	#
	def canOptimiseShort(self,opim):
		return False
	#
	#		Compile a unary function INC/DEC/RTN etc.
	#
	def unary(self,cmd):
		if cmd == RTOpcodes.CLR:												# CLR uses LDR#
			self.cmdImm(RTOpcodes.LDR,0)
			return
		assert False
	#
	#		Compile a call to the given addres
	#
	def call(self,target):
		self.cb.append(Asm6502.JSR_A)
		self.cb.append16(target)
	#
	#		Compile a branch to an absolute address. Returns a 'patch' address that
	#		can be updated.
	#
	def branch(self,cmd,target = 0):
		assert False
	#
	#		Patch a branch
	#
	def patchBranch(self,patchAddr,patchTarget):
		assert False
	#
	#		String constant.
	#
	def string(self,s):
		assert False

if __name__ == "__main__":
	cb = CodeBlock()
	im = IdentifierManager()
	cb.importRuntime(im)
	rt = M6502CodeGenerator(cb)
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