@echo off
del *.prg
python ..\scripts\scanner.py
if errorlevel 1 goto x
python ..\scripts\gen6502.py
if errorlevel 1 goto x
pushd ..\runtime
call build -q
copy runtime.prg ..\compiler >NUL
popd 
make -s
:x