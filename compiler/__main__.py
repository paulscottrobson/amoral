# *****************************************************************************
# *****************************************************************************
#
#		Name:		__main__.py
#		Purpose:	Macro Assembler main program
#		Created:	8th March 2020
#		Author:		Paul Robson (paul@robsons.org.uk)
#
# *****************************************************************************
# *****************************************************************************

from wrapper import *

if len(sys.argv) > 1:
	cw = CompilerWrapper()
	cw.process(sys.argv[1:])
	cw.complete()
else:
	CompilerWrapper().help()