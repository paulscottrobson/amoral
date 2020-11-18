@echo off
python ..\scripts\scanner.py
python ..\scripts\rasm.py
64tass %* --m65c02 runtime.asm -o runtime.prg -L runtime.lst
