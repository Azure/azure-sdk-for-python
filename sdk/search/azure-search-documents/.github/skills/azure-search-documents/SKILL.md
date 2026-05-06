---
name: azure-search-documents
description: 'Post-regeneration customization guide for azure-search-documents. Verifies _patch.py imports, ApiVersion, enum aliases, mypy/pylint, and changelog after codegen. WHEN: regenerate azure-search-documents; modify azure-search-documents; fix azure-search-documents bug; add azure-search-documents feature; azure-search-documents tsp-client update; edit azure-search-documents _patch.py.'
---

# azure-search-documents — Post-Regeneration Customization Guide

After running `tsp-client update`, the generated code is a raw skeleton — not a shippable SDK. This skill tells you exactly which `_patch.py` files customize it and how to verify those customizations still work after regeneration.

The generator never touches `_patch.py` files, so your customizations survive regeneration. But they import from generated modules that **do** change. A renamed model, a new parameter, or a removed enum value will silently break a `_patch.py` file. The verification steps below catch those breaks.

## Step 1: Run Regeneration

```bash
cd sdk/search/azure-search-documents

# Update tsp-location.yaml with the new spec commit SHA, then:
tsp-client update
# or: azsdk_package_generate_code

# If the API version changed, _metadata.json updates automatically;
# reconcile the hand-maintained ApiVersion enum in Step 3.
```

## Step 2: Verify Imports in All `_patch.py` Files

Every non-empty `_patch.py` imports from generated modules. After regeneration, check those imports still resolve:

```bash
python -c "from azure.search.documents import SearchClient, SearchIndexingBufferedSender, ApiVersion, DEFAULT_VERSION, IndexDocumentsBatch"
python -c "from azure.search.documents.aio import SearchClient, SearchIndexingBufferedSender"
python -c "from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient"
python -c "from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient"
python -c "from azure.search.documents.indexes.models import SearchField, SearchFieldDataType, SimpleField, SearchableField, ComplexField, KnowledgeBase"
python -c "from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient"
python -c "from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient"
```

If any fail, a generated class/enum was renamed or removed. See `references/customizations.md` for the exact import each `_patch.py` depends on.

The `_patch.py` files that have customizations (others are empty boilerplate):

```
azure/search/documents/
├── _patch.py                          # SearchClient subclass, SearchIndexingBufferedSender, ApiVersion enum, DEFAULT_VERSION
├── _operations/_patch.py              # SearchItemPaged, search(), custom index_documents/413 splitting, continuation-token helpers
├── models/_patch.py                   # IndexDocumentsBatch, RequestEntityTooLargeError
├── aio/_patch.py                      # Async SearchClient, async SearchIndexingBufferedSender
├── aio/_operations/_patch.py          # AsyncSearchItemPaged, async search(), reuses sync helpers
├── indexes/_patch.py                  # SearchIndexClient, SearchIndexerClient (audience kwarg plumbing)
├── indexes/_operations/_patch.py      # Polymorphic delete/create-or-update, list_index_names, _convert_index_response
├── indexes/models/_patch.py           # SearchField(hidden), field builders, SearchIndexerDataSourceConnection overloads, KnowledgeBase, SearchFieldDataType aliases
├── indexes/aio/_patch.py              # Async SearchIndexClient/SearchIndexerClient mirrors
├── indexes/aio/_operations/_patch.py  # Async mirror of indexes operations mixin
├── knowledgebases/_patch.py           # KnowledgeBaseRetrievalClient (audience kwarg plumbing)
└── knowledgebases/aio/_patch.py       # Async KnowledgeBaseRetrievalClient
```

## Step 3: Check ApiVersion

The generator targets the version in `_metadata.json`. The hand-maintained `ApiVersion` enum in `azure/search/documents/_patch.py` must include it.

```bash
# 1. See what API version the generator used
python -c "import json; print(json.load(open('_metadata.json'))['apiVersion'])"

# 2. See what versions the SDK currently advertises
grep -A 20 'class ApiVersion' azure/search/documents/_patch.py

# 3. Check the current default
grep 'DEFAULT_VERSION' azure/search/documents/_patch.py
```

If the generated API version is **not** in the enum:
1. Add the new member to `ApiVersion` in `azure/search/documents/_patch.py` (e.g., `V2026_05_01_PREVIEW = "2026-05-01-preview"`).
2. Update `DEFAULT_VERSION` to point to the new member.
3. Update docstrings on the public client subclasses (`SearchClient`, `SearchIndexClient`, `SearchIndexerClient`, `KnowledgeBaseRetrievalClient`) that name the default version.

Verify the default round-trips:

```bash
python -c "from azure.search.documents._patch import ApiVersion, DEFAULT_VERSION; print(DEFAULT_VERSION.value)"
```

## Step 4: Expose New Generated Methods Through `_patch.py`

New generated operations do NOT automatically surface in the user-expected shape. Diff what regeneration added:

```bash
git diff --name-only | grep "_operations\.py" | grep -v _patch
git diff azure/search/documents/indexes/_operations/_operations.py | grep -E '^\+\s+(async\s+)?def '
git diff azure/search/documents/_operations/_operations.py | grep -E '^\+\s+(async\s+)?def '
```

For each new method, pick the exposure path:

1. **Pass-through via generated mixin inheritance** — if the generated signature is already user-friendly, the `_<Client>OperationsMixin` subclass in `_patch.py` inherits it automatically. Verify the method name does NOT collide with an existing `_patch.py` override.

2. **Override in the operations mixin** — needed when the method requires custom paging (`SearchItemPaged`), request-body rewriting (`_build_search_request`), response conversion (`_convert_search_result`, `_convert_index_response`), or 413 batch splitting.

3. **Polymorphic str-or-model wrapper** — for `delete_*` on a named resource (index, synonym map, alias, indexer, data source, skillset, knowledge base, knowledge source). Accept either the `str` name or the resource model; forward `e_tag` + `match_condition` when a model is passed.

4. **Create-or-update wrapper** — for `create_or_update_*`. Forward `prefer="return=representation"`, `match_condition`, `etag`, plus package-specific flags:
   - `allow_index_downtime` for `create_or_update_index`
   - `skip_indexer_reset_requirement_for_cache` for indexers
   - `skip_indexer_reset` / `disable_cache_reprocessing_change_detection` for skillsets

5. **List projection wrapper** — for `list_*`. Add a `select` parameter, a name-only projection via `cls` callback (`list_index_names`, `list_indexer_names`, `list_skillset_names`), or convert a generated projection type back to the canonical model via `_convert_index_response`.

6. **Re-export via `__all__`** — any NEW symbol you add or override in `_patch.py` MUST be appended to that file's `__all__`. Otherwise `patch_sdk()` will not surface it.

   ```bash
   python -c "import azure.search.documents as m; print(sorted(m.__all__))"
   python -c "import azure.search.documents.indexes as m; print(sorted(m.__all__))"
   ```

Every sync wrapper needs a matching async mirror under `aio/`. Shared helpers (`_build_search_request`, `_convert_search_result`, `_convert_index_response`, `_pack_continuation_token`, `_unpack_continuation_token`) live in the **sync** `_operations/_patch.py` and are **imported** by async — do not duplicate them.

## Step 5: Check for Model/Enum Changes That Affect Customizations

```bash
git diff azure/search/documents/models/_models.py azure/search/documents/models/_enums.py
git diff azure/search/documents/indexes/models/_models.py azure/search/documents/indexes/models/_enums.py
```

Watch for:
- **Renamed enum values** — `indexes/models/_patch.py` monkey-patches camelCase aliases onto `SearchFieldDataType` (`String`, `Int32`, `Int64`, `Single`, `Double`, `Boolean`, `DateTimeOffset`, `GeographyPoint`, `ComplexType`). All right-hand-side UPPER_CASE members must still exist.
- **Changed model constructors** — `IndexDocumentsBatch`, `SearchField`, `SearchIndexerDataSourceConnection`, `KnowledgeBase` are subclassed in `_patch.py`; base-class constructor changes break them.
- **New fields on `SearchResult`** — `_convert_search_result()` extracts `@search.*` metadata (`score`, `reranker_score`, `highlights`, `captions`, `document_debug_info`, `reranker_boosted_score`). New metadata fields must be added there.
- **Changed `SearchRequest`** — `_build_search_request()` constructs this model directly; new query parameters must be wired through, including any new pipe-delimited semantic encoding.
- **`SearchIndexResponse.semantic`** — used by `_convert_index_response()`; if the field is renamed, update the mapping.
- **`SearchField.retrievable`** — the `hidden` property in `SearchField` subclass is its inverse; if renamed, update the property.

## Step 6: Run package validation

Run the full validation suite (mypy, pylint, and the rest) in one shot:

```
azsdk_package_run_check with checkType="All"
```

`mypy.ini` and the repo-level `pylintrc` already exclude generated internals, `_vendor/`, `tests/`, and `samples/` — errors will originate in `_patch.py` customizations.

## Step 7: Update Documentation and Samples

### CHANGELOG

Open `CHANGELOG.md` and find the topmost `## (Unreleased)` section. Add entries under:

- `### Features Added` — new operations, models, parameters, API version support
- `### Breaking Changes` — renamed/removed models, changed signatures, dropped API versions
- `### Bugs Fixed` — fixes to `_patch.py` logic, pagination, encoding, batching

Example:

```markdown
## 11.x.0bN (Unreleased)

### Features Added

- Added `create_or_update_knowledge_base` to `SearchIndexClient`.
- Support for API version `2026-05-01-preview`.

### Breaking Changes

- Renamed `OldModel` to `NewModel`.
```

If no `(Unreleased)` section exists, create one above the latest release using the next version from `azure/search/documents/_version.py`.

### README

- Add usage examples for new client classes (`KnowledgeBaseRetrievalClient` etc.) or operations.
- Update "Key concepts" for new resource types.
- Update the listed API version in "Getting started" if `DEFAULT_VERSION` changed.

---

# Customization Patterns Reference

Each pattern below exists in the codebase today. After regeneration, verify each still works. See `references/customizations.md` for the exhaustive file-by-file inventory.

## Client Constructor Customizations (audience / parameter reorder)

- `SearchClient` in `_patch.py` (sync + async) reorders params to `(endpoint, index_name, credential)`. The generated base uses `(endpoint, credential, index_name)`.
- `SearchIndexClient`, `SearchIndexerClient` (`indexes/_patch.py` + async) and `KnowledgeBaseRetrievalClient` (`knowledgebases/_patch.py` + async) all pop the `audience` kwarg and convert it into `credential_scopes=[audience + "/.default"]`.

If regeneration changes the base constructor signature (param order, required kwargs), update each subclass.

## Custom Search Pagination

`search()` does **not** use standard Azure SDK paging. It uses `SearchItemPaged` / `AsyncSearchItemPaged` with a custom `SearchPageIterator` because:
- Search paginates via POST with `nextPageParameters` body, not GET with `nextLink`.
- First-page metadata (facets, count, coverage, answers, debug info) must be available before iteration starts.
- Results are converted to dicts with `@search.*` keys.

Continuation token is Base64-encoded JSON: `{"apiVersion": ..., "nextLink": ..., "nextPageParameters": {...}}`.

Shared helpers (`_build_search_request`, `_convert_search_result`, `_pack_continuation_token`, `_unpack_continuation_token`) live in sync `_operations/_patch.py` and are imported by async.

## Pipe-Delimited Semantic Encoding

`_build_search_request()` encodes semantic parameters into pipe-delimited wire format:

```
query_answer="extractive", count=3         →  "extractive|count-3"
query_caption="extractive", highlight=True →  "extractive|highlight-true"
```

New semantic-search parameters follow this pattern.

## 413 Batch Splitting

`index_documents()` in `_operations/_patch.py` recursively splits an `IndexDocumentsBatch` in half when the service returns `RequestEntityTooLargeError` (413). Retry-on-split uses `is_retryable_status_code()` (409/422/503).

## SearchIndexingBufferedSender

Entirely hand-authored in `_patch.py` (sync) and `aio/_patch.py` (async); not generated. Wraps `SearchClient` with:
- Auto-flush timer (`threading.Timer` sync / `asyncio.Task` async).
- 413 recursive batch splitting.
- Retry per document key (409/422/503) bounded by `max_retries_per_action`.
- Key-field auto-detection against the index schema.
- The async version detects sync vs async callbacks via `asyncio.iscoroutinefunction()`.

## Field Builders and `SearchFieldDataType` Helpers (`indexes/models/_patch.py`)

- `SimpleField(...)` — sets `searchable=False` explicitly.
- `SearchableField(...)` — auto-types to `String` / `Collection(String)`.
- `ComplexField(...)` — sets type to `Complex` / `Collection(Complex)`.
- `SearchField` subclass adds `hidden` property (inverse of `retrievable`).
- `SearchFieldDataType.Collection = staticmethod(_collection_helper)` — monkey-patched onto the generated enum.

## Backward-Compatible Enum Aliases

Applied at module load in `indexes/models/_patch.py`:

```python
SearchFieldDataType.Int32 = SearchFieldDataType.INT32   # camelCase → UPPER
# (String, Int64, Single, Double, Boolean, DateTimeOffset, GeographyPoint, ComplexType)
```

After regeneration, verify every right-hand-side UPPER_CASE member still exists in the generated enum. If a new enum value collides with a Python keyword, add an alias.

## Polymorphic Delete / Create-Or-Update Pattern

All delete/update operations in `indexes/_operations/_patch.py` accept str or model:

```python
def delete_index(self, index, *, match_condition=MatchConditions.Unconditionally, **kwargs):
    try:
        name = index.name   # model object
        return self._delete_index(name=name, etag=index.e_tag, match_condition=match_condition, **kwargs)
    except AttributeError:
        return self._delete_index(name=index, **kwargs)   # string
```

Covered resources: index, synonym map, alias, indexer, data source connection, skillset, knowledge base, knowledge source. New resource types added to the spec need the same pair of wrappers in sync **and** async.

## `_convert_index_response` Helper

`list_indexes(select=...)` returns `SearchIndexResponse` (projection type). `_convert_index_response()` maps it to `SearchIndex` — notably `response.semantic` → `semantic_search`. Shared between sync and async via import; do not duplicate.

---

When to use `_patch.py` vs TypeSpec: prefer TypeSpec decorators / emitter options for things the spec can express (renames, flattening, client names). Use `_patch.py` for Python-specific behavior: pagination contracts, threading/asyncio, polymorphic call patterns, 413 splitting, monkey-patched enum helpers, and backward-compat aliases. See [typespec-python emitter docs](https://github.com/Azure/autorest.python/blob/main/packages/typespec-python/README.md).
