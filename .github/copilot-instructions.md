# Copilot Instructions


# General Repository Guidelines
- DO check this [website](https://azure.github.io/azure-sdk/python_design.html), and link to pages found there, if possible, when asked about guidelines, or guidance on how to write SDKs. The general guidelines for SDK in this repo are defined there.
- DO ensure folks have the appropriate setup when working with this repository. Use the verify_setup tool in the azure-sdk-validation server.

When someone asks to run validation on their library, ask them what supported environments they would like to run, such as pylint or mypy. Use the tox tool to run these.

# Generating an SDK From TypeSpec

Initialize and validate a TypeSpec client library for Azure SDK for Python. Please:

1. Generate the SDK from the TypeSpec configuration file at [URL to tspconfig.yaml]. If the URL doesn't contain the latest commit hash, please retrieve it from GitHub API first.

2. After generation is complete, validate the output by:
   - Running pylint validation using tox: `tox -e pylint -c [path to tox.ini] --root .`
   - Running mypy type checking using tox: `tox -e mypy -c [path to tox.ini] --root .`

3. If any errors or warnings are found, provide guidance on fixing them following Azure SDK best practices.

Please use Python 3.9 for compatibility, and refer to the Azure SDK design guidelines (https://azure.github.io/azure-sdk/python_design.html) for any implementation decisions.

<!-- When asked to generate an SDK from TypeSpec, do the following:
- Prompt the user to provide the url to the TypeSpec configuration file (tspconfig.yaml) of the library they are working on. This file is usually located in the root directory of the library.
- If the user passed the url to the tspconfig.yaml file, check if the file exists. If it does not exist, ask them to provide the correct url. We do not need to download the typespec files. The url should have the most recent commit hash of the tspconfig.yaml file instead of a branch name like `main`. If the url does not have a commit hash, use the GitHub API to get the most recent commit hash of the tspconfig.yaml file. If you are unable to do this, ask the user to provide the correct url. `curl -s "https://api.github.com/repos/Azure/azure-rest-api-specs/commits?path=,path to tspconfig.yaml>&per_page=1"`  helpful.
- Please ensure you use the latest commit hash for the file in the URL, install the necessary TypeSpec client generator CLI tool if it's not already present, and then run the initialization command.
- Do not use the `main` branch name in the url. The url should look like this: `https://raw.githubusercontent.com/Azure/azure-sdk-for-python/<commit_hash>/sdk/<service>/<service>/tspconfig.yaml`.
- Then check if the user has the @azure-tools/typespec-client-generator-cli package installed. If not, ask them to install it using the command `npm install -g @azure-tools/typespec-client-generator-cli`.
- Finally use the @azure-tools/typespec-client-generator-core-cli to generate the SDK using the command `npx @azure-tools/typespec-client-generator-cli init --tsp-config <url to tspconfig.yaml file>`
- If the above steps do not work refer to [this website](https://azure.github.io/typespec-azure/docs/howtos/generate-with-tsp-client/intro_tsp_client/) for more information on how to generate the SDK from TypeSpec.
- After we generate the SDK, ensure to validate the output and check for any errors or warnings by running pylint and mypy with their respective tox commands [see here](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox). If there are any issues, please refer to the relevant sections below for guidance on how to fix them. -->

# Pylint

## Running Pylint
- When asked how to run pylint, or given a command to run pylint, DO check [this website](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md) and guide the user based on the information you find there. 
- DO use a python 3.9 environment that is compatible with the code you are working on. If you are not sure, please ask the user for the python version they are using. 
- Do run pylint using the command `tox -e pylint --c <path to tox.ini> --root .` if the user is working on a specific file. The path to the tox.ini file by default is `azure-sdk-for-python/eng/tox/tox.ini`
- For formatting the tox command DO check [this website](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox) and guide the user based on the information you find there.



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


# MyPy

## Running MyPy and Fixing MyPy Warnings
- When asked how to run mypy, or given a command to run mypy, DO check [this website](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox) and guide the user based on the information you find there.
- Do check this website on guidance on how to best fix MyPy issues [website link](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
- DO use a python 3.9 environment that is compatible with the code you are working on. If you are not sure, please ask the user for the python version they are using. 