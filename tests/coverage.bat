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

if "%1%" == "" (
	set PYTHONDIR=%SystemDrive%\Python27
) else (
	set PYTHONDIR=%1%
)

if "%2%" == "" (
	set COVERAGEDIR=htmlcov
) else (
	set COVERAGEDIR=%2%
)

if "%PYTHONPATH%" == "" (
	set PYTHONPATH=..
) else (
	set PYTHONPATH=%PYTHONPATH%;..
)

if exist "%PYTHONDIR%\Scripts\coverage.exe" (
	goto :coverage
)


REM ---------------------------------------------------------------------------
if not exist "%PYTHONDIR%\Scripts\pip.exe" (
	echo Cannot do a code coverage run when neither 'coverage' nor 'pip' are installed.
	goto :exit_door
)

echo Installing 'coverage' package...
%PYTHONDIR%\Scripts\pip.exe install coverage
echo Finished installing 'coverage' package

REM ---------------------------------------------------------------------------
:coverage
echo Starting coverage run using %PYTHONDIR%
%PYTHONDIR%\Scripts\coverage.exe run -m unittest discover -p "test_*.py"
%PYTHONDIR%\Scripts\coverage.exe html -d %COVERAGEDIR%
start %CD%\%COVERAGEDIR%\index.html
echo Finished coverage run!

REM ---------------------------------------------------------------------------
:exit_door
exit /B %UNITTEST_EC%