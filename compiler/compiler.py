# *******************************************************************************************
# *******************************************************************************************
#
#       File:           compiler.py
#       Date:           15th November 2020
#       Purpose:        Compiles an entire file
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

from asm6502 import *
from runtime import *
from codemanager import *
from codegenerator import *
from exception import *
from parser import *
from block import *

# *******************************************************************************************
#
#										Main Compiler class
#
# *******************************************************************************************
#
#		This sublclasses Block but should be viewed as splitting the compiler into two parts
#		the "in procedure" stuff and the globals stuff for clarity. 
#

class Compiler(BlockCompiler):

	def __init__(self,identMgr,codeBlock,slowGenerator,fastGenerator):
		BlockCompiler.__init__(self,identMgr,codeBlock,slowGenerator,fastGenerator)
		self.mode = None
		self.setMode(Compiler.SLOWMODE)
		self.slowBytes = 0
		self.fastBytes = 0
		self.modes = { "fast":Compiler.FASTMODE,"slow":Compiler.SLOWMODE,"code":Compiler.CODEMODE }
		self.pCodeRoutine = identMgr.find("run.pcode").getValue()
	#
	#		Compile one stream.
	#
	def compile(self,stream):
		self.stream = stream 														# remember stream.
		self.parser = Parser(stream)												# create parser for it
		done = False
		while not done:
			nxt = self.parser.get()													# what's next
			if nxt == "":
				done = True
			elif nxt == ";":														# ignore semicolon
				pass
			elif nxt == "var":														# global variable ?
				self.declareVariables(False)										# declare variables.
			elif nxt in self.modes:													# switch mode ?
				self.setMode(self.modes[nxt])
			elif nxt == "func" or nxt == "proc":									# these are identical.
				self.defineProcedure()
			else:	
				raise AmoralException("Syntax error")	
	#
	#		Set mode to FAST SLOW or CODE
	#
	def setMode(self,mode):
		self.mode = mode 															# remember mode
		self.setPCode(mode != Compiler.FASTMODE)									# P-Code unless Fast.
	#
	#		Define a new procedure
	#
	def defineProcedure(self):
		self.im.clearLocals()														# forget locals.
		procName = self.parser.get()
		if procName == "" or procName[0] < 'a' or procName[0] > 'z':
			raise AmoralException("Bad proc/func name "+procName)
		#
		address = self.cb.open(procName)											# open a new procedure
		procObj = Procedure(procName,address)										# object representing it
		self.im.addGlobal(procObj)													# add to the identifier mgr
		#				
		if self.parser.get() != "(":												# param list open
			raise AmoralException("Missing ( on call")
		nxt = self.parser.get()														# some parameters ?
		if nxt != ")":
			self.parser.put(nxt)
			self.declareVariables(True,procObj)										# get parameters.
			if self.parser.get() != ")":											# param list close.
				raise AmoralException("Missing ) on parameters")
		#
		startAddr = self.cb.getAddr()
		#
		if self.mode != Compiler.CODEMODE:											# do we do the header ?
			n = procObj.getParamCount()												# get parameters
			if n > 0:																# if some.
				varID = procObj.getParams()[n-1].getValue()							# get variable #
				varAddr = self.cb.getVariableBase()+varID*2							# physical address.
				self.cb.append(Asm6502.STA_A)										# sta Addr
				self.cb.append16(varAddr)
				self.cb.append(Asm6502.STX_A)										# stx VarAddr+1
				self.cb.append16(varAddr+1)
			#
			if self.mode == Compiler.SLOWMODE:										# call to routine ?
				self.cb.append(Asm6502.JSR_A)										# JSR
				self.cb.append16(self.pCodeRoutine)
		#
		self.blockCompile()															# compile body.
		if self.mode == Compiler.SLOWMODE:											# Ret (from PCode)
			self.cb.append(RTOpcodes.RET)
		self.cb.append(Asm6502.RTS)													# and end with RTS
		self.cb.close()																# close definition.
		#
		codeUsed = self.cb.getAddr()-startAddr 										# code used.
		if self.mode == Compiler.SLOWMODE:
			self.slowBytes += codeUsed
		else:
			self.fastBytes += codeUsed

	#
	def codeStats(self):
		totalCode = self.slowBytes+self.fastBytes
		print("Slow (P-Code) : {0:5} ({1}%)".format(self.slowBytes,int(100*self.slowBytes/totalCode)))
		print("Fast (6502)   : {0:5} ({1}%)".format(self.fastBytes,int(100*self.fastBytes/totalCode)))


Compiler.FASTMODE = 'F'
Compiler.SLOWMODE = 'S'
Compiler.CODEMODE = 'C'		

if __name__ == "__main__":
	cb = CodeBlock()
	im = IdentifierManager()
	cb.importRuntime(im)
	rt = RuntimeCodeGenerator(cb)
	cm = Compiler(im,cb,rt,None)

	src = """
		var ga,gb,gdemo;
		proc say.hi(n,n1) { 
			print.hex(n+n1);
			print.string(" HELLO, WORLD!");
			print.crlf();
		}
		#
		#		Main program.
		#
		proc main() {
			var i
			print.hex(true);print.hex(false);print.crlf();
			times(10,i) {
				say.hi(i,100)
			}
		}
	"""
	src = src.split("\n")															# make into lines.
	f = cm.compile(TextStream(src))													# compile 

	cb.createApplication(im)														# dump it.
	print("Next '"+cm.parser.get()+"'")												# check EOF
	print(im.toString())															# show identifiers
	cm.codeStats()
