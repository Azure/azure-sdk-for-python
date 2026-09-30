# SKILL.md Template for Azure SDK for Python Package Skills

Use this template when creating a new package skill. Replace placeholders with package-specific content.

```yaml
---
name: <package-name>
description: '<Brief description>. WHEN: regenerate <package-name>; modify <package-name>; fix <package-name> bug; add <package-name> feature; <package-name> tsp-client update.'
---
```

The `name` field and directory name MUST match the Python distribution package name (e.g., `azure-search-documents`, `azure-ai-projects`, `azure-mgmt-appconfiguration`).

## Content Principles

- **Workflow-first.** The primary audience is an agent running post-regeneration cleanup. Structure the skill so the agent can execute it top-to-bottom: regenerate → verify imports → check API version → check for new operations → check for model/enum changes → lint/type-check → update docs. See *Structure Options* below.
- **Include the commands the agent needs to copy-paste.** `tsp-client update`, `python -c "from <pkg> import X"` import smoke tests, `grep -A 20 'class ApiVersion' <path>`, `git diff --name-only | grep _operations\.py`, `azsdk_package_run_check with checkType="All"`, etc. Do not force the agent to invent commands. "Don't re-document MCP tools" means don't paraphrase an entire MCP tool contract — it does **not** mean omit the one-line invocation an agent is expected to run.
- **Point to source for things that change.** Never hardcode API version strings, release numbers, or the current `DEFAULT_VERSION` value. Point at `_patch.py`, `_metadata.json`, or `_version.py`.
- **Prefer TypeSpec-level customizations over `_patch.py`.** Note when a customization could be expressed by a TypeSpec decorator or emitter option instead.
- **Focus on the convenience layer.** What does the agent need to know to write/maintain `_patch.py`, hand-written utilities, and async parity correctly.

## Structure Options

Pick the one that fits how the package is maintained.

### Option A — Step-by-step workflow (recommended when non-empty `_patch.py` files exist)

Numbered steps the agent executes in order. Canonical skeleton:

1. Run Regeneration (`tsp-client update` or `azsdk_package_generate_code`)
2. Verify Imports in All `_patch.py` Files (import smoke tests)
3. Check ApiVersion (reconcile `_metadata.json` with the hand-maintained `ApiVersion` enum)
4. Check for New Operations That Need Wrappers (git diff generated operations)
5. Check for Model/Enum Changes That Affect Customizations (git diff models/enums)
6. Run package validation (`azsdk_package_run_check with checkType="All"`)
7. Update Documentation and Samples (CHANGELOG, README)

Followed by a *Customization Patterns Reference* section that names and briefly describes each hand-written pattern in the codebase (constructor reorder, polymorphic delete, enum aliases, hand-authored batching sender, custom paging, etc.), each with 2–5 sentences on *what it does* and *what would break it*. Exhaustive file-by-file detail goes to `references/customizations.md`.

### Option B — Reference-manual (simpler packages, or when the workflow is shared at a higher level)

Sections in this order:
1. **Common Pitfalls** — 3–5 most dangerous mistakes, FIRST. Always include: never edit generated files; check `_patch.py` FIRST; maintain async parity.
2. **Architecture** — namespace layout, generated vs hand-written, non-empty `_patch.py` files.
3. **After Regeneration** — error categorization table, API version management, breaking-change detection.
4. **Post-Regeneration Customizations** — per-pattern notes with async-counterpart guidance.
5. **Testing Notes** — optional.
6. **References** — table linking to `references/*.md`.

## Required Content (both options)

Regardless of structure, the skill MUST include:

- Frontmatter with `name` == directory name == distribution package name, and a `WHEN:` trigger list that includes the package name.
- A list or tree of the non-empty `_patch.py` files in the package (the agent's map of "where customizations live"). Example:
  ```
  azure/<ns>/
  ├── _patch.py                    # <role>
  ├── _operations/_patch.py        # <role>
  ├── models/_patch.py             # <role>
  └── aio/…                        # async mirror
  ```
- A reminder that `_patch.py` files are never overwritten by regeneration, but their imports from generated modules CAN break silently.
- Guidance that every sync customization must have an async mirror under `aio/`, and that shared helpers are **imported** (not duplicated) from sync into async.
- Explicit import smoke-test commands for the top public symbols. Example:
  ```bash
  python -c "from <namespace> import <TopClient>"
  python -c "from <namespace>.aio import <TopClient>"
  python -c "from <namespace>.<submod> import <KeyModel>, <KeyEnum>"
  ```
- An `ApiVersion` management note: where the hand-maintained enum and `DEFAULT_VERSION` live, and how to reconcile them with `_metadata.json`'s `apiVersion` after regeneration. Include the exact reconciliation commands, e.g.:
  ```bash
  python -c "import json; print(json.load(open('_metadata.json'))['apiVersion'])"
  grep -A 20 'class ApiVersion' <path-to-_patch.py>
  ```
- A **"Expose New Generated Methods Through `_patch.py`"** step with a diff command and the exposure paths that apply to the package:
  - Pass-through via generated mixin inheritance (just verify no collision)
  - Override in the operations mixin (custom paging, request rewriting, response conversion, error handling)
  - Polymorphic str-or-model `delete_*` wrapper (forward `e_tag` / `match_condition`)
  - `create_or_update_*` wrapper (forward `prefer="return=representation"`, `match_condition`, `etag`, plus package-specific flags like `allow_index_downtime`, `skip_indexer_reset`)
  - List projection wrapper (`select`, name-only via `cls`, generated-projection-to-canonical-model conversion)
  - **`__all__` re-export** — any new public symbol added/overridden in `_patch.py` MUST be appended to that file's `__all__`, otherwise `patch_sdk()` will not expose it. Include the verification command `python -c "import <namespace>; print(sorted(<namespace>.__all__))"`.
  Skip categories that do not apply.
- A "Check for Model/Enum Changes" step listing what a diff of the generated models/enums would break in the customizations (renamed enum values → aliases; changed model constructors → subclass constructors; new fields on response models → extractor helpers; new parameters on request models → builder helpers).
- A linting / type-checking step that runs `azsdk_package_run_check with checkType="All"` (covers mypy, pylint, and the rest of the validation suite in one invocation). Mention what the repo-level / package-level config already ignores so the agent knows where errors will come from.
- A **Documentation and Samples** step covering:
  - CHANGELOG: find the topmost `## (Unreleased)` section; add entries under `### Features Added` / `### Breaking Changes` / `### Bugs Fixed`; create the section above the latest release if missing. Include a small example block.
  - README: when to update usage examples, Key Concepts, and the listed API version.
- A per-pattern *Customization Patterns Reference* naming each hand-written pattern that actually exists in the codebase (NOT a generic list).

## Optional Content

- **Architecture reference file** — only create `references/architecture.md` if the layout is complex enough that readers need a separate map. Most packages are fine describing layout inline with a tree diagram.
- **Testing Notes** — include if the package has non-default test setup (Test Proxy `assets.json`, service-specific fixtures, required env vars).
- **References table** — useful if there are multiple reference files.

## Structural Rules

| Rule | Enforced By |
|---|---|
| `name` matches directory name (= distribution package name) | `vally lint` |
| All markdown links resolve | `vally lint` |
| No orphaned reference files | `vally lint` |
| Code references still exist in codebase | Manual review |
| SKILL.md under 5000 tokens | `vally lint` |
| No version numbers or release-specific info | Manual review |
| Trigger phrases include distribution package name | Manual review |
| No cross-language content | Manual review |
| Async parity reminder present | Manual review |
| Import smoke-test commands present | Manual review |
| CHANGELOG / README update step present | Manual review |
