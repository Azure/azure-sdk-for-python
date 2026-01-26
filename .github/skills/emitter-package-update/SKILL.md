---
name: emitter-package-update
description: Automate bumping typespec-python version in emitter-package.json for the Azure SDK for Python repository. Use this skill when the user wants to update @azure-tools/typespec-python to the latest version, create a PR for the version bump, or manage emitter-package.json updates.
---

# Emitter Package Update

Bump `@azure-tools/typespec-python` to the latest version in `emitter-package.json` and create a PR.

## Prerequisites

Before running this workflow, verify the following tools are installed:

```bash
# Check npm-check-updates
npx npm-check-updates --version

# Check tsp-client
tsp-client --version

# Check GitHub CLI
gh --version
```

If any tool is missing:
- **npm-check-updates**: Install via `npm install -g npm-check-updates`
- **tsp-client**: Install via `npm install -g @azure-tools/typespec-client-generator-cli`
- **GitHub CLI**: Install from https://cli.github.com/ or via `winget install GitHub.cli`

## Workflow

### 1. Prepare Repository

Reset and sync the SDK repo to a clean state:

```bash
git reset HEAD && git checkout . && git clean -fd && git checkout origin/main && git pull origin main
```

### 2. Determine Latest Version

Run npm-check-updates to find the latest `@azure-tools/typespec-python` version:

```bash
npx npm-check-updates --packageFile eng/emitter-package.json
```

Extract the target version from the output (e.g., `0.46.4`).

### 3. Create Feature Branch

```bash
git checkout -b bump-typespec-python-{version}
```

Replace `{version}` with the actual version number (e.g., `bump-typespec-python-0.46.4`).

### 4. Update Dependencies

Apply the version update:

```bash
npx npm-check-updates --packageFile eng/emitter-package.json -u
```

Regenerate the lock file:

```bash
tsp-client generate-lock-file
```

### 5. Commit Changes

```bash
git add eng/emitter-package.json eng/emitter-package-lock.json
git commit -m "bump typespec-python {version}"
```

### 6. Create Pull Request

Push branch and create PR:

```bash
git push -u origin bump-typespec-python-{version}
gh pr create --title "bump typespec-python {version}" --body "Bump @azure-tools/typespec-python to version {version}"
```
