# CoPilot skills for azure-ai-projects development

## Prerequisite

* Clone the `azure-sdk-for-python` repo to your local machine, if you don't already have it:
  ```
  git clone https://github.com/Azure/azure-sdk-for-python.git
  ```
* Change to the directory `sdk\ai\azure-ai-projects`. 
* Switch to the current feature branch, for example: `git switch feature/azure-ai-projects/2.3.0`.
* Make sure you don't have any files edited or added in this branch (clean `git status` state).

## Emit from TypeSpec and create a PR

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





