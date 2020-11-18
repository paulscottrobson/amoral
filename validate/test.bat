@echo off
del *.bin
copy ..\bin\runtime.prg . >NUL
python gentest.py
python ..\bin\amoral.zip -s -o test.prg test.amo
if errorlevel 1 goto x
..\bin\x16emu -debug -prg test.prg -scale 2 -run
del *.bin
:x