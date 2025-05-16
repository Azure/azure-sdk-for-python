# Copilot Instructions

DO prompt the user to create a virtual environment with `<path_to_python_installation>/python.exe -m venv <environment_name>` and activate it, before running any commands.

# General Repository Guidelines
- DO check this [website](https://azure.github.io/azure-sdk/python_design.html), and link to pages found there, if possible, when asked about guidelines, or guidance on how to write SDKs. The general guidelines for SDK in this repo are defined there.

# Pylint

## Running Pylint
- When asked how to run pylint, or given a command to run pylint, DO check [this website](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md) and guide the user based on the information you find there. 
- DO use a python 3.8 environment that is compatible with the code you are working on. If you are not sure, please ask the user for the python version they are using. 


## Fixing Pylint Warnings

### Dos and Don'ts
- DO use the table in https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md and the code examples as a guide on how to fix each rule. 
- DO refer to the pylint documentation: https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html.


- DO NOT solve a pylint warning if you are not 100% confident about the answer. If you think your approach might not be the best, stop trying to fix the warning and leave it as is.
- DO NOT create a new file when solving a pylint error, all solutions must remain in the current file.
- DO NOT import a module or modules that do not exist to solve a pylint warning.
- DO NOT add new dependencies or imports to the project to solve a pylint warning.
- DO NOT make larger changes where a smaller change would fix the issue.
- DO NOT change the code style or formatting of the code unless it is necessary to fix a pylint warning.
- DO NOT delete code or files unless it is necessary to fix a warning.