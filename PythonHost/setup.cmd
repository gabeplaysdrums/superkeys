@echo off
setlocal

set _flavor=%~1
if "%_flavor%" == "" set _flavor=Debug
shift /1

copy /y %~dp0..\%_flavor%\SuperKeys.dll %~dp0
copy /y %~dp0..\%_flavor%\SuperKeys.pdb %~dp0
copy /y %~dp0..\Interception\library\x86\interception.dll %~dp0

endlocal