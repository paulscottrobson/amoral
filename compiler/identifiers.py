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
		name = name.strip().lower()
		if name in self.locals:
			return self.locals[name]
		return self.globals[name] if name in self.globals else None
	#
	#		Add an identifier any type
	#
	def _add(self,identifier,isLocal):
		name = identifier.getName()
		if name in self.locals or name in self.globals:
			raise "Duplicate identifier {0}".format(name)
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
		return groupName+":\n"+"\n".join(["\t{0}\n".format(idents[x].toString()) for x in idents.keys()])


if __name__ == "__main__":
	im = IdentifierManager()
	im.addLocal(Variable("count",32))
	im.addGlobal(Procedure("test.proc",0x1AF7))
	print(im.toString())
	print(im.find("COUNT").toString())
	print(im.find("test.PROC").toString())	