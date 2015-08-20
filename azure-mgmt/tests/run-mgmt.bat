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

if "%PYTHONPATH%" == "" (
	set PYTHONPATH=.
)
set PYTHONPATH=%PYTHONPATH%;..\..\azure-common
set PYTHONPATH=%PYTHONPATH%;..\..\azure-mgmt
set PYTHONPATH=%PYTHONPATH%;..\..\azure-mgmt-common
set PYTHONPATH=%PYTHONPATH%;..\..\azure-mgmt-compute
set PYTHONPATH=%PYTHONPATH%;..\..\azure-mgmt-network
set PYTHONPATH=%PYTHONPATH%;..\..\azure-mgmt-resource
set PYTHONPATH=%PYTHONPATH%;..\..\azure-mgmt-storage

echo Running tests using %PYTHONDIR%
%PYTHONDIR%\python.exe -m unittest discover -p "test_mgmt_*.py"


set UNITTEST_EC=%ERRORLEVEL%
echo Finished running tests!


REM ---------------------------------------------------------------------------
:exit_door
exit /B %UNITTEST_EC%