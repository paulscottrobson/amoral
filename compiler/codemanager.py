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
		self.show = True 															# debug output
		self.currentHeader = None 													# not in a definition.
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
	#		Append a byte
	#
	def append(self,data):
		self.binary.append(data)													# write it out
		self.nextFree += 1															# bump next free
		assert self.nextFree - self.loadAddress == len(self.binary)					# check it's valid.
		if self.show:
			print("{0:04x} : {1:02x}".format(self.nextFree-1,data))
	#
	#		Get current write address
	#
	def getAddr(self):
		return self.nextFree		
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
					im.addGlobal(Procedure(name,p))									# add to identmgr
				#
				link = link + offset
			else:
				link = 0

if __name__ == "__main__":
	cb = CodeBlock()		
	im = IdentifierManager()
	cb.importRuntime(im)
	print(im.toString())
	#
	cb.append(42)
	cb.append(255)