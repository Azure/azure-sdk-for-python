# CoPilot skills for azure-ai-projects development

## General Prerequisite

* Clone the `azure-sdk-for-python` repo to your local machine, if you don't already have it:
  ```
  git clone https://github.com/Azure/azure-sdk-for-python.git
  ```
* Change to the directory `sdk\ai\azure-ai-projects`. 
* Switch to the feature branch staging the next release: `git switch feature/azure-ai-projects/vnext`.
* Make sure you don't have any files edited or added in this branch (clean `git status` state).

## Emit from TypeSpec and create a PR

### Skill Prerequisite

1. Windows machine with PowerShell (Windows PowerShell 5.1+)<br>Install: `winget install --id Microsoft.PowerShell --source winget`
1. Git CLI, configured user identity, and authenticated access to GitHub remote<br>Install: `winget install --id Git.Git --source winget`<br>Configure: `git config --global user.name "<your-name>"` and `git config --global user.email "<your-email>"`
1. GitHub CLI (gh), authenticated (for PR creation)<br>Install: `winget install --id GitHub.cli --source winget`<br>Login: `gh auth login`
1. Python 3.9 or newer (matches pyproject.toml requires-python >=3.9)<br>Install: `winget install --id Python.Python.3 --source winget`
1. `pip` installed<br>Setup/upgrade: `python -m ensurepip --upgrade` and `python -m pip install --upgrade pip`
1. TypeSpec tsp-client command available in PATH (used by skill Step 4)<br>Install: `npm install -g @azure-tools/typespec-client-generator-cli`
1. Node.js + npm (typically required to install/use tsp-client)<br>Install: `winget install --id OpenJS.NodeJS.LTS --source winget`
1. Dependencies for developing azure-ai-projects, per dev_requirements.txt (this covers tools such as black and azpysdk support)<br>Install: `python -m pip install -r dev_requirements.txt`
1. Local clone of Azure/azure-rest-api-specs only if using the local TypeSpec source option<br>Setup: `git clone https://github.com/Azure/azure-rest-api-specs.git`

### Using GitHub CoPilot in VSCode

* Open VSCode in the current folder.
* Open the CoPilot chat window ("Toggle Chat").
* Make sure you are in "Agent" mode.
* Start typing `/` followed by the skill name, like `/azure-ai-projects` and press tab to auto complete it to the designed skill, like `/azure-ai-projects-emit-from-typespec`, then press Enter.
* Answer some questions and approve execution to go through the workflow

### Using CoPilot CLI or Agency Copilot CLI

* Install [GitHub CoPilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) or [Agency CoPilot CLI](https://aka.ms/agency) (VPN required) if you don't already have it.
* Run CoPilot CLI by typing `copilot`
* Start typing `/` followed by the skill name, like `/azure-ai-projects` and press tab to auto complete it to the desired skill, like `/azure-ai-projects-emit-from-typespec`, then press Enter.
* Answer some questions and approve execution to go through the workflow

## Skills

### azure-ai-projects-emit-from-typespec

This skill creates a new topic branch, emits SDK from TypeSpec, runs some post-processing and creates a PR.

### azure-ai-projects-update-changelog

This skill updates the file CHANGELOG.md, comparing the source in the current branch which the source of the latest public release. It does not create a new topic branch or a PR.

### azure-ai-projects-author-samples

This skill compares a newly emitted or merged public API surface with its selected base, then creates or updates idiomatic synchronous and asynchronous Python samples. It also keeps unrecorded samples excluded from the recorded sample harness.

### azure-ai-projects-author-tests

This skill updates existing pytest coverage and authors complete sync/async Test Proxy tests for new behavior. New recorded service tests remain explicitly skipped until a human adds recordings.
