# azure-search-documents — Architecture

For everything related to `_patch.py` (the map, patterns, per-file inventory), see [customizations.md](customizations.md).

## Source Layout

Package: `sdk/search/azure-search-documents/`

```
tsp-location.yaml          # TypeSpec spec pointer (commit SHA, directory, repo)
pyproject.toml             # Package metadata, version, dependencies
CHANGELOG.md               # Release notes
assets.json                # Test recording tag
azure/search/documents/    # Source code (generated + handwritten — see customizations.md)
tests/                     # All tests (sync, async, playback, live)
samples/                   # All samples (sync, async)
```

## Branching Strategy

Two parallel release tracks:

- **Preview releases** — build from main, so the latest preview contains all features. New branch: `search/<api-version>` (e.g. `search/2026-05-01-preview`).
- **GA releases** — build from the previous GA. New branch: `search/<api-version>-ga` (e.g. `search/2026-05-01-ga`).

## CHANGELOG Conventions

Each release entry uses up to three sub-headings:

- **`### Features Added`** — new APIs, new operations, new optional parameters, new API-version support.
- **`### Breaking Changes`** — removed/renamed types or properties, removed required parameters, removed operations. See section structure below.
- **`### Bugs Fixed`** — fixes to `_patch.py` logic (pagination, encoding, retry, etc.).

### Preview releases

- **Features Added**: New relative to the **previous preview**.
- **Breaking Changes**: Relative to the previous preview. Start with:
  ```
  > These changes do not impact the API of stable versions such as <latest GA version>.
  > Only code written against a beta version such as <latest beta version> may be affected.
  ```

### GA releases

- **Features Added**: New relative to the **previous GA** (not the latest preview).
- **Breaking Changes** has two sections:
  1. **GA-to-GA breaking changes** (before disclaimer): Changes that break compatibility with the previous GA. Listed first, no disclaimer needed.
  2. **Preview-to-GA breaking changes** (after disclaimer): Preview-only items that did not graduate to GA. Start with:
     ```
     > These changes do not impact the API of stable versions such as <previous GA version>.
     > Only code written against a beta version such as <latest beta of this GA's minor> may be affected.
     ```
