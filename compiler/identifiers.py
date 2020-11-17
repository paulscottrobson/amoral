# *******************************************************************************************
# *******************************************************************************************
#
#       File:           identifiers.py
#       Date:           14th November 2020
#       Purpose:        Identifier manager
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import re
from exception import *

# *******************************************************************************************
#
#								Identifier classes
#	
# *******************************************************************************************

class Identifier(object):
	def __init__(self,name,value):
		self.name = name.strip().lower()
		self.value = value
	#
	def getName(self):
		return self.name
	#
	def getValue(self):
		return self.value
	#
	def toString(self):
		return "{0}:{1:12}:={2:5} ${2:04x} ".format(self.getType(),self.getName(),self.getValue())

class Variable(Identifier):
	def getType(self):
		return "V"

class Procedure(Identifier):
	def __init__(self,name,value):
		Identifier.__init__(self,name,value)
		self.parameters = []
	#
	def getType(self):
		return "P"
	#
	def addParameter(self,identifier):
		self.parameters.append(identifier)
		return self
	#
	def toString(self):
		params = ",".join([p.getName() for p in self.parameters])
		if len(self.parameters) > 0:
			params += " @{0}:${0:x}".format(self.parameters[0].getValue())
		return Identifier.toString(self)+"("+params+")"
	#
	def getParams(self):
		return self.parameters
	def getParamCount(self):
		return len(self.parameters)

class SystemProcedure(Procedure):
	def __init__(self,name,value):
		if name.find(":") >= 0:														# specifies param count
			parts = name.split(":")													# split up
			name = parts[0]
			Procedure.__init__(self,name,value)
			count = int(parts[1])													# #of params.
			for p in range(0,count-1):												# params except last.
				self.addParameter(Identifier("p"+str(p+1),p))
			if count >= 1:															# don't need a target for
				self.addParameter(Identifier("p"+str(count),-1))					# last parameter.

		else:
			Procedure.__init__(self,name,value)

	def getType(self):
		return "S"

# *******************************************************************************************
#
#								Identifier manager class
#
# *******************************************************************************************

class IdentifierManager(object):
	def __init__(self):
		self.locals = {}
		self.globals = {}
	#
	#		Find identifier
	#
	def find(self,name):
		if name in self.locals:
			return self.locals[name]
		return self.globals[name] if name in self.globals else None
	#
	#		Add an identifier any type
	#
	def _add(self,identifier,isLocal):
		name = identifier.getName()
		if name in self.locals or name in self.globals:
			raise AmoralException("Duplicate identifier {0}".format(name))
		if isLocal:
			self.locals[name] = identifier
		else:
			self.globals[name] = identifier 
	#
	#		Helper methods for _add
	#
	def addLocal(self,ident):
		self._add(ident,True)
	def addGlobal(self,ident):
		self._add(ident,False)
	#	
	#		Clear all locals
	#
	def clearLocals(self):
		self.locals = {}
	#
	#		Convert to string.
	#
	def toString(self):
		return self._toString(self.locals,"Locals")+self._toString(self.globals,"Globals")
	def _toString(self,idents,groupName):
		keyList = [x for x in idents.keys()]		
		keyList.sort()
		return groupName+":\n"+"".join(["\t{0}\n".format(idents[x].toString()) for x in keyList])

# *******************************************************************************************
#
#					Initialised Identifier for testing/development
#
# *******************************************************************************************

class FakeIdentifierManager(IdentifierManager):
	def __init__(self):
		IdentifierManager.__init__(self)
		self.addGlobal(Variable("g0",100))
		self.addGlobal(Variable("g1",101))
		self.addGlobal(Variable("g2",102))
		self.addLocal(Variable("l0",256))
		self.addLocal(Variable("l1",257))
		self.addGlobal(Procedure("proc.none",0x3578))
		self.addGlobal(Procedure("proc.one",0x468A).addParameter(Variable("z1",32)))
		self.addGlobal(Procedure("proc.two",0x759C).addParameter(Variable("y1",40)).addParameter(Variable("y2",41)))
		self.addGlobal(Procedure("proc.three",0xFEDE).addParameter(Variable("x1",40)).addParameter(Variable("x2",41)).addParameter(Variable("x3",42)))

if __name__ == "__main__":
	im = IdentifierManager()
	im.addLocal(Variable("count",32))
	im.addGlobal(Procedure("test.proc",0x1AF7))
	pr = Procedure("param.procedure",0xFF74).addParameter(Variable("a",64)).addParameter(Variable("b",65))
	im.addGlobal(pr)

	print(im.toString())
	print(im.find("COUNT").toString())
	print(im.find("test.PROC").toString())	
	print("==============================")
		
	im2 = FakeIdentifierManager()
	print(im2.toString())