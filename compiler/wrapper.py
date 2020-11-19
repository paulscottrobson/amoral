# *******************************************************************************************
# *******************************************************************************************
#
#       File:           wrapper.py
#       Date:           16th November 2020
#       Purpose:        Wraps compiler
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import sys
from codemanager import *
from codegenerator import *
from codegenerator65 import *
from exception import *
from aparser import *
from block import *
from compiler import *
from version import *

# *******************************************************************************************
#
#										Compiler wrapper
#
# *******************************************************************************************

class CompilerWrapper(object):
	#
	def __init__(self):
		self.codeBlock = CodeBlock()												# code block w/runtime
		self.identMgr = IdentifierManager()											# identifier manager
		self.codeBlock.importRuntime(self.identMgr)									# import from runtime
		self.rtSlow = RuntimeCodeGenerator(self.codeBlock)							# slow runtime
		self.rtFast = M6502CodeGenerator(self.codeBlock,self.identMgr) 				# fast runtime
		self.compiler = Compiler(self.identMgr,self.codeBlock,self.rtSlow,self.rtFast) # compiler object
		self.outputFile = "application.prg"											# default output file
		self.showStats = False 														# show statistics
		self.showIdentifiers = False
		self.hasCode = False
	#
	#		Compile a stream
	#
	def compile(self,stream):
		self.compiler.compileManageErrors(stream)									# compile the stream.
	#
	#		Handle sequence of commands.
	#
	def process(self,cmdList):
		for i in range(0,len(cmdList)):												# work through
			if cmdList[i] != "":													# ignore blanked
				if cmdList[i].startswith("-"):
					option = cmdList[i][1].lower()
					if option == "s":												# stand alones
						self.showStats = True
					elif option == "n":												
						self.codeBlock.stripNames()
					elif option == "i":
						self.showIdentifiers = True
					#	
					elif "o".find(option) >= 0:										# have a parameter.
						if i == len(cmdList)-1:										# can't be last.
							print("Missing operand in command line")
							sys.exit(1)
						operand = cmdList[i+1]										# get and remove it
						cmdList[i+1] = ""
						if option == "o":											# operands
							self.outputFile = operand
						else:
							print("Unknown option "+cmdList[i])
							sys.exit(1)
					else:
						print("Unknown option "+cmdList[i])
						sys.exit(1)
				else:
					self.compile(SourceFileStream(cmdList[i]))
					self.hasCode = True
	#
	#		End a build.
	#
	def complete(self,fileName = None):
		if not self.hasCode:
			print("No source files.")
			sys.exit(1)
		fileName = fileName if fileName is not None else self.outputFile
		self.codeBlock.createApplication(self.identMgr,fileName)					# write out the result.
		if self.showStats:
			self.compiler.codeStats()
		if self.showIdentifiers:
			print(self.identMgr.toString())
	#
	#		Show help.
	#
	def help(self):
		v = VersionInformation()
		print("AMORAL Compiler by Paul Robson (paul@robsons.org.uk) v{0} ({1})".format(v.getVersion(),v.getDate()))
		print("\tamoral <options> <source files>")
		print("\t\t -i                Display identifiers")
		print("\t\t -n                Remove identifiers from program")
		print("\t\t -o <output file>  Specify output file")
		print("\t\t -s                Display slow/fast usage")

if __name__ == "__main__":
	cw = CompilerWrapper()
	cw.process(["-o","test.prg","test.amo"])
	cw.complete()
