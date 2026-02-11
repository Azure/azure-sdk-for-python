---
name: sdkinternal-py-version-update
description: "Update the azure-ai-contentunderstanding SDK version (beta or GA) and changelog. Use this skill when bumping the package version for a new release, transitioning from preview to GA, or updating the changelog with new entries."
---

# Update SDK Version and Changelog

This skill guides updating the version and changelog for the `azure-ai-contentunderstanding` package. It covers preview (beta) bumps, GA promotions, and changelog best practices.

## Overview

Updating a version involves changes across multiple files. The key principle is:

- **`_version.py`** is the single source of truth for the version number
- **`CHANGELOG.md`** must document all changes for every release
- **`pyproject.toml`** classifiers must reflect beta vs stable status
- **`README.md`** version table must be kept in sync

---

## Version Rules

Follow the [Package Version Rules](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/package_version/package_version_rule.md):

### Determine Preview vs Stable

- If the SDK's API version contains "preview" (e.g., `2020-01-01-preview`), the package version **must be preview** (beta).
- Otherwise, it **should be stable** (GA).
- Preview versions use a `b` suffix: `1.0.0b1`, `1.0.0b2`, etc.
- Stable versions have no suffix: `1.0.0`, `1.1.0`, etc.

### Calculate the Next Version

| Previous Version | Next Version Type | Change Type       | Next Version  |
|------------------|-------------------|-------------------|---------------|
| `x.y.zbN`        | Preview           | Any               | `x.y.zbN+1`  |
| `x.y.z`          | Preview           | Breaking change   | `x+1.0.0b1`  |
| `x.y.z`          | Preview           | New feature       | `x.y+1.0b1`  |
| `x.y.z`          | Preview           | Bugfix only       | `x.y.z+1b1`  |
| Any preview      | Stable (first GA) | N/A               | `1.0.0`       |
| `x.y.z` (stable) | Stable            | Breaking change   | `x+1.0.0`    |
| `x.y.z` (stable) | Stable            | New feature       | `x.y+1.0`    |
| `x.y.z` (stable) | Stable            | Bugfix only       | `x.y.z+1`    |

### Examples

- `1.0.0b1` → next preview → `1.0.0b2`
- `1.0.0b1` → first GA → `1.0.0`
- `1.0.0` → new feature (stable) → `1.1.0`
- `1.0.0` → breaking change preview → `2.0.0b1`

---

## Files to Change

### 1. `_version.py` — Version String (REQUIRED)

**Path:** `azure/ai/contentunderstanding/_version.py`

This is the **single source of truth**. `pyproject.toml` reads the version dynamically from here.

```python
# Before (preview):
VERSION = "1.0.0b1"

# After (GA):
VERSION = "1.0.0"

# After (next preview):
VERSION = "1.0.0b2"
```

### 2. `CHANGELOG.md` — Release Notes (REQUIRED)

**Path:** `CHANGELOG.md` (package root)

Add a new section at the top, below `# Release History`. See [Changelog Guidelines](#changelog-guidelines) below for formatting rules.

### 3. `pyproject.toml` — Development Status Classifier (REQUIRED)

**Path:** `pyproject.toml` (package root)

Update the classifier to match the release type:

```toml
# For preview/beta releases:
"Development Status :: 4 - Beta",

# For stable/GA releases:
"Development Status :: 5 - Production/Stable",
```

### 4. `README.md` — SDK Version Table and Content Review (REQUIRED)

**Path:** `README.md` (package root)

Update the SDK version → API version mapping table:

```markdown
| SDK version | Supported API service version |
| ----------- | ----------------------------- |
| 1.0.0       | 2025-11-01                    |
```

When releasing a new version that supports a new API version, **add a new row** rather than replacing the old one, so users on older versions can still find their API version mapping.

#### Content Review Checklist (especially for Beta → GA transitions)

When transitioning from preview to GA, review the README content for preview-specific information that needs revision:

| Check | Preview (Beta) | GA (Stable) |
|-------|----------------|-------------|
| Preview disclaimers/warnings | May have "This is a preview SDK" notices | Remove preview disclaimers |
| Breaking changes warnings | "APIs may change between versions" | Remove or soften language |
| Install command | May have `--pre` flag | Use stable install: `pip install azure-ai-contentunderstanding` |
| Stability notes | "Not recommended for production" | Remove or update for production readiness |
| Feature flags | "Preview feature" labels | Remove preview labels |

Also check related READMEs:
- `samples/README.md` — Remove any preview-specific notes
- `tests/README.md` — Remove any preview-specific notes

---

## Changelog Guidelines

Follow the [Azure SDK Changelog Policy](https://azure.github.io/azure-sdk/policies_releases.html#change-logs).

### Format

```markdown
# Release History

## <version> (<release-date or Unreleased>)

### Features Added
- Description of new features

### Breaking Changes
- Description of breaking changes

### Bugs Fixed
- Description of bug fixes

### Other Changes
- Description of other changes (e.g., dependency updates, docs improvements)
```

### Rules

1. **New entry goes at the top**, directly under `# Release History`
2. **Date format:** `YYYY-MM-DD` (e.g., `2026-02-09`)
3. **Use `Unreleased`** as the date if the release date is not yet finalized: `## 1.0.0 (Unreleased)`
4. **Only include sections that have content** — omit empty sections
5. **Each bullet should be a concise, user-facing description** of the change
6. **Do not delete previous entries** — the changelog is cumulative

### Comparing Versions for Changelog Content

When updating the changelog, compare against the **previous release** to identify what changed. Here's how:

#### Method 1: Git diff against the previous release tag

```bash
# List existing tags for this package
git tag -l "azure-ai-contentunderstanding*"

# Diff against the previous release tag
git diff azure-ai-contentunderstanding_1.0.0b1..HEAD -- sdk/contentunderstanding/azure-ai-contentunderstanding/
```

#### Method 2: Compare generated code changes

After regenerating the SDK from a new TypeSpec commit, compare the generated code:

```bash
# See what changed in the generated code
git diff --stat HEAD -- sdk/contentunderstanding/azure-ai-contentunderstanding/azure/

# Show detailed changes in models
git diff HEAD -- sdk/contentunderstanding/azure-ai-contentunderstanding/azure/ai/contentunderstanding/models/

# Show detailed changes in operations
git diff HEAD -- sdk/contentunderstanding/azure-ai-contentunderstanding/azure/ai/contentunderstanding/operations/
```

#### Method 3: Compare API surface (public exports)

```bash
# Check changes in __init__.py for new/removed exports
git diff HEAD -- sdk/contentunderstanding/azure-ai-contentunderstanding/azure/ai/contentunderstanding/__init__.py

# Check changes in models __init__.py
git diff HEAD -- sdk/contentunderstanding/azure-ai-contentunderstanding/azure/ai/contentunderstanding/models/__init__.py
```

#### What to look for

| Change Type | Where to Look | Changelog Section |
|-------------|---------------|-------------------|
| New models/enums added to `__init__.py` | `models/__init__.py` | Features Added |
| New methods on client | `_client.py`, `_operations/` | Features Added |
| Removed or renamed models/methods | `__init__.py`, `_client.py` | Breaking Changes |
| Changed method signatures (params added/removed/renamed) | `_operations/`, `_client.py` | Breaking Changes (if removed/renamed) or Features Added (if added with defaults) |
| New optional parameters | `_operations/` | Features Added |
| Bug fixes in `_patch.py` | `_patch.py` files | Bugs Fixed |
| Dependency version updates | `pyproject.toml` | Other Changes |
| New samples added | `samples/` | Other Changes |

#### Example: Beta to GA changelog

When promoting from beta to GA, the changelog should summarize the overall capabilities rather than listing every incremental change from beta iterations:

```markdown
## 1.0.0 (2026-02-09)

### Features Added
- GA release of Azure AI Content Understanding client library for Python

### Other Changes
- Promoted from 1.0.0b1 to 1.0.0 (stable/GA)
```

If there were specific changes between the last beta and GA:

```markdown
## 1.0.0 (2026-02-09)

### Features Added
- GA release of Azure AI Content Understanding client library for Python
- Added `new_method` to `ContentUnderstandingClient`
- Added `NewModel` for processing results

### Breaking Changes
- Removed `old_method` from `ContentUnderstandingClient`
- Renamed `OldModel` to `NewModel`

### Bugs Fixed
- Fixed issue where `begin_analyze` would timeout on large files

### Other Changes
- Promoted from 1.0.0b1 to 1.0.0 (stable/GA)
- Updated minimum `azure-core` dependency to 1.37.0
```

---

## Step-by-Step Workflows

### Workflow A: Preview (Beta) Version Bump

For releasing a new preview version (e.g., `1.0.0b1` → `1.0.0b2`):

1. **Update `_version.py`**
   ```python
   VERSION = "1.0.0b2"
   ```

2. **Update `CHANGELOG.md`** — Add new entry at the top:
   ```markdown
   ## 1.0.0b2 (2026-MM-DD)

   ### Features Added
   - Added support for new analyzer type `prebuilt-contractSearch`

   ### Bugs Fixed
   - Fixed deserialization of `KeyFrameTimesMs` property
   ```

3. **`pyproject.toml`** — Keep classifier as `Development Status :: 4 - Beta` (no change needed)

4. **Update `README.md`** version table if the API version changed

### Workflow B: Preview to GA Promotion

For promoting from preview to GA (e.g., `1.0.0b1` → `1.0.0`):

1. **Update `_version.py`**
   ```python
   VERSION = "1.0.0"
   ```

2. **Update `CHANGELOG.md`** — Add GA entry at the top:
   ```markdown
   ## 1.0.0 (2026-MM-DD)

   ### Features Added
   - GA release of Azure AI Content Understanding client library for Python

   ### Other Changes
   - Promoted from 1.0.0b1 to 1.0.0 (stable/GA)
   ```

3. **Update `pyproject.toml`** — Change classifier:
   ```toml
   "Development Status :: 5 - Production/Stable",
   ```

4. **Update `README.md`** version table:
   ```markdown
   | 1.0.0       | 2025-11-01                    |
   ```

### Workflow C: Stable Version Bump

For releasing a new stable version (e.g., `1.0.0` → `1.1.0`):

1. **Update `_version.py`**
   ```python
   VERSION = "1.1.0"
   ```

2. **Update `CHANGELOG.md`** — Add new entry at the top with appropriate sections

3. **`pyproject.toml`** — Keep classifier as `Development Status :: 5 - Production/Stable` (no change needed)

4. **Update `README.md`** version table — Add a new row if the API version changed

---


## Validation Checklist

After updating the version, verify:

- [ ] `_version.py` contains the correct version string
- [ ] `CHANGELOG.md` has a new entry with the correct version, date, and change descriptions
- [ ] `CHANGELOG.md` previous entries are preserved (not deleted)
- [ ] `pyproject.toml` classifier matches: `4 - Beta` for preview, `5 - Production/Stable` for GA
- [ ] `README.md` version table is updated
- [ ] `README.md` content reviewed for preview-specific information (disclaimers, warnings, `--pre` flags)
- [ ] `samples/README.md` checked for preview-specific content
- [ ] `tests/README.md` checked for preview-specific content
- [ ] If using `Unreleased` as date, remember to update it before the actual release
- [ ] Run `tox -e sphinx -c ../../../eng/tox/tox.ini --root .` to validate docs build

---

## CODEOWNERS

When releasing a new version, ensure the [CODEOWNERS](https://github.com/Azure/azure-sdk-for-python/blob/main/.github/CODEOWNERS) file has the correct owners for the package path. The format is:

```
# PRLabel: %Cognitive - Content Understanding
/sdk/contentunderstanding/                                           @owner1 @owner2 @owner3
```

---

## Reference Documentation

- [Package Version Rules](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/package_version/package_version_rule.md) — How to calculate the next version number
- [Release Process](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/release.md) — End-to-end release workflow and PyPI publishing
- [Changelog Policy](https://azure.github.io/azure-sdk/policies_releases.html#change-logs) — Azure SDK changelog formatting guidelines
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html) — Overall Python SDK design guidance
- [Deprecation Process](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/deprecation_process.md) — How to deprecate a package (for reference)
