# *******************************************************************************************
# *******************************************************************************************
#
#       File:           aparser.py
#       Date:           14th November 2020
#       Purpose:        Parses Input Streams
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import re,sys
from exception import *

# *******************************************************************************************
#
#								Input Stream base class
#
# *******************************************************************************************

class Stream(object):
	#	
	def setError(self,fileName):
		AmoralException.LINE = 0
		AmoralException.FILE = fileName
	#
	def nextLine(self):
		AmoralException.LINE += 1

# *******************************************************************************************
#
#				Simple input stream that works from a string array.
#
# *******************************************************************************************

class TextStream(Stream):
	#
	#		Set up
	#
	def __init__(self,streamText):
		self.setError("<TextStream>")
		self.streamText = streamText
	#
	#		Get next line.
	#
	def get(self):
		self.nextLine()
		return "" if self.isDone() else self.streamText.pop(0)
	#
	#		Check end of stream.
	#
	def isDone(self):
		return len(self.streamText) == 0

# *******************************************************************************************
#
#						Simple input stream that works from a file
#
# *******************************************************************************************

class SourceFileStream(TextStream):
	def __init__(self,srcFile):
		try:
			srcText = open(srcFile).readlines()
		except FileNotFoundError:
			print("No source file "+srcFile)
			sys.exit(1)
		TextStream.__init__(self,srcText)
		self.setError(srcFile)
		
# *******************************************************************************************
#
#								Parse an input stream.
#
# *******************************************************************************************

class AmoralParser(object):
	def __init__(self,stream):
		self.stream = stream 														# source.
		self.currentLine = ""														# current line text.
		self.parseObjectStack = []													# returned objects
		self.doubleTokens = { ">>":0,"<<":0,"++":0,"--":0,">=":0,"==":0,"<>":0 }	# supported 2 char tokens
	#
	#		Get next parsed object.
	#
	def get(self):
		if len(self.parseObjectStack) != 0:											# something on stack
			return self.parseObjectStack.pop()										# return most recent first
		while self.currentLine == "" and not self.isDone():							# skip blanks
			self.currentLine = self.processLine(self.stream.get())					# get line.
		if self.isDone(): 															# end of stream
			return ""
		#
		c = self.currentLine[0].upper()												# first character
		#
		if c >= "0" and c <= "9":													# numeric value ?
			m = re.match("^(\\d+)\\s*(.*)$",self.currentLine)
			self.currentLine = m.group(2)
			return m.group(1)
		#
		if c == "$":																# hexadecimal value ?
			m = re.match("^\\$([0-9a-fA-F]+)\\s*(.*)$",self.currentLine)
			if m is None:
				raise AmoralException("Bad hexadecimal constant")
			self.currentLine = m.group(2)
			return str(int(m.group(1),16))				
		#
		if c == "'":																# character constant
			m = re.match("^\\'(.)\\'\\s*(.*)$",self.currentLine)
			if m is None:
				raise AmoralException("Bad character constant")
			self.currentLine = m.group(2)
			return str(ord(m.group(1)))				
		#
		if c == '"':																# string constant
			m = re.match('^\\"(.*?)\\"\\s*(.*)$',self.currentLine)
			if m is None:
				raise AmoralException("Bad string constant")
			self.currentLine = m.group(2)
			return '"'+m.group(1)
		#
		if c >= "A" and c <= "Z":													# identifier.
			m = re.match('^([A-Za-z0-9\\_\\.]+)\\s*(.*)$',self.currentLine)
			self.currentLine = m.group(2)
			return m.group(1).lower()
		#
		if self.currentLine[:2] in self.doubleTokens:								# 2 char punctuation
			s = self.currentLine[:2]
			self.currentLine = self.currentLine[2:].strip()
			return s
		#
		s = self.currentLine[0]
		self.currentLine = self.currentLine[1:].strip()
		return s
		#
		raise AmoralException("Cannot parse line")
	#
	#		Put an element back.	
	#	
	def put(self,element):
		if element != "":
			self.parseObjectStack.append(element)
	#
	#		Check if completed
	#
	def isDone(self):
		return self.stream.isDone() and self.currentLine == "" and len(self.parseObjectStack) == 0
	#
	#		Preprocess line.
	#
	def processLine(self,s):
		s = s if s.find("#") < 0 else s[:s.find("#")]								# remove comments
		return s.replace("\t"," ").strip()											# handle tabs and strip

if __name__ == "__main__":
	src = """
	#
	#	New stuff
	#
		45 999 0 $2A $10FF '*' 'A'
		"Hello" ""
		Cat hello.world point_42

		>> > != @name+9 ==
	""".split("\n")
	pa = Parser(TextStream(src))
	while not pa.isDone():
		print("[[ "+pa.get()+" ]]")

