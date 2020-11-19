@echo off
call build
python amoral.zip -s -o test.prg balls.amo
if errorlevel 1 goto x
..\bin\x16emu -debug -prg test.prg -scale 2 -run
:x