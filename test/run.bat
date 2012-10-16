@echo OFF
SETLOCAL
REM----------------------------------------------------------------------------
REM Copyright (c) Microsoft.  All rights reserved.
REM
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.
REM You may obtain a copy of the License at
REM   http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing, software
REM distributed under the License is distributed on an "AS IS" BASIS,
REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM See the License for the specific language governing permissions and
REM limitations under the License.
REM----------------------------------------------------------------------------
cls

if "%PYTHONPATH%" == "" (
	set PYTHONPATH=..\src
) else (
	set PYTHONPATH=%PYTHONPATH%:..\src
)

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