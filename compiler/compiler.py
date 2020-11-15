# *******************************************************************************************
# *******************************************************************************************
#
#       File:           compiler.py
#       Date:           15th November 2020
#       Purpose:        Main Compiler
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

from runtime import *
from codemanager import *
from codegenerator import *
from exception import *
from parser import *

# *******************************************************************************************
#
#											Compiler Class
#	
# *******************************************************************************************

class Compiler(object):
	def __init__(self,identMgr,codeGen):
		self.im = identMgr
		self.cg = codeGen
		self.unary = { 		"++":RTOpcodes.INC,"--":RTOpcodes.DEC,
							"<<":RTOpcodes.SHL,">>":RTOpcodes.SHR }

		self.command = {	"!":RTOpcodes.STR,"+":RTOpcodes.ADD,"-":RTOpcodes.SUB,
							"*":RTOpcodes.MLT,"/":RTOpcodes.DIV,"%":RTOpcodes.MOD,
							"&":RTOpcodes.AND,"|":RTOpcodes.ORR,"^":RTOpcodes.XOR }

	#
	#		Compile simple elements (e.g. no procedure calls, no structures) from the
	#		current stream, until something is found that cannot be processed. 
	#		Return this element (which will be put back in the parser queue)
	#
	def innerCompile(self):
		failed = None 																# not None when exit
		while failed is None:
			s = self.parser.get()													# get what is next.
			ident = self.im.find(s)													# look for it as an identifier
			#
			if s == "":																# end of stream.
				failed = ""
			#
			elif s == ";":															# ignore ;
				pass
			#
			elif s.startswith('"'):													# quoted string
				self.cg.string(s[1:])
			#
			elif s == "0":															# zero const use clear.
				self.cg.unary(RTOpcodes.CLR)
			#
			elif s >= "0" and s <= "9":												# is it a constant ?
				self.cg.cmdImm(RTOpcodes.LDR,int(s))
			#
			#																		# alphanumeric (variable)
			elif s[0] >= 'a' and s[0] <= 'z' and ident is not None and isinstance(ident,Variable):	
				self.cg.cmdVar(RTOpcodes.LDR,ident.getValue())
			#
			elif s in self.unary:													# unary operators.
				self.cg.unary(self.unary[s])
			#
			elif s in self.command:													# binary operators.
				self.compileOperation(s)
			#
			else: 																	# syntax or EOF, fail.
				self.parser.put(s)													# push back on parser stack
				failed = s 															# and we exit.
		return failed
	#
	#		Compile a single binary operator (including STO) of type +<const> or +<variable>
	#
	def compileOperation(self,op):
		s = self.parser.get() 														# what's next.
		if s == "":
			raise AmoralException("Nothing to operate on")							# has to be something.
		#
		if s[0] >= "0" and s[0] <= "9":												# is it a constant.
			value = int(s)
			if self.command[op] == RTOpcodes.STR:									# cannot store immediate
				raise AmoralException("Cannot store immediate")
			self.cg.cmdImm(self.command[op],value)
		#
		else:
			ident = self.im.find(s)													# find the identifier.
			if ident is None:														# validate it.
				raise AmoralException("Unknown identifier "+s)
			if not isinstance(ident,Variable):
				raise AmoralException("Identifier "+s+" not a variable")
			self.cg.cmdVar(self.command[op],ident.getValue())



if __name__ == "__main__":
	cb = CodeBlock()
	im = FakeIdentifierManager()
	cb.importRuntime(im)
	rt = RuntimeCodeGenerator(cb)
	#
	cm = Compiler(im,rt)
	cb.open("main")
	xa = im.find("run.pcode")
	cb.append(0x20)
	cb.append16(xa.getValue())
	src = '42 612 g0 l1 ++ << << +9 *2 *l0 "Hi!"'.split("\n")
	cm.parser = Parser(TextStream(src))
	f = cm.innerCompile()
	print("Failed on '"+f+"'")
	cb.close()
	cb.createApplication()
	