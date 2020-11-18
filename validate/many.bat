@echo off
call test.bat

:test
python gentest.py
python ..\bin\amoral.zip -s -o test.prg test.amo
..\bin\x16emu -debug -prg test.prg -scale 2 -run
del *.bin
goto test