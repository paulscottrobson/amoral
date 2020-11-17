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

.PHONY : all

all : amoral.zip

DEPS = asm6502.py benchmark.py block.py codegenerator.py codemanager.py compiler.py exception.py identifiers.py parser.py runtime.py structure.py version.py wrapper.py

amoral.zip : $(DEPS)
	zip -q amoral.zip $^ __main__.py
	$(CCOPY) amoral.zip ..$(S)bin