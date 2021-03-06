# *******************************************************************************************
# *******************************************************************************************
#
#       File:           exception.py
#       Date:           14th November 2020
#       Purpose:        Exception class for compiler
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

class AmoralException(Exception):
	pass

AmoralException.LINE = 0
AmoralException.FILE = ""