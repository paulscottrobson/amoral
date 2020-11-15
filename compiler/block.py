# *******************************************************************************************
# *******************************************************************************************
#
#       File:           block.py
#       Date:           15th November 2020
#       Purpose:        Compiles a block in curly brackets. 
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
#									Block Compiler Class
#	
# *******************************************************************************************

class BlockCompiler(object):
	def __init__(self,identMgr,codeBlock,slowGenerator,fastGenerator):
		self.im = identMgr
		self.slowGenerator = slowGenerator
		self.fastGenerator = fastGenerator
		self.slowBytes = 0
		self.fastBytes = 0
		self.setPCode(True)
		self.cb = codeBlock
		#
		#		Unary functions
		#
		self.unary = { 		"++":RTOpcodes.INC,"--":RTOpcodes.DEC,
							"<<":RTOpcodes.SHL,">>":RTOpcodes.SHR }
		#
		#		Binary functions.
		#					
		self.command = {	"!":RTOpcodes.STR,"+":RTOpcodes.ADD,"-":RTOpcodes.SUB,
							"*":RTOpcodes.MLT,"/":RTOpcodes.DIV,"%":RTOpcodes.MOD,
							"&":RTOpcodes.AND,"|":RTOpcodes.ORR,"^":RTOpcodes.XOR }
	#
	#		Compile block, e.g. a piece of code between {}. This includes all those in
	#		inner compile.
	#
	#		Handles:
	#			Variable Declarations
	#			if, while, and times
	#			Procedure/Function Calls.
	#				
	def blockCompile(self):
		if self.parser.get() != "{":												# first {
			raise AmoralException("Missing {")
		completed = False
		while not completed:
			fs = self.innerCompile()												# compile inner stuff.
			#
			if fs == "}":															# found the end
				self.parser.get()													# throw it.
				completed = True
			#
			elif fs == "var":														# variable declaration
				self.parser.get()													# throw it.
				self.declareVariables(True)											# declare the variables.
			#
			elif fs == "times":														# times()
				self.parser.get()													# throw it.
				self.timesStructure()				
			#
			elif fs[0] >= 'a' and fs[0] <= 'z':										# Identifier must be a call.
				self.parser.get()													# throw it.
				proc = self.im.find(fs)												# look up the name
				if proc is None or not isinstance(proc,Procedure):					# check okay.
					raise AmoralException("Unknown procedure "+fs)
				self.callProcedure(proc)											# generate code.
			#
			else:
				raise AmoralException("Syntax Error "+fs)
	#	
	#		Compile simple elements (e.g. no procedure calls, no structures) from the
	#		current stream, until something is found that cannot be processed. 
	#		Return this element (which will be put back in the parser queue)
	#
	#		Handles : 
	#
	#			Integer and String Constants
	#			Variable Load and Store, Operations on Constants and Variables
	#			Unary operators (not RET)
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
			elif s == "~":															# ignore ~
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
			self.cg.cmdImm(self.command[op],value)									# generate code
		#
		else:
			ident = self.im.find(s)													# find the identifier.
			if ident is None:														# validate it.
				raise AmoralException("Unknown identifier "+s)
			if not isinstance(ident,Variable):
				raise AmoralException("Identifier "+s+" not a variable")
			self.cg.cmdVar(self.command[op],ident.getValue())						# generate code
	#
	#		Declare variables ; next element should be first variable.
	#		Returns count.
	#
	def declareVariables(self,isLocal,proc = None):
		done = False
		count = 0
		while not done:
			name = self.parser.get()
			if name == "" or name[0] < 'a' or name[0] > 'z':						# not an identifier.
				raise AmoralException("Bad variable name "+name)
			varID = self.cb.allocateVariable()										# get var id
			identifier = Variable(name,varID)										# create identifier.
			count += 1 																# bump count.
			if isLocal:																# add to known list.
				self.im.addLocal(identifier)
			else:
				self.im.addGlobal(identifier)
			#
			if proc is not None:													# if parameter, add them.
				nx = proc.addParameter(proc)							
			#
			nx = self.parser.get()
			if nx != ",":															# if not comma
				self.parser.put(nx)													# put it back.
				done = True 														# and we're done.
		return count
	#
	#		Procedure call.
	#
	def callProcedure(self,proc):
		params = proc.getParams()													# get parameters.
		paramCount = proc.getParamCount()
		if self.parser.get() != "(":												# check (
			raise AmoralException("Missing ( on procedure call")		
		for i in range(0,paramCount):												# do parameters
			nxt = self.innerCompile()												# do a parameter.
			if i != paramCount-1:													# if not last.
				if nxt != ",":														# check comma follows
					raise AmoralException("Parameter error on procedure call")		
				self.parser.get()													# consume comma.
				self.cg.cmdVar(RTOpcodes.STR,params[i].getValue())					# store parameter.
		if self.parser.get() != ")":												# check )
			raise AmoralException("Parameter error on procedure call")		
		self.cg.call(proc.getValue())												# compile call code.
	#
	#		Handle times
	#
	def timesStructure(self):
		if self.parser.get() != "(":												# check (
			raise AmoralException("Missing (")		
		nx = self.innerCompile()													# get total count.
		if nx == ",":																# if times(x,y)
			self.parser.get()														# throw comma
			ident = self.im.find(self.parser.get())									# grab index variable
			if ident is None or not isinstance(ident,Variable):
				raise AmoralException("Missing times index variable")
			varID = ident.getValue()												# this is the var ID.
		else:
			varID = self.cb.allocateVariable()										# allocate unnamed variable
		if self.parser.get() != ")":												# check )
			raise AmoralException("Missing )")		
		self.cg.cmdVar(RTOpcodes.STR,varID)											# write it.
		timesLoop = self.cb.getAddr()												# loop address			
		#
		#	Loop
		#
		self.cg.decVar(varID)														# decrement the variable.
		self.blockCompile()															# loop body.
		self.cg.loadBranchNonZero(varID,timesLoop)									# loop back if <> 0
	#
	#		Set or clear generate PCode flag.
	#							
	def setPCode(self,usePCode):
		self.usePCode = usePCode
		self.cg = self.slowGenerator if usePCode else self.fastGenerator



if __name__ == "__main__":
	cb = CodeBlock()
	im = FakeIdentifierManager()
	cb.importRuntime(im)
	cb.show = True
	rt = RuntimeCodeGenerator(cb)
	#
	cm = BlockCompiler(im,cb,rt,None)
	cb.open("main")
	xa = im.find("run.pcode")
	cb.append(0x20)
	cb.append16(xa.getValue())
	src = '42 612 g0 l1 ++ << << +9 *2 *l0 "Hi!"'
	src = """{ var a,b,c; 43!a;print.character(42);print.character(a+1);
			print.hex(32766);print.string("HELLO WORLD!")
			halt.program(); }"""

	src = "{ var a; times(2) { times(5,a) { print.hex(a); }} halt.program(); }"
	src = '{ var a;print.string("START"); times(100) { times(1000) { a++!a }}	 print.string("END"); halt.program(); }'
	src = src.split("\n")
	cm.parser = Parser(TextStream(src))
	f = cm.blockCompile()
	cb.close()
	cb.createApplication(im)
	print("Next '"+cm.parser.get()+"'")
	print(im.toString())	
