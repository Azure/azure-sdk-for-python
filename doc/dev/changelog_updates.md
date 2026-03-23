# Documenting Changes with Chronus

This guide explains how to use [Chronus](https://github.com/timotheeguerin/chronus) to document changes in packages that use `pyproject.toml`.

## Overview

Chronus is a changelog management tool used in this monorepo to ensure that every pull request that modifies a package includes a corresponding change description. These change descriptions are later aggregated into the package's `CHANGELOG.md` when a release is made.

The repository configuration lives in [`.chronus/config.yaml`](https://github.com/Azure/azure-sdk-for-python/blob/main/.chronus/config.yaml) at the root of the repository.

## Prerequisites

Chronus is distributed as an npm package. To use it, you need [Node.js](https://nodejs.org/) installed (LTS version recommended). You can then run Chronus without a global install using `npx`:

```bash
npx chronus <command>
```

Alternatively, install it globally:

```bash
npm install -g @chronus/chronus
```

## Adding a Change Description

When you make changes to a package that has a `pyproject.toml`, run `chronus add` from the root of the repository:

```bash
npx chronus add
```

This will interactively:

1. Detect which packages have been modified on your branch (compared to `main`).
2. Prompt you to select the relevant package(s).
3. Prompt you to choose the kind of change from the list below.
4. Ask for a short description of the change.
5. Write a change file under `.chronus/changes/` in the repository root.

### Change Kinds

The following change kinds are defined for this repository:

| Kind          | Version bump | Changelog section  | Description                                     |
|---------------|--------------|--------------------|-------------------------------------------------|
| `breaking`    | major        | Breaking Changes   | Changes that break existing features            |
| `feature`     | minor        | Features Added     | Adds new features                               |
| `deprecation` | minor        | Other Changes      | Deprecates an existing feature (not breaking)   |
| `fix`         | patch        | Bugs Fixed         | Fixes to existing features                      |
| `dependencies`| patch        | Other Changes      | Dependency version bumps                        |
| `internal`    | none         | Other Changes      | Internal changes that are not user-facing       |

> **Note:** Use `internal` for changes that are not visible to SDK consumers (e.g., test improvements, refactoring, CI changes). These will not trigger a version bump.

### Specifying a Package Directly

You can skip the interactive prompt by passing the package path(s) directly:

```bash
npx chronus add sdk/storage/azure-storage-blob
```

### Example Workflow

```bash
# After making changes to azure-storage-blob, add a change description
npx chronus add sdk/storage/azure-storage-blob

# Chronus will prompt you:
# ? What kind of change is this? › fix
# ? Describe the change: › Fixed an issue where upload would fail on large files
```

This creates a file like `.chronus/changes/azure-storage-blob-abc123.md` containing:

```markdown
---
changeKind: fix
packages:
  - sdk/storage/azure-storage-blob
---

Fixed an issue where upload would fail on large files
```

You commit this file along with your code changes.

## Verifying Change Descriptions

To check whether all modified packages have a corresponding change description (e.g., before opening a PR), run:

```bash
npx chronus verify
```


If your changes don't need a changelog entry (e.g., pure documentation or test-only changes unrelated to package behavior), you can add an `internal` change kind entry to satisfy the requirement without bumping the version.

## Viewing the Current Status

To see a summary of all pending changes and the resulting version bumps:

```bash
npx chronus status
```

## Packages Using `pyproject.toml`

Packages in this repository that use `pyproject.toml` (instead of or alongside `setup.py`) are fully supported by Chronus. The `pyproject.toml` is used for package metadata, while the `CHANGELOG.md` in the package directory remains the canonical user-facing changelog.

Chronus reads the package version from the Python package metadata and writes changelog entries into the `CHANGELOG.md` file with `npx chronus changelog`. You do not need to manually edit `CHANGELOG.md` for your changes.

## Further Reading

- [Chronus CLI Reference](https://github.com/timotheeguerin/chronus/blob/main/docs/cli.md)
- [Chronus Change Kinds](https://github.com/timotheeguerin/chronus/blob/main/docs/change-kinds.md)
- [Azure SDK Release Process](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/release.md)
- [Package Version Rules](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/package_version/package_version_rule.md)
