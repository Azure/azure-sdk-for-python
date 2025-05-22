# Copilot Instructions


# General Repository Guidelines
- DO check this [website](https://azure.github.io/azure-sdk/python_design.html), and link to pages found there, if possible, when asked about guidelines, or guidance on how to write SDKs. The general guidelines for SDK in this repo are defined there.
- DO ensure folks have the appropriate setup when working with this repository. Use the verify_setup tool in the azure-sdk-validation server.


# Generating an SDK From TypeSpec

## Agent Context
- Check if there are any TypeSpec project paths in the context. If there are, use those paths to locally generate the SDK from the tspconfig.yaml file. If there 
are no TypeSpec project paths in the context, ask the user for the path to the tspconfig.yaml file. If the user does not have a path, ask them to provide one.

## Prerequisites
- The user should have a GitHub account and be logged in to GitHub using the GitHub CLI `gh auth login`.
- The user should have a GitHub Personal Access Token (PAT) with the `repo` scope.
- Make sure the user is on a new branch for their changes. If they are not, prompt them to create a new branch using `git checkout -b <branch name>`.

## Basic Rules:
### When running tsp-client commands:
-  If syncing from a local repo, do not grab a commit hash.
- Do not manually create directories. The command will create the directories for you.
- If asked to sync or generate `package-name` we need to find the path to the package's tsp-location.yaml
 in the azure-sdk-for-python repo and run the command in the same directory.
- If provided a url to a tspconfig.yaml ensure it has the most recent commit hash of the tspconfig.yaml file
 instead of a branch name like `main`. If the url does not have a commit hash, use the GitHub API to get the most recent commit hash of the tspconfig.yaml file.
  If you are unable to do this, ask the user to provide the correct url.
   `curl -s "https://api.github.com/repos/Azure/azure-rest-api-specs/commits?path=,path to tspconfig.yaml>&per_page=1"`
- Ensure that node, python, tox, and the required dependencies are installed in your environment


### When following the steps to generate an SDK from TypeSpec:
- Do not repeat any steps in the instructions. Instead, follow the steps numerically and provide the user with the results of each step before moving on to the next step.

## Steps to Generate:

### Step 1: Validate the correct environment is set up
- Check if the user has the correct environment set up. If not, guide them to set it up. 
- Using the `verify_setup` tool in the azure-sdk-validation server is a good way to do this.

### Step 2: Run the correct tsp-client command(s):
- The typspec-python mcp server tools should be used to run the commands.
- If the user gives a local path, run only the local mcp tools using the path to the tspconfig.yaml file in the local azure-rest-api-specs repo.
- If any of the commands fail, check the error message and guide the user to fix the issue.
   - If a command fails due to a TypeSpec error, direct the user back to the TypeSpec to fix the error.
- If the user is generating a new package, ensure that the package name is valid and follows the naming conventions for Python packages.

### Step 3: Validate the generated SDK and Fix the issues
   - Installing the newly generated package and its dev_requirements in a .venv and installing tox.
   - Use the tox mcp tool from the azure-sdk-validation server to run the following validations when possible:
      - Running pylint validation using tox: `tox -e pylint -c [path to tox.ini] --root .`
      - Running mypy type checking using tox: `tox -e mypy -c [path to tox.ini] --root .`
      - Running pyright validation using tox: `tox -e pyright -c [path to tox.ini] --root .`
      - Running verifytypes validation using tox: `tox -e verifytypes -c [path to tox.ini] --root .`
   - Fix any issues found during validation.
   - After fixing the issues, run the validation again to ensure that all issues are fixed.
   - Proceed to the next step if all issues are fixed.

### Step 4: Post-Processing of the SDK
- Create a CHANGELOG.md entry for the changes made. If there is no CHANGELOG.md file, create one in the root directory of the package. 
The CHANGELOG entry should look like:

         ## 1.0.0 (YYYY-MM-DD)

         ### Features Added
         - Added a new feature to do X.

         ### Breaking Changes
            - Changed the way Y is done, which may break existing code that relies on the old behavior.

         ### Bugs Fixed
            - Fixed a bug that caused Z to not work as expected.

         ### Other Changes
            - Updated the documentation to reflect the new changes.
            - Refactored the code to improve readability and maintainability.

- Confirm that the package version in the most recent CHANGELOG entry is correct based on the API spec version and the last released package version. 
If the package version is not correct, update it in _version.py and the CHANGELOG entry.

### Step 5: Commit and Push the Changes
- Display the list of changed files in the repository and prompt the user to confirm the changes. Ignore uncommitted changes in .github and .vscode folders.
   - If the user confirms:
      - Prompt the user to commit the changes:
         - Run `git add <changed files>` to stage the changes.
         - Run `git commit -m "<commit message>"` to commit the changes.
      - Push the changes to the GitHub remote, ensuring the branch name is not "main."
         - Run `git push -u origin <branch name>` to push the changes.
         - If the push fails due to authentication, prompt the user to run `gh auth login` and retry the push command.
         - If the user does not confirm, prompt them to fix the changes and re-run validation.

### Step 6: Manage Pull Requests
- Check if a pull request exists for the current branch:
   - If a pull request exists, inform the user and display its details.
   - If no pull request exists:
      - Ensure the current branch name is not "main." If it is, prompt the user to create a new branch using `git checkout -b <branch name>`.
      - Push the changes to the remote branch. If the branch does not exist on GitHub, create it and push the changes.
      - Generate a title and description for the pull request based on the changes. Prompt the user to confirm or edit them.
      - Prompt the user to select the target branch for the pull request, defaulting to "main."
      - Create the pull request in DRAFT mode with the specified project, target branch, title, and description.
   - Retrieve and display the pull request summary, including its status, checks, and comments. Highlight any action items.
   - Return the link to the pull request for the user to review and hand off back to the azure-rest-api-specs Agent.

### Step 7: Finalize the Process
 - Prompt the user to review the pull request and make any necessary changes.
 - If the user is satisfied with the pull request guide them to go back to the TypeSpec project and make any necessary changes.


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