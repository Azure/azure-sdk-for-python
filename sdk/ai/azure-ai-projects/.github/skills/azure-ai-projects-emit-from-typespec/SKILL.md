---
name: azure-ai-projects-emit-from-typespec
license: MIT
metadata:
  version: "1.0.0"
  distribution: local
description: "Emit the azure-ai-projects Python SDK from TypeSpec, apply post-emitter fixes, update changelog, and create a Pull Request. WHEN: \"emit SDK from TypeSpec\", \"generate azure-ai-projects SDK\", \"update azure-ai-projects from TypeSpec\", \"emit from TypeSpec\", \"regenerate azure-ai-projects\". DO NOT USE FOR: other Azure SDK packages, manual code edits without TypeSpec. INVOKES: azsdk-common-generate-sdk-locally skill, post-emitter-fixes.cmd script, git commands, gh CLI for PR creation."
compatibility:
  requires: "azure-sdk-mcp server, local azure-sdk-for-python clone, git, gh CLI"
---

# Emit azure-ai-projects Python SDK from TypeSpec

This skill guides Copilot through emitting the azure-ai-projects Python SDK from TypeSpec,
applying post-emitter fixes, updating the changelog, installing package from sources and creating a Pull Request.

**Working directory:** `sdk/ai/azure-ai-projects`

**Skills:** This workflow relies on skills defined under `.github/skills/` at the root of the repository. Use those skills for SDK generation, building, changelog updates, and other SDK lifecycle operations instead of running commands directly. In particular:

- **`azsdk-common-generate-sdk-locally`** – For generating SDK from TypeSpec, building, running checks/tests, updating changelog, metadata, and version.

---

## Step 1: Gather information from the user

Ask the user the following questions **one at a time**, waiting for each answer before proceeding.

### 1a. Topic branch name

Ask the user to choose **one** of the following two options for the target topic branch:

1. **Create a new topic branch (with default branch name)**  – Create a new topic branch for the emitted changes. If selected, this default branch name will be used "<github-userid>/<emit-from-typespec-DD-MM-HH-MM>", where `github-userid` is the user's GitHub ID and `DD-MM-HHMM` is the current date-time using date, month, hour and minute. For example, if the GitHub ID is "dargilco" and the current date and time is May 1st, 2026 at 8:13am, the default branch name would be `dargilco/emit-from-typespec-01-05-0813`. This should be the default option, and the default branch name should be displayed. If you press enter without typing anything, this option will be selected.

2. **Create a new topic branch (branch name given by user)** - Ask the user for the branch name. Mention that a common format is "<github-userid>/<work-title>". If the user enters a branch name `feature/azure-ai-projects/2.2.0` then stop and report that they cannot emit directly to the current feature branch.

3. **Emit to current branch** – Emit directly to the current branch without creating a new topic branch. This is not common, but may be necessary if the user is re-running this workflow because of a previous failure, where the topic branch was already created. If the current branch is named `feature/azure-ai-projects/2.2.0` then stop and report that they cannot emit directly to the current feature branch.

### 1b. TypeSpec source

Ask the user to choose **one** of the following three options for the TypeSpec source:

1. **Latest commit on `feature/foundry-release`** – Automatically find the latest commit to the `feature/foundry-release` branch in [Azure/azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) that touched files under `specification/ai-foundry/data-plane/Foundry`, and use that commit hash. This should be the default option. If you press enter without typing anything, this option will be selected.

2. **Local TypeSpec folder** – Emit from a local clone of the [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repository. If selected, ask for the **full folder path** to the TypeSpec project. This is the folder ending with `\specification\ai-foundry\data-plane\Foundry`. If it does not end with that string, stop and report the error to the user. Do not continue.

3. **TypeSpec commit hash** – Emit from a specific commit in the [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repository. If selected, ask for the **full commit SHA** (40 characters).


---

## Step 2: Record the current branch

Before creating the topic branch, record the name of the **current Git branch**. This is the branch that the topic branch will be created from, and the branch the PR will target.

```
git branch --show-current
```

Save this as `BASE_BRANCH`.

---

## Step 3: Create the topic branch

Create the topic branch off the current branch and switch to it:

```
git fetch
git switch -c <topic-branch> origin/<BASE_BRANCH>
```

Replace `<topic-branch>` with the name provided by the user in Step 1a.

---

## Step 4: Emit SDK from TypeSpec

Use the **`azsdk-common-generate-sdk-locally`** skill to generate the SDK code. The skill knows how to invoke `azsdk_package_generate_code` and related MCP tools.

Provide the skill with the TypeSpec source selected by the user. With is either:

- **Local folder:** Pass the local spec repo path for local generation. Or,
- **Commit hash:** Update `commit:` in `tsp-location.yaml` to the full SHA first, then invoke the skill for generation.

Note:
- You are only allowed to use the `tsp-client update` command. Do not use any of the other `tsp-client` commands.
- If you are generating from local TypeSpec folder, do not edit the file `tsp-location.yaml`. Leave it as is. It should not be used by the emitter.
- If you are generating from local TypeSpec folder, make sure that the local folder path you provide `tsp-client update --local-spec-repo` ends with `specification\ai-foundry\data-plane\Foundry`.
- **If the generation fails**, stop and report the error to the user. Do not continue.

---

## Step 5: Run post-emitter fixes

After a successful emit, run the post-emitter fix script located in the `sdk/ai/azure-ai-projects` folder:

```
post-emitter-fixes.cmd
```

This script applies azure-ai-projects-specific corrections to the emitted code (restores `pyproject.toml`, fixes enum names, patches Sphinx doc-string issues, and runs `black` formatting).

**If the script fails**, stop and report the error to the user. Do not continue. Do not attempt to analyze the script failures and fix them with Copilot. The script should be fixed by the engineering team if it is not working.

---

## Step 6: Fix patched code

The emitted code may have introduced another beta sub-client (a new property on class `BetaOperations`). It may have also added another enum value to the existing internal class `_FoundryFeaturesOptInKeys`. This means that the client library needs to set a new HTTP request header when making REST API calls to the service, to opt-in to the new service features which are still in preview. If that's the case, do the following:

* Update the dictionary `_BETA_OPERATION_FEATURE_HEADERS` defined in `azure\ai\projects\models\_patch.py`, to include a new key-value pair to map the new beta sub-client name to the proper value from `_FoundryFeaturesOptInKeys`. If no new beta sub-client was introduced, but a new enum value was added to `_FoundryFeaturesOptInKeys`, you will need to update one of the existing key-value pairs in `_BETA_OPERATION_FEATURE_HEADERS` to a comma-separated join of multiple values from `_FoundryFeaturesOptInKeys`.

* Do a similar change to the dictionary `EXPECTED_FOUNDRY_FEATURES` defined in the test file `tests\foundry_features_header\foundry_features_header_test_base.py`: add a new key-value pair if a new beta sub-client was introduced, or update an existing key-value pair to include the new enum value if no new beta sub-client was introduced. 

* Finally, look at the two files `azure\ai\projects\operations\_patch.py` and `azure\ai\projects\aio\operations\_patch.py`. They define the public `BetaOperations` classes for the sync and async clients. To support a new sub-client, you will need to add a new property to this class with the proper doc string. You will need to update the import statement at the top of the file to import the new sub-client class. And you will need to update `__all__` statement at the bottom of the file to include the new sub-client class name. Follow the examples you see there for `BetaDatasetsOperations` or `BetaSkillsOperations`.

If a new enum value was added to `_AgentDefinitionOptInKeys`, please print a note on screen that mentions which value was added, and tell the user that a review is needed to make sure this new value is properly used. But otherwise continue on.

---

## Step 7: Install package from sources

In the folder `sdk\ai\azure-ai-projects`, run `pip install -e .` to install the package from sources. If there are any errors, stop and report the error to the user. Do not continue.

---

## Step 8: Update CHANGELOG.md

Use the **`azsdk-common-generate-sdk-locally`** skill's changelog capability (`azsdk_package_update_changelog_content`) to update `CHANGELOG.md` in the `sdk/ai/azure-ai-projects` folder with a summary of changes from the TypeSpec emit. Some guidelines to follow:
* Start by examining the public SDK API surface of the latest released version of the azure-ai-projects package. The source code for this version can be found in the Main branch of the `azure-sdk-for-python` repository, in the folder `sdk\ai\azure-ai-projects`. 
* Then compare it to the public SDK API surface of current version in this topic branch. 
* Look at the existing change log from the latest version (if exists) and edit or add to it to capture all the changes you see. If a change log does not exist for the current version at the top of `CHANGELOG.md`, create a new one.
* If a new method was added, there is no need to add the list of all new classes that define the inputs and output of the method. It's enough to mention that the new method was added.
* Show the user the proposed changelog entry and ask for confirmation or edits before saving.

---

## Step 9: Update samples and tests

If there were any breaking changes in existing APIs, like class or method renames, update the samples and tests accordingly to reflect those changes. Changes should be made in the "samples" and "tests" folders under `sdk/ai/azure-ai-projects`.

---

## Step 10: Commit and push

Stage all changes (excluding file names that start with `.env`), commit, and push the topic branch:

```
git add -A -- ':!.env*'
git commit -m "Emit SDK from TypeSpec and apply post-emitter fixes

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push -u origin <topic-branch>
```

---

## Step 11: Create a Pull Request

Create a draft PR from the **topic branch** to the **base branch** (recorded in Step 2):

```
gh pr create --draft --base <BASE_BRANCH> --head <topic-branch> --assignee @me --title "<PR title>" --body "<PR body>"
```

- **Title:** Use a descriptive title such as `[azure-ai-projects] Emit SDK from TypeSpec (<short description>)`.
- **Body:** Include which TypeSpec source was used and a summary of the changelog entry.

Show the user the PR URL when done.

---

## Step 12: Optionally run tests locally

Prompt the user with this message: "Tests will run as part of the Pull Request. However, you can optionally run tests locally in a Python virtual environment, right now. It will take a few minutes. Do you want to run tests locally? (yes/no)"

If the user answers "yes", run all tests from recordings. Follow these guidelines:
* Run tests in a local Python virtual environment. Create this virtual environment if it does not already exists:
  ```
  python -m venv .venv
  ```
  and activate it:
  ```
  .venv\Scripts\activate
  ```
* Show test progress on screen, as tests are run.


