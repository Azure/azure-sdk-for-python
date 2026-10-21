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

This skill updates existing pytest coverage and authors complete sync/async Test Proxy tests for new behavior. New recorded service tests remain enabled so missing-recording errors surface in PR validation and authors can contact the SDK maintainer for help.

### azure-ai-projects-add-sample-test-case

This skill registers one or more existing samples in the recorded sample-test harness using PowerShell. It checks existing test IDs, adds missing include entries or removes exclusions, and creates sync/async folder tests with `servicePreparer` when needed. It previews changes before an explicitly approved apply and does not run samples or create recordings.

### azure-ai-projects-sample-validation

This skill validates exact or wildcard-selected recorded samples through recording, playback, local live execution, or the azure-ai-projects Azure DevOps live-test pipeline. It resolves every matching pytest node, supports repeatable command-line environment overrides, and waits for queued ADO validation to complete.

After a confirmed completed ADO live run, Copilot offers Add, Update, or Skip for independent profiles, one per exact test ID. Saving a profile is separate from assigning it to a Foundry project pipeline or rerunning it.

### azure-ai-projects-test-profiles

This skill configures test profiles without requiring a prior run. Profiles map exact pytest IDs to required environment names and ADO Library value references; they contain no pipeline IDs, endpoint values, or secrets. One manually runnable pipeline per Foundry project endpoint uses the shared stage template, a project value group, and an editable membership list. Configuration can be administered manually or with preview-and-approval PowerShell helpers. An optional master triggers endpoint pipelines only. No custom backend is required; see [manual setup](azure-ai-projects-test-profiles/references/setup.md).

### azure-ai-projects-model-reference-graph

This skill generates structured and readable graphs that trace every generated model through direct references, inheritance, runtime ownership, and public operation methods. It supports model-usage investigation and TypeSpec removal analysis without treating static reachability as proof that a model is safe to remove.

### azure-ai-projects-run-issue-regeneration

This skill orchestrates an unattended TypeSpec regeneration for a GitHub issue already assigned to Copilot (an issue labeled with a `TypeSpec commit` and `Base branch`). It validates those inputs, then runs `azure-ai-projects-emit-from-typespec`, `azure-ai-projects-author-samples`, and `azure-ai-projects-author-tests` in order against the issue assignment's existing working branch and draft pull request, instead of the interactive branch/PR creation those skills use for a human developer. Use the other skills directly for interactive, local regeneration.

Changelog updates are excluded from this workflow. The SDK maintainer runs `azure-ai-projects-update-changelog` separately at their discretion.
