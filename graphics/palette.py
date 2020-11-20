# *******************************************************************************************
# *******************************************************************************************
#
#       File:           palette.py
#       Date:           20th November 2020
#       Purpose:        Standard 16 colour palette not designed for NTSC televisions
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import re
#
#       Convert a palette value into 4 bit.
#
def pv(n):
    return int((n+7.5)*15/255.0)
#
#       Convert RGB: n,n,n into 4 bit tuple.
#
def process(p):
    m = re.match("^RGB\\:\\s*(\\d+)\\,\\s*(\\d+)\\,\\s*(\\d+)\\s*$",p)
    assert m is not None,p
    return [int(x) for x in m.groups()]
#
#       Raw RGB colour data for my palette.
#
rawData = """
Black/Transparent.
   RGB: 0, 0, 0 
Red
    RGB: 173, 35, 35 
Green
    RGB: 29, 105, 20 
Yellow
    RGB: 255, 238, 51 
Blue
    RGB: 42, 75, 215 
Purple
    RGB: 129, 38, 192 
Cyan
    RGB: 41, 208, 208 
White
    RGB: 255, 255, 255 

Black
   RGB: 0, 0, 0 
Pink
    RGB: 255, 205, 243 
Lt. Green
    RGB: 129, 197, 122 
Orange
    RGB: 255, 146, 51 
Lt. Blue
    RGB: 157, 175, 255 
Brown
    RGB: 129, 74, 25 
Dk. Gray
    RGB: 87, 87, 87 
Lt. Gray
    RGB: 160, 160, 160 
"""

p = [x.strip() for x in rawData.split("\n") if x.find("RGB") >= 0]
assert len(p) == 16
p = [process(x) for x in p]
#
#       Python format.
#
print("#\n#\tPython format\n#\t\n{0}\n\n".format(str(p)))
#
#       Four bit format.
#
p = [ [pv(x[0]),pv(x[1]),pv(x[2])] for x in p]
p = [ x[2]+x[1]*16+x[0]*256 for x in p]
p = ["{0:04x}".format(x) for x in p]
print("#\n#\tAmoral format\n#\t\n[[\"{0}\"]]\n\n".format(" ".join(p)))

