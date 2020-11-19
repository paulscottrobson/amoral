@echo off
call make -q
if errorlevel 1 goto x
..\bin\x16emu.exe -debug -prg runtime.prg -scale 2 -run
:x