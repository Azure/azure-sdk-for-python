# Copilot Instructions

DO NOT REPEAT ANY STEPS. IF GUIDING A USER, DO NOT REPEAT THE INSTRUCTIONS. THE USER SHOULD BE ABLE TO FOLLOW THE INSTRUCTIONS WITHOUT NEEDING YOU TO REPEAT.

# General Repository Guidelines
- DO check this [website](https://azure.github.io/azure-sdk/python_design.html), and link to pages found there, if possible, when asked about guidelines, or guidance on how to write SDKs. The general guidelines for SDK in this repo are defined there.
- DO ensure folks have the appropriate setup when working with this repository. Use the verify_setup tool in the azure-sdk-validation server.
- Before running any commands in the terminal, ensure the user has a python virtual environment set up and activated. If they do not have one, guide them to create one using `python -m venv <env_name>` and activate it with the appropriate command for their operating system.

# Generating an SDK From TypeSpec

## Agent Context
- Check if there are any TypeSpec project paths in the context. If there are, use those paths to locally generate the SDK from the tspconfig.yaml file. If there 
are no TypeSpec project paths in the context, ask the user for the path to the tspconfig.yaml file.

## Prerequisites
- The user should have a GitHub account and be logged in to GitHub using the GitHub CLI `gh auth login`.
- Make sure the user is on a new branch for their changes. If they are not, prompt them to create a new branch using `git checkout -b <branch name>`.

## Basic Rules:
### When running tsp-client commands:
-  If syncing from a local repo, do not grab a commit hash.
- Do not manually create directories. The command will create the directories for you.
- If asked to sync or generate `package-name` we need to find the path to the package's tsp-location.yaml
 in the azure-sdk-for-python repo and run the command in the same directory.
- If provided a url to a tspconfig.yaml, ensure it has the most recent commit hash of the tspconfig.yaml file
 instead of a branch name like `main`. If the url does not have a commit hash, use the GitHub API to get the most recent commit hash of the tspconfig.yaml file.
  If you are unable to do this, ask the user to provide the correct url.
   `curl -s "https://api.github.com/repos/Azure/azure-rest-api-specs/commits?path=,path to tspconfig.yaml>&per_page=1"`
- Ensure that node, python, tox and the required dependencies are installed in your environment

### Following the steps:
- Do follow the steps in the order they are given.
- Do not skip any steps unless the user explicitly asks to skip a step.
- Do complete each step as described in the instructions before moving on to the next step.
- DO NOT REPEAT THE INSTRUCTIONS. The user should be able to follow the instructions without needing to repeat them.

## Steps to Generate:
Here is the order of steps to follow when generating an SDK from TypeSpec: Verify Environment, Generate SDK, Static Validation, Cleanup of the SDK, Commit and Push the Changes, Manage Pull Requests, Finalize the Process.

### STEP 1 - Verify Environment:
- Use the `verify_setup` tool in the azure-sdk-validation server to check if the correct dependencies are installed.
   - If the user is missing any dependencies, prompt them to install the missing dependencies before moving on to the next step.

### STEP 2 - Generate SDK:
- The typspec-python mcp server tools should be used to generate the SDK.
- If the user gives a local path, run only the local mcp tools using the path to the tspconfig.yaml file in the local azure-rest-api-specs repo.
- If any of the commands fail, check the error message and guide the user to fix the issue.
   - If a command fails due to a TypeSpec error, direct the user back to the TypeSpec in the azure-rest-api-specs repo to fix the error.

### STEP 3 - Static Validation:
- Use the tox mcp tool from the azure-sdk-validation server to run the static validations. 
- DO provide a summary of the results and any errors or warnings that need to be addressed after each validation step.
- If any validation run fails, fix it and rerun that step before running the next validation.
- Run pylint validation step using tox: `tox -e pylint -c [path to tox.ini] --root .`
- Run mypy type checking step using tox: `tox -e mypy -c [path to tox.ini] --root .`
- Run pyright validation step using tox: `tox -e pyright -c [path to tox.ini] --root .`
- Run verifytypes validation step using tox: `tox -e verifytypes -c [path to tox.ini] --root .`

### STEP 4 - Update documentation:
- Create a CHANGELOG.md entry for the changes made. If there is no CHANGELOG.md file, create one in the root directory of the package. 
- Confirm that the package version in the most recent CHANGELOG entry is correct based on the API spec version and the last released package version. 
If the package version is not correct, update it in _version.py and the CHANGELOG entry.

### STEP 5 - Commit and Push the Changes
- Display the list of changed files in the repository and prompt the user to confirm the changes. Ignore uncommitted changes in .github and .vscode folders.
   - If the user confirms:
      - Prompt the user to commit the changes:
         - Run `git add <changed files>` to stage the changes.
         - Run `git commit -m "<commit message>"` to commit the changes.
      - Push the changes to the GitHub remote, ensuring the branch name is not "main."
         - Run `git push -u origin <branch name>` to push the changes.
         - If the push fails due to authentication, prompt the user to run `gh auth login` and retry the push command.
         - If the user does not confirm, prompt them to fix the changes and re-run validation.

### STEP 6 - Manage Pull Requests
- Check if a pull request exists for the current branch:
   - If a pull request exists, inform the user and display its details.
   - If no pull request exists:
      - Ensure the current branch name is not "main." If it is, prompt the user to create a new branch using `git checkout -b <branch name>`.
      - Push the changes to the remote branch. If the branch does not exist on GitHub, create it and push the changes.
      - Generate a title and description for the pull request based on the changes. Prompt the user to confirm or edit them.
      - Prompt the user to select the target branch for the pull request, defaulting to "main."
      - Create the pull request in DRAFT mode with the specified project, target branch, title, and description.
      - Always return the link to the pull request to the user.
   - Retrieve and display the pull request summary, including its status, checks, and comments. Highlight any action items.

### STEP 7 - Finalize the Process
 - Do return the url to the created pull request for the user to review.
 - Do prompt the user to hand off back to the azure-rest-api-specs Agent: 
 `Use the azure-rest-api-specs agent to handle the rest of the process and provide it the pull request.`

# Pylint

## Running Pylint
- When asked how to run pylint, or given a command to run pylint, DO check [this website](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md) and guide the user based on the information you find there. 
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