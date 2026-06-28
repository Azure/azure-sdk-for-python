---
name: emitter-package-update
description: Automate updating the emitter package dependencies in eng/emitter-package.json for the Azure SDK for Python repository, then open a PR. Use this skill when the user wants to update @azure-tools/typespec-python (or any other dependency in emitter-package.json) to the latest version, create a PR for an emitter-package version bump, or manage emitter-package.json updates.
---

# Emitter Package Update

Update the dependencies in `eng/emitter-package.json` to their latest versions — including
`@azure-tools/typespec-python` when a newer release exists — and, if anything changed, open a PR.

## Background

The Python emitter ecosystem consists of two packages:
- **Branded emitter** (`@azure-tools/typespec-python`): Lives in [Azure/typespec-azure](https://github.com/Azure/typespec-azure/tree/main/packages/typespec-python). This is the emitter used for Azure SDK generation.
- **Unbranded emitter** (`@typespec/http-client-python`): Lives in [microsoft/typespec](https://github.com/microsoft/typespec/tree/main/packages/http-client-python). The branded emitter wraps this package.

When `eng/emitter-package.json` is updated on `main`, the [TypeSpec Python Regenerate Tests](../../workflows/typespec-python-regenerate.yml) workflow triggers automatically. It regenerates the test code, pushes it to a `regen/typespec-python-main` source branch, and (because GitHub Actions cannot open PRs in this repo) creates/updates a tracking issue with a pre-filled compare link that a maintainer clicks to open the PR against the [`typespec-python-generated-tests`](https://github.com/Azure/azure-sdk-for-python/tree/typespec-python-generated-tests/eng/tools/azure-sdk-tools/emitter/generated) target branch.

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

Reset and sync the SDK repo to a clean state.
> **Warning:** this discards all uncommitted changes and switches to `main`. Only run it on
> a clone/worktree dedicated to this task, never on a branch with work you want to keep.

```bash
git reset HEAD && git checkout . && git clean -fd && git checkout origin/main && git pull origin main
```

Record the current `@azure-tools/typespec-python` version from `eng/emitter-package.json`
(checking both the `dependencies` and `devDependencies` sections) so you can tell later
whether it was bumped.

### 2. Update Dependencies (still on `main`)

The goal is to update **every** package across **both** the `dependencies` and
`devDependencies` sections of `eng/emitter-package.json` to its latest version — not just
`@azure-tools/typespec-python`. Run `npm-check-updates`, which upgrades all entries in both
sections by default:

```bash
npx npm-check-updates --packageFile eng/emitter-package.json -u
```

> **Restricted-network fallback (e.g. the coding-agent sandbox):** `npm-check-updates`
> needs access to the npm registry, which may be firewalled. If it cannot reach the registry,
> determine the latest `@azure-tools/typespec-python` version from GitHub instead — the
> newest published tag in [Azure/typespec-azure](https://github.com/Azure/typespec-azure/tags)
> (cross-checked against `packages/typespec-python/package.json` on `main`) — and edit
> `eng/emitter-package.json` by hand to that version.

Align `@azure-tools/openai-typespec` and `@typespec/openapi3` with the versions pinned in [azure-rest-api-specs/package.json](https://github.com/Azure/azure-rest-api-specs/blob/main/package.json) to ensure consistency between the emitter and the spec repo. Read the spec repo's current values for those two packages and set them to match in `eng/emitter-package.json` (do not assume specific version numbers — use whatever the spec repo currently pins).

If a specific version was requested, pin `@azure-tools/typespec-python` to that exact
version in `eng/emitter-package.json` (overriding what npm-check-updates picked).

### 3. Check for Changes

Determine whether anything actually changed:

```bash
git diff --quiet -- eng/emitter-package.json
```

**Decision rule:** A PR must be created whenever there is *any* change to `eng/emitter-package.json` — this includes the case where `@azure-tools/typespec-python` itself is unchanged but one or more other dependencies (e.g. `@typespec/*`, `@azure-tools/openai-typespec`) were updated or aligned. Do **not** require a `typespec-python` version bump as a precondition for opening a PR.

- If there **is** a diff (exit code `1`), proceed to step 4 and open a PR.
- Only if there is **no** diff at all (exit code `0`) — meaning every dependency is already up to date — discard the working-tree changes and stop, as there is nothing to commit:

```bash
git checkout -- eng/emitter-package.json
```

### 4. Create Feature Branch

Read the (possibly updated) `@azure-tools/typespec-python` version and compare it with the
value recorded in step 1 to choose names:

- **If typespec-python was bumped** to `{version}`:
  - branch: `bump-typespec-python-{version}`
  - commit / PR title: `bump typespec-python {version}`
  - PR body: `Bump @azure-tools/typespec-python to version {version}`
- **Otherwise** (only other dependencies changed):
  - branch: `update-emitter-package-dependencies`
  - commit / PR title: `update emitter-package dependencies`
  - PR body: `Update emitter-package.json dependencies to their latest aligned versions.`

Create the branch, carrying over the working-tree changes:

```bash
git checkout -b {branch_name}
```

If a branch with that name already exists locally from a previous run, delete it first
(`git branch -D {branch_name}`) — or, if it holds work you want to keep, choose a different
name — before re-creating it.

### 5. Regenerate Lock File

```bash
tsp-client generate-lock-file
```

This regenerates `eng/emitter-package-lock.json`.

> **Restricted-network note:** `tsp-client generate-lock-file` also resolves packages
> from the npm registry. If the registry is unreachable, the lock file cannot be
> regenerated in the sandbox. In that case commit only the `eng/emitter-package.json`
> change (skip the lock file in step 6), and call out in the PR body that
> `eng/emitter-package-lock.json` still needs to be regenerated in an environment with
> npm-registry access before merge.

### 6. Commit Changes

Stage both files when the lock file was regenerated:

```bash
git add eng/emitter-package.json eng/emitter-package-lock.json
git commit -m "{commit_message}"
```

If the lock file was **not** regenerated (restricted-network case in step 5), stage only the
package file instead:

```bash
git add eng/emitter-package.json
git commit -m "{commit_message}"
```

### 7. Create Pull Request

Push the branch and create the PR:

```bash
git push -u origin {branch_name}
gh pr create --title "{pr_title}" --body "{pr_body}"
```

### 8. After Merge

Once the PR merges to `main`, the [TypeSpec Python Regenerate Tests](../../workflows/typespec-python-regenerate.yml) workflow triggers automatically because `eng/emitter-package.json` was modified. It will:
1. Build `http-client-python` from `microsoft/typespec@main` and regenerate all test code
2. Commit the regenerated files to the `regen/typespec-python-main` source branch and force-push it
3. Create or update a tracking issue containing a pre-filled "compare" link (GitHub Actions cannot open PRs in this repo) so a maintainer can open the PR against the [`typespec-python-generated-tests`](https://github.com/Azure/azure-sdk-for-python/tree/typespec-python-generated-tests/eng/tools/azure-sdk-tools/emitter/generated) target branch. Merging that PR does **not** auto-close the tracking issue — close it manually.
   - The tracking issue is assigned to whoever triggered a manual (`workflow_dispatch`) run, or to @iscai-msft and @msyyc for automatic `push`/`schedule` runs.
4. If the workflow fails, a separate failure-notification issue is created (or commented on) and assigned to @iscai-msft and @msyyc
