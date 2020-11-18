# *******************************************************************************************
# *******************************************************************************************
#
#       File:           gentest.py
#       Date:           18th November 2020
#       Purpose:        Generates test code.
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import random

class GenerateTestCode(object):
	def __init__(self,seed = 42,varCount = 10,fileName = "test.amo"):
		if seed is None:
			seed = random.randint(0,99999)
		random.seed(seed)
		print("Test using "+str(seed))
		self.h = open(fileName,"w")
		self.createAssert()
		self.h.write("proc main() {\n")
		self.variables = {}
		for i in range(0,varCount):
			self.createVariable()
	#
	#		Create variable, add to hash, output initialisation code.
	#
	def createVariable(self):
		vName = ""
		while vName == "" or vName in self.variables:
			vName = "".join([chr(random.randint(0,25)+65) for x in range(0,random.randint(1,5))]).upper()
		value = self.getRandom()
		self.variables[vName] = value 
		self.h.write("\tvar {0} {1}  !{0}\n".format(vName,value))
	#
	#		Get one constant or variable
	#
	def pick(self):
		if random.randint(0,3) == 0:
			varNameList = [x for x in self.variables.keys()]
			varName = varNameList[random.randint(0,len(varNameList)-1)]
			return [varName,self.variables[varName]]
		n = self.getRandom()
		return [str(n),n]
	#
	#		Get randomly ranged number
	#
	def getRandom(self):
		return random.randint(0,255) if random.randint(0,1) == 0 else random.randint(0,65535)
	#
	#		End the test code - check the variables and quit
	#
	def close(self):
		for v in self.variables.keys():
			self.createTest(v,str(self.variables[v]))
		self.h.write("\texit.emulator()\n")
		self.h.write("}\n")
		self.h.close()
		self.h = None
	#
	#		Create assert procedure
	#
	def createAssert(self):
		self.h.write("proc assert(n1,n2,s) {\n")
		self.h.write("\tif (n1-n2 <> 0) { print.string(s);print.crlf();halt.program(); }\n")
		self.h.write("}\n\n")
	#
	#		Create one test
	#
	def createTest(self,n1,n2):
		self.h.write('\tassert({0},{1},"{2}")\n'.format(n1,n2,n1+"="+n2))
	#
	#		Check that assignments work.
	#
	def checkAssignment(self,n = 20):
		for i in range(0,n):
			varNameList = [x for x in self.variables.keys()]
			varName = varNameList[random.randint(0,len(varNameList)-1)]
			#
			newValue = self.pick()
			self.h.write("\t{0} !{1}\n".format(newValue[0],varName))
			self.variables[varName] = newValue[1]
	#
	#		Check Binary Arithmetic
	#
	def checkBinary(self,n = 20,opList = None):
		allOps = "+-*/%&|^"
		opList = opList if opList is not None else allOps
		for i in range(0,n):
			n1 = self.pick()
			n2 = self.pick()
			op = opList[random.randint(0,len(opList)-1)]
			if (op != "/" and op != "%") or n2[1] != 0:
				if op == "+":
					r = (n1[1] + n2[1]) & 0xFFFF
				elif op == "-":
					r = (n1[1] - n2[1]) & 0xFFFF
				elif op == "&":
					r = (n1[1] & n2[1]) & 0xFFFF
				elif op == "|":
					r = (n1[1] | n2[1]) & 0xFFFF
				elif op == "^":
					r = (n1[1] ^ n2[1]) & 0xFFFF
				elif op == "*":
					r = (n1[1] * n2[1]) & 0xFFFF
				elif op == "/":
					r = int(n1[1] / n2[1]) & 0xFFFF
				elif op == "%":
					r = int(n1[1] % n2[1]) & 0xFFFF
				else:
					assert False
				self.createTest(n1[0]+" "+op+" "+n2[0],str(r))
	#
	#		Check unary arithmetic
	#
	def checkUnary(self,n = 20,opList = None):
		allOps = "+-<>"
		opList = opList if opList is not None else allOps
		for i in range(0,n):
			n1 = self.pick()
			op = opList[random.randint(0,len(opList)-1)]
			if op == "+":
				r = (n1[1] + 1) & 0xFFFF
			elif op == "-":
				r = (n1[1] - 1) & 0xFFFF
			elif op == "<":
				r = (n1[1] << 1) & 0xFFFF
			elif op == ">":
				r = (n1[1] >> 1) & 0xFFFF
			else:
				assert False
			self.createTest(n1[0]+" "+op+op,str(r))

if __name__ == "__main__":
	gen = GenerateTestCode(None,10)
	gen.checkAssignment(10)
	gen.checkBinary(100)
	gen.checkUnary(100)
	gen.close()