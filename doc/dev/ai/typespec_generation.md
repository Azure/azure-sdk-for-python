# TypeSpec Generation with AI Agent


## Pre-Requisites
Before generating an SDK with TypeSpec, please ensure you have met the following prerequisites:

1.  **Authenticate with GitHub CLI:**
    Run `gh auth login` in your terminal and follow the prompts to authenticate.
2.  **Create and switch to a feature branch:**
    It's important to work on a feature branch, not the `main` branch. If you haven't already, create and switch to a new branch:
    ```bash
    git checkout -b <your-new-branch-name>
    ```
    Replace `<your-new-branch-name>` with a descriptive name for your branch.
3. Have `uv` package manager installed in your environment.

## Interacting with Copilot for SDK Generation

This guide outlines how to interact with GitHub Copilot to streamline the Azure SDK for Python generation process using TypeSpec. Copilot will assist you by following the established workflow, running commands, and helping to fix validation issues.

### General Interaction Principles

*   **Be Clear and Specific:** When you ask Copilot to perform a task, be as clear and specific as possible.
*   **Provide Information:** Copilot may ask for information like file paths or confirmation to proceed. Please provide this information promptly.
*   **Review Suggestions:** Always review code changes, commit messages, and PR descriptions suggested by Copilot before approving them.
*   **Follow Instructions:** Copilot will guide you through the process. It will not repeat instructions unnecessarily, so please follow them carefully.

#### Initiating the SDK Generation Process with Copilot

To start the SDK generation process, you should clearly state your intention to Copilot. Here are a few examples of effective initial prompts:

*   "I need to generate a new Python SDK using TypeSpec."
*   "Can you help me generate an Azure SDK for Python SDK from a TypeSpec definition?"
*   "Let's start the TypeSpec SDK generation workflow for Python."
*   If you already know the path to your `tspconfig.yaml`, you can include it: "I want to generate a Python SDK. My `tspconfig.yaml` is located at `<path/to/your/tspconfig.yaml>`."
*   If your TypeSpec project is in a remote repository: "I need to generate a Python SDK from a TypeSpec definition located at the following URL: `<URL_to_tspconfig.yaml_in_remote_repo>`."

Based on your initial prompt, Copilot will then proceed with Phase 1 (Context Assessment) as described below.

### SDK Generation Workflow with Copilot

Here's how Copilot will assist you through each phase and step of the SDK generation process:

**Phase 1: Context Assessment**

*   You will typically start by informing Copilot that you want to generate an SDK.
*   Copilot will first try to determine the location of your TypeSpec project.
    *   If it can find `tspconfig.yaml` paths in the provided context, it will proceed with those.
    *   If not, Copilot will ask you to provide the path to your `tspconfig.yaml` file.

**Phase 2: Prerequisites Check**

*   Copilot will remind you of the necessary prerequisites:
    1.  Ensure you are authenticated with the GitHub CLI (`gh auth login`).
    2.  Ensure you are on a feature branch, not `main`. Copilot may remind you to create one if needed (`git checkout -b <branch_name>`).

**Phase 3: TSP-CLIENT Rules Adherence**

*   Copilot is programmed to follow critical rules for `tsp-client`, such as:
    *   Using local repository paths correctly.
    *   Allowing commands to auto-create necessary directories.
    *   Using commit hashes for URL references to `tspconfig.yaml` if a remote URL is used.

**Execution Sequence (7 Mandatory Steps)**

Copilot will guide you through these steps. It will inform you of expected durations for long-running operations.

**Step 1: Environment Verification**
*   **Your action:** Ask Copilot to start the SDK generation process.
*   **Copilot's action:**
    *   It will first run the `verify_setup` tool to check your development environment.
    *   If dependencies are missing, Copilot will inform you and wait for you to install them before proceeding. It will remind you to activate your Python virtual environment if it seems inactive.

**Step 2: SDK Generation**
*   **Copilot's action:**
    *   Copilot will inform you that this step will take approximately 5-6 minutes.
    *   It will then use the appropriate `typespec-python` MCP server tools to generate the SDK.
        *   If a local `tspconfig.yaml` path was provided or found, it will use that.
    *   If generation commands fail, Copilot will show you the error messages and may suggest common causes or ask you to analyze the TypeSpec errors in your source repository.

**Step 3: Static Validation (Sequential)**
*   **Copilot's action:**
    *   Copilot will inform you that each validation substep (Pylint, MyPy, Pyright, Verifytypes) will take approximately 3-5 minutes.
    *   It will run each validation command sequentially:
        1.  `tox -e pylint ...`
        2.  `tox -e mypy ...`
        3.  `tox -e pyright ...`
        4.  `tox -e verifytypes ...`
    *   After each command, Copilot will:
        *   Provide a summary of the results.
        *   If errors or warnings are found, it will attempt to fix them by editing the relevant files, following Azure SDK guidelines. It will only edit files with reported issues.
        *   It will then rerun the *same validation step* to ensure the fixes were successful.
    *   Copilot will only proceed to the next validation step once the current one passes without issues.
*   **Your action:** Review any changes Copilot makes to fix validation issues.

**Step 4: Documentation Update**
*   **Copilot's action:**
    *   Copilot will assist in creating or updating `CHANGELOG.md`. It will ask you for a summary of changes if needed.
    *   It will verify that the package version in `_version.py` matches the API specification version.
    *   If the version is incorrect, Copilot will update `_version.py` and the `CHANGELOG.md` accordingly.
    *   It will ensure the `CHANGELOG.md` entry date is set to the current date.
*   **Your action:** Provide a concise summary of changes for the changelog when prompted. Review the generated changelog entry.

**Step 5: Commit and Push**
*   **Copilot's action:**
    *   Copilot will show you the list of changed files (ignoring `.github`, `.vscode`, etc.).
    *   It will ask for your confirmation to proceed with the commit.
    *   If you confirm, Copilot will:
        *   Suggest a commit message.
        *   Run `git add <changed_files>`.
        *   Run `git commit -m "<commit_message>"`.
        *   Run `git push -u origin <branch_name>`.
    *   If `git push` fails due to authentication, Copilot will prompt you to run `gh auth login`.
*   **Your action:**
    *   Review the list of changed files.
    *   Review and approve or modify the commit message.
    *   If you reject the commit, Copilot will guide you to fix any outstanding issues and revalidate.

**Step 6: Pull Request Management**
*   **Copilot's action:**
    *   Copilot will check if a Pull Request (PR) already exists for the current branch.
        *   If a PR exists, it will show you its details.
        *   If no PR exists:
            *   It will verify you are not on the `main` branch.
            *   It will ensure changes are pushed to the remote branch.
            *   It will generate a PR title and description based on the changes and commit message.
            *   It will create the PR in DRAFT mode.
            *   It will return the PR link.
    *   Copilot will always display a PR summary, including its status, checks, and any action items.
*   **Your action:** Review the PR title and description. You may need to publish the draft PR manually if you are satisfied.

**Step 7: Handoff**
*   **Copilot's action:**
    *   Copilot will provide the PR URL for your review.
    *   It will then prompt you with the exact text: "Use the azure-rest-api-specs agent to handle the rest of the process and provide it the pull request."
*   **Your action:** Copy the PR URL and use the `azure-rest-api-specs` agent as instructed.

By following this guide and interacting effectively with Copilot, you can significantly accelerate the SDK generation process while ensuring adherence to Azure SDK standards.


### Checking the health status of a library

To get a quick glance of a library's health and whether it can pass CI checks to release the package, you can ask VS Code Copilot to check its health status. For example, while in `Agent` mode, you can say:

`What is the health status of azure-ai-projects?`

This will report the library's status from [aka.ms/azsdk/python/health](https://www.aka.ms/azsdk/python/health) and help identify any blockers for release.
