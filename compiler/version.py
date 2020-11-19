# *******************************************************************************************
# *******************************************************************************************
#
#       File:           version.py
#       Date:           16th November 2020
#       Purpose:        Version notes.
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

# *******************************************************************************************
#
#								Version and Update Record
#
# *******************************************************************************************

class VersionInformation(object):
	def getDate(self):
		return "19-Nov-20"
	def getVersion(self):
		return "0.02a"

#	Date 		Version		Notes
#	====		=======		=====
#	16/11/20	0.01a		Development version. Core mostly works, no 6502 code yet. 
#	18/11/20				Function calls now allowed in parameter sequences
# 	19/11/20 	0.02a 		First 6502 code generator working. Added => -> syntax mirrors.
#							Changed [] to [[ ]]
