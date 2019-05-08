@echo OFF
SETLOCAL
REM -------------------------------------------------------------------------
REM Copyright (c) Microsoft Corporation. All rights reserved.
REM Licensed under the MIT License. See License.txt in the project root for
REM license information.
REM --------------------------------------------------------------------------
cls

if "%1%" == "" (
	set PYTHONDIR=%SystemDrive%\Python27
) else (
	set PYTHONDIR=%1%
)

if "%PYTHONPATH%" == "" (
	set PYTHONPATH=.
)

set PYTHONPATH=%PYTHONPATH%;..

echo Running tests using %PYTHONDIR%
%PYTHONDIR%\python.exe -m unittest discover -p "test_*.py"


set UNITTEST_EC=%ERRORLEVEL%
echo Finished running tests!


REM ---------------------------------------------------------------------------
:exit_door
exit /B %UNITTEST_EC%