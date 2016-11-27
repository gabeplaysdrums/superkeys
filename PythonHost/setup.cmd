@echo off
setlocal

copy /y %~dp0..\Debug\SuperKeys.dll %~dp0
copy /y %~dp0..\Debug\SuperKeys.pdb %~dp0
copy /y %~dp0..\Interception\library\x86\interception.dll %~dp0

endlocal