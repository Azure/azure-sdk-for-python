---
name: azure-search-documents
description: "**WORKFLOW SKILL** — Orchestrate the full release cycle for azure-search-documents SDK including TypeSpec generation, _patch.py customization audit, testing, linting, changelog, and versioning. WHEN: \"search SDK release\", \"regenerate search SDK\", \"update search API version\", \"search pre-release validation\", \"fix search test failures\", \"search changelog\", \"fix _patch.py breaks\", \"bump ApiVersion\", \"add operation wrappers\". REQUIRES: azure-sdk-mcp tools. FOR SINGLE OPERATIONS: Use azsdk MCP tools directly."
---

# azure-search-documents — Package Skill

## When to Use This Skill

Activate when user wants to:
- Prepare a new GA or preview release
- Regenerate SDK from TypeSpec (new API version or current spec)
- Run pre-release validation (tests, linting, checks)
- Fix `_patch.py` files broken by a regeneration
- Add convenience wrappers for newly-generated operations

## Prerequisites

- Read [references/architecture.md](references/architecture.md) for source layout, branching, and CHANGELOG conventions
- Read [references/customizations.md](references/customizations.md) for the `_patch.py` map, patterns reference, and per-file inventory — this is the catalog you verify against in Phase 2
- Read [references/testing.md](references/testing.md) for running tests and writing new tests
- Azure SDK MCP server must be running (provides `azsdk_*` tools)

## Environment Setup (MANDATORY for venv tools)

Run any command that needs the venv (`python`, `pip`, `azpysdk`, `pytest`) via the `run-in-venv.ps1` wrapper. It activates the package `.venv` for the duration of one call. Plain `git` / `grep` / file commands don't need wrapping.

Set a session alias once, then use the short form:

```powershell
Set-Alias venv .\.github\skills\azure-search-documents\scripts\run-in-venv.ps1

venv azpysdk pylint .
venv python -m pytest tests\
venv pip list
```

Use `python -m pytest` rather than bare `pytest` to avoid stale-shebang issues with relocated venvs. `python -c "..."` lines below must be wrapped the same way.

## Steps

### Phase 0 — Determine Scope

Ask the user:
1. New API version or regeneration of current spec?
2. GA release or beta/preview release?
3. Target version number and release date?

If new API version: get the spec **commit SHA**, **API version string** (e.g., `2026-04-01`), and the **spec PR link** (e.g., a PR in `Azure/azure-rest-api-specs`).

- **commit SHA** → goes into `tsp-location.yaml` for Phase 1.
- **API version string** → drives the `ApiVersion` enum and `DEFAULT_VERSION` update in Phase 2 step 3.
- **spec PR link** → keep on hand for the release PR description and CHANGELOG cross-reference; useful for reviewers tracing the SDK change back to its TypeSpec source.

> [!CAUTION]
> **STOP** if the user cannot provide the commit SHA. Do not guess or use HEAD.

### Phase 1 — Generate SDK

1. If commit SHA is changing, update `commit` in `tsp-location.yaml`.
2. Use `azsdk_package_generate_code` to generate SDK from TypeSpec.

### Phase 2 — Sync Handwritten Code with Generated Code

After regeneration, handwritten code (primarily `_patch.py` files, plus `_version.py` at release time) must be reconciled with whatever changed in the generated layer. Use `git diff` to see exactly what changed, then update `_patch.py` to match.

The `_patch.py` map, customization patterns, and per-file inventory all live in [references/customizations.md](references/customizations.md). Keep it open while working through this phase.

#### 1. Capture full generated diff

```bash
git diff -- azure/search/documents/ ':!*/_patch.py'
```

This tells you exactly what was added, removed, or renamed. Run against the unstaged changes from the regenerator — do **not** diff against `origin/main`, which mixes in unrelated branch history.

#### 2. Smoke-test imports across all entrypoints

If a generated class/enum was renamed or removed, a `_patch.py` import will break. Run:

```powershell
venv azpysdk import_all .
```

This imports every public module under `azure.search.documents` and exits non-zero on the first broken import. For the exact import each `_patch.py` depends on, see the per-file inventory in `customizations.md`.

#### 3. Reconcile `ApiVersion` enum and `DEFAULT_VERSION`

The generated code targets a new API version (read from `_metadata.json`); the hand-maintained `ApiVersion` enum in `_patch.py` must include it. If missing:

1. Add the new member (e.g., `V2026_05_01_PREVIEW = "2026-05-01-preview"`).
2. Update `DEFAULT_VERSION`.
3. Update the `ApiVersion` docstring.
4. Apply the same change in **both sync and async** `_patch.py` files.
5. If `_metadata.json` is stale relative to `DEFAULT_VERSION`, update it manually.

#### 4. Reconcile all `_patch.py` files against the diff

Loop through all 15 `_patch.py` files with the Phase 2 diff handy. For each:

- **Added** APIs → add convenience wrappers, re-exports to `__all__`, or model overrides as needed.
- **Removed** APIs → remove all references. Grep the name across ALL `_patch.py` files to catch the entire call chain (wrapper classes delegate to inner classes).
- **Renamed/changed** APIs → adopt the new name or signature everywhere.
- **Sync + async** — every sync `_patch.py` has an async mirror. Apply identical changes to both.
- **Search both** Python snake_case (`debug_info`) and JSON camelCase (`debugInfo`), case-insensitive.

When deciding whether a newly-generated operation needs a wrapper, the categories that typically do are: **delete** (polymorphic str-or-model), **create-or-update** (`prefer="return=representation"`, `match_condition`, `etag` forwarding), and **list** (may need a `select` or name-only projection). See "Patterns Reference" in `customizations.md` for canonical implementations.

For model/enum diff hotspots (`SearchResult`, `SearchRequest`, `SearchFieldDataType`, subclassed models, renamed enum values), see the per-file Verify checklists and the "Patterns Reference" in `customizations.md` — every customization there names the generated symbols it depends on.

`apiview-properties.json` is regenerated automatically by `azsdk_package_generate_code` (used as `--mapping-path` for `apistubgen`). No manual edits needed; just verify it changed in your diff if the public API surface did.

### Phase 3 — Update and Run Tests

**1. Loop through all test files** with the Phase 2 generated-code diff handy. For each one:

- **Added** APIs → add new tests for new features or operations.
- **Removed** APIs → remove or rewrite tests that call them.
- **Renamed/changed** APIs → update test references to use the new names or signatures.
- Check both sync and async test files.

**2.** Run unit tests, then live tests. See [references/testing.md](references/testing.md) for commands and recording workflow.

**Gate:** All unit and live tests pass.

### Phase 4 — Build, Lint, and Checks

Use MCP tools to validate:

1. `azsdk_package_build_code` — build and detect compilation errors.
2. `azsdk_package_run_check` with `Linting` — run pylint and mypy. Fix any errors in `_patch.py` files. The package's `mypy.ini` and the repo's `pylintrc` already exclude `_generated/`, `_vendor/`, `tests/`, and `samples/`, so only `_patch.py` customizations are checked.
3. `azsdk_package_run_check` with `Changelog`, `Cspell`, `Snippets` — run remaining checks.

> For the one case where editing generated code is permitted (inline `# pylint: disable=` for lint issues), see [`customizations.md` → Editing rules](references/customizations.md#editing-rules).

**Gate:** Build, lint, and all checks pass.

### Phase 5 — Update Changelog

Follow the CHANGELOG conventions in [references/architecture.md](references/architecture.md). Use `azsdk_package_update_changelog_content` to draft entries, then review and adjust.

If no `## <next version> (Unreleased)` section exists in `CHANGELOG.md`, create one above the latest release. Use the next version from `_version.py`.

**Source of truth:** the auto-generated code is authoritative — if something exists in generated code, treat it as present. Fall back to the TypeSpec config in the spec PR only when the generated code is ambiguous.

#### 2-way verification (actual code ↔ our CHANGELOG)

After drafting the CHANGELOG, do a systematic cross-check:

1. **Code → our CHANGELOG**: For every item in actual generated code that changed, verify it's reflected in our CHANGELOG. Use the Phase 2 `azpysdk import_all .` (catches removed/renamed symbols at import time), plus targeted `python -c "from … import X; print(X)"` checks for individual symbols.
2. **Our CHANGELOG → code**: For every item in our CHANGELOG, verify it matches actual code (e.g., removed properties are truly absent, new models actually exist).

#### Sorting

All lists within each CHANGELOG section should be sorted alphabetically by fully qualified name.

### Phase 6 — Update Samples and README

1. **Samples**: Update existing samples and add new ones for any new features or changed APIs.
2. **README**:
   - Add usage examples for new client classes or operations.
   - Update the "Key concepts" section if new resource types were introduced.
   - Update the listed API version in the "Getting started" section if it changed.

### Phase 7 — Update Version and Metadata

Use `azsdk_package_update_version` and `azsdk_package_update_metadata` to bump the version and update package metadata.

## Reference Files

| File | Contents |
|------|----------|
| [references/architecture.md](references/architecture.md) | Source layout, branching, CHANGELOG conventions |
| [references/customizations.md](references/customizations.md) | `_patch.py` map, patterns reference, per-file inventory |
| [references/testing.md](references/testing.md) | Running tests, writing new tests, test recording |
