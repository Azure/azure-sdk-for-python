# CoPilot skills for azure-ai-projects development

## Prerequisite

* Clone the `azure-sdk-for-python` repo to your local machine, if you don't already have it:
  ```
  git clone https://github.com/Azure/azure-sdk-for-python.git
  ```
* Change to the directory `sdk\ai\azure-ai-projects`. 
* Switch to the current feature branch: `git switch feature/azure-ai-projects/2.2.0`.
* Make sure you don't have any files edited or added in this branch (clean `git status` state).

## Emit from TypeSpec and create a PR

### Using GitHub CoPilot in VSCode

* Open VSCode in the current folder.
* Open the CoPilot chat window ("Toggle Chat").
* Ask Copilot to "emit SDK from TypeSpec" or "generate azure-ai-projects SDK" - the `azure-ai-projects-emit-from-typespec` skill will be automatically invoked based on your request.
* Answer some questions and approve execution to go through the workflow

### Using CoPilot CLI or Agency Copilot CLI

* Install [GitHub CoPilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) or [Agency CoPilot CLI](https://aka.ms/agency) (VPN required) if you don't already have it.
* Run CoPilot CLI by typing `copilot`
* Ask Copilot to "emit SDK from TypeSpec" or "generate azure-ai-projects SDK" - the skill will be automatically invoked.
* Answer some questions and approve execution to go through the workflow






