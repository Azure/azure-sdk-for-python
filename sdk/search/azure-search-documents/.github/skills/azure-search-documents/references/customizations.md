# Post-Regeneration Customization Checklist

File-by-file inventory of every non-empty `_patch.py` in `azure-search-documents`. Use this after running `tsp-client update` to verify each customization still holds.

---

## File: `azure/search/documents/_patch.py`

### Depends On (from generated code)
- `._client.SearchClient` as `_SearchClient` (base class)
- `._operations._patch.SearchItemPaged`
- `.models._patch.RequestEntityTooLargeError`, `.models._patch.IndexDocumentsBatch`
- `.models.IndexAction`, `.models.IndexingResult`
- `.indexes.SearchIndexClient` (for schema lookup in buffered sender)

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `ApiVersion` | enum | Hand-maintained list of supported API versions (`CaseInsensitiveEnumMeta`) |
| `DEFAULT_VERSION` | constant | Current default (points at an `ApiVersion` member) |
| `is_retryable_status_code()` | function | Returns True for 409, 422, 503 |
| `SearchClient` | class | Subclass of `_SearchClient`; reorders constructor to `(endpoint, index_name, credential)` and pops `audience` into `credential_scopes` |
| `SearchIndexingBufferedSender` | class | Hand-authored batching sender; `threading.Timer` auto-flush, recursive 413 splitting, per-doc retry (409/422/503), key field auto-detection |

### `__all__`
```python
["SearchClient", "SearchItemPaged", "SearchIndexingBufferedSender",
 "ApiVersion", "DEFAULT_VERSION", "RequestEntityTooLargeError", "IndexDocumentsBatch"]
```

### After Regeneration, Verify
- [ ] `_SearchClient` base constructor signature unchanged (positional and keyword params)
- [ ] `_metadata.json` `apiVersion` is a member of `ApiVersion`; otherwise add member + update `DEFAULT_VERSION`
- [ ] Docstrings on `SearchClient` / `SearchIndexingBufferedSender` still list the correct default version
- [ ] Re-exports from `.models._patch` (`IndexDocumentsBatch`, `RequestEntityTooLargeError`) and `._operations._patch` (`SearchItemPaged`) still resolve

---

## File: `azure/search/documents/_operations/_patch.py`

### Depends On (from generated code)
- `._operations._SearchClientOperationsMixin` as `_SearchClientOperationsMixinGenerated` (base class)
- `..models._models.SearchRequest`, `..models._models.SearchDocumentsResult`, `..models._models.SearchResult`
- `..models` re-exports
- `..models._patch.RequestEntityTooLargeError`
- `azure.core.paging.ItemPaged`, `PageIterator`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `_convert_search_result(result)` | function | Extracts `@search.score`, `@search.reranker_score`, `@search.highlights`, `@search.captions`, `@search.document_debug_info`, `@search.reranker_boosted_score` |
| `_pack_continuation_token(response, api_version)` | function | Base64-encoded JSON: `{apiVersion, nextLink, nextPageParameters}` |
| `_unpack_continuation_token(token)` | function | Decodes token → `(next_link, next_page_request)` |
| `_build_search_request(...)` | function | Constructs `SearchRequest`; pipe-delimited encoding for `answers`/`captions`/`rewrites` |
| `SearchPageIterator` | class | Custom `PageIterator`; exposes `get_facets()`, `get_count()`, `get_coverage()`, `get_answers()`, `get_debug_info()` |
| `SearchItemPaged` | class | Extends `ItemPaged`; forwards the metadata accessors |
| `_SearchClientOperationsMixin` | class | Overrides `search()`, `index_documents()` (413 recursive splitting), `upload_documents()`, `delete_documents()`, `merge_documents()`, `merge_or_upload_documents()`, `get_document_count()` convenience helpers |

### `__all__`
```python
["_SearchClientOperationsMixin", "SearchItemPaged"]
```

### After Regeneration, Verify
- [ ] `SearchRequest` fields still match what `_build_search_request` sets; new search parameters must be wired through
- [ ] `SearchResult` fields still match what `_convert_search_result` extracts; new `@search.*` fields must be added there
- [ ] Generated mixin methods invoked via `super()` (e.g., `_search_post`, `_index`) still exist with compatible signatures
- [ ] `SearchDocumentsResult.next_page_parameters` / `next_link` still exist (used by `_pack_continuation_token`)

---

## File: `azure/search/documents/models/_patch.py`

### Depends On (from generated code)
- `._models.IndexDocumentsBatch` as `IndexDocumentsBatchGenerated` (base class)
- `._models.IndexAction`
- `._enums.IndexActionType`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `RequestEntityTooLargeError` | class | `HttpResponseError` subclass for 413 |
| `IndexDocumentsBatch` | class | Adds `add_upload_actions`, `add_delete_actions`, `add_merge_actions`, `add_merge_or_upload_actions`, `dequeue_actions`, `enqueue_actions`, `actions` property |
| `_flatten_args(...)` | function | Flattens variadic doc args (supports both `fn([doc1, doc2])` and `fn(doc1, doc2)`) |

Sets `IndexDocumentsBatch.__module__ = "azure.search.documents"` so Sphinx documents it at the public namespace and avoids duplicate object-description warnings.

### `__all__`
```python
["IndexDocumentsBatch"]
```

### After Regeneration, Verify
- [ ] `IndexDocumentsBatchGenerated` base constructor still accepts `actions=` (stored under key `"value"`)
- [ ] `IndexAction` + `IndexActionType` still exist with same action type values (`upload`, `delete`, `merge`, `mergeOrUpload`)

---

## File: `azure/search/documents/aio/_patch.py`

### Depends On (from generated code)
- `._client.SearchClient` as async `_SearchClient` (base class)
- `._operations._patch.AsyncSearchItemPaged`
- `..models._patch.RequestEntityTooLargeError`, `..models._patch.IndexDocumentsBatch`
- `..models.IndexAction`, `..models.IndexingResult`
- `..indexes.aio.SearchIndexClient` (for schema lookup)
- `.._patch.DEFAULT_VERSION`, `.._patch.is_retryable_status_code`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchClient` | class | Async subclass, same reorder + audience kwarg pop as sync |
| `SearchIndexingBufferedSender` | class | Async batching sender; `asyncio.Task` auto-flush, `asyncio.iscoroutinefunction()` callback dispatch, same 413/retry behaviour |

### `__all__`
```python
["SearchClient", "SearchIndexingBufferedSender"]
```

### After Regeneration, Verify
- [ ] Same base-class checks as sync `_patch.py`
- [ ] `DEFAULT_VERSION`, `is_retryable_status_code` imports from sync `_patch.py` still resolve

---

## File: `azure/search/documents/aio/_operations/_patch.py`

### Depends On (from generated code)
- Same generated models as sync `_operations/_patch.py`
- `azure.core.async_paging.AsyncItemPaged`, `AsyncPageIterator`

### Imports From Sync (NOT Duplicated)
- `_build_search_request`, `_convert_search_result`, `_pack_continuation_token`, `_unpack_continuation_token`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `AsyncSearchPageIterator` | class | Async version of `SearchPageIterator` |
| `AsyncSearchItemPaged` | class | Async version of `SearchItemPaged` |
| `_SearchClientOperationsMixin` | class | Async operations mixin; mirrors sync overrides |

### `__all__`
```python
["_SearchClientOperationsMixin", "AsyncSearchItemPaged"]
```

### After Regeneration, Verify
- [ ] Same checks as sync `_operations/_patch.py`
- [ ] Imports from sync `_operations/_patch.py` still resolve (don't let async drift into duplication)

---

## File: `azure/search/documents/indexes/_patch.py`

### Depends On (from generated code)
- `._client.SearchIndexClient` as `_SearchIndexClient` (base class)
- `._client.SearchIndexerClient` as `_SearchIndexerClient` (base class)

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchIndexClient` | class | Subclass; pops `audience` kwarg into `credential_scopes=[audience + "/.default"]` |
| `SearchIndexerClient` | class | Subclass; same `audience` pattern |

### `__all__`
```python
["SearchIndexClient", "SearchIndexerClient"]
```

### After Regeneration, Verify
- [ ] Generated `_SearchIndexClient` / `_SearchIndexerClient` still accept `endpoint`, `credential`, and `credential_scopes` kwarg
- [ ] No conflicting `audience` kwarg introduced at the generated layer

---

## File: `azure/search/documents/indexes/_operations/_patch.py`

### Depends On (from generated code)
- Generated `_SearchIndexClientOperationsMixin` and `_SearchIndexerClientOperationsMixin` (base classes)
- `azure.core.match_conditions.MatchConditions`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `_convert_index_response(response)` | function | Maps `SearchIndexResponse` → `SearchIndex` (`semantic` → `semantic_search`) |

**`_SearchIndexClientOperationsMixin`** wraps:

| Method | Customization |
|--------|--------------|
| `delete_index(index)` | Polymorphic: str or `SearchIndex` |
| `create_or_update_index(index)` | Forwards `prefer="return=representation"`, `match_condition`, `allow_index_downtime` |
| `delete_synonym_map(synonym_map)` | Polymorphic: str or `SynonymMap` |
| `create_or_update_synonym_map(synonym_map)` | Forwards `prefer`, `match_condition` |
| `delete_alias(alias)` | Polymorphic: str or `SearchAlias` |
| `create_or_update_alias(alias)` | Forwards `prefer`, `match_condition` |
| `delete_knowledge_base(kb)` | Polymorphic: str or `KnowledgeBase` |
| `create_or_update_knowledge_base(kb)` | Forwards `prefer`, `match_condition` |
| `delete_knowledge_source(ks)` | Polymorphic: str or `KnowledgeSource` |
| `create_or_update_knowledge_source(ks)` | Forwards `prefer`, `match_condition` |
| `list_indexes(*, select)` | Uses `_convert_index_response` for projections |
| `list_index_names()` | Name-only via `cls` callback |
| `get_synonym_maps(*, select)` | Returns list |

**`_SearchIndexerClientOperationsMixin`** wraps:

| Method | Customization |
|--------|--------------|
| `delete_data_source_connection(dsc)` | Polymorphic: str or `SearchIndexerDataSourceConnection` |
| `create_or_update_data_source_connection(dsc)` | Forwards `prefer`, `match_condition`, `skip_indexer_reset_requirement_for_cache` |
| `delete_indexer(indexer)` | Polymorphic: str or `SearchIndexer` |
| `create_or_update_indexer(indexer)` | Forwards `prefer`, `match_condition`, `skip_indexer_reset_requirement_for_cache`, `disable_cache_reprocessing_change_detection` |
| `delete_skillset(skillset)` | Polymorphic: str or `SearchIndexerSkillset` |
| `create_or_update_skillset(skillset)` | Forwards `prefer`, `match_condition`, `skip_indexer_reset_requirement_for_cache`, `disable_cache_reprocessing_change_detection` |
| `get_skillset_names()` | Name-only projection |

### `__all__`
```python
["_SearchIndexClientOperationsMixin", "_SearchIndexerClientOperationsMixin"]
```

### After Regeneration, Verify
- [ ] Generated `_delete_*`, `_create_or_update_*`, `_list_*` base methods still exist with compatible signatures
- [ ] `SearchIndexResponse.semantic` still exists (used by `_convert_index_response`)
- [ ] New resource types added to the spec → add polymorphic delete + create-or-update wrappers here (and in the async mirror)
- [ ] `prefer="return=representation"` header still accepted by the service

---

## File: `azure/search/documents/indexes/models/_patch.py`

### Depends On (from generated code)
- `._models.SearchField` as `_SearchField` (base class)
- `._models.SearchIndexerDataSourceConnection` as `_SearchIndexerDataSourceConnection` (base class)
- `._models.KnowledgeBase` as `_KnowledgeBase` (base class)
- `._enums.SearchFieldDataType` as `_SearchFieldDataType`
- `._enums.LexicalAnalyzerName`
- Type-only imports for `DataChangeDetectionPolicy`, `DataDeletionDetectionPolicy`, `DataSourceCredentials`, `SearchIndexerDataContainer`, `SearchIndexerDataIdentity`, `SearchResourceEncryptionKey`, `SearchIndexerDataSourceType`

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchField` | class | Adds `hidden` property (inverse of `retrievable`); accepts `hidden` kwarg |
| `SearchIndexerDataSourceConnection` | class | Three `@overload`s (credentials / connection_string / mapping) |
| `KnowledgeBase` | class | Placeholder subclass (entry point for future customizations) |
| `SimpleField(...)` | function | Builder; forces `searchable=False` |
| `SearchableField(...)` | function | Builder; auto-types to `String` / `Collection(String)` |
| `ComplexField(...)` | function | Builder; sets type to `Complex` / `Collection(Complex)` |
| `Collection(typ)` | function | Wraps type in `"Collection(...)"` string form |
| `_collection_helper(typ)` | function | Private helper used by `SearchFieldDataType.Collection` staticmethod |

### Monkey-Patched on `SearchFieldDataType`
```python
SearchFieldDataType.Collection      = staticmethod(_collection_helper)
SearchFieldDataType.String          = SearchFieldDataType.STRING
SearchFieldDataType.Int32           = SearchFieldDataType.INT32
SearchFieldDataType.Int64           = SearchFieldDataType.INT64
SearchFieldDataType.Single          = SearchFieldDataType.SINGLE
SearchFieldDataType.Double          = SearchFieldDataType.DOUBLE
SearchFieldDataType.Boolean         = SearchFieldDataType.BOOLEAN
SearchFieldDataType.DateTimeOffset  = SearchFieldDataType.DATE_TIME_OFFSET
SearchFieldDataType.GeographyPoint  = SearchFieldDataType.GEOGRAPHY_POINT
SearchFieldDataType.ComplexType     = SearchFieldDataType.COMPLEX
```

### `__all__`
```python
["KnowledgeBase", "SearchField", "SearchFieldDataType",
 "SearchIndexerDataSourceConnection", "SimpleField", "SearchableField", "ComplexField"]
```

### After Regeneration, Verify
- [ ] All right-hand-side UPPER_CASE enum members (`STRING`, `INT32`, `INT64`, `SINGLE`, `DOUBLE`, `BOOLEAN`, `DATE_TIME_OFFSET`, `GEOGRAPHY_POINT`, `COMPLEX`) still exist on generated `SearchFieldDataType`
- [ ] `_SearchField`, `_SearchIndexerDataSourceConnection`, `_KnowledgeBase` base constructors unchanged
- [ ] `SearchField.retrievable` still exists (the `hidden` property inverts it)
- [ ] If a new generated enum value collides with a Python keyword, add an alias

---

## File: `azure/search/documents/indexes/aio/_patch.py`

### Depends On (from generated code)
- `._client.SearchIndexClient` as async `_SearchIndexClient` (base class)
- `._client.SearchIndexerClient` as async `_SearchIndexerClient` (base class)

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `SearchIndexClient` | class | Async subclass; same `audience` → `credential_scopes` pattern |
| `SearchIndexerClient` | class | Async subclass; same pattern |

### `__all__`
```python
["SearchIndexClient", "SearchIndexerClient"]
```

### After Regeneration, Verify
- [ ] Same checks as sync `indexes/_patch.py`

---

## File: `azure/search/documents/indexes/aio/_operations/_patch.py`

Async mirror of `indexes/_operations/_patch.py`. Same polymorphic delete / create-or-update wrappers, all `async`.

Imports `_convert_index_response` from sync — NOT duplicated.

### `__all__`
```python
["_SearchIndexClientOperationsMixin", "_SearchIndexerClientOperationsMixin"]
```

### After Regeneration, Verify
- [ ] Same checks as sync `indexes/_operations/_patch.py`
- [ ] Import of `_convert_index_response` from sync still resolves

---

## File: `azure/search/documents/knowledgebases/_patch.py`

### Depends On (from generated code)
- `._client.KnowledgeBaseRetrievalClient` as `_KnowledgeBaseRetrievalClient` (base class)

### Defines
| Symbol | Type | What It Does |
|--------|------|-------------|
| `KnowledgeBaseRetrievalClient` | class | Subclass; pops `audience` kwarg into `credential_scopes` |

### `__all__`
```python
["KnowledgeBaseRetrievalClient"]
```

### After Regeneration, Verify
- [ ] Generated base still accepts `endpoint`, `credential`, `knowledge_base_name`, `credential_scopes`
- [ ] No conflicting `audience` kwarg introduced at the generated layer

---

## File: `azure/search/documents/knowledgebases/aio/_patch.py`

Async mirror of `knowledgebases/_patch.py`. `KnowledgeBaseRetrievalClient` subclass applying the same `audience` → `credential_scopes` pattern against the async generated base.

### `__all__`
```python
["KnowledgeBaseRetrievalClient"]
```

### After Regeneration, Verify
- [ ] Same checks as sync `knowledgebases/_patch.py`

---

## Empty `_patch.py` Files (No Customizations)

These contain only `__all__ = []` and empty `patch_sdk()`. No action needed after regeneration.

- `azure/search/documents/knowledgebases/_operations/_patch.py`
- `azure/search/documents/knowledgebases/models/_patch.py`
- `azure/search/documents/knowledgebases/aio/_operations/_patch.py`
