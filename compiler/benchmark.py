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
from block import *

# *******************************************************************************************
#
#									Run benchmark.
#	
# *******************************************************************************************

def runBenchmark(count,code):
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
	src = """{{ 
				read.timer();print.hex(~);
				times({0}) {{ {1} }}
				read.timer();print.hex(~);
				halt.program();
			}}
	""".format(count,code)

	cb.show = False																	# True to o/p code.
	src = src.split("\n")															# make into parser
	cm.parser = Parser(TextStream(src))												# set the parser (cheat)
	f = cm.blockCompile()															# compile 
	cb.close()																		# close definition
	cb.createApplication(im)														# dump it.

if __name__ == "__main__":

	bm1 = """  var k; times(1000,k) { } """
	bm1Count = 50

	bm2 = """ var k; 0!k while (k <> 1001) { k++!k; } """
	bm2Count = 40

	bm3 = """ var a,k; 0!k while (k <> 1001) { k++!k; k/k*k+k-k!a } """
	bm3Count = 20

	bm4 = """ var a,k; 0!k while (k <> 1001) { k++!k; k/2*3+4-5!a } """
	bm4Count = 20

	runBenchmark(bm4Count,bm4)