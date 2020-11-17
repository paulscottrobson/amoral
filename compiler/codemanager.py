# *******************************************************************************************
# *******************************************************************************************
#
#       File:           codemanager.py
#       Date:           14th November 2020
#       Purpose:        Handles Code/Runtime manager
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

from identifiers import *
from asm6502 import *

# *******************************************************************************************
#
#						Code Manager, handles binary built from runtime
#
# *******************************************************************************************

class CodeBlock(object):
	#
	#		Load in and pre-process code block.
	#
	def __init__(self,runtime = "runtime.prg"):
		self.binary = [x for x in open(runtime,"rb").read(-1)]						# read in binary
		self.loadAddress = self.binary[0]+self.binary[1]*256						# get load address
		self.binary = self.binary[2:]												# remove from binary block
		#
		x = self.binary[1]+self.binary[2]*256 										# check JMP self
		assert x == self.loadAddress,"Runtime a test version"						# not a test build
		#
		x = self.binary[24]+self.binary[25]*256 									# check boot addr matches
		assert x == self.loadAddress,"Boot address mismatch"						# not a test build
		#
		self.variables = x = self.binary[26]+self.binary[27]*256					# variable base address
		#
		self.nextFree = x = self.binary[28]+self.binary[29]*256						# next free address
		assert self.nextFree-self.loadAddress == len(self.binary) 					# check it all matches up.
		self.firstWriteable = self.nextFree 										# can't write below this.
		#
		self.show = False 															# debug output
		self.currentHeader = None 													# not in a definition.
		self.executeAddress = None													# what we run.
		self.nextVariable = 6														# next allocatable variable
		self.nextZeroPage = self.binary[23]											# next free zp slot
		#
		#	Variable zero is the first param of two for system calls with 2 parameters.
		#
	#
	#		Read a byte, the address is the mapped address on the Code Block
	#
	def read(self,addr):
		assert addr >= self.loadAddress
		if addr >= self.nextFree:													# unused memory.
			return 0
		return self.binary[addr-self.loadAddress]									# get it.
	#
	#		Write a byte (must be pre-existing)
	#		
	def write(self,addr,data):
		assert addr >= self.firstWriteable and addr < self.nextFree 				# check in compile write area
		self.binary[addr-self.loadAddress] = data 									# write it.
		if self.show:
			print("{0:04x} : {1:02x} (Update)".format(addr,data))
	#
	#		Append a byte/word
	#
	def append(self,data):
		self.binary.append(data)													# write it out
		self.nextFree += 1															# bump next free
		assert self.nextFree - self.loadAddress == len(self.binary)					# check it's valid.
		if self.show:
			print("{0:04x} : {1:02x}".format(self.nextFree-1,data))
	#
	def append16(self,data):
		self.binary.append(data & 0xFF)												# write it out
		self.binary.append(data >> 8)
		self.nextFree += 2															# bump next free
		assert self.nextFree - self.loadAddress == len(self.binary)					# check it's valid.
		if self.show:
			print("{0:04x} : {1:04x}".format(self.nextFree-2,data))
	#
	#		Get current write address
	#
	def getAddr(self):
		return self.nextFree	
	#
	#		Get variable base
	#
	def getVariableBase(self):
		return self.variables
	#
	#		Open a new definition.
	#	
	def open(self,definitionName):
		assert self.currentHeader is None 											# not already open.
		definitionName = definitionName.strip().lower()+chr(0)						# preprocess
		self.currentHeader = self.getAddr()											# remember header
		self.append16(0)															# dummy offset patched later
		for c in definitionName:													# name of routine
			self.append(ord(c))
		if self.getAddr() % 2 != 0:													# make even address.
			self.append(0)
		self.executeAddress = self.getAddr()										# run last defined.
		return self.getAddr()
	#
	#		Close open definition.
	#
	def close(self):
		assert self.currentHeader is not None 										# check open.
		offset = self.getAddr()-self.currentHeader 									# calc offset
		self.write(self.currentHeader,offset & 0xFF)								# patch offset when opened
		self.write(self.currentHeader+1,offset >> 8)	
		self.currentHeader = None 													# close definition.
	#
	#		Import the routines into the identifier manager.
	#
	def importRuntime(self,im):
		link = self.loadAddress + 32												# chain starts here.
		while link != 0:
			offset = self.read(link)+self.read(link+1)*256 							# offset to next.
			if offset != 0:
				name = ""															# build the name
				p = link + 2
				while self.read(p) != 0:
					name = name + chr(self.read(p))
					p += 1
				p += 1																# skip over chr(0)
				p = p if (p % 2) == 0 else p+1 										# must be even address.
				#
				if not name.startswith("."):										# if not hidden.
					im.addGlobal(SystemProcedure(name,p))							# add to identmgr
				#
				link = link + offset
			else:
				link = 0
	#
	#		Create final application.
	#
	def createApplication(self,im,fileName = "application.prg"):
		assert self.executeAddress is not None 										# no procedure !
		initAddr = im.find("clear.variables").getValue()
		self.binary[0] = Asm6502.NOP 												# Bootup code NOP
		#
		self.binary[1] = Asm6502.JSR_A 												# Initialisation code
		self.binary[2] = initAddr & 0xFF
		self.binary[3] = initAddr >> 8
		#
		self.binary[4] = Asm6502.JSR_A 												# JSR <start>
		self.binary[5] = self.executeAddress & 0xFF
		self.binary[6] = self.executeAddress >> 8
		#
		loopAddr = self.loadAddress+7
		self.binary[7] = Asm6502.JMP_A												# Loop to end program.
		self.binary[8] = loopAddr & 0xFF
		self.binary[9] = loopAddr >> 8

		#
		self.append16(0)															# end marker.
		#
		self.binary[30] = self.getAddr() & 0xFF 									# free memory pointer
		self.binary[31] = self.getAddr() >> 8
		#
		h = open(fileName,"wb")
		h.write(bytes([self.loadAddress & 0xFF]))									# 2 byte load addr
		h.write(bytes([self.loadAddress >> 8]))
		h.write(bytes(self.binary))
	#
	#		Allocate variable id.
	#
	def allocateVariable(self):
		self.nextVariable += 1
		return self.nextVariable-1
	#
	#		Allocate zero page 2 bytes
	#
	def allocateZeroPage(self):
		self.nextZeroPage += 2
		return self.nextZeroPage-2
		
if __name__ == "__main__":
	cb = CodeBlock()		
	im = IdentifierManager()
	cb.importRuntime(im)
	print(im.toString())
	#
	cb.open("test1")
	cb.append(0xFF)
	cb.close()
