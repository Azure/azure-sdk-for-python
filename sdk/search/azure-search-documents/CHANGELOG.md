# Release History

## 12.0.0 (2026-04-01)

### Features Added

- Below clients, models, and enum members are added for knowledge base support
  - `azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient`
  - `azure.search.documents.indexes.models.AzureBlobKnowledgeSource`
  - `azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSource`
  - `azure.search.documents.indexes.models.KnowledgeBase`
  - `azure.search.documents.indexes.models.SearchIndexKnowledgeSource`
  - `azure.search.documents.indexes.models.WebKnowledgeSource`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecordType.MODEL_WEB_SUMMARIZATION`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseModelWebSummarizationActivityRecord`
  - `azure.search.documents.knowledgebases.models.KnowledgeRetrievalMinimalReasoningEffort`
  - `azure.search.documents.knowledgebases.models.KnowledgeRetrievalReasoningEffort`
  - `azure.search.documents.knowledgebases.models.KnowledgeSourceStatistics`
  - `azure.search.documents.knowledgebases.models.KnowledgeSourceStatus`
  - `azure.search.documents.knowledgebases.models.KnowledgeSourceSynchronizationError`

- Below properties are added or changed for index and indexer enhancements
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.identity` for managed identity support on data source connections.
  - `azure.search.documents.indexes.models.SearchIndexerKnowledgeStore.identity` for managed identity support on knowledge store projections.
  - `azure.search.documents.indexes.models.SearchResourceEncryptionKey.key_version` changed from required to optional, aligning with service behavior.

- Below enum members and properties are added for Markdown parsing
  - `azure.search.documents.indexes.models.BlobIndexerParsingMode.MARKDOWN` enum value for native Markdown file parsing in blob indexers.
  - `azure.search.documents.indexes.models.IndexingParametersConfiguration.markdown_header_depth` (`h1` through `h6`) to set header depth for sectioning.
  - `azure.search.documents.indexes.models.IndexingParametersConfiguration.markdown_parsing_submode` (`oneToOne` or `oneToMany`) to control document splitting.

- Below models are added
  - `azure.search.documents.indexes.models.ChatCompletionCommonModelParameters`
  - `azure.search.documents.indexes.models.ChatCompletionResponseFormat`
  - `azure.search.documents.indexes.models.ChatCompletionSchema`
  - `azure.search.documents.indexes.models.ChatCompletionSkill`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkill`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingProperties`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingUnit`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkillExtractionOptions`
  - `azure.search.documents.knowledgebases.models.AIServices`
  - `azure.search.documents.knowledgebases.models.CompletedSynchronizationState`
  - `azure.search.documents.knowledgebases.models.SynchronizationState`

### Breaking Changes

- `serialize()` and `deserialize()` methods on models are removed. Use `as_dict()` to serialize and the model constructor to deserialize (e.g., `index.as_dict()` instead of `index.serialize()`, `SearchIndex(data)` instead of `SearchIndex.deserialize(data)`).
- Below models do not exist in this release
  - `azure.search.documents.indexes.models.EntityRecognitionSkill`
  - `azure.search.documents.indexes.models.EntityRecognitionSkillVersion`
  - `azure.search.documents.indexes.models.PathHierarchyTokenizer` (renamed to `PathHierarchyTokenizerV2`)
  - `azure.search.documents.indexes.models.SentimentSkill`
  - `azure.search.documents.indexes.models.SentimentSkillVersion`
- Below enum members do not exist in this release
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceType.MY_SQL` (renamed to `MYSQL`)
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceType.ONE_LAKE` (renamed to `ONELAKE`)
- Below properties do not exist in this release
  - `azure.search.documents.indexes.models.BinaryQuantizationCompression.rerank_with_original_vectors`
  - `azure.search.documents.indexes.models.ScalarQuantizationCompression.rerank_with_original_vectors`
  - `azure.search.documents.indexes.models.VectorSearchCompression.rerank_with_original_vectors`

> The following changes do not impact the API of stable versions such as 11.6.0.
> Only code written against a beta version such as 11.7.0b2 may be affected.

- Below models do not exist in this release
  - `azure.search.documents.indexes.models.AIServicesVisionParameters`
  - `azure.search.documents.indexes.models.AIServicesVisionVectorizer`
  - `azure.search.documents.indexes.models.AzureMachineLearningSkill`
  - `azure.search.documents.indexes.models.AzureOpenAITokenizerParameters`
  - `azure.search.documents.indexes.models.IndexedSharePointContainerName`
  - `azure.search.documents.indexes.models.IndexerCurrentState`
  - `azure.search.documents.indexes.models.IndexerExecutionStatusDetail`
  - `azure.search.documents.indexes.models.IndexerPermissionOption`
  - `azure.search.documents.indexes.models.IndexerRuntime`
  - `azure.search.documents.indexes.models.IndexingMode`
  - `azure.search.documents.indexes.models.IndexStatisticsSummary`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalLowReasoningEffort`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalMediumReasoningEffort`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalOutputMode`
  - `azure.search.documents.indexes.models.KnowledgeSourceIngestionPermissionOption`
  - `azure.search.documents.indexes.models.PermissionFilter`
  - `azure.search.documents.indexes.models.SearchIndexerCache`
  - `azure.search.documents.indexes.models.SearchIndexPermissionFilterOption`
  - `azure.search.documents.indexes.models.ServiceIndexersRuntime`
  - `azure.search.documents.indexes.models.SplitSkillEncoderModelName`
  - `azure.search.documents.indexes.models.SplitSkillUnit`
  - `azure.search.documents.indexes.models.VisionVectorizeSkill`
  - `azure.search.documents.knowledgebases.models.IndexedSharePointKnowledgeSourceParams`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSharePointReference`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseModelAnswerSynthesisActivityRecord`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseModelQueryPlanningActivityRecord`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseRemoteSharePointReference`
  - `azure.search.documents.knowledgebases.models.RemoteSharePointKnowledgeSourceParams`
  - `azure.search.documents.models.DebugInfo`
  - `azure.search.documents.models.HybridCountAndFacetMode`
  - `azure.search.documents.models.HybridSearch`
  - `azure.search.documents.models.QueryLanguage`
  - `azure.search.documents.models.QueryResultDocumentInnerHit`
  - `azure.search.documents.models.QueryResultDocumentRerankerInput`
  - `azure.search.documents.models.QueryResultDocumentSemanticField`
  - `azure.search.documents.models.QueryRewritesDebugInfo`
  - `azure.search.documents.models.QueryRewritesType`
  - `azure.search.documents.models.QueryRewritesValuesDebugInfo`
  - `azure.search.documents.models.QuerySpellerType`
  - `azure.search.documents.models.SearchDocumentsResult`
  - `azure.search.documents.models.SearchScoreThreshold`
  - `azure.search.documents.models.SemanticDebugInfo`
  - `azure.search.documents.models.SemanticFieldState`
  - `azure.search.documents.models.SemanticQueryRewritesResultType`
  - `azure.search.documents.models.VectorSimilarityThreshold`
  - `azure.search.documents.models.VectorThreshold`
  - `azure.search.documents.models.VectorThresholdKind`
  - SharePoint knowledge source types (`IndexedSharePointKnowledgeSource`, `RemoteSharePointKnowledgeSource` and related models including `IndexedSharePointKnowledgeSourceParameters`, `RemoteSharePointKnowledgeSourceParameters`, `SharePointSensitivityLabelInfo`)

- Below properties do not exist in this release
  - `azure.search.documents.indexes.models.ChatCompletionSkill.auth_resource_id`
  - `azure.search.documents.indexes.models.ChatCompletionSkill.batch_size`
  - `azure.search.documents.indexes.models.ChatCompletionSkill.degree_of_parallelism`
  - `azure.search.documents.indexes.models.ChatCompletionSkill.http_headers`
  - `azure.search.documents.indexes.models.ChatCompletionSkill.http_method`
  - `azure.search.documents.indexes.models.ChatCompletionSkill.timeout`
  - `azure.search.documents.indexes.models.IndexerExecutionResult.mode`
  - `azure.search.documents.indexes.models.IndexerExecutionResult.status_detail`
  - `azure.search.documents.indexes.models.KnowledgeBase.answer_instructions`
  - `azure.search.documents.indexes.models.KnowledgeBase.output_mode`
  - `azure.search.documents.indexes.models.KnowledgeBase.retrieval_instructions`
  - `azure.search.documents.indexes.models.KnowledgeBase.retrieval_reasoning_effort`
  - `azure.search.documents.indexes.models.KnowledgeSourceIngestionParameters.ingestion_permission_options`
  - `azure.search.documents.indexes.models.SearchField.permission_filter`
  - `azure.search.documents.indexes.models.SearchField.sensitivity_label`
  - `azure.search.documents.indexes.models.SearchIndex.permission_filter_option`
  - `azure.search.documents.indexes.models.SearchIndex.purview_enabled`
  - `azure.search.documents.indexes.models.SearchIndexer.cache`
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.indexer_permission_options`
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.sub_type`
  - `azure.search.documents.indexes.models.SearchIndexerDataUserAssignedIdentity.federated_identity_client_id`
  - `azure.search.documents.indexes.models.SearchIndexerKnowledgeStore.parameters`
  - `azure.search.documents.indexes.models.SearchIndexerStatus.current_state`
  - `azure.search.documents.indexes.models.SearchIndexerStatus.runtime`
  - `azure.search.documents.indexes.models.SearchServiceStatistics.indexers_runtime`
  - `azure.search.documents.indexes.models.SemanticConfiguration.flighting_opt_in`
  - `azure.search.documents.indexes.models.SplitSkill.azure_open_ai_tokenizer_parameters`
  - `azure.search.documents.indexes.models.SplitSkill.unit`
  - `azure.search.documents.knowledgebases.models.AzureBlobKnowledgeSourceParams.always_query_source`
  - `azure.search.documents.knowledgebases.models.IndexedOneLakeKnowledgeSourceParams.always_query_source`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.max_output_size`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.messages`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.output_mode`
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.retrieval_reasoning_effort`
  - `azure.search.documents.knowledgebases.models.KnowledgeSourceParams.always_query_source`
  - `azure.search.documents.knowledgebases.models.WebKnowledgeSourceParams.always_query_source`
  - `azure.search.documents.models.DebugInfo.query_rewrites`
  - `azure.search.documents.models.DocumentDebugInfo.inner_hits`
  - `azure.search.documents.models.DocumentDebugInfo.semantic`
  - `azure.search.documents.models.FacetResult.avg`
  - `azure.search.documents.models.FacetResult.cardinality`
  - `azure.search.documents.models.FacetResult.facets`
  - `azure.search.documents.models.FacetResult.max`
  - `azure.search.documents.models.FacetResult.min`
  - `azure.search.documents.models.FacetResult.sum`
  - `azure.search.documents.models.SearchDocumentsResult.debug_info`
  - `azure.search.documents.models.SearchDocumentsResult.semantic_query_rewrites_result_type`
  - `azure.search.documents.models.VectorizableTextQuery.query_rewrites`
  - `azure.search.documents.models.VectorQuery.filter_override`
  - `azure.search.documents.models.VectorQuery.per_document_vector_limit`
  - `azure.search.documents.models.VectorQuery.threshold`

- Below parameters do not exist in this release
  - `SearchClient.search.hybrid_search`
  - `SearchClient.search.query_language`
  - `SearchClient.search.query_rewrites`
  - `SearchClient.search.semantic_fields`
  - `SearchClient.search.speller`
  - `SearchIndexerClient.create_or_update_data_source_connection.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_indexer.disable_cache_reprocessing_change_detection`
  - `SearchIndexerClient.create_or_update_indexer.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_skillset.disable_cache_reprocessing_change_detection`
  - `SearchIndexerClient.create_or_update_skillset.skip_indexer_reset_requirement_for_cache`

- Below operations do not exist in this release
  - `SearchIndexClient.list_index_stats_summary`
  - `SearchIndexerClient.reset_documents`
  - `SearchIndexerClient.reset_skills`
  - `SearchIndexerClient.resync`

- Below enum values do not exist in this release
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT4_O`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT4_O_MINI`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT41`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT41_MINI`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT41_NANO`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT5`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT5_MINI` (renamed to `GPT_5_MINI`)
  - `azure.search.documents.indexes.models.AzureOpenAIModelName.GPT5_NANO` (renamed to `GPT_5_NANO`)
  - `azure.search.documents.indexes.models.KnowledgeSourceKind.INDEXED_ONE_LAKE` (renamed to `INDEXED_ONELAKE`)
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceType.SHARE_POINT` (renamed to `SHAREPOINT`)
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecordType.INDEXED_ONE_LAKE` (renamed to `INDEXED_ONELAKE`)
  - `azure.search.documents.knowledgebases.models.KnowledgeBaseReferenceType.INDEXED_ONE_LAKE` (renamed to `INDEXED_ONELAKE`)
  - `azure.search.documents.knowledgebases.models.KnowledgeRetrievalReasoningEffortKind.LOW`
  - `azure.search.documents.knowledgebases.models.KnowledgeRetrievalReasoningEffortKind.MEDIUM`

### Deprecated

The following changes are due to the migration from AutoRest to TypeSpec code generation. The old API continues to work at runtime via backward-compatible aliases:

- `azure.search.documents.indexes.models.SearchFieldDataType` enum values are now UPPER_CASE (e.g., `STRING` instead of `String`). PascalCase aliases (e.g., `SearchFieldDataType.String`) are preserved and continue to work at runtime.
- `azure.search.documents.indexes.models.SearchField` now uses `retrievable` (from the API) as its native property instead of `hidden`. A `hidden` property (the inverse of `retrievable`) is preserved for backward compatibility via getter/setter.

### Other Changes

- Updated default API version to `2026-04-01`.
- Some boolean properties now default to `None` instead of `True` or `False`. There is no behavioral change — the server applies the same default when the property is omitted. Examples include:
  - `azure.search.documents.indexes.models.CommonGramTokenFilter.ignore_case`
  - `azure.search.documents.indexes.models.CommonGramTokenFilter.use_query_mode`
  - `azure.search.documents.indexes.models.DictionaryDecompounderTokenFilter.only_longest_match`
  - `azure.search.documents.indexes.models.KeywordMarkerTokenFilter.ignore_case`
  - `azure.search.documents.indexes.models.StopwordsTokenFilter.ignore_case`
  - `azure.search.documents.indexes.models.SynonymTokenFilter.ignore_case`

## 11.7.0b2 (2025-11-13)

### Features Added

- Added new models:
  - `azure.search.documents.indexes.models.AIServices`
  - `azure.search.documents.indexes.models.CompletedSynchronizationState`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkill`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingProperties`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingUnit`
  - `azure.search.documents.indexes.models.ContentUnderstandingSkillExtractionOptions`
  - `azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSource`
  - `azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSourceParameters`
  - `azure.search.documents.indexes.models.IndexedSharePointContainerName`
  - `azure.search.documents.indexes.models.IndexedSharePointKnowledgeSource`
  - `azure.search.documents.indexes.models.IndexedSharePointKnowledgeSourceParameters`
  - `azure.search.documents.indexes.models.IndexerRuntime`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalLowReasoningEffort`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalMediumReasoningEffort`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalMinimalReasoningEffort`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalOutputMode`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalReasoningEffort`
  - `azure.search.documents.indexes.models.KnowledgeRetrievalReasoningEffortKind`
  - `azure.search.documents.indexes.models.KnowledgeSourceAzureOpenAIVectorizer`
  - `azure.search.documents.indexes.models.KnowledgeSourceContentExtractionMode`
  - `azure.search.documents.indexes.models.KnowledgeSourceIngestionParameters`
  - `azure.search.documents.indexes.models.KnowledgeSourceIngestionPermissionOption`
  - `azure.search.documents.indexes.models.KnowledgeSourceStatistics`
  - `azure.search.documents.indexes.models.KnowledgeSourceStatus`
  - `azure.search.documents.indexes.models.KnowledgeSourceSynchronizationStatus`
  - `azure.search.documents.indexes.models.KnowledgeSourceVectorizer`
  - `azure.search.documents.indexes.models.RemoteSharePointKnowledgeSource`
  - `azure.search.documents.indexes.models.RemoteSharePointKnowledgeSourceParameters`
  - `azure.search.documents.indexes.models.SearchIndexFieldReference`
  - `azure.search.documents.indexes.models.ServiceIndexersRuntime`
  - `azure.search.documents.indexes.models.SynchronizationState`
  - `azure.search.documents.indexes.models.WebKnowledgeSource`
  - `azure.search.documents.indexes.models.WebKnowledgeSourceDomain`
  - `azure.search.documents.indexes.models.WebKnowledgeSourceDomains`
  - `azure.search.documents.indexes.models.WebKnowledgeSourceParameters`

- Expanded existing models and enums:
  - Added support for `avg`, `min`, `max`, and `cardinality` metrics on `azure.search.documents.models.FacetResult`.
  - Added `is_adls_gen2` and `ingestion_parameters` options on `azure.search.documents.indexes.models.AzureBlobKnowledgeSourceParameters`.
  - Added support for `gpt-5`, `gpt-5-mini`, and `gpt-5-nano` values on `azure.search.documents.indexes.models.AzureOpenAIModelName`.
  - Added support for `web`, `remoteSharePoint`, `indexedSharePoint`, and `indexedOneLake` values on `azure.search.documents.indexes.models.KnowledgeSourceKind`.
  - Added support for `onelake` and `sharepoint` values on `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.type`.
  - Added `azure.search.documents.indexes.models.SearchField.sensitivity_label`.
  - Added `azure.search.documents.indexes.models.SearchIndexerStatus.runtime`.
  - Added `azure.search.documents.indexes.models.SearchIndex.purview_enabled`.
  - Added `azure.search.documents.indexes.models.SearchServiceLimits.max_cumulative_indexer_runtime_seconds`.
  - Added `azure.search.documents.indexes.models.SearchServiceStatistics.indexers_runtime`.
  - Added `product` aggregation support to `azure.search.documents.indexes.models.ScoringFunctionAggregation`.
  - Added `share_point` to `azure.search.documents.indexes.models.SearchIndexerDataSourceType`.
  - Added `include_references`, `include_reference_source_data`, `always_query_source`, and `reranker_threshold` options on `azure.search.documents.knowledgebases.models.SearchIndexKnowledgeSourceParams`.
  - Added `error` tracking details on `azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecord` derivatives.

- Client and service enhancements:
  - Added support for HTTP 206 partial content responses when calling `azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient.knowledge_retrieval.retrieve`.
  - Added optional `x_ms_enable_elevated_read` keyword to `azure.search.documents.SearchClient.search` and `azure.search.documents.aio.SearchClient.search` for elevated document reads.

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.6.0.
> Only code written against a beta version such as 11.6.0b12 may be affected.

- Knowledge base naming and routing refresh:
  - Renamed the knowledge agent surface area to the knowledge base equivalents:
    - `azure.search.documents.indexes.models.KnowledgeAgent` -> `azure.search.documents.indexes.models.KnowledgeBase`
    - `azure.search.documents.indexes.models.KnowledgeAgentAzureOpenAIModel` -> `azure.search.documents.indexes.models.KnowledgeBaseAzureOpenAIModel`
    - `azure.search.documents.indexes.models.KnowledgeAgentModel` -> `azure.search.documents.indexes.models.KnowledgeBaseModel`
    - `azure.search.documents.indexes.models.KnowledgeAgentModelKind` -> `azure.search.documents.indexes.models.KnowledgeBaseModelKind`
  - Knowledge base clients now target `/knowledgebases` REST routes and accept `knowledge_base_name` instead of the agent name parameter.
  - Replaced `azure.search.documents.indexes.models.KnowledgeAgentOutputConfiguration` with `azure.search.documents.indexes.models.KnowledgeBase.output_mode`.
  - Replaced `azure.search.documents.indexes.models.KnowledgeAgentOutputConfigurationModality` with `azure.search.documents.indexes.models.KnowledgeRetrievalOutputMode`.
  - Removed `azure.search.documents.indexes.models.KnowledgeAgentRequestLimits`; callers should apply request guardrails at the service level.
- Knowledge source parameterization updates:
  - Updated `azure.search.documents.indexes.models.AzureBlobKnowledgeSourceParameters` to use `azure.search.documents.indexes.models.KnowledgeSourceIngestionParameters`, replacing the previous `identity`, `embedding_model`, `chat_completion_model`, `ingestion_schedule`, and `disable_image_verbalization` properties with the new `is_adls_gen2` and `ingestion_parameters` shape.
  - Updated `azure.search.documents.indexes.models.KnowledgeSourceReference` to carry only the source name, moving the `include_references`, `include_reference_source_data`, `always_query_source`, `max_sub_queries`, and `reranker_threshold` options onto the concrete parameter types.
- Compression configuration cleanup:
  - Removed the `default_oversampling` property from `azure.search.documents.indexes.models.BinaryQuantizationCompression`, `azure.search.documents.indexes.models.ScalarQuantizationCompression`, and `azure.search.documents.indexes.models.VectorSearchCompression`.
  - Removed the `rerank_with_original_vectors` property from `azure.search.documents.indexes.models.BinaryQuantizationCompression`, `azure.search.documents.indexes.models.ScalarQuantizationCompression`, and `azure.search.documents.indexes.models.VectorSearchCompression`.
- Knowledge source parameter field realignment:
  - Replaced `azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters.source_data_select` with `azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters.source_data_fields`.
  - Added `azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters.search_fields` for field mapping.
  - Added optional `azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters.semantic_configuration_name`.

## 11.6.0 (2025-10-10)

### Features Added

- Added `azure.search.documents.DocumentDebugInfo`.
- Added `azure.search.documents.QueryDebugMode`.
- Added `azure.search.documents.QueryResultDocumentSubscores`.
- Added `azure.search.documents.SingleVectorFieldResult`.
- Added `azure.search.documents.TextResult`.
- Added `azure.search.documents.VectorsDebugInfo`.
- Added new parameter `debug` in `azure.search.documents.SearchClient.search`.
- Added `azure.search.documents.indexes.LexicalNormalizer`.
- Added `azure.search.documents.indexes.LexicalNormalizerName`.
- Added `azure.search.documents.indexes.AnalyzeTextOptions.normalizer_name`.
- Added `azure.search.documents.indexes.CustomNormalizer`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkill`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillExtractionOptions`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillChunkingProperties`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillChunkingUnit`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillMarkdownHeaderDepth`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillOutputFormat`.
- Added `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillOutputMode`.
- Added `azure.search.documents.indexes.RankingOrder`.
- Added `azure.search.documents.indexes.RescoringOptions`.
- Added `azure.search.documents.indexes.SearchField.normalizer_name`.
- Added `azure.search.documents.indexes.SearchIndex.normalizer`.
- Added `azure.search.documents.indexes.SearchIndexerKnowledgeStoreParameters`.
- Added `azure.search.documents.indexes.VectorSearchCompressionRescoreStorageMethod`.
- Support for running `VectorQuery`s against sub-fields of complex fields.
- Added support for `2025-09-01` service version.
  - Support for reranker boosted scores in search results and the ability to sort results on either reranker or reranker
    boosted scores in `SemanticConfiguration.rankingOrder`.
  - Support for `VectorSearchCompression.RescoringOptions` to configure how vector compression handles the original
    vector when indexing and how vectors are used during rescoring.
  - Added `SearchIndex.description` to provide a textual description of the index.
  - Support for `LexicalNormalizer` when defining `SearchIndex`, `SimpleField`, and `SearchableField` and the ability to
    use it when analyzing text with `SearchIndexClient.analyzeText` and `SearchIndexAsyncClient.analyzeText`.
  - Support `DocumentIntelligenceLayoutSkill` skillset skill and `OneLake` `SearchIndexerDataSourceConnection` data source.
  - Support for `QueryDebugMode` in searching to retrieve detailed information about search processing. Only `vector` is
    supported for `QueryDebugMode`.

### Breaking Changes

- `VectorSearchCompression.rerankWithOriginalVectors` and `VectorSearchCompression.defaultOversampling` don't work with
  `2025-09-01` and were replaced by `VectorSearchCompression.RescoringOptions.enabledRescoring` and
  `VectorSearchCompression.RescoringOptions.defaultOversampling`. If using `2024-07-01` continue using the old properties,
  otherwise if using `2025-09-01` use the new properties in `RescoringOptions`.

### Other Changes

- Updated default API version to `2025-09-01`.

## 11.7.0b1 (2025-09-05)

### Features Added

- Added `azure.search.documents.models.DebugInfo`.
- Added `azure.search.documents.indexes.models.AzureBlobKnowledgeSource`.
- Added `azure.search.documents.indexes.models.AzureBlobKnowledgeSourceParameters`.
- Added `azure.search.documents.indexes.models.IndexerResyncBody`.
- Added `azure.search.documents.indexes.models.KnowledgeAgentOutputConfiguration`.
- Added `azure.search.documents.indexes.models.KnowledgeAgentOutputConfigurationModality`.
- Added `azure.search.documents.indexes.models.KnowledgeSource`.
- Added `azure.search.documents.indexes.models.KnowledgeSourceKind`.
- Added `azure.search.documents.indexes.models.KnowledgeSourceReference`.
- Added `azure.search.documents.indexes.models.SearchIndexKnowledgeSource`.
- Added `azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters`.
- Removed `azure.search.documents.indexes.models.KnowledgeAgentTargetIndex`.
- Added `azure.search.documents.indexes.models.SearchIndex.description`.
- Added `azure.search.documents.agent.models.KnowledgeAgentAzureBlobActivityArguments`.
- Added `azure.search.documents.agent.models.KnowledgeAgentAzureBlobActivityRecord`.
- Added `azure.search.documents.agent.models.KnowledgeAgentAzureBlobReference`.
- Added `azure.search.documents.agent.models.KnowledgeAgentModelAnswerSynthesisActivityRecord`.
- Added `azure.search.documents.agent.models.KnowledgeAgentRetrievalActivityRecord`.
- Added `azure.search.documents.agent.models.KnowledgeAgentSearchIndexActivityArguments`.
- Added `azure.search.documents.agent.models.KnowledgeAgentSearchIndexActivityRecord`.
- Added `azure.search.documents.agent.models.KnowledgeAgentSearchIndexReference`.
- Added `azure.search.documents.agent.models.KnowledgeAgentSemanticRerankerActivityRecord`.
- Added `azure.search.documents.agent.models.KnowledgeSourceParams`.
- Added `azure.search.documents.agent.models.SearchIndexKnowledgeSourceParams`.
- Removed `azure.search.documents.agent.models.KnowledgeAgentAzureSearchDocReference`.
- Removed `azure.search.documents.agent.models.KnowledgeAgentIndexParams`.
- Removed `azure.search.documents.agent.models.KnowledgeAgentSearchActivityRecord`.
- Removed `azure.search.documents.agent.models.KnowledgeAgentSearchActivityRecordQuery`.
- Removed `azure.search.documents.agent.models.KnowledgeAgentSemanticRankerActivityRecord`.
- Added KnowledgeSource operations in `SearchIndexClient`.

### Other Changes

- Updated default API version to `2025-08-01-preview`.

## 11.5.3 (2025-06-25)

### Bugs Fixed

- Fixed the issue search operation did not handle 206 correctly.

## 11.6.0b12 (2025-05-14)

### Features Added

- Added `azure.search.documents.agent.KnowledgeAgentRetrievalClient`.
- Added knowledge agents operations in `SearchIndexClient`.
- Added `resync` method in `SearchIndexerClient`.
- Exposed `@search.reranker_boosted_score` in the search results.
- Added `x_ms_query_source_authorization` as a keyword argument to `SearchClient.search`.
- Added property `azure.search.documents.indexes.models.SearchField.permission_filter`.
- Added property `azure.search.documents.indexes.models.SearchIndex.permission_filter_option`.
- Added property `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.indexer_permission_options`.

- Added new models:
    - `azure.search.documents.models.QueryResultDocumentInnerHit`
    - `azure.search.documents.indexes.models.ChatCompletionExtraParametersBehavior`
    - `azure.search.documents.indexes.models.ChatCompletionResponseFormat`
    - `azure.search.documents.indexes.models.ChatCompletionResponseFormatType`
    - `azure.search.documents.indexes.models.ChatCompletionResponseFormatJsonSchemaProperties`
    - `azure.search.documents.indexes.models.ChatCompletionSchema`
    - `azure.search.documents.indexes.models.ChatCompletionSkill`
    - `azure.search.documents.indexes.models.CommonModelParameters`
    - `azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillChunkingProperties`
    - `azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillChunkingUnit`
    - `azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillExtractionOptions`
    - `azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillOutputFormat`
    - `azure.search.documents.indexes.models.IndexerPermissionOption`
    - `azure.search.documents.indexes.models.IndexerResyncOption`
    - `azure.search.documents.indexes.models.KnowledgeAgent`
    - `azure.search.documents.indexes.models.KnowledgeAgentAzureOpenAIModel`
    - `azure.search.documents.indexes.models.KnowledgeAgentModel`
    - `azure.search.documents.indexes.models.KnowledgeAgentModelKind`
    - `azure.search.documents.indexes.models.KnowledgeAgentRequestLimits`
    - `azure.search.documents.indexes.models.KnowledgeAgentTargetIndex`
    - `azure.search.documents.indexes.models.PermissionFilter`
    - `azure.search.documents.indexes.models.RankingOrder`
    - `azure.search.documents.indexes.models.SearchIndexPermissionFilterOption`

### Bugs Fixed

- Fixed the issue batching in upload_documents() did not work.    #40157

### Other Changes

- Updated the API version to "2025-05-01-preview"

## 11.6.0b11 (2025-03-25)

### Bugs Fixed

- Fixed the issue that could not deserialize `document_debug_info`.    #40138

## 11.6.0b10 (2025-03-11)

### Features Added

- Added `SearchIndexClient.list_index_stats_summary`.
- Added `SearchIndexerCache.id`.
- Added new model `azure.search.documents.indexes.models.IndexStatisticsSummary`.

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.5.0.
> Only code written against a beta version such as 11.6.0b9 may be affected.
- Renamed `azure.search.documents.indexes.models.AIStudioModelCatalogName` to `azure.search.documents.indexes.models.AIFoundryModelCatalogName`.

### Other Changes

- Updated the API version to "2025-03-01-preview"

## 11.6.0b9 (2025-01-14)

### Bugs Fixed

- Exposed `@search.document_debug_info` in the search results.

## 11.6.0b8 (2024-11-21)

### Features Added

- Added `get_debug_info` in Search results.

## 11.6.0b7 (2024-11-18)

### Features Added

- Added `SearchResourceEncryptionKey`.`identity` support.
- Added `query_rewrites` & `query_rewrites_count` in `SearchClient.Search`.
- Added `query_rewrites` in `VectorizableTextQuery`.
- Added new models:
  - `azure.search.documents.QueryRewritesType`
  - `azure.search.documents.indexes.AIServicesAccountIdentity`
  - `azure.search.documents.indexes.AIServicesAccountKey`
  - `azure.search.documents.indexes.AzureOpenAITokenizerParameters`
  - `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillMarkdownHeaderDepth`
  - `azure.search.documents.indexes.DocumentIntelligenceLayoutSkillOutputMode`
  - `azure.search.documents.indexes.DataSourceCredentials`
  - `azure.search.documents.indexes.DocumentIntelligenceLayoutSkill`
  - `azure.search.documents.indexes.IndexerCurrentState`
  - `azure.search.documents.indexes.MarkdownHeaderDepth`
  - `azure.search.documents.indexes.MarkdownParsingSubmode`
  - `azure.search.documents.indexes.RescoringOptions`
  - `azure.search.documents.indexes.ResourceCounter`
  - `azure.search.documents.indexes.SkillNames`
  - `azure.search.documents.indexes.SplitSkillEncoderModelName`
  - `azure.search.documents.indexes.SplitSkillUnit`
  - `azure.search.documents.indexes.VectorSearchCompressionKind`
  - `azure.search.documents.indexes.VectorSearchCompressionRescoreStorageMethod`

### Other Changes

- Updated the API version to "2024-1-01-preview"

## 11.5.2 (2024-10-31)

### Bugs Fixed

- Fixed the issue that `encryptionKey` was lost during serialization.  #37521

## 11.6.0b6 (2024-10-08)

### Bugs Fixed

- Fixed the issue that `encryptionKey` in `SearchIndexer` was lost during serialization.  #37521

## 11.6.0b5 (2024-09-19)

### Features Added

- `SearchIndexClient`.`get_search_client` inherits the API version.

### Bugs Fixed

- Fixed the issue that we missed ODATA header when using Entra ID auth.
- Fixed the issue that `encryptionKey` was lost during serialization.  #37251

### Other Changes

- Updated the API version to "2024-09-01-preview"

### Breaking changes

> These changes do not impact the API of stable versions such as 11.5.0.
> Only code written against a beta version such as 11.6.0b4 may be affected.
- Below models were renamed
  - `azure.search.documents.indexes.models.SearchIndexerIndexProjections` -> `azure.search.documents.indexes.models.SearchIndexerIndexProjection`
  - `azure.search.documents.indexes.models.LineEnding` -> `azure.search.documents.indexes.models.OrcLineEnding`
  - `azure.search.documents.indexes.models.ScalarQuantizationCompressionConfiguration` -> `azure.search.documents.indexes.models.ScalarQuantizationCompression`
  - `azure.search.documents.indexes.models.VectorSearchCompressionConfiguration` -> `azure.search.documents.indexes.models.VectorSearchCompression`
  - `azure.search.documents.indexes.models.VectorSearchCompressionTargetDataType` -> `azure.search.documents.indexes.models.VectorSearchCompressionTarget`
- Below properties were renamed
  - `azure.search.documents.indexes.models.AzureMachineLearningVectorizer.name` -> `azure.search.documents.indexes.models.AzureMachineLearningVectorizer.vectorizer_name`
  - `azure.search.documents.indexes.models.AzureOpenAIEmbeddingSkill.deployment_id` -> `azure.search.documents.indexes.models.AzureOpenAIEmbeddingSkill.deployment_name`
  - `azure.search.documents.indexes.models.AzureOpenAIEmbeddingSkill.resource_uri` -> `azure.search.documents.indexes.models.AzureOpenAIEmbeddingSkill.resource_url`
  - `azure.search.documents.indexes.models.AzureOpenAIVectorizer.azure_open_ai_parameters` -> `azure.search.documents.indexes.models.AzureOpenAIVectorizer.parameters`
  - `azure.search.documents.indexes.models.AzureOpenAIVectorizer.name` -> `azure.search.documents.indexes.models.AzureOpenAIVectorizer.vectorizer_name`
  - `azure.search.documents.indexes.models.SearchIndexerDataUserAssignedIdentity.user_assigned_identity` -> `azure.search.documents.indexes.models.SearchIndexerDataUserAssignedIdentity.resource_id`
  - `azure.search.documents.indexes.models.VectorSearchProfile.compression_configuration_name` -> `azure.search.documents.indexes.models.VectorSearchProfile.compression_name`
  - `azure.search.documents.indexes.models.VectorSearchProfile.vectorizer` -> `azure.search.documents.indexes.models.VectorSearchProfile.vectorizer_name`
  - `azure.search.documents.indexes.models.VectorSearchVectorizer.name` -> `azure.search.documents.indexes.models.VectorSearchVectorizer.vectorizer_name`

## 11.5.1 (2024-07-30)

### Other Changes

- Improved type checks.

## 11.5.0 (2024-07-16)

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.4.0.
> Only code written against a beta version such as 11.6.0b4 may be affected.
- Below models are renamed
  - `azure.search.documents.indexes.models.SearchIndexerIndexProjections` -> `azure.search.documents.indexes.models.SearchIndexerIndexProjection`
  - `azure.search.documents.indexes.models.LineEnding` -> `azure.search.documents.indexes.models.OrcLineEnding`
  - `azure.search.documents.indexes.models.ScalarQuantizationCompressionConfiguration` -> `azure.search.documents.indexes.models.ScalarQuantizationCompression`
  - `azure.search.documents.indexes.models.VectorSearchCompressionConfiguration` -> `azure.search.documents.indexes.models.VectorSearchCompression`
  - `azure.search.documents.indexes.models.VectorSearchCompressionTargetDataType` -> `azure.search.documents.indexes.models.VectorSearchCompressionTarget`

- Below models do not exist in this release
  - `azure.search.documents.models.QueryLanguage`
  - `azure.search.documents.models.QuerySpellerType`
  - `azure.search.documents.models.QueryDebugMode`
  - `azure.search.documents.models.HybridCountAndFacetMode`
  - `azure.search.documents.models.HybridSearch`
  - `azure.search.documents.models.SearchScoreThreshold`
  - `azure.search.documents.models.VectorSimilarityThreshold`
  - `azure.search.documents.models.VectorThreshold`
  - `azure.search.documents.models.VectorThresholdKind`
  - `azure.search.documents.models.VectorizableImageBinaryQuery`
  - `azure.search.documents.models.VectorizableImageUrlQuery`
  - `azure.search.documents.indexes.models.SearchAlias`
  - `azure.search.documents.indexes.models.AIServicesVisionParameters`
  - `azure.search.documents.indexes.models.AIServicesVisionVectorizer`
  - `azure.search.documents.indexes.models.AIStudioModelCatalogName`
  - `azure.search.documents.indexes.models.AzureMachineLearningParameters`
  - `azure.search.documents.indexes.models.AzureMachineLearningSkill`
  - `azure.search.documents.indexes.models.AzureMachineLearningVectorizer`
  - `azure.search.documents.indexes.models.CustomVectorizer`
  - `azure.search.documents.indexes.models.CustomNormalizer`
  - `azure.search.documents.indexes.models.DocumentKeysOrIds`
  - `azure.search.documents.indexes.models.IndexingMode`
  - `azure.search.documents.indexes.models.LexicalNormalizer`
  - `azure.search.documents.indexes.models.LexicalNormalizerName`
  - `azure.search.documents.indexes.models.NativeBlobSoftDeleteDeletionDetectionPolicy`
  - `azure.search.documents.indexes.models.SearchIndexerCache`
  - `azure.search.documents.indexes.models.SkillNames`
  - `azure.search.documents.indexes.models.VisionVectorizeSkill`

- SearchAlias operations do not exist in this release
- `SearchIndexerClient.reset_documents` does not exist in this release
- `SearchIndexerClient.reset_skills` does not exist in this release

- Below properties do not exist
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.identity`
  - `azure.search.documents.indexes.models.SearchIndex.normalizers`
  - `azure.search.documents.indexes.models.SearchField.normalizer_name`

- Below parameters do not exist
  - `SearchClient.search.debug`
  - `SearchClient.search.hybrid_search`
  - `SearchClient.search.query_language`
  - `SearchClient.search.query_speller`
  - `SearchClient.search.semantic_fields`
  - `SearchIndexerClient.create_or_update_indexer.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_data_source_connection.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_skillset.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_indexer.disable_cache_reprocessing_change_detection`
  - `SearchIndexerClient.create_or_update_skillset.disable_cache_reprocessing_change_detection`

### Other Changes

- Updated default API version to `2024-07-01`.

## 11.6.0b4 (2024-05-07)

### Features Added

- Added new models:
  - `azure.search.documents.models.HybridCountAndFacetMode`
  - `azure.search.documents.models.HybridSearch`
  - `azure.search.documents.models.SearchScoreThreshold`
  - `azure.search.documents.models.VectorSimilarityThreshold`
  - `azure.search.documents.models.VectorThreshold`
  - `azure.search.documents.models.VectorThresholdKind`
  - `azure.search.documents.models.VectorizableImageBinaryQuery`
  - `azure.search.documents.models.VectorizableImageUrlQuery`
  - `azure.search.documents.indexes.models.AIServicesVisionParameters`
  - `azure.search.documents.indexes.models.AIServicesVisionVectorizer`
  - `azure.search.documents.indexes.models.AIStudioModelCatalogName`
  - `azure.search.documents.indexes.models.AzureMachineLearningParameters`
  - `azure.search.documents.indexes.models.AzureMachineLearningVectorizer`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName`
  - `azure.search.documents.indexes.models.VectorEncodingFormat`
  - `azure.search.documents.indexes.models.VisionVectorizeSkill`
- Added `hybrid_search` support for `SearchClient.search` method.
- Updated default API version to `2024-05-01-preview`.

### Bugs Fixed

- Fixed the bug that SearchClient failed when both answer count and answer threshold applied.

## 11.6.0b3 (2024-04-09)

### Features Added

- Added `IndexerExecutionEnvironment`, `IndexingMode`, `LineEnding`, `NativeBlobSoftDeleteDeletionDetectionPolicy`, `ScalarQuantizationCompressionConfiguration`, `ScalarQuantizationParameters`, `SearchServiceCounters`, `SearchServiceLimits`, `SearchServiceStatistics`, `VectorSearchCompressionConfiguration` & `VectorSearchCompressionTargetDataType`.
- Added `stored` in `SearchField`.

## 11.6.0b2 (2024-03-05)

### Breaking Changes

- `SearchIndexerSkillset`, `SearchField`, `SearchIndex`, `AnalyzeTextOptions`, `SearchResourceEncryptionKey`, `SynonymMap`, `SearchIndexerDataSourceConnection` are no longer subclasses of `_serialization.Model`.

### Bugs Fixed

- Fixed the issue that `SearchIndexerSkillset`, `SearchField`, `SearchIndex`, `AnalyzeTextOptions`, `SearchResourceEncryptionKey`, `SynonymMap`, `SearchIndexerDataSourceConnection` could not be serialized and `as_dict` did not work.
- Fixed the issue that `context` was missing for `EntityRecognitionSkill` and `SentimentSkill`. #34623

### Other Changes

- Default to API version `V2024_03_01_PREVIEW`

## 11.6.0b1 (2024-01-31)

### Features Added

- Added back `semantic_query` for `Search` method.
- Added back alias operations to `SearchIndexClient`.
- Added back `AzureOpenAIEmbeddingSkill`, `AzureOpenAIParameters` and `AzureOpenAIVectorizer`.
- Added back `query_language`, `query_speller`, `semantic_fields` and `debug` for `Search` method.
- Added `send_request` method for `SearchClient` & `SearchIndexClient` to run a network request using the client's existing pipeline.

### Bugs Fixed

- Fixed the issue that we added unexpected `retrievable` property for `SearchField`.

### Other Changes

- Python 3.7 is no longer supported. Please use Python version 3.8 or later.

## 11.4.0 (2023-10-13)

### Features Added

- Added new models:
  - `VectorSearchAlgorithmMetric`
  - `IndexProjectionMode`
  - `SearchIndexerIndexProjections`
  - `SearchIndexerIndexProjectionSelector`
  - `SearchIndexerIndexProjectionsParameters`
  - `BlobIndexerDataToExtract`
  - `BlobIndexerImageAction`
  - `BlobIndexerParsingMode`
  - `CharFilterName`
  - `CustomEntity`
  - `CustomEntityAlias`
  - `DataChangeDetectionPolicy`
  - `DataDeletionDetectionPolicy`
  - `DefaultCognitiveServicesAccount`
  - `HighWaterMarkChangeDetectionPolicy`
  - `HnswAlgorithmConfiguration`
  - `IndexerExecutionResult`
  - `IndexingParameters`
  - `IndexingParametersConfiguration`
  - `IndexingSchedule`
  - `LexicalAnalyzerName`
  - `LexicalTokenizerName`
  - `PIIDetectionSkill`
  - `PIIDetectionSkillMaskingMode`
  - `ScoringProfile`
  - `SemanticSearch`
- Added `index_projections` support for `SearchIndexerSkillset`

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b11 may be affected.

- Renamed `AnswerResult` to `QueryAnswerResult` and `CaptionResult` to `QueryCaptionResult`.
- Renamed `SemanticErrorHandling` to `SemanticErrorMode`.
- Renamed `RawVectorQuery` to `VectorizedQuery`.
- Renamed `ExhaustiveKnnVectorSearchAlgorithmConfiguration` to `ExhaustiveKnnAlgorithmConfiguration`.
- Renamed `PrioritizedFields` to `SemanticPrioritizedFields`.
- Renamed `query_caption_highlight` to `query_caption_highlight_enabled`.
- `query_language` and `query_speller` are not available for `Search` method in this stable release.
- `alias` operations are not available in this stable release.
- `AzureOpenAIEmbeddingSkill`, `AzureOpenAIParameters` and `AzureOpenAIVectorizer` are not available in 11.4.0.
- Renamed `vector_search_profile` to `vector_search_profile_name` in `SearchField`.
- Renamed `SemanticSettings` to `SemanticSearch`.

### Other Changes

- Used API version "2023-11-01".

## 11.4.0b11 (2023-10-11)

### Features Added

- Added `vector_filter_mode` support for `Search` method.
- Exposed `VectorizableTextQuery` in `azure.search.document.models`.

## 11.4.0b10 (2023-10-10)

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b6 may be affected.
- Renamed `vector_search_configuration` to `vector_search_profile` in `SearchField`.
- Renamed `vectors` to `vector_queries` in `Search` method.
- Renamed `azure.search.documents.models.Vector` to `azure.search.documents.models.VectorQuery`.
- Stopped supporting api version `V2023_07_01_PREVIEW` anymore.

### Other Changes

- Default to use API version `V2023_10_01_PREVIEW`

## 11.4.0b9 (2023-09-12)

### Bugs Fixed

- Fixed the bug that list type of `order_by` was not correctly handled. #31837

## 11.4.0b8 (2023-08-08)

### Features Added

- Exposed `HnswVectorSearchAlgorithmConfiguration`

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b6 may be affected.
- Instead of using `VectorSearchAlgorithmConfiguration`, now you need to use concrete types like `HnswVectorSearchAlgorithmConfiguration`.

## 11.4.0b7 (2023-08-08)

### Features Added

- Added multi-vector search support. Now instead of passing in `vector`, `top_k` and `vector_fields`, search method accepts `vectors` which is a list of `Vector` object.

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b6 may be affected.
- Stopped supporting `vector`, `top_k` and `vector_fields` in `SearchClient.search` method.

## 11.4.0b6 (2023-07-11)

### Features Added

- Added `top_k` support for `VectorSearch`.

## 11.4.0b5 (2023-07-11)

### Features Added

- Exposed `azure.search.documents.models.Vector`.

## 11.4.0b4 (2023-07-11)

### Features Added

- Added `VectorSearch` support.

### Breaking Changes

- Deprecated `SentimentSkillV1` and `EntityRecognitionSkillV1`.

## 11.4.0b3 (2023-02-07)

### Features Added

- Added the semantic reranker score and captions on `SearchResult`.(thanks to @LucasVascovici for the contribution)

## 11.4.0b2 (2022-11-08)

### Features Added

- Enabled `OcrSkill` and `ImageAnalysisSkill`

### Other Changes

- Added Python 3.11 support.

## 11.4.0b1 (2022-09-08)

### Features Added

- Added support to create, update and delete aliases via the `SearchIndexClient`.

## 11.3.0 (2022-09-06)

### Note

- Some of the features that were available in the `11.3.0b8` version are not available in this GA. They would be available in the upcoming beta release.

### Features Added

- Added support for other national clouds.
- Added support for TokenCredential

### Bugs Fixed

- Fixed issue where async `search` call would fail with a 403 error when retrieving large number of documents.

### Other Changes

- Python 3.6 is no longer supported. Please use Python version 3.7 or later.

## 11.2.2 (2022-04-14)

### Bugs Fixed

- Fixes a bug allowing users to set keys for cognitive service skills using the API. Exposes `DefaultCognitiveServicesAccount` and `CognitiveServicesAccountKey`

## 11.3.0b8 (2022-03-08)

### Features Added

- Added support to create, update and delete aliases via the `SearchIndexClient`.

## 11.3.0b7 (2022-02-08)

### Features Added

- Support for [`AzureMachineLearningSkill`](https://learn.microsoft.com/azure/search/cognitive-search-aml-skill). The AML skill allows you to extend AI enrichment with a custom [Azure Machine Learning](https://learn.microsoft.com/azure/machine-learning/overview-what-is-azure-machine-learning) (AML) model. Once an AML model is [trained and deployed](https://learn.microsoft.com/azure/machine-learning/concept-azure-machine-learning-architecture#workspace), an AML skill integrates it into AI enrichment.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 11.2.1 (2022-01-10)

Minor updates.

## 11.3.0b6 (2021-11-19)

### Features Added

- Added properties to `SearchClient.search`: `semantic_configuration_name`
- Added properties to `SearchIndex`: `semantic_settings`
- Added models: `PrioritizedFields`, `SemanticConfiguration`, `SemanticField`, `SemanticSettings`
- Added new values to model `QueryLanguage`

## 11.3.0b5 (2021-11-09)

### Features Added

- Added properties to `SearchClient.search`: `session_id`, `scoring_statistics`.
- Added properties to `SearchIndexerDataSourceConnection`: `identity`, `encryption_key`.
- Added `select` property to the following `SearchIndexClient` operations: `get_synonym_maps`, `list_indexes`.
- Added `select` property to the following `SearchIndexersClient` operations: `get_data_source_connections`, `get_indexers`, `get_skillsets`.
- Added operations to `SearchIndexerClient`: `reset_skills`, `reset_documents`.
- Added model: `DocumentKeysOrIds`

## 11.3.0b4 (2021-10-05)

### Features Added

- Added properties to `SearchClient`: `query_answer`, `query_answer_count`,
  `query_caption`, `query_caption_highlight` and `semantic_fields`.

### Breaking Changes

- Renamed `SearchClient.speller` to `SearchClient.query_speller`.
- Renamed model `Speller` to `QuerySpellerType`.
- Renamed model `Answers` to `QueryAnswerType`. 
- Removed keyword arguments from `SearchClient`: `answers` and `captions`.
- `SentimentSkill`, `EntityRecognitionSkill`: added client-side validation to prevent sending unsupported parameters.
- Renamed property `ignore_reset_requirements` to `skip_indexer_reset_requirement_for_cache`.

## 11.3.0b3 (2021-09-08)

### Features Added

- Added new models: 
  - `azure.search.documents.models.QueryCaptionType`
  - `azure.search.documents.models.CaptionResult`
  - `azure.search.documents.indexes.models.CustomEntityLookupSkillLanguage`
  - `azure.search.documents.indexes.models.EntityRecognitionSkillVersion`
  - `azure.search.documents.indexes.models.LexicalNormalizerName`
  - `azure.search.documents.indexes.models.PIIDetectionSkill`
  - `azure.search.documents.indexes.models.PIIDetectionSkillMaskingMode`
  - `azure.search.documents.indexes.models.SearchIndexerCache`
  - `azure.search.documents.indexes.models.SearchIndexerDataIdentity`
  - `azure.search.documents.indexes.models.SearchIndexerDataNoneIdentity`
  - `azure.search.documents.indexes.models.SearchIndexerDataUserAssignedIdentity`
  - `azure.search.documents.indexes.models.SentimentSkillVersion`
- Added `normalizer_name` property to `AnalyzeTextOptions` model.

### Breaking Changes

- Removed:
  - `azure.search.documents.indexes.models.SentimentSkillV3`
  - `azure.search.documents.indexes.models.EntityRecognitionSkillV3`
- Renamed:
  - `SearchField.normalizer` renamed to `SearchField.normalizer_name`.

### Other Changes
- `SentimentSkill` and `EntityRecognitionSkill` can now be created by specifying
  the `skill_version` keyword argument with a `SentimentSkillVersion` or
  `EntityRecognitionSkillVersion`, respectively. The default behavior if `skill_version`
  is not specified is to create a version 1 skill.

## 11.3.0b2 (2021-08-10)

### Features Added

- Added new skills: `SentimentSkillV3`, `EntityLinkingSkill`, `EntityRecognitionSkillV3`

## 11.3.0b1 (2021-07-07)

### Features Added

- Added AAD support
- Added support for semantic search
- Added normalizer support

## 11.2.0 (2021-06-08)

This version will be the last version to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

**New features**

- Added support for knowledge store    #18461
- Added new data source type ADLS gen2  #16852

## 11.2.0b3 (2021-05-11)

### New features

- Added support for knowledge store    #18461

## 11.2.0b2 (2021-04-13)

### New features

- Added support for semantic search    #17638

## 11.2.0b1 (2021-04-06)

### New features

- Added new data source type ADLS gen2  #16852
- Added normalizer support  #17579

## 11.1.0 (2021-02-10)

**Breaking Changes**

- `IndexDocumentsBatch` does not support `enqueue_action` any longer. `enqueue_actions` takes a single action too.
- `max_retries` of `SearchIndexingBufferedSender` is renamed to `max_retries_per_action`
- `SearchClient` does not support `get_search_indexing_buffered_sender`

## 11.1.0b4 (2020-11-10)

**Features**

- Added `get_search_indexing_buffered_sender` support for `SearchClient`
- Added `initial_batch_action_count` support for `SearchIndexingBufferedSender`
- Added `max_retries` support for `SearchIndexingBufferedSender`

## 11.1.0b3 (2020-10-06)

**Breaking Changes**

- Renamed `SearchIndexDocumentBatchingClient` to `SearchIndexingBufferedSender`
- Renamed `SearchIndexDocumentBatchingClient.add_upload_actions` to `SearchIndexingBufferedSender.upload_documents`
- Renamed `SearchIndexDocumentBatchingClient.add_delete_actions` to `SearchIndexingBufferedSender.delete_documents`
- Renamed `SearchIndexDocumentBatchingClient.add_merge_actions` to `SearchIndexingBufferedSender.merge_documents`
- Renamed `SearchIndexDocumentBatchingClient.add_merge_or_upload_actions` to `SearchIndexingBufferedSender.merge_or_upload_documents`
- Stopped supporting `window` kwargs for `SearchIndexingBufferedSender`
- Splitted kwarg `hook` into `on_new`, `on_progress`, `on_error`, `on_remove` for `SearchIndexingBufferedSender`

**Features**

- Added `auto_flush_interval` support for `SearchIndexingBufferedSender`

## 11.1.0b2 (2020-09-08)

**Features**

- Added `azure.search.documents.RequestEntityTooLargeError`
- `Flush` method in `BatchClient` now will not return until all actions are done

**Breaking Changes**

- Removed `succeeded_actions` & `failed_actions` from `BatchClient`
- Removed `get_index_document_batching_client` from `SearchClient`

## 11.1.0b1 (2020-08-11)

**Features**

- new `SearchIndexDocumentBatchingClient`

`SearchIndexDocumentBatchingClient` supports handling document indexing actions in an automatic way. It can trigger the flush method automatically based on pending tasks and idle time.

### Fixes

- Doc & Sample fixes

## 11.0.0 (2020-07-07)

**Features**

- Exposed more models:

  * BM25SimilarityAlgorithm
  * ClassicSimilarityAlgorithm
  * EdgeNGramTokenFilterSide
  * EntityCategory
  * EntityRecognitionSkillLanguage
  * FieldMapping
  * FieldMappingFunction
  * ImageAnalysisSkillLanguage
  * ImageDetail
  * IndexerExecutionStatus
  * IndexerStatus
  * KeyPhraseExtractionSkillLanguage
  * MicrosoftStemmingTokenizerLanguage
  * MicrosoftTokenizerLanguage
  * OcrSkillLanguage
  * PhoneticEncoder
  * ScoringFunctionAggregation
  * ScoringFunctionInterpolation

## 1.0.0b4 (2020-06-09)

**Breaking Changes**

- Reorganized `SearchServiceClient` into `SearchIndexClient` & `SearchIndexerClient`    #11507
- Split searchindex.json and searchservice.json models and operations into separate namespaces #11508
- Renamed `edm` to `SearchFieldDataType`    #11511
- Now Search Synonym Map creation/update returns a model    #11514
- Renaming  #11565

  * SearchIndexerDataSource -> SearchIndexerDataSourceConnection
  * SearchField.SynonymMaps -> SearchField.SynonymMapNames
  * SearchField.Analyzer -> SearchField.AnalyzerName
  * SearchField.IndexAnalyzer -> SearchField.IndexAnalyzerName
  * SearchField.SearchAnalyzer -> SearchField.SearchAnalyzerName
  * SearchableField.SynonymMaps -> SearchableField.SynonymMapNames
  * SearchableField.Analyzer -> SearchableField.AnalyzerName
  * SearchableField.IndexAnalyzer -> SearchableField.IndexAnalyzerName
  * SearchableField.SearchAnalyzer -> SearchableField.SearchAnalyzerName
  * Similarity -> SimilarityAlgorithm
  * Suggester -> SearchSuggester
  * PathHierarchyTokenizerV2 -> PathHierarchyTokenizer
- Renamed DataSource methods to DataSourceConnection    #11693
- Autocomplete & suggest methods now takes arguments search_text & suggester_name rather than query objects   #11747
- Create_or_updates methods does not support partial updates    #11800
- Renamed AnalyzeRequest to AnalyzeTextOptions  #11800
- Renamed Batch methods #11800

## 1.0.0b3 (2020-05-04)

**Features**

- Add support for synonym maps operations #10830
- Add support for skillset operations #10832
- Add support of indexers operation #10836
- Add helpers for defining searchindex fields #10833

**Breaking Changes**

- `SearchIndexClient` renamed to `SearchClient`

## 1.0.0b2 (2020-04-07)

**Features**

- Added index service client    #10324
- Accepted an array of RegexFlags for PatternAnalyzer and PatternTokenizer  #10409

**Breaking Changes**

- Removed `SearchApiKeyCredential` and now using `AzureKeyCredential` from azure.core.credentials as key credential

## 1.0.0b1 (2020-03-10)

First release of Azure Search SDK for Python
