---
name: next-version-update
description: Automate promoting next-* tool versions (pylint, mypy, pyright) to become the current pinned versions in azure-sdk-for-python. Use this skill when the weekly next-* CI checks are passing and you want to update the pinned tool versions for all packages.
---

# Next Version Update

Promote `next-*` tool versions (pylint, mypy, pyright) to become the current pinned versions, update all relevant configuration files, and set new next-* targets for tracking upcoming releases.

## Overview

The repository pins specific versions of pylint, mypy, and pyright and runs weekly `next-*` jobs to proactively detect compatibility issues with upcoming versions. When CI confirms the next-* versions are clean, this skill promotes them to become the current pinned versions.

Files updated in **azure-sdk-for-python**:
- `eng/tox/tox.ini` – pinned versions for `[testenv:pylint]`, `[testenv:mypy]`, `[testenv:pyright]`
- `eng/tools/azure-sdk-tools/azpysdk/pylint.py` – `PYLINT_VERSION` constant
- `eng/tools/azure-sdk-tools/azpysdk/mypy.py` – `MYPY_VERSION` constant
- `eng/tools/azure-sdk-tools/azpysdk/pyright.py` – `PYRIGHT_VERSION` constant
- `pylintrc` – root pylintrc used by the current pylint version
- `eng/pylintrc` – pylintrc used by the `next-pylint` job (update for new next version)
- `doc/analyze_check_versions.md` – version table documentation

Files updated in **azure-sdk-tools** (separate PR):
- `tools/apiview/parsers/python/apistubgen/pylintrc` – pylintrc for apiview stub generator
- `tools/apiview/parsers/python/apistubgen/requirements.txt` – pylint version pin for apiview stub generator

Files updated in **Microsoft/TypeSpec** (separate PR, for any pylint/mypy/pyright version update):
- `packages/compiler/package.json` or emitter-specific `package.json` – pyright version pin used by the TypeSpec compiler and emitters
- Any Python-based tooling configuration files that reference pylint or mypy versions

## Prerequisites

Verify the following before running:

```bash
# Check Python is available
python --version

# Check pip is available
pip --version

# Check GitHub CLI
gh --version
```

## Workflow

### 1. Verify Next-Version CI Is Passing

Before promoting, confirm the next-* weekly analyze jobs have passed for the `http-client-python` (in Microsoft/TypeSpec repo) service and other core (azure-sdk-for-python azure-core/corehttp/azure-mgmt-core) packages. 

Check the Azure DevOps pipeline named **"python - corehttp - tests-weekly"** or similar weekly analyze pipelines. All three of the following jobs must pass (or only have pre-existing failures that are tracked):

- **Run Pylint Next** (uses `next-pylint` tox env)
- **Run MyPy Next** (uses `next-mypy` tox env)
- **Run Pyright Next** (uses `next-pyright` tox env)

Also verify via GitHub issues: the vnext issue creator creates/closes issues per-package. Check that there are no open `next-pylint`, `next-mypy`, or `next-pyright` issues for the core packages.

### 2. Read Current Next Versions

Read the current next-* versions from `doc/analyze_check_versions.md`:

```bash
grep -E "pylint_version|mypy_version|pyright_version" eng/tox/tox.ini
```

Note the **Next Version** values for pylint, mypy, and pyright. These are the versions being promoted to current.

### 3. Determine New Next Versions

Look up the latest available versions on PyPI to set as the new next-* targets:

```bash
# Get latest pylint version
pip index versions pylint 2>/dev/null | head -1

# Get latest mypy version
pip index versions mypy 2>/dev/null | head -1

# Get latest pyright version
pip index versions pyright 2>/dev/null | head -1
```

If `pip index` is unavailable, use:
```bash
pip install pylint== 2>&1 | grep "from versions"
pip install mypy== 2>&1 | grep "from versions"
pip install pyright== 2>&1 | grep "from versions"
```

### 4. Prepare Repository

Reset and sync the SDK repo to a clean state:

```bash
git reset HEAD && git checkout . && git clean -fd && git checkout origin/main && git pull origin main
```

### 5. Create Feature Branch

```bash
git checkout -b bump-next-versions-{YYYYMMDD}
```

Replace `{YYYYMMDD}` with today's date (e.g., `bump-next-versions-20260420`).

### 6. Update `eng/tox/tox.ini`

**Promote next versions to current** (update the `[testenv:pylint]`, `[testenv:mypy]`, `[testenv:pyright]` sections):

In the `[testenv:pylint]` section:
```
pylint_version={OLD_NEXT_PYLINT_VERSION}
```

In the `[testenv:mypy]` section:
```
mypy_version={OLD_NEXT_MYPY_VERSION}
```

In the `[testenv:pyright]` section:
```
pyright_version={OLD_NEXT_PYRIGHT_VERSION}
```

**Set new next-* versions** (update the `[testenv:next-pylint]`, `[testenv:next-mypy]`, `[testenv:next-pyright]` sections):

In the `[testenv:next-pylint]` section:
```
pylint_version={NEW_NEXT_PYLINT_VERSION}
```

In the `[testenv:next-mypy]` section:
```
mypy_version={NEW_NEXT_MYPY_VERSION}
```

In the `[testenv:next-pyright]` section:
```
pyright_version={NEW_NEXT_PYRIGHT_VERSION}
```

### 7. Update `azpysdk` Python Constants

Update the version constants used by the azpysdk CLI:

In `eng/tools/azure-sdk-tools/azpysdk/pylint.py`:
```python
PYLINT_VERSION = "{OLD_NEXT_PYLINT_VERSION}"
```

In `eng/tools/azure-sdk-tools/azpysdk/mypy.py`:
```python
MYPY_VERSION = "{OLD_NEXT_MYPY_VERSION}"
```

In `eng/tools/azure-sdk-tools/azpysdk/pyright.py`:
```python
PYRIGHT_VERSION = "{OLD_NEXT_PYRIGHT_VERSION}"
```

### 8. Update `pylintrc` Files

When pylint's **version** changes, the root `pylintrc` and `eng/pylintrc` may need to be updated to disable new warnings or enable newly-available rules.

**For a major version bump:**

1. Check the pylint changelog for new/renamed rules that affect the codebase.
2. Update `pylintrc` (root) by copying the content from `eng/pylintrc`:
   ```bash
   cp eng/pylintrc pylintrc
   ```
3. Update `eng/pylintrc` for the new next-pylint version:
   - Add any new rules that need to be disabled for the next version.
   - Refer to pylint's changelog: `https://pylint.readthedocs.io/en/stable/whatsnew/`

**For a minor/patch version bump:** Typically no pylintrc changes are needed, but verify by running:
```bash
cd sdk/core/corehttp
tox -e next-pylint
```

### 9. Update `doc/analyze_check_versions.md`

Update the version table to reflect the new pinned versions and next targets:

```markdown
| Tool | Current Version | Next Version | Next Version Merge Date |
|------|-----------------|--------------|-------------------------|
Pylint | {OLD_NEXT_PYLINT_VERSION} | {NEW_NEXT_PYLINT_VERSION} | {TARGET_DATE} |
MyPy | {OLD_NEXT_MYPY_VERSION} | {NEW_NEXT_MYPY_VERSION} | {TARGET_DATE} |
Pyright | {OLD_NEXT_PYRIGHT_VERSION} | {NEW_NEXT_PYRIGHT_VERSION} | {TARGET_DATE} |
```

The `{TARGET_DATE}` should be approximately 12 weeks from today (the date when the next-* versions would be merged if CI passes).

If there is no newer version available yet, use `N/A` for both **Next Version** and **Next Version Merge Date**.

### 10. Update `eng/apiview_reqs.txt`

Update the pylint version used by the apiview stub generator:

```
pylint=={OLD_NEXT_PYLINT_VERSION}
```

> **Note:** The `astroid` and related packages may also need version updates to be compatible with the new pylint version. Run the apistub check locally to verify:
> ```bash
> cd sdk/core/azure-core
> tox -e apistub
> ```

### 11. Commit Changes in azure-sdk-for-python

```bash
git add pylintrc eng/pylintrc eng/tox/tox.ini \
        eng/tools/azure-sdk-tools/azpysdk/pylint.py \
        eng/tools/azure-sdk-tools/azpysdk/mypy.py \
        eng/tools/azure-sdk-tools/azpysdk/pyright.py \
        doc/analyze_check_versions.md \
        eng/apiview_reqs.txt
git commit -m "Promote next-* tool versions: pylint {OLD_NEXT_PYLINT_VERSION}, mypy {OLD_NEXT_MYPY_VERSION}, pyright {OLD_NEXT_PYRIGHT_VERSION}"
```

### 12. Create Pull Request in azure-sdk-for-python

Push branch and create PR:

```bash
git push -u origin bump-next-versions-{YYYYMMDD}
gh pr create \
  --title "Promote next-* tool versions: pylint {OLD_NEXT_PYLINT_VERSION}, mypy {OLD_NEXT_MYPY_VERSION}, pyright {OLD_NEXT_PYRIGHT_VERSION}" \
  --body "Promotes the next-* versions of pylint, mypy, and pyright to the current pinned versions after verifying the weekly CI jobs pass.

## Changes
- pylint: {OLD_PYLINT_VERSION} → {OLD_NEXT_PYLINT_VERSION} (next: {NEW_NEXT_PYLINT_VERSION})
- mypy: {OLD_MYPY_VERSION} → {OLD_NEXT_MYPY_VERSION} (next: {NEW_NEXT_MYPY_VERSION})
- pyright: {OLD_PYRIGHT_VERSION} → {OLD_NEXT_PYRIGHT_VERSION} (next: {NEW_NEXT_PYRIGHT_VERSION})

## Verification
- [ ] Weekly next-pylint CI passes for http-client-python
- [ ] Weekly next-mypy CI passes for http-client-python
- [ ] Weekly next-pyright CI passes for http-client-python"
```

### 13. Update azure-sdk-tools Repository (Separate PR)

For a pylint **version** bump, create a separate PR in the [azure-sdk-tools](https://github.com/Azure/azure-sdk-tools) repository:

1. Clone azure-sdk-tools and create a feature branch:
   ```bash
   cd /path/to/azure-sdk-tools
   git checkout -b bump-apiview-pylint-{OLD_NEXT_PYLINT_VERSION}
   ```

2. Update the pylint version in the apiview stub generator requirements:
   - File: `tools/apiview/parsers/python/apistubgen/requirements.txt`
   - Change `pylint=={OLD_PYLINT_VERSION}` → `pylint=={OLD_NEXT_PYLINT_VERSION}`

3. Update the pylintrc for the apiview stub generator if needed:
   - File: `tools/apiview/parsers/python/apistubgen/pylintrc`
   - Add any new disable entries needed for the new pylint major version.

4. Run the apiview tests to verify:
   ```bash
   cd tools/apiview/parsers/python
   pip install -e . && pytest tests/
   ```

5. Commit and create PR:
   ```bash
   git add tools/apiview/parsers/python/apistubgen/
   git commit -m "bump apiview pylint to {OLD_NEXT_PYLINT_VERSION}"
   git push -u origin bump-apiview-pylint-{OLD_NEXT_PYLINT_VERSION}
   gh pr create --title "bump apiview pylint to {OLD_NEXT_PYLINT_VERSION}" \
     --body "Updates the pylint version used by the apiview stub generator from {OLD_PYLINT_VERSION} to {OLD_NEXT_PYLINT_VERSION}."
   ```

### 14. Update Microsoft/TypeSpec Repository (Separate PR)

For **any** next-* version update (pylint, mypy, or pyright), create a separate PR in the [Microsoft/TypeSpec](https://github.com/microsoft/typespec) repository to keep the tool versions aligned. TypeSpec uses pyright for type-checking its TypeScript packages and may reference pylint/mypy in Python-based tooling.

> **Before starting:** Read the TypeSpec contribution guidelines at https://github.com/microsoft/typespec/blob/main/CONTRIBUTING.md. Key requirements include signing the Microsoft CLA, running `rush update` after dependency changes, and ensuring `rush build` passes.

1. Fork and clone the TypeSpec repository (if not already done):
   ```bash
   gh repo fork microsoft/typespec --clone
   cd typespec
   ```

2. Install Rush (TypeSpec uses Rush for monorepo management):
   ```bash
   npm install -g @microsoft/rush
   ```

3. Create a feature branch that names all tools being updated:
   ```bash
   # Example for all three tools:
   git checkout -b bump-tool-versions-pylint-{OLD_NEXT_PYLINT_VERSION}-mypy-{OLD_NEXT_MYPY_VERSION}-pyright-{OLD_NEXT_PYRIGHT_VERSION}
   ```

4. Find all files that reference the tool versions and update them:

   **For pyright** (used across the TypeScript monorepo):
   ```bash
   # Find package.json files that pin pyright
   grep -r "\"pyright\"" --include="package.json" . | grep -v node_modules
   ```
   Update each occurrence from `{OLD_PYRIGHT_VERSION}` → `{OLD_NEXT_PYRIGHT_VERSION}`.

   **For pylint** (used in any Python tooling):
   ```bash
   # Find requirements files or pyproject.toml files that pin pylint
   grep -r "pylint==" --include="*.txt" --include="*.toml" --include="*.cfg" . | grep -v node_modules
   ```
   Update each occurrence from `{OLD_PYLINT_VERSION}` → `{OLD_NEXT_PYLINT_VERSION}`.

   **For mypy** (used in any Python tooling):
   ```bash
   # Find requirements files or pyproject.toml files that pin mypy
   grep -r "mypy==" --include="*.txt" --include="*.toml" --include="*.cfg" . | grep -v node_modules
   ```
   Update each occurrence from `{OLD_MYPY_VERSION}` → `{OLD_NEXT_MYPY_VERSION}`.

5. Run Rush update to regenerate the lockfile:
   ```bash
   rush update
   ```

6. Run Rush build to verify the update doesn't break anything:
   ```bash
   rush build
   ```

7. Run the type-checking and lint checks to confirm there are no new errors:
   ```bash
   rush check-format
   rush lint
   ```

8. Commit and push the changes:
   ```bash
   git add .
   git commit -m "bump tool versions: pylint {OLD_NEXT_PYLINT_VERSION}, mypy {OLD_NEXT_MYPY_VERSION}, pyright {OLD_NEXT_PYRIGHT_VERSION}"
   git push -u origin bump-tool-versions-pylint-{OLD_NEXT_PYLINT_VERSION}-mypy-{OLD_NEXT_MYPY_VERSION}-pyright-{OLD_NEXT_PYRIGHT_VERSION}
   ```

9. Create the pull request, following the TypeSpec PR template:
   ```bash
   gh pr create \
     --repo microsoft/typespec \
     --title "bump tool versions: pylint {OLD_NEXT_PYLINT_VERSION}, mypy {OLD_NEXT_MYPY_VERSION}, pyright {OLD_NEXT_PYRIGHT_VERSION}" \
     --body "Updates the pinned tool versions across the repo:
   - pylint: {OLD_PYLINT_VERSION} → {OLD_NEXT_PYLINT_VERSION}
   - mypy: {OLD_MYPY_VERSION} → {OLD_NEXT_MYPY_VERSION}
   - pyright: {OLD_PYRIGHT_VERSION} → {OLD_NEXT_PYRIGHT_VERSION}

   ## Checklist
   - [ ] I have signed the Microsoft CLA
   - [ ] \`rush update\` has been run
   - [ ] \`rush build\` passes
   - [ ] No new type or lint errors introduced"
   ```

10. Monitor the PR CI and address any new errors that surface in TypeSpec packages.

> **Note:** If only some tools are pinned in the TypeSpec repo (e.g., TypeSpec may only pin pyright and not pylint/mypy), skip the steps for tools that are not referenced. Check existing issues or PRs (search for `pylint`, `mypy`, `pyright` in open PRs) before opening duplicates.
