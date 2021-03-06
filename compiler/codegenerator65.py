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
		if baseCmd == RTOpcodes.DCV:											# dec var
			self.cb.append(Asm6502.LDA_A)										# lda xxxx
			self.cb.append16(address)
			self.cb.append(Asm6502.BNE)											# bne *+3
			self.cb.append(3)
			self.cb.append(Asm6502.DEC_A)										# dec xxxx+1
			self.cb.append16(address+1)
			self.cb.append(Asm6502.DEC_A)										# dec xxxx
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
			if (const >> 8) == 0 and self.canOptimiseShort(baseCmd):			# 0-255 constants.
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
		#
		assert False
	#
	#		Can optimise short constants ? 0-255
	#
	def canOptimiseShort(self,opim):
		if opim == RTOpcodes.ORR or opim == RTOpcodes.XOR:						# ORR/XOR unchanged
			return True
		#
		if opim == RTOpcodes.AND:												# AND zeros MSB
			self.cb.append(Asm6502.LDX_IM)
			self.cb.append(0)
			return True
		#
		if opim == RTOpcodes.ADD or opim == RTOpcodes.SUB:						# ADD/SUB do carry.
			self.cb.append(Asm6502.BCC if opim == RTOpcodes.ADD else Asm6502.BCS)
			self.cb.append(1)
			self.cb.append(Asm6502.INX if opim == RTOpcodes.ADD else Asm6502.DEX)
			return True
		#
		print("Fail {0:x}".format(opim))
		return False
	#
	#		Compile a unary function INC/DEC/RTN etc.
	#
	def unary(self,cmd):
		if cmd == RTOpcodes.CLR:												# CLR uses LDR#
			self.cmdImm(RTOpcodes.LDR,0)
			return
		if cmd == RTOpcodes.INC:												# INC 65C02 opt.
			self.cb.append(Asm6502.CLC)
			self.cb.append(Asm6502.ADC_IM)
			self.cb.append(1)
			self.cb.append(Asm6502.BNE)
			self.cb.append(1)
			self.cb.append(Asm6502.INX)
			return
		#
		if cmd == RTOpcodes.DEC:												# DEC 65C02
			self.cb.append(Asm6502.SEC)
			self.cb.append(Asm6502.SBC_IM)
			self.cb.append(1)
			self.cb.append(Asm6502.BCS)
			self.cb.append(1)
			self.cb.append(Asm6502.DEX)
			return
		#
		if cmd == RTOpcodes.SHL:
			self.cb.append(Asm6502.ASL)											# ASLA
			self.cb.append(Asm6502.TAY)											# TAY
			self.cb.append(Asm6502.TXA)											# TXA
			self.cb.append(Asm6502.ROL)											# ROLA
			self.cb.append(Asm6502.TAX)											# TAX
			self.cb.append(Asm6502.TYA)											# TYA
			return
		#
		if cmd == RTOpcodes.SHR:
			self.cb.append(Asm6502.TAY)											# TAY
			self.cb.append(Asm6502.TXA)											# TXA
			self.cb.append(Asm6502.LSR)											# LSRA
			self.cb.append(Asm6502.TAX)											# TAX
			self.cb.append(Asm6502.TYA)											# TYA
			self.cb.append(Asm6502.ROR)											# RORA
			return
		#
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
		if cmd == RTOpcodes.BNE:												# non-zero
			self.cb.append(Asm6502.CMP_IM)
			self.cb.append(0)
			self.cb.append(Asm6502.BNE)
			self.cb.append(4)
			self.cb.append(Asm6502.CPX_IM)
			self.cb.append(0)
			self.cb.append(Asm6502.BEQ)
			self.cb.append(3)
			self.cb.append(Asm6502.JMP_A)
			code = self.cb.getAddr()
			self.cb.append16(target)
			return code
		#
		if cmd == RTOpcodes.BEQ:												# zero
			self.cb.append(Asm6502.CMP_IM)
			self.cb.append(0)
			self.cb.append(Asm6502.BNE)
			self.cb.append(7)
			self.cb.append(Asm6502.CPX_IM)
			self.cb.append(0)
			self.cb.append(Asm6502.BNE)
			self.cb.append(3)
			self.cb.append(Asm6502.JMP_A)
			code = self.cb.getAddr()
			self.cb.append16(target)
			return code
		#
		if cmd == RTOpcodes.BPL or cmd == RTOpcodes.BMI:						# plus/minus
			self.cb.append(Asm6502.CPX_IM)
			self.cb.append(0)
			self.cb.append(Asm6502.BMI if cmd == RTOpcodes.BPL else Asm6502.BPL)
			self.cb.append(3)
			self.cb.append(Asm6502.JMP_A)
			code = self.cb.getAddr()
			self.cb.append16(target)
			return code
		#
		if cmd == RTOpcodes.BRA:												# always
			self.cb.append(Asm6502.JMP_A)
			code = self.cb.getAddr()
			self.cb.append16(target)
			return code
		#
		assert False, "Opcode {0:x}".format(cmd)
	#
	#		Patch a branch
	#
	def patchBranch(self,patchAddr,patchTarget):
		self.cb.write(patchAddr,patchTarget & 0xFF)
		self.cb.write(patchAddr+1,patchTarget >> 8)
	#
	#		String constant.
	#
	def string(self,s):
		self.cb.append(Asm6502.JSR_A)
		self.cb.append16(self.im.find("string.constant").getValue())
		for c in s:
			self.cb.append(ord(c))
		self.cb.append(0)

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