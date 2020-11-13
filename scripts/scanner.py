# *******************************************************************************************
# *******************************************************************************************
#
#       File:           scanner.py
#       Date:           13th November 2020
#       Purpose:        Scans runtime source for command/unary markers.
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import sys,re,os

commands = {}
entries = {}

for root,dirs,files in os.walk(".."+os.sep+"runtime"):
	for f in [x for x in files if x.endswith(".asm")]:
		for l in [x for x in open(root+os.sep+f).readlines() if x.find(";;") >= 0]:
			m = re.match("^(.*?)\\:\\s*\\;\\;\\s+([a-zA-Z]+)\\s+\\$([0-9a-fA-F]+)\\s*$",l)
			assert m is not None,"Fails "+l+" in "+f
			opcode = int(m.group(3),16)
			entry = opcode & 15 if opcode < 0xF0 else (opcode & 15)+16
			assert opcode not in commands,"Duplicate "+l+" in "+f
			assert entry not in entries,"Duplicate "+l+" in "+f
			commands[opcode] = { "mnemonic":m.group(2),"label":m.group(1),"entry":entry,"opcode":opcode }
			entries[entry] = commands[opcode]
#
#		Create jump table
#
h = open(".."+os.sep+"runtime"+os.sep+"generated"+os.sep+"jumptable.inc","w")
h.write(";\n;\tAutomatically generated\n;\n")
for i in range(0,32):
	n = i + 0x80 if i < 16 else i+0xE0
	if i not in entries:
		h.write("\t.word {0:24} ; ${1:02x} {2}\n".format("OpcodeError",n,"?"))
	else:
		h.write("\t.word {0:24} ; ${1:02x} {2}\n".format(entries[i]["label"],n,entries[i]["mnemonic"]))		
h.close()		