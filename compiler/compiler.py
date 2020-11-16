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
	#
	#		Compile one stream.
	#
	def compile(self,stream):
		self.stream = stream 														# remember stream.
		self.parser = Parser(stream)												# create parser for it

		
		self.blockCompile()



	#
	#		Set mode to FAST SLOW or CODE
	#
	def setMode(self,mode):
		self.mode = mode 															# remember mode
		self.setPCode(mode != Compiler.FASTMODE)									# P-Code unless Fast.




Compiler.FASTMODE = 'F'
Compiler.SLOWMODE = 'S'
Compiler.CODEMODE = 'C'		

if __name__ == "__main__":
	cb = CodeBlock()
	im = IdentifierManager()
	cb.importRuntime(im)
	rt = RuntimeCodeGenerator(cb)
	cm = Compiler(im,cb,rt,None)
	#
	cb.open("main")																	# create new def
	xa = im.find("run.pcode")														# write JSR run.pcode
	cb.append(0x20)
	cb.append16(xa.getValue())
	#
	#		Test sources.
	#

	src = """{ var a,b,c;times(20) { times(1444) {} read.timer()!a 0 ;print.hex(a);print.crlf(); };halt.program(); }"""

	cb.show = False																	# True to o/p code.

	src = src.split("\n")															# make into lines.
	f = cm.compile(TextStream(src))													# compile 
	cb.close()																		# close definition
	cb.createApplication(im)														# dump it.
	print("Next '"+cm.parser.get()+"'")												# check EOF
	print(im.toString())															# show identifiers
