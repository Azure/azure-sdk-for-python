# Post-Regeneration Customization Checklist

Use this file after running `tsp-client update` to verify every customization. Each section is a `_patch.py` file with the exact classes, functions, and aliases it defines, plus what generated symbols it depends on.

---

## File: `azure/search/documents/_patch.py`

### Depends On (from generated code)
- `._client.SearchClient` as `_SearchClient` (base class)

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchClient` | class | Subclass of `_SearchClient`; reorders constructor to `(endpoint, index_name, credential)` |
| `SearchIndexingBufferedSender` | class | Hand-authored batching sender. Uses `threading.Timer` for auto-flush, recursive 413 splitting, retry per doc key (409/422/503), key field auto-detection |
| `is_retryable_status_code()` | function | Returns True for 409, 422, 503 |

### After Regeneration, Verify
- [ ] `_SearchClient` base class constructor signature unchanged
- [ ] If API version changed, add new `ApiVersion` member and update default

---

## File: `azure/search/documents/models/_patch.py`

### Depends On (from generated code)
- `.._generated.models.IndexDocumentsBatch` as `IndexDocumentsBatchGenerated` (base class)
- `._enums.ScoringStatistics`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `IndexDocumentsBatch` | class | Adds `add_upload_actions`, `add_delete_actions`, `add_merge_actions`, `add_merge_or_upload_actions`, `dequeue_actions`, `enqueue_actions`, `actions` property |
| `RequestEntityTooLargeError` | class | `HttpResponseError` subclass for 413 |

### After Regeneration, Verify
- [ ] `IndexDocumentsBatchGenerated` base class still exists with compatible constructor

---

## File: `azure/search/documents/_operations/_patch.py`

### Depends On (from generated code)
- `..models._models.SearchRequest` (constructed directly in `_build_search_request`)
- `..models._models.SearchResult` (field access in `_convert_search_result`)
- `azure.core.paging.ItemPaged`, `azure.core.paging.PageIterator`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `_convert_search_result(result)` | function | Extracts `@search.score`, `@search.reranker_score`, `@search.highlights`, `@search.captions`, `@search.document_debug_info`, `@search.reranker_boosted_score` |
| `_pack_continuation_token(response, api_version)` | function | Returns base64 JSON: `{apiVersion, nextLink, nextPageParameters}` |
| `_unpack_continuation_token(token)` | function | Decodes token to `(next_link, next_page_request)` |
| `_build_search_request(search_text, **kwargs)` | function | Builds `SearchRequest`. Pipe-delimited encoding for answers/captions/rewrites |
| `SearchPageIterator` | class | Custom page iterator with `get_facets()`, `get_count()`, `get_coverage()`, `get_answers()`, `get_debug_info()` |
| `SearchItemPaged` | class | Extends `ItemPaged` with same metadata accessors |
| `_SearchClientOperationsMixin` | class | Overrides: `search()`, `index_documents()` (413 splitting), `upload_documents()`, `delete_documents()`, `merge_documents()`, `merge_or_upload_documents()` |

### After Regeneration, Verify
- [ ] `SearchRequest` model fields still match what `_build_search_request` sets — new search parameters need to be wired through
- [ ] `SearchResult` model fields still match what `_convert_search_result` extracts — new `@search.*` fields need to be added
- [ ] Generated mixin methods that `_SearchClientOperationsMixin` calls (e.g., `_search_post`) still exist with same signatures

---

## File: `azure/search/documents/aio/_patch.py`

### Depends On (from generated code)
- `.._client.SearchClient` as async `_SearchClient` (base class)

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchClient` | class | Async subclass, same reorder as sync |
| `SearchIndexingBufferedSender` | class | Async version: `asyncio.Task` instead of `threading.Timer`, `iscoroutinefunction()` callback detection |

### After Regeneration, Verify
- [ ] Same checks as sync `_patch.py`

---

## File: `azure/search/documents/aio/_operations/_patch.py`

### Depends On (from generated code)
- Same models as sync `_operations/_patch.py`
- `azure.core.async_paging.AsyncItemPaged`, `AsyncPageIterator`

### Imports From Sync (NOT Duplicated)
- `_build_search_request`, `_convert_search_result`, `_pack_continuation_token`, `_unpack_continuation_token`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `AsyncSearchPageIterator` | class | Async version of `SearchPageIterator` |
| `AsyncSearchItemPaged` | class | Async version of `SearchItemPaged` |
| `_SearchClientOperationsMixin` | class | Async operations mixin, same methods as sync |

### After Regeneration, Verify
- [ ] Same checks as sync `_operations/_patch.py`
- [ ] Imports from sync `_operations/_patch.py` still resolve

---

## File: `azure/search/documents/indexes/models/_patch.py`

### Depends On (from generated code)
- `._models.SearchField` as `_SearchField` (base class)
- `._models.SearchIndexerDataSourceConnection` as `_SearchIndexerDataSourceConnection` (base class)
- `._models.KnowledgeBase` as `_KnowledgeBase` (base class)
- `._enums.SearchFieldDataType`, `OcrSkillLanguage`, `SplitSkillLanguage`, `TextTranslationSkillLanguage`
- Various model imports for type annotations

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchField` | class | Adds `hidden` property (inverse of `retrievable`), constructor accepts `hidden` kwarg |
| `SearchIndexerDataSourceConnection` | class | Accepts `connection_string` str or `credentials` object |
| `KnowledgeBase` | class | Deserializes `retrieval_reasoning_effort` from dict |
| `SimpleField()` | function | Builder: sets `searchable=False` explicitly |
| `SearchableField()` | function | Builder: auto-types to `String`/`Collection(String)` |
| `ComplexField()` | function | Builder: sets type to `Complex`/`Collection(Complex)` |
| `Collection()` | function | Wraps type in `"Collection(...)"` format |

### Enum Aliases
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

### After Regeneration, Verify
- [ ] All right-hand-side enum members (`STRING`, `INT32`, etc.) still exist
- [ ] `_SearchField`, `_SearchIndexerDataSourceConnection`, `_KnowledgeBase` base constructors unchanged
- [ ] No new enum values that collide with Python keywords — if so, add aliases
- [ ] `SearchField.retrievable` property still exists (used by `hidden` inversion)

---

## File: `azure/search/documents/indexes/_operations/_patch.py`

### Depends On (from generated code)
- Generated `_SearchIndexClientOperationsMixin` and `_SearchIndexerClientOperationsMixin` (base classes)
- `azure.core.match_conditions.MatchConditions`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `_convert_index_response(response)` | function | Maps `SearchIndexResponse` → `SearchIndex` (semantic → semantic_search) |

**`_SearchIndexClientOperationsMixin`** wraps:
| Method | Customization |
|--------|--------------|
| `delete_index(index)` | Polymorphic: str or SearchIndex |
| `create_or_update_index(index)` | Adds prefer, match_condition, allow_index_downtime |
| `delete_synonym_map(synonym_map)` | Polymorphic: str or SynonymMap |
| `create_or_update_synonym_map(synonym_map)` | Adds prefer, match_condition |
| `delete_alias(alias)` | Polymorphic: str or SearchAlias |
| `create_or_update_alias(alias)` | Adds prefer, match_condition |
| `delete_knowledge_base(kb)` | Polymorphic: str or KnowledgeBase |
| `create_or_update_knowledge_base(kb)` | Adds prefer, match_condition |
| `delete_knowledge_source(ks)` | Polymorphic: str or KnowledgeSource |
| `create_or_update_knowledge_source(ks)` | Adds prefer, match_condition |
| `list_indexes(*, select)` | Uses `_convert_index_response` for projections |
| `list_index_names()` | Name-only projection via `cls` callback |
| `get_synonym_maps(*, select)` | Returns list |

**`_SearchIndexerClientOperationsMixin`** wraps:
| Method | Customization |
|--------|--------------|
| `delete_data_source_connection(dsc)` | Polymorphic: str or object |
| `create_or_update_data_source_connection(dsc)` | Adds prefer, match_condition, skip_indexer_reset |
| `delete_indexer(indexer)` | Polymorphic: str or SearchIndexer |
| `create_or_update_indexer(indexer)` | Adds prefer, match_condition, skip/disable cache |
| `delete_skillset(skillset)` | Polymorphic: str or SearchIndexerSkillset |
| `create_or_update_skillset(skillset)` | Adds prefer, match_condition, skip/disable cache |

### After Regeneration, Verify
- [ ] All generated `_delete_*`, `_create_or_update_*`, `_list_*` base methods still exist with compatible signatures
- [ ] `SearchIndexResponse` still has `.semantic` field (used by `_convert_index_response`)
- [ ] New resource types added to spec → add polymorphic delete/update wrappers here
- [ ] Verify prefer header value `"return=representation"` still applies

---

## File: `azure/search/documents/indexes/aio/_operations/_patch.py`

Async mirror of `indexes/_operations/_patch.py`. Same methods, all `async`.

Imports `_convert_index_response` from sync — NOT duplicated.

### After Regeneration, Verify
- [ ] Same checks as sync `indexes/_operations/_patch.py`
- [ ] Import of `_convert_index_response` from sync still resolves

---

## Empty `_patch.py` Files (No Customizations)

These contain only `__all__ = []` and empty `patch_sdk()`. No action needed after regeneration.

- `azure/search/documents/indexes/_patch.py`
- `azure/search/documents/indexes/aio/_patch.py`
- `azure/search/documents/knowledgebases/_patch.py`
- `azure/search/documents/knowledgebases/models/_patch.py`
- `azure/search/documents/knowledgebases/aio/_patch.py`
