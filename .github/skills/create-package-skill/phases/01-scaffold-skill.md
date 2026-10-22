# Phase 1: Scaffold SKILL.md 📝

> 📍 **Phase 1 — Scaffold SKILL.md** | Generate the main skill file.

> 📖 Read `references/skill-template.md` for the full template and the two allowed structure options.

Using the package profile from Phase 0, generate a `SKILL.md` at:
```
sdk/<service>/<package-name>/.github/skills/<package-name>/SKILL.md
```

The skill directory name MUST match the Python distribution package name
(e.g., `azure-search-documents`, `azure-ai-projects`, `azure-mgmt-appconfiguration`).
This is both the `name` in frontmatter and the directory name (vally lint enforces the match).

## Structure decision

From the Phase 0 profile, pick the structure option that fits:

- **Option A — step-by-step workflow** (preferred when the package has multiple non-empty `_patch.py` files, hand-authored utility modules, or a hand-maintained `ApiVersion` enum). This is how `azure-search-documents` is structured.
- **Option B — reference manual** (simpler packages with few customizations; use when Option A would feel padded).

Ask the user to confirm the choice, defaulting to A when any of these are true: >=2 non-empty `_patch.py`; `ApiVersion`/`DEFAULT_VERSION` present in `_patch.py`; hand-authored `Buffered`/`Batching`/`Paged` class detected.

## Content principles (recap)

- **Keep it static** regarding release state (no version numbers, no current default API version) — but **do** include copy-pasteable commands the agent will need.
- **Point to source** for mutable things (API version enum → point at `_patch.py`; generator target → point at `_metadata.json`).
- **Prefer TypeSpec over `_patch.py`** when the customization is expressible in the spec — note this in the customization patterns section.
- **Include MCP tool invocations** where appropriate (`azsdk_package_generate_code`, `azsdk_package_run_check`, etc.). For validation, use `azsdk_package_run_check with checkType="All"`. Include the direct `tsp-client update` CLI fallback for generation since agents routinely run it.

## Required sections — Option A (step-by-step)

### Frontmatter

```yaml
---
name: <package-name>
description: '<Brief description>. WHEN: regenerate <package-name>; modify <package-name>; fix <package-name> bug; add <package-name> feature; <package-name> tsp-client update; edit <package-name> _patch.py.'
---
```

Semicolons separate triggers (YAML-safe). Every trigger should include the distribution package name.

### Intro (2–4 sentences)

State the core premise in plain language:
- The generator never touches `_patch.py`, so customizations survive regeneration.
- But `_patch.py` imports from generated modules, which DO change.
- A rename / new parameter / removed enum value silently breaks `_patch.py`.
- The following steps catch those breaks.

### Step 1 — Run Regeneration

Minimal shell block with `cd sdk/<service>/<package-name>`, then `tsp-client update`
(or `azsdk_package_generate_code`). Mention updating `tsp-location.yaml` with the new
spec commit SHA, and `_metadata.json` if the API version changed.

### Step 2 — Verify Imports in All `_patch.py` Files

Provide import smoke-test commands for the top public symbols (fill from Phase 0 scan):

```bash
python -c "from <namespace> import <TopClient>"
python -c "from <namespace>.aio import <TopClient>"
python -c "from <namespace>.<submod> import <KeyModel>, <KeyEnum>"
```

List every non-empty `_patch.py` file in a tree diagram with its role (one line each).
Tell the agent: if any import fails, a generated class/enum was renamed or removed —
check `references/customizations.md` for the exact import each `_patch.py` depends on.

### Step 3 — Check ApiVersion (only if `ApiVersion` enum exists in a `_patch.py`)

Concrete commands to reconcile `_metadata.json` with the hand-maintained enum:

```bash
python -c "import json; print(json.load(open('_metadata.json'))['apiVersion'])"
grep -A 20 'class ApiVersion' <path-to-_patch.py>
grep 'DEFAULT_VERSION' <path-to-_patch.py>
```

If the generated API version is not in the enum: add the member, update `DEFAULT_VERSION`,
update the docstring. Include a round-trip verification:

```bash
python -c "from <namespace>._patch import ApiVersion, DEFAULT_VERSION; print(DEFAULT_VERSION.value)"
```

### Step 4 — Expose New Generated Methods Through `_patch.py`

New generated operations do NOT automatically appear on the public surface in the
shape users expect. For each new method, decide which exposure path applies:

```bash
# What new operations did regeneration add?
git diff --name-only | grep "_operations\.py" | grep -v _patch
git diff <path-to-generated-_operations.py> | grep -E '^\+\s+(async\s+)?def '
```

Exposure paths (pick the one that applies to each new method):

1. **Pass-through via generated mixin inheritance** — if the generated signature is
   already user-friendly, the `_<Client>OperationsMixin` subclass in `_patch.py`
   inherits it automatically. Only verify the method name does NOT collide with an
   existing `_patch.py` override.

2. **Override in the operations mixin** — if the method needs custom paging, custom
   request building, response conversion, or error handling, add the override to
   the `_<Client>OperationsMixin` class in the appropriate `_operations/_patch.py`
   (and the async mirror). Typical triggers: custom `ItemPaged`, request-body
   rewriting, `@search.*` field extraction, 413 batch splitting.

3. **Polymorphic str-or-model wrapper** — for `delete_*` operations on a named
   resource. Accept either a `str` name or the resource model; forward `e_tag` /
   `match_condition` when the caller passes a model.

4. **Create-or-update wrapper** — for `create_or_update_*` operations. Forward
   `prefer="return=representation"`, `match_condition`, and `etag`; plus any
   package-specific flags (e.g., `allow_index_downtime`, `skip_indexer_reset`,
   `skip/disable cache`).

5. **List projection wrapper** — for `list_*` operations that need a `select`
   parameter, a name-only projection via `cls` callback, or a conversion from a
   generated projection type back to the canonical model
   (e.g., `_convert_<X>_response`).

6. **Re-export via `__all__`** — any NEW public symbol defined or overridden in
   `_patch.py` MUST be added to that file's `__all__`. Without this, `patch_sdk()`
   will not surface it and the symbol will be missing from `from <ns> import *`
   and from the `__init__.py` public API. Verify with:
   ```bash
   python -c "import <namespace>; print(sorted(<namespace>.__all__))"
   ```

Reminder: every sync exposure/wrapper needs a matching async mirror under `aio/`.
Skip the categories above that do not apply to this package.

### Step 5 — Check for Model/Enum Changes That Affect Customizations

```bash
git diff <path-to-generated-models-and-enums>
```

List what to watch for, tailored to the package (from Phase 0 scan):
- Renamed enum values → backward-compat aliases in `_patch.py` reference old names
- Changed model constructors → subclassed models in `_patch.py` may break
- New fields on response models → extractor helpers need to be updated
- Changed request models → builder helpers need to wire new parameters through

### Step 6 — Run package validation

Run the full validation suite in one shot:

```
azsdk_package_run_check with checkType="All"
```

Mention what the package- and repo-level config already ignore (typically generated internals, `_vendor/`, `tests/`, `samples/`) so the agent knows errors will originate in `_patch.py` customizations.

### Step 7 — Update Documentation and Samples

**CHANGELOG**:
- Find the topmost `## (Unreleased)` section in `CHANGELOG.md`.
- Add entries under `### Features Added`, `### Breaking Changes`, or `### Bugs Fixed`.
- If no `(Unreleased)` section exists, create one above the latest release with the next version from `_version.py`.
- Include a small example entry block.

**README**:
- Update usage examples for new client classes or operations.
- Update Key Concepts for new resource types.
- Update listed API version in Getting Started if it changed.

### Customization Patterns Reference (inline)

For each hand-written pattern that actually exists in the package (from Phase 0 scan),
add a 2–5 sentence subsection naming the pattern and describing *what it does* and
*what would break it*. Typical patterns:

- Constructor reorder on a public client subclass
- Custom paging (standard `ItemPaged` replaced with a custom iterator)
- Hand-authored batching / buffered sender
- Polymorphic delete / create-or-update pattern
- Backward-compatible enum aliases (camelCase → UPPER_CASE)
- Field builders
- Monkey-patched staticmethod helpers
- Wire-format encoding helpers (e.g., pipe-delimited parameters)

Each subsection should point to the specific `_patch.py` it lives in and, where relevant,
note: "Use `_patch.py` when TypeSpec cannot express the behavior, or when the behavior
is Python-specific. For TypeSpec-level customizations (preferred when possible), see
[typespec-python emitter docs](https://github.com/Azure/autorest.python/blob/main/packages/typespec-python/README.md)."

### Pointer to `references/customizations.md`

Single line / short paragraph telling the agent to read `references/customizations.md`
for the exhaustive file-by-file inventory.

## Required sections — Option B (reference manual)

See `references/skill-template.md` *Option B* for the section list. Apply the same
required content (tree of non-empty `_patch.py`, async parity reminder, import smoke
tests, `ApiVersion` reconciliation, CHANGELOG/README step, per-pattern reference).

## Step 1 — Present

Generate the full SKILL.md content and print it. Fill in package-specific details from
the Phase 0 profile. Mark anything you could not confirm with `<!-- TODO: Verify -->` or
`<!-- TODO: Domain expert to fill in -->`.

## Step 2 — CONFIRM

Question: "Create this SKILL.md now (recommended), edit first, or skip?"

If confirmed, create the skill directory and SKILL.md file.

📍 **Phase 1 complete** | Created: SKILL.md | Next: Phase 2

---
## → Next: Phase 2 — Generate References
Read [02-generate-references.md](02-generate-references.md) and begin immediately.
