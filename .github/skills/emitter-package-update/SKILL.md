---
name: emitter-package-update
description: Automate bumping typespec-python version in emitter-package.json for the Azure SDK for Python repository. Use this skill when the user wants to update @azure-tools/typespec-python to the latest version, create a PR for the version bump, or manage emitter-package.json updates.
---

# Emitter Package Update

Bump `@azure-tools/typespec-python` to the latest version in `emitter-package.json` and create a PR.

## Background

The Python emitter ecosystem consists of two packages:
- **Branded emitter** (`@azure-tools/typespec-python`): Lives in [Azure/typespec-azure](https://github.com/Azure/typespec-azure/tree/main/packages/typespec-python). This is the emitter used for Azure SDK generation.
- **Unbranded emitter** (`@typespec/http-client-python`): Lives in [microsoft/typespec](https://github.com/microsoft/typespec/tree/main/packages/http-client-python). The branded emitter wraps this package.

When `eng/emitter-package.json` is updated on `main`, the [TypeSpec Python Regenerate Tests](../../workflows/typespec-python-regenerate.yml) workflow triggers automatically and regenerates test code at `eng/emitter/gen/`.

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

Extract the target version from the output (e.g., `0.61.3`).

### 3. Create Feature Branch

```bash
git checkout -b bump-typespec-python-{version}
```

Replace `{version}` with the actual version number (e.g., `bump-typespec-python-0.61.3`).

### 4. Update Dependencies

Apply the version update:

```bash
npx npm-check-updates --packageFile eng/emitter-package.json -u
```

Align `@azure-tools/openai-typespec` and `@typespec/openapi3` with the versions pinned in [azure-rest-api-specs/package.json](https://github.com/Azure/azure-rest-api-specs/blob/main/package.json) to ensure consistency between the emitter and the spec repo. Check the spec repo's versions and update `eng/emitter-package.json` accordingly (e.g., set `"@azure-tools/openai-typespec": "1.8.0"` and `"@typespec/openapi3": "1.9.0"` to match).

### 5. Regenerate Config Files

If you have a local clone of `typespec-azure`, regenerate the lock file using the branded emitter's `package.json` to ensure `devDependencies` are aligned:

```bash
tsp-client generate-config-files \
  --package-json=<path-to-local-typespec-azure>/packages/typespec-python/package.json
```

Otherwise, regenerate the lock file only:

```bash
tsp-client generate-lock-file
```

### 6. Commit Changes

```bash
git add eng/emitter-package.json eng/emitter-package-lock.json
git commit -m "bump typespec-python {version}"
```

### 7. Create Pull Request

Push branch and create PR:

```bash
git push -u origin bump-typespec-python-{version}
gh pr create --title "bump typespec-python {version}" --body "Bump @azure-tools/typespec-python to version {version}"
```

### 8. After Merge

Once the PR merges to `main`, the [TypeSpec Python Regenerate Tests](../../workflows/typespec-python-regenerate.yml) workflow triggers automatically because `eng/emitter-package.json` was modified. It will:
1. Install the branded emitter at the version specified in `eng/emitter-package.json`
2. Regenerate all test code
3. Create a follow-up PR with the updated generated files at `eng/emitter/gen/`
4. Tag @iscai-msft and @msyyc as reviewers
