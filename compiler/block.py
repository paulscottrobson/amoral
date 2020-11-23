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
		#		Test fails
		#
		self.testFail = { 	"==":RTOpcodes.BNE,"<>":RTOpcodes.BEQ, 
							">=":RTOpcodes.BMI,"<":RTOpcodes.BPL }
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
			elif fs == "while":														# while ?
				self.parser.get()
				self.whileStructure()			
			#
			elif fs == "if":														# if ?
				self.parser.get()
				self.ifStructure()			
			#
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
	#			Inline code.
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
			elif s == "[[":															# inline code.
				self.inlineCode()
			#
			elif s.startswith('"'):													# quoted string
				self.cg.string(s[1:])
			#
			elif s == "0":															# zero const use clear.
				self.cg.unary(RTOpcodes.CLR)
			#
			elif s[0] >= "0" and s[0] <= "9":										# is it a constant ?
				self.cg.cmdImm(RTOpcodes.LDR,int(s))
			#
			elif s == "true" or s == "false":										# true/false
				self.cg.cmdImm(RTOpcodes.LDR,0xFFFF if s == "true" else 0)
			#																		# alphanumeric (variable)
			elif s[0] >= 'a' and s[0] <= 'z' and ident is not None:					# identifier 
				if isinstance(ident,Variable):										# variable
					nxt = self.parser.get()											# array access
					if nxt == "[":
						nxt = self.innerCompile()									# compile index.
						if nxt != "]":												# must end in ]
							raise AmoralException("Missing ] on index")
						self.cg.indexCalculate(ident.getValue())
						self.parser.get()											# throw ]
					else:															# variable
						self.parser.put(nxt)										# put it back.
						self.cg.cmdVar(RTOpcodes.LDR,ident.getValue())				
				#
				elif isinstance(ident,Procedure):									# proc/func invoke
					self.callProcedure(ident)										# generate code.
				elif isinstance(ident,Constant):									# constant.
					self.cg.cmdImm(RTOpcodes.LDR,ident.getValue())
				else:
					assert False,"What else ?"
			#
			elif s == "@":															# address of variable/proc
				ident = self.im.find(self.parser.get())
				if ident is None:
					raise AmoralException("@ missing variable")
				n = ident.getValue()												# get address
				if isinstance(ident,Variable):										# make variables real address
					n = n*2+self.cb.getVariableBase()
				self.cg.cmdImm(RTOpcodes.LDR,n)										# load it in.
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
			if isinstance(ident,Constant):											# <op>constant
				self.cg.cmdImm(self.command[op],ident.getValue())			
			elif isinstance(ident,Variable):
				self.cg.cmdVar(self.command[op],ident.getValue())					# <op>variable
			else:
				raise AmoralException("Identifier "+s+" not a variable/constant")
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
				nx = proc.addParameter(identifier)							
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
		self.cg.cmdVar(RTOpcodes.DCV,varID)											# decrement the variable.
		self.blockCompile()															# loop body.
		self.cg.loadBranchNonZero(varID,timesLoop)									# loop back if <> 0
	#
	#		Handle while
	#
	def whileStructure(self):
		whileLoop = self.cb.getAddr()												# we come back here.
		failPatch = self.compileCondition()											# compile the test
		self.blockCompile()															# while body.
		self.cg.branch(RTOpcodes.BRA,whileLoop)										# loop back at end.
		self.cg.patchBranch(failPatch,self.cb.getAddr())							# jump here when test fails
	#
	#		Handle if
	#
	def ifStructure(self):
		failPatch = self.compileCondition()											# compile the test
		self.blockCompile()															# while body.
		self.cg.patchBranch(failPatch,self.cb.getAddr())							# jump here when test fails
	#
	#		Compile condition, returns branch address when test fails.
	#		
	def compileCondition(self):
		if self.parser.get() != "(":												# check (
			raise AmoralException("Missing (")		
		test = self.innerCompile()													# get value to test.		
		if test not in self.testFail:
			raise AmoralException("Bad test")
		self.parser.get()															# consume test
		cval = self.parser.get()													# get value to test against
		if cval == "" or cval[0] < "0" or cval[0] > "9":
			raise AmoralException("Bad comparison constant")
		if self.parser.get() != ")":												# check )
			raise AmoralException("Missing )")		
		if cval != "0":																# adjust for constant.
			self.cg.cmdImm(RTOpcodes.SUB,int(cval))
		return self.cg.branch(self.testFail[test])									# write branch, patched l8r
	#
	#		Set or clear generate PCode flag.
	#							
	def setPCode(self,usePCode):
		self.usePCode = usePCode
		self.cg = self.slowGenerator if usePCode else self.fastGenerator
		assert self.cg is not None
	#
	#		Assemble inline code.
	#
	def inlineCode(self):
		code = self.parser.get().lower().replace(" ","")
		if not code.startswith('"') or len(code)%2 == 0:							# validate len/type
			raise AmoralException("Bad code block")
		for p in range(1,len(code),2):
			try:
				self.cb.append(int(code[p:p+2],16))
			except ValueError:
				raise AmoralException("Bad hex byte "+code[p:p+2])

		if self.parser.get() != "]]":
			raise AmoralException("Missing ]]")

if __name__ == "__main__":
	cb = CodeBlock()
	im = FakeIdentifierManager()
	cb.importRuntime(im)
	rt = RuntimeCodeGenerator(cb)
	cm = BlockCompiler(im,cb,rt,None)
	#
	cb.open("main")																	# create new def
	xa = im.find("run.pcode")														# write JSR run.pcode
	cb.append(0x20)
	cb.append16(xa.getValue())
	#
	#		Test sources.
	#
	src = '{ 42 612 g0 l1 ++ << << +9 *2 *l0 "Hi!" }'

	src = """{ var a,b,c; 43!a;print.character(42);print.character(a+1);
			print.hex(32766);print.string("HELLO WORLD!")
			halt.program(); }"""

	src = "{ var a; times(2) { times(5,a) { print.hex(a); }} halt.program(); }"

	src = '{ var a;print.string("START"); times(100) { times(1000) { a++!a }}	 print.string("END"); halt.program(); }'

	src = """{ var a;4!a;
				while (a < 10) { if (a%2 == 0) { print.hex(a); }
								 a++!a; }
				halt.program();
			}"""

	src = """{ var a,b,c;times(20) { times(4444) {} read.timer();print.hex(~) };halt.program(); }"""

	cb.show = False																	# True to o/p code.

	src = src.split("\n")															# make into lines
	cm.parser = Parser(TextStream(src))												# set the parser (cheat)
	f = cm.blockCompile()															# compile 
	cb.close()																		# close definition
	cb.createApplication(im)														# dump it.
	print("Next '"+cm.parser.get()+"'")												# check EOF
	print(im.toString())															# show identifiers
