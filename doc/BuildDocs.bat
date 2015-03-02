call InstallDocDependencies.bat
sphinx-apidoc -e -o .\ref ..\azure
call make.bat html