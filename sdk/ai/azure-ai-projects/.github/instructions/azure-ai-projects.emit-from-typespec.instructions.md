# Emit Python SDK from TypeSpec

These instructions guide Copilot through emitting the azure-ai-projects Python SDK from TypeSpec,
applying post-emitter fixes, updating the changelog, and creating a Pull Request.

**Working directory:** `sdk/ai/azure-ai-projects`

**Skills:** This workflow relies on skills defined under `.github/skills/` at the root of the
repository. Use those skills for SDK generation, building, changelog updates, and other SDK
lifecycle operations instead of running commands directly. In particular:

- **`azsdk-common-generate-sdk-locally`** – For generating SDK from TypeSpec, building, running
  checks/tests, updating changelog, metadata, and version.

---

## Step 1: Gather information from the user

Ask the user the following questions **one at a time**, waiting for each answer before proceeding.

### 1a. Topic branch name

Ask the user to choose **one** of the following two options for the target topic branch:

1. **Emit to current branch** – Emit directly to the current branch without creating a new topic branch. 
This is not common, but may be necessary if the user is re-running this workflow because of a previous
failure, where the topic branch was already created.

2. **Create a new topic branch** – Create a new topic branch for the emitted changes. If selected, ask
 for a topic branch name. Mention that the expected format is
`<github-userid>/<work-title>` (e.g. `dargilco/emit-from-typespec-04-29-2026`).

### 1b. TypeSpec source

Ask the user to choose **one** of the following three options for the TypeSpec source:

1. **Local TypeSpec folder** – Emit from a local clone of the
   [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repository.
   If selected, ask for the **full folder path** to the TypeSpec project. This is the folder
   ending with `\specification\ai-foundry\data-plane\Foundry`.

2. **TypeSpec commit hash** – Emit from a specific commit in the
   [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repository.
   If selected, ask for the **full commit SHA** (40 characters).

3. **Latest commit on `feature/foundry-release`** – Automatically find the latest commit
   to the `feature/foundry-release` branch in
   [Azure/azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) that touched
   files under `specification/ai-foundry/data-plane/Foundry`, and use that commit hash.

---

## Step 2: Record the current branch

Before creating the topic branch, record the name of the **current Git branch**. This is
the branch that the topic branch will be created from, and the branch the PR will target.

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

Use the **`azsdk-common-generate-sdk-locally`** skill to generate the SDK code. The skill
knows how to invoke `azsdk_package_generate_code` and related MCP tools.

Provide the skill with the TypeSpec source selected by the user:

- **Local folder:** Pass the local spec repo path for local generation.
- **Commit hash:** Update `commit:` in `tsp-location.yaml` to the full SHA first,
  then invoke the skill for generation.

**If the generation fails**, stop and report the error to the user. Do not continue.

---

## Step 5: Run post-emitter fixes

After a successful emit, run the post-emitter fix script located in the
`sdk/ai/azure-ai-projects` folder:

```
post-emitter-fixes.cmd
```

This script applies azure-ai-projects-specific corrections to the emitted code (restores
`pyproject.toml`, fixes enum names, patches Sphinx doc-string issues, and runs `black`
formatting).

**If the script fails**, stop and report the error to the user. Do not continue. Do not attempt
to analyze the script failures and fix them with Copilot. The script should be fixed by the engineering
team if it is not working.

---

## Step 6: Update CHANGELOG.md

Use the **`azsdk-common-generate-sdk-locally`** skill's changelog capability
(`azsdk_package_update_changelog_content`) to update `CHANGELOG.md` in the
`sdk/ai/azure-ai-projects` folder with a summary of changes from the TypeSpec emit.

Show the user the proposed changelog entry and ask for confirmation or edits before saving.

---

## Step 7: Commit and push

Stage all changes (excluding file names that start with `.env`), commit, and push the topic branch:

```
git add -A -- ':!.env*'
git commit -m "Emit SDK from TypeSpec and apply post-emitter fixes

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push -u origin <topic-branch>
```

---

## Step 8: Create a Pull Request

Create a PR from the **topic branch** to the **base branch** (recorded in Step 2):

```
gh pr create --base <BASE_BRANCH> --head <topic-branch> --title "<PR title>" --body "<PR body>"
```

- **Title:** Use a descriptive title such as
  `[azure-ai-projects] Emit SDK from TypeSpec (<short description>)`.
- **Body:** Include which TypeSpec source was used and a summary of the changelog entry.

Show the user the PR URL when done.
