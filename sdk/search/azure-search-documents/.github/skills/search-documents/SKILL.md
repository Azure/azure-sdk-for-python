---
name: search-documents-python
description: 'Post-regeneration customization guide for the azure-search-documents Python SDK. After running tsp-client update, consult this skill to re-apply all search-specific customizations and produce a production-ready SDK. USE WHEN: regenerating the search SDK from TypeSpec, running tsp-client update, fixing broken _patch.py imports after regeneration, adding a new operation or model to the search SDK, verifying the SDK still works after spec changes, or any task that mentions "regenerate", "tsp-client", "typespec", or "codegen" in the context of this package.'
---

# azure-search-documents — Post-Regeneration Customization Guide

After running `tsp-client update`, the generated code is a raw skeleton — not a shippable SDK. This skill tells you exactly what customizations exist in `_patch.py` files and how to verify they still work after regeneration.

The generator never touches `_patch.py` files, so your customizations survive regeneration. But they import from generated modules that **do** change. A renamed model, a new parameter, or a removed enum value will silently break a `_patch.py` file. The verification steps below catch these breaks.

## Step 1: Run Regeneration

```bash
cd sdk/search/azure-search-documents

# Update tsp-location.yaml with the new spec commit SHA, then:
tsp-client update

# If API version changed, update _metadata.json too
```

## Step 2: Verify Imports in All `_patch.py` Files

Every `_patch.py` with customizations imports from generated modules. After regeneration, check that these imports still resolve. The fastest way:

```bash
python -c "from azure.search.documents import SearchClient"
python -c "from azure.search.documents.aio import SearchClient"
python -c "from azure.search.documents.indexes.models import SearchField, SearchFieldDataType"
python -c "from azure.search.documents.models import IndexDocumentsBatch"
```

If any fail, a generated class/enum was renamed or removed. Read `references/customizations.md` for the exact import each `_patch.py` depends on.

The `_patch.py` files that have customizations (all others are empty boilerplate):

```
azure/search/documents/
├── _patch.py                    # SearchClient, SearchIndexingBufferedSender, ApiVersion
├── _operations/_patch.py        # SearchItemPaged, search(), document CRUD
├── models/_patch.py             # IndexDocumentsBatch, RequestEntityTooLargeError
├── aio/_patch.py                # Async SearchClient, async SearchIndexingBufferedSender
├── aio/_operations/_patch.py    # AsyncSearchItemPaged, async search()/CRUD
├── indexes/_operations/_patch.py        # Polymorphic delete/update, list helpers
├── indexes/models/_patch.py             # SearchField, field builders, enum aliases
└── indexes/aio/_operations/_patch.py    # Async index/indexer operations
```

## Step 3: Check ApiVersion

## Step 4: Check for New Operations That Need Wrappers

Look at what changed in the generated operations files:

```bash
git diff --name-only | grep "_operations\.py" | grep -v _patch
```

If a new operation was added to the generated `_operations.py`, decide whether it needs a convenience wrapper in `_patch.py`. Operations that need wrappers:
- **Delete operations** — need the polymorphic str-or-model pattern (see "Polymorphic Delete Pattern" below)
- **Create-or-update operations** — need `prefer="return=representation"`, `match_condition`, and `etag` forwarding
- **List operations** — may need a `select` parameter or name-only projection

Operations that pass through without a wrapper (if the generated signature is already user-friendly) can be left alone — they're inherited from the generated mixin.

Remember: every sync wrapper in `_operations/_patch.py` needs a matching async wrapper in `aio/_operations/_patch.py`.

## Step 5: Check for Model/Enum Changes That Affect Customizations

```bash
git diff models/_enums.py models/_models.py indexes/models/_enums.py indexes/models/_models.py
```

Watch for:
- **Renamed enum values** — backward-compat aliases in `_patch.py` may reference old names
- **New enum values that collide with Python keywords** — the generator renames them with `_ENUM` suffix (e.g., `IS` → `IS_ENUM`), and you must add a backward-compat alias
- **Changed model constructors** — `IndexDocumentsBatch`, `SearchField`, `SearchIndexerDataSourceConnection`, `KnowledgeBase` are subclassed in `_patch.py` and may break if the base constructor changes
- **New fields on `SearchResult`** — `_convert_search_result()` in `_operations/_patch.py` extracts `@search.*` metadata fields; new ones need to be added
- **Changed `SearchRequest` model** — `_build_search_request()` constructs this model directly; new parameters need to be wired through
- **Changed `SearchFieldDataType` model** — `indexes/models/_patch.py` monkey-patches `SearchFieldDataType.Collection` as a `staticmethod` and adds camelCase backward-compat aliases (e.g., `Int32` → `INT32`). If values are added, removed, or renamed in the generated enum, the aliases and `Collection` helper must be updated to match

## Step 6: Run azpysdk mypy and fix all failures

## Step 7: Run azpysdk pylint and fix all failures

## Step 8: Update Documentation and Samples

# Customization Patterns Reference

Each pattern below describes a customization that exists in the codebase today. After regeneration, verify each one still works. Read `references/customizations.md` for the exhaustive file-by-file inventory.

## SearchClient Constructor Reordering

`SearchClient` in `_patch.py` swaps parameter order to `(endpoint, index_name, credential)`. The generated base uses `(endpoint, credential, index_name)`. If regeneration changes the base constructor signature, update the subclass.

## Custom Search Pagination

`search()` does **not** use standard Azure SDK paging. It uses `SearchItemPaged` / `AsyncSearchItemPaged` with a custom `SearchPageIterator` because:
- Search paginates via POST with `nextPageParameters` body, not GET with `nextLink`
- First-page metadata (facets, count, answers) must be available before iteration
- Results are converted to dicts with `@search.*` keys

The continuation token is Base64-encoded JSON: `{"apiVersion": "...", "nextLink": "...", "nextPageParameters": {...}}`

Shared helpers (`_build_search_request`, `_convert_search_result`, `_pack_continuation_token`, `_unpack_continuation_token`) live in sync `_operations/_patch.py` and are imported by async. Don't duplicate them.

## Pipe-Delimited Semantic Encoding

`_build_search_request()` encodes semantic parameters into pipe-delimited wire format:
```
query_answer="extractive", count=3  →  "extractive|count-3"
query_caption="extractive", highlight=True  →  "extractive|highlight-true"
```
New semantic parameters should follow this pattern.

## SearchIndexingBufferedSender

Entirely hand-authored in `_patch.py` (sync) and `aio/_patch.py` (async). Not generated. Wraps `SearchClient` with auto-flush timer, 413 recursive batch splitting, retry per document key (409/422/503), and key field auto-detection. The async version supports both sync and async callbacks via `asyncio.iscoroutinefunction()`.

## Field Builders

`SimpleField()`, `SearchableField()`, `ComplexField()` in `indexes/models/_patch.py`. `SimpleField` explicitly sets `searchable=False`. `SearchableField` auto-sets type to `String`/`Collection(String)`.

`SearchField` subclass adds `hidden` property (inverse of `retrievable`).

`SearchFieldDataType.Collection` is a `staticmethod` monkey-patched onto the generated enum.

## Backward-Compatible Enum Aliases

Monkey-patched at module load in `_patch.py` files:
```python
SearchFieldDataType.Int32 = SearchFieldDataType.INT32   # camelCase → UPPER
OcrSkillLanguage.IS = OcrSkillLanguage.IS_ENUM           # Python keyword collision
ScoringStatistics.Global = ScoringStatistics.GLOBAL_ENUM
```
After regeneration, verify the right-hand-side names still exist in the generated enums. If a new enum collides with a Python keyword, add an alias.

## Polymorphic Delete Pattern

All delete/update operations in `indexes/_operations/_patch.py` accept str or model object:
```python
def delete_index(self, index, *, match_condition=MatchConditions.Unconditionally, **kwargs):
    try:
        name = index.name   # model object
        return self._delete_index(name=name, etag=index.e_tag, match_condition=match_condition, **kwargs)
    except AttributeError:
        name = index         # string
        return self._delete_index(name=name, **kwargs)
```
New resource types need this same wrapper in both sync and async.

## Removed Model Tombstones

`EntityRecognitionSkill`, `SentimentSkill` → `_RemovedModel` subclasses that `raise ValueError` on instantiation. Keep these for backward compat.

## `_convert_index_response` Helper

`list_indexes(select=...)` returns `SearchIndexResponse` (projection type). `_convert_index_response()` maps it to `SearchIndex`, notably `response.semantic` → `semantic_search`. Shared between sync and async via import.
