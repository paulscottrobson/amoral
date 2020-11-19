#
#		Build file for runtime.
#
ifeq ($(OS),Windows_NT)
CCOPY = copy
CCOPYQ = >NUL
CMAKE = mingw32-make
S = \\
else
CCOPY = cp
CCOPYQ = 
CMAKE = make
S = /
endif

TESTMODE = 0

.PHONY : all

all : runtime.prg

runtime.prg : $(wildcard *.asm sys/x16/*.asm)
	python ..$(S)scripts$(S)scanner.py
	python ..$(S)scripts$(S)rasm.py
	64tass -D test=$(TESTMODE) -q --m65c02 runtime.asm -o runtime.prg -L runtime.lst
	$(CCOPY) runtime.prg ..$(S)bin $(CCOPYQ)