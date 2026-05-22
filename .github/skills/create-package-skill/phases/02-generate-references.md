# Phase 2: Generate References 📚

> 📍 **Phase 2 — Generate References** | Create supporting reference documents.

Only two reference files are ever considered, and only one is required:

| File | Required? | Purpose |
|---|---|---|
| `references/customizations.md` | **Required** if any `_patch.py` file is non-empty, or hand-written utility modules exist | File-by-file inventory of every non-empty `_patch.py` |
| `references/architecture.md` | **Optional** | Only create if the layout is complex enough that a tree diagram inline in SKILL.md is insufficient |

Packages like `azure-search-documents` intentionally ship with `customizations.md` only — the layout fits comfortably inline in SKILL.md.

## references/customizations.md (canonical format)

Use one **section per non-empty `_patch.py` file**, in this structure:

```
## File: `<path>/_patch.py`

### Depends On (from generated code)
- `<generated.module.Symbol>` as `<alias>` (base class / direct import)
- ...

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `<Name>` | class / function / constant | <one line> |
| ...    | ...   | ...            |

### After Regeneration, Verify
- [ ] <specific check, e.g., base class constructor signature unchanged>
- [ ] <specific check, e.g., generated enum member names still match the alias right-hand sides>
- [ ] ...
```

If the file imports shared helpers from the sync partner instead of duplicating them,
add an **Imports From Sync (NOT Duplicated)** subsection listing the symbols.

For each polymorphic-wrapper mixin or multi-method class, use a nested table of
`Method | Customization`.

End the file with a section listing **Empty `_patch.py` Files (No Customizations)** —
just file paths, to tell the agent "no action needed after regeneration" for these.

### Extraction rules

- Read the actual `_patch.py` files. Extract imports, class names, function names,
  method names, and monkey-patched assignments (e.g., `X.Foo = Y.FOO`).
- Use real snippets — do not fabricate code.
- For each `Defines` row, the "What It Does" cell MUST be grounded in the actual source.
- For each `After Regeneration, Verify` checkbox, pick the specific generated symbol
  whose change would break this `_patch.py` — list that symbol by name.
- Do NOT include version numbers, current default API version values, or release-specific info.

### Patterns worth calling out (when they exist)

If any of these patterns appear in the package, each MUST be documented:

- Constructor reorder / parameter swap on a public client subclass
- Custom paging (replacement of `ItemPaged` / `AsyncItemPaged`)
- Hand-authored batching / buffered sender (not generated at all)
- Polymorphic delete / create-or-update taking str or model object
- Backward-compatible enum aliases (assignment statements like `E.Foo = E.FOO`)
- Monkey-patched staticmethod (e.g., `E.Collection = staticmethod(Collection)`)
- Field builders (e.g., `SimpleField`, `SearchableField`, `ComplexField`)
- Response-model conversion helpers (e.g., `_convert_*_response`)
- Request-model builder helpers (e.g., `_build_*_request`)
- Continuation-token pack / unpack helpers

## references/architecture.md (optional)

Only create this file when the layout is complex enough that a tree diagram inline in SKILL.md is insufficient.

If you do create it, include:

- **Repository layout** — directory tree with generated/hand-written annotations
- **Namespace layout** — tree under `<namespace-root>/`
- **Code generation** — toolchain (TypeSpec `@azure-tools/typespec-python` or autorest), `tsp-location.yaml` format, `_metadata.json`
- **Generated vs custom** — table with how to identify each
- **Public client types** — sync/async client classes and file locations
- **API version management** — where the version enum lives, how `_patch.py` interacts with it
- **Key supporting files** — policies, helpers, `mypy.ini`, `assets.json`, etc.
- **Dependencies** — key runtime / dev / test deps
- **Build / test / lint** — MCP tools (`azsdk_package_run_check with checkType="All"`) and any package-specific test entry points (not full command re-documentation)

## Step 1 — Present

Print the proposed reference files content.

## Step 2 — CONFIRM

Question: "Create these reference files now (recommended), edit first, or skip?"

📍 **Phase 2 complete** | Created: references/ | Next: Phase 3

---
## → Next: Phase 3 — Validate
Read [03-validate.md](03-validate.md) and begin immediately.
