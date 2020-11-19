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

DEPS = asm6502.py benchmark.py block.py codegenerator.py codemanager.py compiler.py exception.py \
	   identifiers.py aparser.py runtime.py structure.py version.py wrapper.py codegenerator65.py

amoral.zip : $(DEPS)
	python ..$(S)scripts$(S)scanner.py
	python ..$(S)scripts$(S)gen6502.py
	$(CMAKE) -s -C ..$(S)runtime
	$(CCOPY) ..$(S)bin$(S)runtime.prg . $(CCOPYQ)
	zip -q amoral.zip $^ __main__.py $(CCOPYQ)
	$(CCOPY) amoral.zip ..$(S)bin $(CCOPYQ)
