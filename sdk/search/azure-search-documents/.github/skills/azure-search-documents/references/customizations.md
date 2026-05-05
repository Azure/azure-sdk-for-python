# azure-search-documents — Customizations

This file is the catalog you verify against after every regeneration. It has four parts:

1. **Generated vs Handwritten** — the editing rule.
2. **`_patch.py` Map** — where each customization file lives.
3. **Patterns Reference** — narrative tour of each customization pattern, why it exists, and what to watch for after regeneration.
4. **Per-File Inventory** — for each `_patch.py`: what it depends on, what it defines (named symbols only), and what to verify after regen.

---

## Generated vs Handwritten

This SDK uses **TypeSpec** code generation. All files except `_patch.py` and `_version.py` are generated and overwritten on regeneration.

#### Editing rules

- **Only edit `_patch.py` files.** They customize generated behavior (convenience methods, parameter normalization, response transformation, re-exports). Each sync `_patch.py` has an async mirror under `aio/`.
- **Sole exception:** inline `# pylint: disable=` comments may be added to generated files for lint issues. This is the only case where editing generated code is allowed.

#### Docstrings on wrappers

When a `_patch.py` method wraps a generated method, copy the generated method's docstring as your starting point. Only adjust the parts that no longer apply — e.g. a parameter you removed, a parameter you added, a return type you changed. Everything else (descriptions, types, exceptions) should stay identical to the generated docstring.

#### Why this catalog exists

The generator never touches `_patch.py` files, so customizations survive regeneration. But they import from generated modules that **do** change. A renamed model, a new parameter, or a removed enum value will silently break a `_patch.py` file. The patterns and per-file inventory below tell you what to verify.

---

## `_patch.py` Map

4 sub-packages, 15 files total. All must be audited after every regeneration.

```
documents/                              # SearchClient
├── _patch.py                           # SearchClient, SearchIndexingBufferedSender, ApiVersion, DEFAULT_VERSION, audience handling
├── _operations/_patch.py               # SearchItemPaged, search(), document CRUD, 413 splitting
├── models/_patch.py                    # IndexDocumentsBatch, RequestEntityTooLargeError
├── aio/_patch.py                       # Async SearchClient + async SearchIndexingBufferedSender, audience handling
├── aio/_operations/_patch.py           # AsyncSearchItemPaged, async search()/CRUD
├── indexes/                            # SearchIndexClient + SearchIndexerClient
│   ├── _patch.py                       # SearchIndexClient, SearchIndexerClient (audience handling)
│   ├── _operations/_patch.py           # Polymorphic delete/update, list helpers, _convert_index_response
│   ├── models/_patch.py                # SearchField, field builders, enum aliases, Collection staticmethod
│   ├── aio/_patch.py                   # Async SearchIndexClient + SearchIndexerClient (audience handling)
│   └── aio/_operations/_patch.py       # Async polymorphic delete/update, async list helpers
└── knowledgebases/                     # KnowledgeBaseRetrievalClient
    ├── _patch.py                       # KnowledgeBaseRetrievalClient (audience handling)
    ├── _operations/_patch.py           # (empty)
    ├── models/_patch.py                # (empty)
    ├── aio/_patch.py                   # Async KnowledgeBaseRetrievalClient (audience handling)
    └── aio/_operations/_patch.py       # (empty)
```

---

## Patterns Reference

Each pattern below describes a customization that exists in the codebase today. After regeneration, verify each one still works. Read the per-file inventory below for the exhaustive file-by-file breakdown.

### SearchClient Constructor Reordering

`SearchClient` in `_patch.py` swaps parameter order to `(endpoint, index_name, credential)`. The generated base uses `(endpoint, credential, index_name)`. If regeneration changes the base constructor signature, update the subclass.

```python
class SearchClient(_SearchClient):
    def __init__(
        self, endpoint: str, index_name: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any
    ) -> None:
        audience = kwargs.pop("audience", None)
        if audience:
            kwargs.setdefault("credential_scopes", [audience.rstrip("/") + "/.default"])
        super().__init__(endpoint=endpoint, credential=credential, index_name=index_name, **kwargs)
```

### Custom Search Pagination

`search()` does **not** use standard Azure SDK paging. It uses `SearchItemPaged` / `AsyncSearchItemPaged` with a custom `SearchPageIterator` because:
- Search paginates via POST with `nextPageParameters` body, not GET with `nextLink`
- First-page metadata (facets, count, answers) must be available before iteration
- Results are converted to dicts with `@search.*` keys

The continuation token is Base64-encoded JSON: `{"apiVersion": "...", "nextLink": "...", "nextPageParameters": {...}}`

Shared helpers (`_build_search_request`, `_convert_search_result`, `_pack_continuation_token`, `_unpack_continuation_token`) live in sync `_operations/_patch.py` and are imported by async. Don't duplicate them.

### Pipe-Delimited Semantic Encoding

`_build_search_request()` encodes semantic parameters into pipe-delimited wire format:
```
query_answer="extractive", count=3  →  "extractive|count-3"
query_caption="extractive", highlight=True  →  "extractive|highlight-true"
```
New semantic parameters should follow this pattern.

### SearchIndexingBufferedSender

Entirely hand-authored in `_patch.py` (sync) and `aio/_patch.py` (async). Not generated. Wraps `SearchClient` with auto-flush timer, 413 recursive batch splitting, retry per document key (409/422/503), and key field auto-detection. The async version supports both sync and async callbacks via `asyncio.iscoroutinefunction()`.

### Field Builders

`SimpleField()`, `SearchableField()`, `ComplexField()` in `indexes/models/_patch.py`. `SimpleField` explicitly sets `searchable=False`. `SearchableField` auto-sets type to `String`/`Collection(String)`.

`SearchField` subclass adds `hidden` property (inverse of `retrievable`).

`SearchFieldDataType.Collection` is a `staticmethod` monkey-patched onto the generated enum.

### Backward-Compatible Enum Aliases

Monkey-patched at module load in `_patch.py` files:
```python
SearchFieldDataType.Int32 = SearchFieldDataType.INT32   # camelCase → UPPER
```
After regeneration, verify the right-hand-side names still exist in the generated enums. If a new enum collides with a Python keyword, add an alias.

### Polymorphic Delete Pattern

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

### `_convert_index_response` Helper

`list_indexes(select=...)` returns `SearchIndexResponse` (projection type). `_convert_index_response()` maps it to `SearchIndex`, notably `response.semantic` → `semantic_search`. Shared between sync and async via import.

### `audience` → `credential_scopes` Translation

All 6 client subclasses (`SearchClient`, `SearchIndexClient`, `SearchIndexerClient`, `KnowledgeBaseRetrievalClient` × sync/async) accept an `audience` kwarg and translate it to `credential_scopes` before delegating to the generated base:

```python
audience = kwargs.pop("audience", None)
if audience:
    kwargs.setdefault("credential_scopes", [audience.rstrip("/") + "/.default"])
super().__init__(endpoint=endpoint, credential=credential, **kwargs)
```

This is a deliberate API-review customization — `audience` is the documented public-facing keyword. After regeneration, every new client class needs the same translation in **both sync and async**. `SearchIndexingBufferedSender` also pops `audience` (and `api_version`) from kwargs for the same reason.

---

## Per-File Inventory

Use this section after running regeneration to verify every customization. Each section is a `_patch.py` file with the exact classes, functions, and aliases it defines, plus what generated symbols it depends on.

### File: `azure/search/documents/_patch.py`

#### Depends On (from generated code)
- `._client.SearchClient` as `_SearchClient` (base class)

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `ApiVersion` | enum | Hand-maintained list of supported API versions (e.g., `V2026_04_01`) |
| `DEFAULT_VERSION` | constant | Default API version (e.g., `ApiVersion.V2026_04_01`) |
| `SearchClient` | class | Subclass of `_SearchClient`; reorders constructor to `(endpoint, index_name, credential)`; translates `audience` kwarg → `credential_scopes` |
| `SearchIndexingBufferedSender` | class | Hand-authored batching sender. Uses `threading.Timer` for auto-flush, recursive 413 splitting, retry per doc key (409/422/503), key field auto-detection. Also pops `audience` and `api_version` from kwargs. |
| `is_retryable_status_code()` | function | Returns True for 409, 422, 503 |

#### After Regeneration, Verify
- [ ] `_SearchClient` base class constructor signature unchanged
- [ ] If API version changed, add new `ApiVersion` member and update `DEFAULT_VERSION`
- [ ] `audience` → `credential_scopes` translation still in `__init__`

---

### File: `azure/search/documents/models/_patch.py`

#### Depends On (from generated code)
- `.._generated.models.IndexDocumentsBatch` as `IndexDocumentsBatchGenerated` (base class)
- `._enums.ScoringStatistics`

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `IndexDocumentsBatch` | class | Adds `add_upload_actions`, `add_delete_actions`, `add_merge_actions`, `add_merge_or_upload_actions`, `dequeue_actions`, `enqueue_actions`, `actions` property |
| `RequestEntityTooLargeError` | class | `HttpResponseError` subclass for 413 |

#### After Regeneration, Verify
- [ ] `IndexDocumentsBatchGenerated` base class still exists with a compatible constructor — if the constructor signature changed, update the subclass `__init__`.

---

### File: `azure/search/documents/_operations/_patch.py`

#### Depends On (from generated code)
- `..models._models.SearchRequest` (constructed directly in `_build_search_request`)
- `..models._models.SearchResult` (field access in `_convert_search_result`)
- `azure.core.paging.ItemPaged`, `azure.core.paging.PageIterator`

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `_convert_search_result(result)` | function | Extracts `@search.score`, `@search.reranker_score`, `@search.highlights`, `@search.captions`, `@search.document_debug_info`, `@search.reranker_boosted_score` |
| `_pack_continuation_token(response, api_version)` | function | Returns base64 JSON: `{apiVersion, nextLink, nextPageParameters}` |
| `_unpack_continuation_token(token)` | function | Decodes token to `(next_link, next_page_request)` |
| `_build_search_request(search_text, **kwargs)` | function | Builds `SearchRequest`. Pipe-delimited encoding for answers/captions/rewrites |
| `SearchPageIterator` | class | Custom page iterator with `get_facets()`, `get_count()`, `get_coverage()`, `get_answers()`, `get_debug_info()` |
| `SearchItemPaged` | class | Extends `ItemPaged` with same metadata accessors |
| `_SearchClientOperationsMixin` | class | Overrides: `search()`, `index_documents()` (413 splitting), `upload_documents()`, `delete_documents()`, `merge_documents()`, `merge_or_upload_documents()` |

#### After Regeneration, Verify
- [ ] `SearchRequest` model fields still match what `_build_search_request` sets — for any new field on `SearchRequest`, decide whether to plumb it through `_build_search_request` (and whether it needs pipe-encoding).
- [ ] `SearchResult` model fields still match what `_convert_search_result` extracts — for any new `@search.*` key, add an extraction line.
- [ ] Generated mixin methods that `_SearchClientOperationsMixin` calls (e.g., `_search_post`, `_index_documents`) still exist with same signatures. If renamed, update the `self._xxx(...)` call sites here.

---

### File: `azure/search/documents/aio/_patch.py`

#### Depends On (from generated code)
- `.._client.SearchClient` as async `_SearchClient` (base class)

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchClient` | class | Async subclass, same reorder as sync; translates `audience` kwarg → `credential_scopes` |
| `SearchIndexingBufferedSender` | class | Async version: `asyncio.Task` instead of `threading.Timer`, `iscoroutinefunction()` callback detection. Also pops `audience` and `api_version` from kwargs. |

#### After Regeneration, Verify
- [ ] Same checks as sync `_patch.py`

---

### File: `azure/search/documents/aio/_operations/_patch.py`

#### Depends On (from generated code)
- Same models as sync `_operations/_patch.py`
- `azure.core.async_paging.AsyncItemPaged`, `AsyncPageIterator`

#### Imports From Sync (NOT Duplicated)
- `_build_search_request`, `_convert_search_result`, `_pack_continuation_token`, `_unpack_continuation_token`

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `AsyncSearchPageIterator` | class | Async version of `SearchPageIterator` |
| `AsyncSearchItemPaged` | class | Async version of `SearchItemPaged` |
| `_SearchClientOperationsMixin` | class | Async operations mixin, same methods as sync |

#### After Regeneration, Verify
- [ ] Same checks as sync `_operations/_patch.py`
- [ ] Imports from sync `_operations/_patch.py` still resolve

---

### File: `azure/search/documents/indexes/_patch.py`

#### Depends On (from generated code)
- `._client.SearchIndexClient` as `_SearchIndexClient` (base class)
- `._client.SearchIndexerClient` as `_SearchIndexerClient` (base class)

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchIndexClient` | class | Subclass; translates `audience` kwarg → `credential_scopes`, then delegates to base `__init__` |
| `SearchIndexerClient` | class | Same pattern, for indexer client |

#### After Regeneration, Verify
- [ ] Both `_SearchIndexClient` and `_SearchIndexerClient` base constructors still accept `(endpoint, credential, **kwargs)`
- [ ] `audience` → `credential_scopes` translation still present in both `__init__`s

---

### File: `azure/search/documents/indexes/aio/_patch.py`

#### Depends On (from generated code)
- `._client.SearchIndexClient` as async `_SearchIndexClient` (base class)
- `._client.SearchIndexerClient` as async `_SearchIndexerClient` (base class)

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchIndexClient` | class | Async subclass; same `audience` → `credential_scopes` translation as sync |
| `SearchIndexerClient` | class | Async indexer client; same pattern |

#### After Regeneration, Verify
- [ ] Same checks as sync `indexes/_patch.py`

---

### File: `azure/search/documents/knowledgebases/_patch.py`

#### Depends On (from generated code)
- `._client.KnowledgeBaseRetrievalClient` as `_KnowledgeBaseRetrievalClient` (base class)

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `KnowledgeBaseRetrievalClient` | class | Subclass; translates `audience` kwarg → `credential_scopes` |

#### After Regeneration, Verify
- [ ] `_KnowledgeBaseRetrievalClient` base constructor still accepts `(endpoint, credential, **kwargs)` (note: `knowledge_base_name` is required and forwarded via kwargs)
- [ ] `audience` → `credential_scopes` translation still present

---

### File: `azure/search/documents/knowledgebases/aio/_patch.py`

#### Depends On (from generated code)
- `._client.KnowledgeBaseRetrievalClient` as async `_KnowledgeBaseRetrievalClient` (base class)

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `KnowledgeBaseRetrievalClient` | class | Async subclass; same `audience` → `credential_scopes` translation as sync |

#### After Regeneration, Verify
- [ ] Same checks as sync `knowledgebases/_patch.py`

---

### File: `azure/search/documents/indexes/models/_patch.py`

#### Depends On (from generated code)
- `._models.SearchField` as `_SearchField` (base class)
- `._models.SearchIndexerDataSourceConnection` as `_SearchIndexerDataSourceConnection` (base class)
- `._models.KnowledgeBase` as `_KnowledgeBase` (base class)
- `._enums.SearchFieldDataType`, `OcrSkillLanguage`, `SplitSkillLanguage`, `TextTranslationSkillLanguage`
- Various model imports for type annotations

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchField` | class | Adds `hidden` property (inverse of `retrievable`), constructor accepts `hidden` kwarg |
| `SearchIndexerDataSourceConnection` | class | Adds `@overload`s so callers can pass either `connection_string=` *or* `credentials=` (plus a raw-mapping overload) |
| `KnowledgeBase` | class | Empty subclass placeholder (just calls `super().__init__`). Kept as an extension point for future API-review-driven customization. |
| `SimpleField()` | function | Builder: sets `searchable=False` explicitly |
| `SearchableField()` | function | Builder: auto-types to `String`/`Collection(String)` |
| `ComplexField()` | function | Builder: sets type to `Complex`/`Collection(Complex)` |
| `Collection()` | function | Wraps type in `"Collection(...)"` format |
| `_collection_helper()` | function (private) | Internal helper called by the `Collection`/`SimpleField`/`SearchableField` builders to format collection types |

#### Enum Aliases
```python
# SearchFieldDataType  (old camelCase -> generated UPPER_CASE)
SearchFieldDataType.String = SearchFieldDataType.STRING
SearchFieldDataType.Int32 = SearchFieldDataType.INT32
SearchFieldDataType.Int64 = SearchFieldDataType.INT64
SearchFieldDataType.Single = SearchFieldDataType.SINGLE
SearchFieldDataType.Double = SearchFieldDataType.DOUBLE
SearchFieldDataType.Boolean = SearchFieldDataType.BOOLEAN
SearchFieldDataType.DateTimeOffset = SearchFieldDataType.DATE_TIME_OFFSET
SearchFieldDataType.GeographyPoint = SearchFieldDataType.GEOGRAPHY_POINT
SearchFieldDataType.ComplexType = SearchFieldDataType.COMPLEX

# Monkey-patched staticmethod
SearchFieldDataType.Collection = staticmethod(Collection)
```

#### After Regeneration, Verify
- [ ] All right-hand-side enum members (`STRING`, `INT32`, etc.) still exist — if any were renamed, update the alias RHS.
- [ ] `_SearchField`, `_SearchIndexerDataSourceConnection`, `_KnowledgeBase` base constructors unchanged (or update the subclass overloads to match).
- [ ] Any new enum value that collides with a Python keyword → add an alias.
- [ ] `SearchField.retrievable` still exists (used by the `hidden` inversion).

---

### File: `azure/search/documents/indexes/_operations/_patch.py`

#### Depends On (from generated code)
- Generated `_SearchIndexClientOperationsMixin` and `_SearchIndexerClientOperationsMixin` (base classes — every wrapper below delegates to a `_xxx`-prefixed method on these)
- `azure.core.match_conditions.MatchConditions`

#### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `_convert_index_response(response)` | function | Maps `SearchIndexResponse` (the projection model returned by `list_indexes(select=...)`) → `SearchIndex`. Notably remaps `response.semantic` → `semantic_search`. Shared with the async mixin via import. |
| `_SearchIndexClientOperationsMixin` | class | Override mixin for `SearchIndexClient`. See pattern categories below. |
| `_SearchIndexerClientOperationsMixin` | class | Override mixin for `SearchIndexerClient`. See pattern categories below. |

#### Wrapper Pattern Categories

Every method on these two mixins falls into one of the categories below. The current method roster lives in the file — `grep "    def " azure/search/documents/indexes/_operations/_patch.py` to see it. Use the categories to decide what each method needs and to slot in new ones after regeneration.

| Category | What the wrapper does | Applies to |
|---|---|---|
| **Polymorphic delete** | Accepts `str` or model object. If model, extract `.name` and pass `etag=obj.e_tag`. Always accepts `match_condition=MatchConditions.Unconditionally`. | `delete_index`, `delete_synonym_map`, `delete_alias`, `delete_knowledge_base`, `delete_knowledge_source`, `delete_data_source_connection`, `delete_indexer`, `delete_skillset` |
| **Create-or-update with prefer/match_condition** | Adds `prefer="return=representation"`, `match_condition`, and resource-specific knobs (e.g., `allow_index_downtime`, `skip_indexer_reset`, `skip_initial_run`, `disable_cache_reprocessing_change_detection`). | Every `create_or_update_*` for the resource types above |
| **List with projection** | Accepts `select=...`, returns the full model; some apply a `cls` callback (e.g., `_convert_index_response`) to map the projection model back to the canonical model. | `list_indexes`, `get_synonym_maps`, `get_skillsets`, `get_indexers`, `get_data_source_connections` |
| **Name-only list helper** | Calls the underlying list with a `cls` callback that projects to `[item.name, ...]`. | `list_index_names`, `get_synonym_map_names`, `list_alias_names`, `get_indexer_names`, `get_data_source_connection_names`, `get_skillset_names` |
| **Resource helper** | One-off convenience that doesn't fit the patterns above. | `analyze_text`, `get_index_statistics`, `get_search_client` (instantiates a `SearchClient` from the index client's endpoint + credential) |

Polymorphic-delete reference implementation (verified against `delete_index`):
```python
def delete_index(self, index, *, match_condition=MatchConditions.Unconditionally, **kwargs):
    try:
        name = index.name
        return self._delete_index(name=name, etag=index.e_tag, match_condition=match_condition, **kwargs)
    except AttributeError:
        return self._delete_index(name=index, **kwargs)
```

#### After Regeneration, Verify
- [ ] Diff the generated `_SearchIndexClientOperationsMixin` / `_SearchIndexerClientOperationsMixin`: for each `_xxx`-prefixed method that **disappeared**, remove its wrapper. For each that **gained a required parameter**, forward it through the wrapper.
- [ ] For each **new** generated method: classify it into one of the categories above. If it's a delete/create-or-update/list on a new resource type, add a wrapper. If it's a one-off, decide whether to expose it directly or wrap.
- [ ] `SearchIndexResponse` still has `.semantic` (used by `_convert_index_response`). If renamed, update the helper.
- [ ] `prefer="return=representation"` still accepted by the generated create-or-update methods.
- [ ] Apply every change to the async mirror in `indexes/aio/_operations/_patch.py`.

---

### File: `azure/search/documents/indexes/aio/_operations/_patch.py`

Async mirror of `indexes/_operations/_patch.py`. Same methods, all `async`.

Imports `_convert_index_response` from sync — NOT duplicated.

#### After Regeneration, Verify
- [ ] Same checks as sync `indexes/_operations/_patch.py`
- [ ] Import of `_convert_index_response` from sync still resolves

---

<sub>**For maintainers of this catalog:** This file describes *shape, not a snapshot*. Stable design decisions (patterns, named helpers, hand-maintained aliases) are enumerated; service-owned method rosters are described by *category* and you scan the actual `_patch.py` for the current list. Anywhere this file lists service-side methods, treat it as illustrative — the file itself is source of truth.</sub>
