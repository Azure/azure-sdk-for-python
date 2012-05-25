@echo OFF
REM----------------------------------------------------------------------------
REM Copyright (c) Microsoft Corporation. 
REM
REM This source code is subject to terms and conditions of the Apache License, 
REM Version 2.0. A copy of the license can be found in the License.html file at 
REM the root of this distribution. If you cannot locate the Apache License, 
REM Version 2.0, please send an email to vspython@microsoft.com. By using this 
REM source code in any fashion, you are agreeing to be bound by the terms of the 
REM Apache License, Version 2.0.
REM
REM You must not remove this notice, or any other, from this software.
REM----------------------------------------------------------------------------
cls

echo Running tests...
%SystemDrive%\Python27\python.exe -m unittest discover -p "test_*.py"
set UNITTEST_EC=%ERRORLEVEL%
echo Finished running tests!

if exist "%SystemDrive%\Python27\Scripts\coverage.exe" (
	goto :coverage
)


REM ---------------------------------------------------------------------------
if not exist "%SystemDrive%\Python27\Scripts\pip.exe" (
	echo Cannot do a code coverage run when neither 'coverage' nor 'pip' are installed.
	goto :exit_door
)

echo Installing 'coverage' package...
%SystemDrive%\Python27\Scripts\pip.exe install coverage==3.5.2
echo Finished installing 'coverage' package

REM ---------------------------------------------------------------------------
:coverage
echo Starting coverage run...
%SystemDrive%\Python27\Scripts\coverage.exe run -m unittest discover -p "test_*.py"
%SystemDrive%\Python27\Scripts\coverage.exe html
start %CD%\htmlcov\index.html
echo Finished coverage run!

REM ---------------------------------------------------------------------------
:exit_door
exit /B %UNITTEST_EC%