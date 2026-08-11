```py
namespace azure.search.documents

    class azure.search.documents.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2020_06_30 = "2020-06-30"
        V2023_11_01 = "2023-11-01"
        V2024_07_01 = "2024-07-01"
        V2025_09_01 = "2025-09-01"
        V2026_04_01 = "2026-04-01"
        V2026_08_01_PREVIEW = "2026-08-01-preview"


    class azure.search.documents.IndexDocumentsBatch(MutableMapping[str, Any]):
        property actions: List[IndexAction]

        def __init__(
                self, 
                *, 
                actions: Optional[List[IndexAction]] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def add_delete_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def add_merge_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def add_merge_or_upload_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def add_upload_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def dequeue_actions(self, **kwargs: Any) -> List[IndexAction]: ...

        def enqueue_actions(
                self, 
                new_actions: Union[IndexAction, List[IndexAction]], 
                **kwargs: Any
            ) -> None: ...


    class azure.search.documents.RequestEntityTooLargeError(HttpResponseError):


    class azure.search.documents.SearchClient(_SearchClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                index_name: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def autocomplete(
                self, 
                search_text: str, 
                suggester_name: str, 
                *, 
                filter: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                minimum_coverage: Optional[float] = ..., 
                mode: Optional[Union[str, AutocompleteMode]] = ..., 
                search_fields: Optional[list[str]] = ..., 
                top: Optional[int] = ..., 
                use_fuzzy_matching: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[AutocompleteItem]: ...

        def close(self) -> None: ...

        def delete_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-05-01-preview': ['query_source_authorization', 'enable_elevated_read']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def get_document(
                self, 
                key: str, 
                *, 
                enable_elevated_read: Optional[bool] = ..., 
                query_source_authorization: Optional[str] = ..., 
                selected_fields: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LookupDocument: ...

        @distributed_trace
        def get_document_count(self, **kwargs: Any) -> int: ...

        @distributed_trace
        def index_documents(
                self, 
                batch: IndexDocumentsBatch, 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        def merge_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        def merge_or_upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        @distributed_trace
        def search(
                self, 
                search_text: Optional[str] = None, 
                *, 
                debug: Optional[Union[str, QueryDebugMode]] = ..., 
                enable_elevated_read: Optional[bool] = ..., 
                facets: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                highlight_fields: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                hybrid_search: Optional[HybridSearch] = ..., 
                include_total_count: Optional[bool] = ..., 
                minimum_coverage: Optional[float] = ..., 
                order_by: Optional[List[str]] = ..., 
                query_answer: Optional[Union[str, QueryAnswerType]] = ..., 
                query_answer_count: Optional[int] = ..., 
                query_answer_threshold: Optional[float] = ..., 
                query_caption: Optional[Union[str, QueryCaptionType]] = ..., 
                query_caption_highlight_enabled: Optional[bool] = ..., 
                query_language: Optional[Union[str, QueryLanguage]] = ..., 
                query_rewrites: Optional[Union[str, QueryRewritesType]] = ..., 
                query_source_authorization: Optional[str] = ..., 
                query_type: Optional[Union[str, QueryType]] = ..., 
                scoring_parameters: Optional[List[str]] = ..., 
                scoring_profile: Optional[str] = ..., 
                scoring_statistics: Optional[Union[str, ScoringStatistics]] = ..., 
                search_fields: Optional[List[str]] = ..., 
                search_mode: Optional[Union[str, SearchMode]] = ..., 
                select: Optional[List[str]] = ..., 
                semantic_configuration_name: Optional[str] = ..., 
                semantic_error_mode: Optional[Union[str, SemanticErrorMode]] = ..., 
                semantic_fields: Optional[List[str]] = ..., 
                semantic_max_wait_in_milliseconds: Optional[int] = ..., 
                semantic_query: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                speller: Optional[Union[str, QuerySpellerType]] = ..., 
                top: Optional[int] = ..., 
                vector_filter_mode: Optional[Union[str, VectorFilterMode]] = ..., 
                vector_queries: Optional[List[VectorQuery]] = ..., 
                **kwargs: Any
            ) -> SearchItemPaged[Dict]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def suggest(
                self, 
                search_text: str, 
                suggester_name: str, 
                *, 
                filter: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                minimum_coverage: Optional[float] = ..., 
                order_by: Optional[List[str]] = ..., 
                search_fields: Optional[List[str]] = ..., 
                select: Optional[List[str]] = ..., 
                top: Optional[int] = ..., 
                use_fuzzy_matching: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[SuggestResult]: ...

        def upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...


    class azure.search.documents.SearchIndexingBufferedSender: implements ContextManager 
        property actions: List[IndexAction]    # Read-only

        def __init__(
                self, 
                endpoint: str, 
                index_name: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                auto_flush: Optional[bool] = ..., 
                auto_flush_interval: Optional[int] = ..., 
                initial_batch_action_count: Optional[int] = ..., 
                max_retries_per_action: Optional[int] = ..., 
                on_error: Optional[callable] = ..., 
                on_new: Optional[callable] = ..., 
                on_progress: Optional[callable] = ..., 
                on_remove: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace
        def close(self, **kwargs) -> None: ...

        @distributed_trace
        def delete_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def flush(
                self, 
                timeout: int = 86400, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def index_documents(
                self, 
                batch: IndexDocumentsBatch, 
                **kwargs
            ) -> List[IndexingResult]: ...

        @distributed_trace
        def merge_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def merge_or_upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...


    class azure.search.documents.SearchItemPaged(ItemPaged[ReturnType]):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        def __next__(self) -> ReturnType: ...

        def get_answers(self) -> Optional[List[QueryAnswerResult]]: ...

        def get_count(self) -> int: ...

        def get_coverage(self) -> float: ...

        def get_debug_info(self) -> Optional[DebugInfo]: ...

        def get_facets(self) -> Optional[Dict]: ...


namespace azure.search.documents.aio

    class azure.search.documents.aio.AsyncSearchItemPaged(AsyncItemPaged[ReturnType]):

        async def __anext__(self) -> ReturnType: ...

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        async def get_answers(self) -> Optional[List[QueryAnswerResult]]: ...

        async def get_count(self) -> int: ...

        async def get_coverage(self) -> float: ...

        async def get_debug_info(self) -> Optional[DebugInfo]: ...

        async def get_facets(self) -> Optional[Dict]: ...


    class azure.search.documents.aio.SearchClient(_SearchClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                index_name: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def autocomplete(
                self, 
                search_text: str, 
                suggester_name: str, 
                *, 
                filter: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                minimum_coverage: Optional[float] = ..., 
                mode: Optional[Union[str, AutocompleteMode]] = ..., 
                search_fields: Optional[list[str]] = ..., 
                top: Optional[int] = ..., 
                use_fuzzy_matching: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[AutocompleteItem]: ...

        async def close(self) -> None: ...

        async def delete_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2026-05-01-preview': ['query_source_authorization', 'enable_elevated_read']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        async def get_document(
                self, 
                key: str, 
                *, 
                enable_elevated_read: Optional[bool] = ..., 
                query_source_authorization: Optional[str] = ..., 
                selected_fields: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> LookupDocument: ...

        @distributed_trace_async
        async def get_document_count(self, **kwargs: Any) -> int: ...

        @distributed_trace_async
        async def index_documents(
                self, 
                batch: IndexDocumentsBatch, 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        async def merge_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        async def merge_or_upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...

        @distributed_trace_async
        async def search(
                self, 
                search_text: Optional[str] = None, 
                *, 
                debug: Optional[Union[str, QueryDebugMode]] = ..., 
                enable_elevated_read: Optional[bool] = ..., 
                facets: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                highlight_fields: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                hybrid_search: Optional[HybridSearch] = ..., 
                include_total_count: Optional[bool] = ..., 
                minimum_coverage: Optional[float] = ..., 
                order_by: Optional[List[str]] = ..., 
                query_answer: Optional[Union[str, QueryAnswerType]] = ..., 
                query_answer_count: Optional[int] = ..., 
                query_answer_threshold: Optional[float] = ..., 
                query_caption: Optional[Union[str, QueryCaptionType]] = ..., 
                query_caption_highlight_enabled: Optional[bool] = ..., 
                query_language: Optional[Union[str, QueryLanguage]] = ..., 
                query_rewrites: Optional[Union[str, QueryRewritesType]] = ..., 
                query_source_authorization: Optional[str] = ..., 
                query_type: Optional[Union[str, QueryType]] = ..., 
                scoring_parameters: Optional[List[str]] = ..., 
                scoring_profile: Optional[str] = ..., 
                scoring_statistics: Optional[Union[str, ScoringStatistics]] = ..., 
                search_fields: Optional[List[str]] = ..., 
                search_mode: Optional[Union[str, SearchMode]] = ..., 
                select: Optional[List[str]] = ..., 
                semantic_configuration_name: Optional[str] = ..., 
                semantic_error_mode: Optional[Union[str, SemanticErrorMode]] = ..., 
                semantic_fields: Optional[List[str]] = ..., 
                semantic_max_wait_in_milliseconds: Optional[int] = ..., 
                semantic_query: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                speller: Optional[Union[str, QuerySpellerType]] = ..., 
                top: Optional[int] = ..., 
                vector_filter_mode: Optional[Union[str, VectorFilterMode]] = ..., 
                vector_queries: Optional[List[VectorQuery]] = ..., 
                **kwargs: Any
            ) -> AsyncSearchItemPaged[Dict]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def suggest(
                self, 
                search_text: str, 
                suggester_name: str, 
                *, 
                filter: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                minimum_coverage: Optional[float] = ..., 
                order_by: Optional[List[str]] = ..., 
                search_fields: Optional[List[str]] = ..., 
                select: Optional[List[str]] = ..., 
                top: Optional[int] = ..., 
                use_fuzzy_matching: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[SuggestResult]: ...

        async def upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs: Any
            ) -> List[IndexingResult]: ...


    class azure.search.documents.aio.SearchIndexingBufferedSender: implements AsyncContextManager 
        property actions: List[IndexAction]    # Read-only

        def __init__(
                self, 
                endpoint: str, 
                index_name: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                auto_flush: Optional[bool] = ..., 
                auto_flush_interval: Optional[int] = ..., 
                initial_batch_action_count: Optional[int] = ..., 
                max_retries_per_action: Optional[int] = ..., 
                on_error: Optional[callable] = ..., 
                on_new: Optional[callable] = ..., 
                on_progress: Optional[callable] = ..., 
                on_remove: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace_async
        async def close(self, **kwargs) -> None: ...

        @distributed_trace_async
        async def delete_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def flush(
                self, 
                timeout: int = 86400, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def index_documents(
                self, 
                batch: IndexDocumentsBatch, 
                **kwargs
            ) -> List[IndexingResult]: ...

        @distributed_trace_async
        async def merge_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def merge_or_upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def upload_documents(
                self, 
                documents: List[Dict], 
                **kwargs
            ) -> None: ...


namespace azure.search.documents.indexes

    class azure.search.documents.indexes.SearchIndexClient(_SearchIndexClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def analyze_text(
                self, 
                index_name: str, 
                analyze_request: AnalyzeTextOptions, 
                **kwargs: Any
            ) -> AnalyzeResult: ...

        def close(self) -> None: ...

        @overload
        def create_alias(
                self, 
                alias: SearchAlias, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchAlias: ...

        @overload
        def create_alias(
                self, 
                alias: SearchAlias, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchAlias: ...

        @overload
        def create_alias(
                self, 
                alias: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchAlias: ...

        @overload
        def create_index(
                self, 
                index: SearchIndex, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndex: ...

        @overload
        def create_index(
                self, 
                index: SearchIndex, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndex: ...

        @overload
        def create_index(
                self, 
                index: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndex: ...

        @overload
        def create_knowledge_base(
                self, 
                knowledge_base: KnowledgeBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @overload
        def create_knowledge_base(
                self, 
                knowledge_base: KnowledgeBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @overload
        def create_knowledge_base(
                self, 
                knowledge_base: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @overload
        def create_knowledge_source(
                self, 
                knowledge_source: KnowledgeSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @overload
        def create_knowledge_source(
                self, 
                knowledge_source: KnowledgeSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @overload
        def create_knowledge_source(
                self, 
                knowledge_source: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @distributed_trace
        def create_or_update_alias(
                self, 
                alias: Union[SearchAlias, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SearchAlias: ...

        @distributed_trace
        def create_or_update_index(
                self, 
                index: Union[SearchIndex, JSON], 
                allow_index_downtime: Optional[bool] = None, 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SearchIndex: ...

        @distributed_trace
        def create_or_update_knowledge_base(
                self, 
                knowledge_base: Union[KnowledgeBase, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @distributed_trace
        def create_or_update_knowledge_source(
                self, 
                knowledge_source: Union[KnowledgeSource, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @distributed_trace
        def create_or_update_synonym_map(
                self, 
                synonym_map: Union[SynonymMap, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SynonymMap: ...

        @overload
        def create_synonym_map(
                self, 
                synonym_map: SynonymMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynonymMap: ...

        @overload
        def create_synonym_map(
                self, 
                synonym_map: SynonymMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynonymMap: ...

        @overload
        def create_synonym_map(
                self, 
                synonym_map: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynonymMap: ...

        @distributed_trace
        def delete_alias(
                self, 
                alias: Union[str, SearchAlias], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_index(
                self, 
                index: Union[str, SearchIndex], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_knowledge_base(
                self, 
                knowledge_base: Union[str, KnowledgeBase], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_knowledge_source(
                self, 
                knowledge_source: Union[str, KnowledgeSource], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_knowledge_source_file(
                self, 
                name: str, 
                file_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_synonym_map(
                self, 
                synonym_map: Union[str, SynonymMap], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_alias(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchAlias: ...

        @distributed_trace
        def get_index(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndex: ...

        @distributed_trace
        def get_index_statistics(
                self, 
                index_name: str, 
                **kwargs: Any
            ) -> GetIndexStatisticsResult: ...

        @distributed_trace
        def get_knowledge_base(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @distributed_trace
        def get_knowledge_source(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @distributed_trace
        def get_knowledge_source_status(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KnowledgeSourceStatus: ...

        def get_search_client(
                self, 
                index_name: str, 
                **kwargs: Any
            ) -> SearchClient: ...

        @distributed_trace
        def get_service_statistics(self, **kwargs: Any) -> SearchServiceStatistics: ...

        @distributed_trace
        def get_synonym_map(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SynonymMap: ...

        @distributed_trace
        def get_synonym_map_names(self, **kwargs: Any) -> List[str]: ...

        @distributed_trace
        def get_synonym_maps(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SynonymMap]: ...

        @distributed_trace
        def list_alias_names(self, **kwargs: Any) -> ItemPaged[str]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-08-01-preview': ['search', 'page_size', 'search_type']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def list_aliases(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SearchAlias]: ...

        @distributed_trace
        def list_index_names(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'accept', 'search', 'page_size', 'search_type', 'client_request_id']}, api_versions_list=['2026-08-01-preview'])
        def list_index_stats_summary(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[IndexStatisticsSummary]: ...

        @distributed_trace
        def list_indexes(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SearchIndex]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-08-01-preview': ['search', 'page_size', 'search_type']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def list_knowledge_bases(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KnowledgeBase]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'accept', 'client_request_id', 'name'], '2026-08-01-preview': ['prefix', 'search', 'page_size', 'search_type']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_knowledge_source_files(
                self, 
                name: str, 
                *, 
                page_size: Optional[int] = ..., 
                prefix: Optional[str] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KnowledgeSourceFile]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-08-01-preview': ['search', 'page_size', 'search_type']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def list_knowledge_sources(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KnowledgeSource]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def update_knowledge_source_file(
                self, 
                file_id: str, 
                name: str, 
                body: UpdateKnowledgeSourceFileRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @overload
        def update_knowledge_source_file(
                self, 
                file_id: str, 
                name: str, 
                body: UpdateKnowledgeSourceFileRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @distributed_trace
        def upload_knowledge_source_file(
                self, 
                name: str, 
                file: Union[bytes, IO[bytes]], 
                *, 
                content_disposition: Optional[str] = ..., 
                filename: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @overload
        def upload_knowledge_source_file_multipart(
                self, 
                name: str, 
                body: UploadKnowledgeSourceFileMultipartRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @overload
        def upload_knowledge_source_file_multipart(
                self, 
                name: str, 
                body: UploadKnowledgeSourceFileMultipartRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...


    class azure.search.documents.indexes.SearchIndexerClient(_SearchIndexerClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def create_data_source_connection(
                self, 
                data_source_connection: SearchIndexerDataSourceConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @overload
        def create_data_source_connection(
                self, 
                data_source_connection: SearchIndexerDataSourceConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @overload
        def create_data_source_connection(
                self, 
                data_source_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @overload
        def create_indexer(
                self, 
                indexer: SearchIndexer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @overload
        def create_indexer(
                self, 
                indexer: SearchIndexer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @overload
        def create_indexer(
                self, 
                indexer: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace
        def create_or_update_data_source_connection(
                self, 
                data_source_connection: Union[SearchIndexerDataSourceConnection, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                skip_indexer_reset_requirement_for_cache: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @distributed_trace
        def create_or_update_indexer(
                self, 
                indexer: Union[SearchIndexer, JSON], 
                *, 
                disable_cache_reprocessing_change_detection: Optional[bool] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                skip_indexer_reset_requirement_for_cache: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace
        def create_or_update_skillset(
                self, 
                skillset: Union[SearchIndexerSkillset, JSON], 
                *, 
                disable_cache_reprocessing_change_detection: Optional[bool] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                skip_indexer_reset_requirement_for_cache: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @overload
        def create_skillset(
                self, 
                skillset: SearchIndexerSkillset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @overload
        def create_skillset(
                self, 
                skillset: SearchIndexerSkillset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @overload
        def create_skillset(
                self, 
                skillset: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @distributed_trace
        def delete_data_source_connection(
                self, 
                data_source_connection: Union[str, SearchIndexerDataSourceConnection], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_indexer(
                self, 
                indexer: Union[str, SearchIndexer], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_skillset(
                self, 
                skillset: Union[str, SearchIndexerSkillset], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_data_source_connection(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @distributed_trace
        def get_data_source_connection_names(self, **kwargs: Any) -> Sequence[str]: ...

        @distributed_trace
        def get_data_source_connections(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SearchIndexerDataSourceConnection]: ...

        @distributed_trace
        def get_indexer(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace
        def get_indexer_names(self, **kwargs: Any) -> Sequence[str]: ...

        @distributed_trace
        def get_indexer_status(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexerStatus: ...

        @distributed_trace
        def get_indexers(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SearchIndexer]: ...

        @distributed_trace
        def get_skillset(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @distributed_trace
        def get_skillset_names(self, **kwargs: Any) -> List[str]: ...

        @distributed_trace
        def get_skillsets(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SearchIndexerSkillset]: ...

        @distributed_trace
        def reset_documents(
                self, 
                name: str, 
                keys_or_ids: Optional[Union[DocumentKeysOrIds, JSON, IO[bytes]]] = None, 
                *, 
                overwrite: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_indexer(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_skills(
                self, 
                name: str, 
                skill_names: Union[SkillNames, JSON, IO[bytes]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def resync(
                self, 
                name: str, 
                indexer_resync: Union[IndexerResyncBody, JSON, IO[bytes]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def run_indexer(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.search.documents.indexes.aio

    class azure.search.documents.indexes.aio.SearchIndexClient(_SearchIndexClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def analyze_text(
                self, 
                index_name: str, 
                analyze_request: AnalyzeTextOptions, 
                **kwargs: Any
            ) -> AnalyzeResult: ...

        async def close(self) -> None: ...

        @overload
        async def create_alias(
                self, 
                alias: SearchAlias, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchAlias: ...

        @overload
        async def create_alias(
                self, 
                alias: SearchAlias, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchAlias: ...

        @overload
        async def create_alias(
                self, 
                alias: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchAlias: ...

        @overload
        async def create_index(
                self, 
                index: SearchIndex, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndex: ...

        @overload
        async def create_index(
                self, 
                index: SearchIndex, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndex: ...

        @overload
        async def create_index(
                self, 
                index: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndex: ...

        @overload
        async def create_knowledge_base(
                self, 
                knowledge_base: KnowledgeBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @overload
        async def create_knowledge_base(
                self, 
                knowledge_base: KnowledgeBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @overload
        async def create_knowledge_base(
                self, 
                knowledge_base: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @overload
        async def create_knowledge_source(
                self, 
                knowledge_source: KnowledgeSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @overload
        async def create_knowledge_source(
                self, 
                knowledge_source: KnowledgeSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @overload
        async def create_knowledge_source(
                self, 
                knowledge_source: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @distributed_trace_async
        async def create_or_update_alias(
                self, 
                alias: Union[SearchAlias, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SearchAlias: ...

        @distributed_trace_async
        async def create_or_update_index(
                self, 
                index: Union[SearchIndex, JSON], 
                allow_index_downtime: Optional[bool] = None, 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SearchIndex: ...

        @distributed_trace_async
        async def create_or_update_knowledge_base(
                self, 
                knowledge_base: Union[KnowledgeBase, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @distributed_trace_async
        async def create_or_update_knowledge_source(
                self, 
                knowledge_source: Union[KnowledgeSource, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @distributed_trace_async
        async def create_or_update_synonym_map(
                self, 
                synonym_map: Union[SynonymMap, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SynonymMap: ...

        @overload
        async def create_synonym_map(
                self, 
                synonym_map: SynonymMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynonymMap: ...

        @overload
        async def create_synonym_map(
                self, 
                synonym_map: SynonymMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynonymMap: ...

        @overload
        async def create_synonym_map(
                self, 
                synonym_map: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SynonymMap: ...

        @distributed_trace_async
        async def delete_alias(
                self, 
                alias: Union[str, SearchAlias], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_index(
                self, 
                index: Union[str, SearchIndex], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_knowledge_base(
                self, 
                knowledge_base: Union[str, KnowledgeBase], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_knowledge_source(
                self, 
                knowledge_source: Union[str, KnowledgeSource], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_knowledge_source_file(
                self, 
                name: str, 
                file_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_synonym_map(
                self, 
                synonym_map: Union[str, SynonymMap], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_alias(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchAlias: ...

        @distributed_trace_async
        async def get_index(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndex: ...

        @distributed_trace_async
        async def get_index_statistics(
                self, 
                index_name: str, 
                **kwargs: Any
            ) -> GetIndexStatisticsResult: ...

        @distributed_trace_async
        async def get_knowledge_base(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @distributed_trace_async
        async def get_knowledge_source(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KnowledgeSource: ...

        @distributed_trace_async
        async def get_knowledge_source_status(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KnowledgeSourceStatus: ...

        def get_search_client(
                self, 
                index_name: str, 
                **kwargs: Any
            ) -> SearchClient: ...

        @distributed_trace_async
        async def get_service_statistics(self, **kwargs: Any) -> SearchServiceStatistics: ...

        @distributed_trace_async
        async def get_synonym_map(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SynonymMap: ...

        @distributed_trace_async
        async def get_synonym_map_names(self, **kwargs: Any) -> List[str]: ...

        @distributed_trace_async
        async def get_synonym_maps(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SynonymMap]: ...

        @distributed_trace
        def list_alias_names(self, **kwargs) -> AsyncItemPaged[str]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-08-01-preview': ['search', 'page_size', 'search_type']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def list_aliases(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SearchAlias]: ...

        @distributed_trace
        def list_index_names(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'accept', 'search', 'page_size', 'search_type', 'client_request_id']}, api_versions_list=['2026-08-01-preview'])
        def list_index_stats_summary(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[IndexStatisticsSummary]: ...

        @distributed_trace
        def list_indexes(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SearchIndex]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-08-01-preview': ['search', 'page_size', 'search_type']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def list_knowledge_bases(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KnowledgeBase]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'accept', 'client_request_id', 'name'], '2026-08-01-preview': ['prefix', 'search', 'page_size', 'search_type']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_knowledge_source_files(
                self, 
                name: str, 
                *, 
                page_size: Optional[int] = ..., 
                prefix: Optional[str] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KnowledgeSourceFile]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-08-01-preview': ['search', 'page_size', 'search_type']}, api_versions_list=['2025-11-01-preview', '2026-04-01', '2026-05-01-preview', '2026-08-01-preview'])
        def list_knowledge_sources(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                search: Optional[str] = ..., 
                search_type: Optional[Union[str, ListingSearchType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KnowledgeSource]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def update_knowledge_source_file(
                self, 
                file_id: str, 
                name: str, 
                body: UpdateKnowledgeSourceFileRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @overload
        async def update_knowledge_source_file(
                self, 
                file_id: str, 
                name: str, 
                body: UpdateKnowledgeSourceFileRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @distributed_trace_async
        async def upload_knowledge_source_file(
                self, 
                name: str, 
                file: Union[bytes, IO[bytes]], 
                *, 
                content_disposition: Optional[str] = ..., 
                filename: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @overload
        async def upload_knowledge_source_file_multipart(
                self, 
                name: str, 
                body: UploadKnowledgeSourceFileMultipartRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...

        @overload
        async def upload_knowledge_source_file_multipart(
                self, 
                name: str, 
                body: UploadKnowledgeSourceFileMultipartRequest, 
                **kwargs: Any
            ) -> KnowledgeSourceFile: ...


    class azure.search.documents.indexes.aio.SearchIndexerClient(_SearchIndexerClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def create_data_source_connection(
                self, 
                data_source_connection: SearchIndexerDataSourceConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @overload
        async def create_data_source_connection(
                self, 
                data_source_connection: SearchIndexerDataSourceConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @overload
        async def create_data_source_connection(
                self, 
                data_source_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @overload
        async def create_indexer(
                self, 
                indexer: SearchIndexer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @overload
        async def create_indexer(
                self, 
                indexer: SearchIndexer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @overload
        async def create_indexer(
                self, 
                indexer: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace_async
        async def create_or_update_data_source_connection(
                self, 
                data_source_connection: Union[SearchIndexerDataSourceConnection, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                skip_indexer_reset_requirement_for_cache: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @distributed_trace_async
        async def create_or_update_indexer(
                self, 
                indexer: Union[SearchIndexer, JSON], 
                *, 
                disable_cache_reprocessing_change_detection: Optional[bool] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                skip_indexer_reset_requirement_for_cache: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace_async
        async def create_or_update_skillset(
                self, 
                skillset: Union[SearchIndexerSkillset, JSON], 
                *, 
                disable_cache_reprocessing_change_detection: Optional[bool] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                skip_indexer_reset_requirement_for_cache: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @overload
        async def create_skillset(
                self, 
                skillset: SearchIndexerSkillset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @overload
        async def create_skillset(
                self, 
                skillset: SearchIndexerSkillset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @overload
        async def create_skillset(
                self, 
                skillset: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @distributed_trace_async
        async def delete_data_source_connection(
                self, 
                data_source_connection: Union[str, SearchIndexerDataSourceConnection], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_indexer(
                self, 
                indexer: Union[str, SearchIndexer], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_skillset(
                self, 
                skillset: Union[str, SearchIndexerSkillset], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_data_source_connection(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @distributed_trace_async
        async def get_data_source_connection_names(self, **kwargs) -> Sequence[str]: ...

        @distributed_trace_async
        async def get_data_source_connections(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SearchIndexerDataSourceConnection]: ...

        @distributed_trace_async
        async def get_indexer(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace_async
        async def get_indexer_names(self, **kwargs) -> Sequence[str]: ...

        @distributed_trace_async
        async def get_indexer_status(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexerStatus: ...

        @distributed_trace_async
        async def get_indexers(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SearchIndexer]: ...

        @distributed_trace_async
        async def get_skillset(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SearchIndexerSkillset: ...

        @distributed_trace_async
        async def get_skillset_names(self, **kwargs) -> Sequence[str]: ...

        @distributed_trace_async
        async def get_skillsets(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> List[SearchIndexerSkillset]: ...

        @distributed_trace_async
        async def reset_documents(
                self, 
                name: str, 
                keys_or_ids: Optional[Union[DocumentKeysOrIds, JSON, IO[bytes]]] = None, 
                *, 
                overwrite: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_indexer(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_skills(
                self, 
                name: str, 
                skill_names: Union[SkillNames, JSON, IO[bytes]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def resync(
                self, 
                name: str, 
                indexer_resync: Union[IndexerResyncBody, JSON, IO[bytes]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def run_indexer(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.search.documents.indexes.models

    def azure.search.documents.indexes.models.ComplexField(
            *, 
            collection: bool = False, 
            fields: Optional[List[SearchField]] = ..., 
            name: str, 
            **kw
        ) -> SearchField: ...


    def azure.search.documents.indexes.models.SearchableField(
            *, 
            analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = ..., 
            collection: bool = False, 
            facetable: bool = False, 
            filterable: bool = False, 
            hidden: bool = False, 
            index_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = ..., 
            key: bool = False, 
            name: str, 
            search_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = ..., 
            searchable: bool = True, 
            sortable: bool = False, 
            synonym_map_names: Optional[List[str]] = ..., 
            **kw
        ) -> SearchField: ...


    def azure.search.documents.indexes.models.SimpleField(
            *, 
            facetable: bool = False, 
            filterable: bool = False, 
            hidden: bool = False, 
            key: bool = False, 
            name: str, 
            sortable: bool = False, 
            type: Union[str, SearchFieldDataType], 
            **kw
        ) -> SearchField: ...


    class azure.search.documents.indexes.models.AIFoundryModelCatalogName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COHERE_EMBED_V3_ENGLISH = "Cohere-embed-v3-english"
        COHERE_EMBED_V3_MULTILINGUAL = "Cohere-embed-v3-multilingual"
        COHERE_EMBED_V4 = "Cohere-embed-v4"
        FACEBOOK_DINO_V2_IMAGE_EMBEDDINGS_VIT_BASE = "Facebook-DinoV2-Image-Embeddings-ViT-Base"
        FACEBOOK_DINO_V2_IMAGE_EMBEDDINGS_VIT_GIANT = "Facebook-DinoV2-Image-Embeddings-ViT-Giant"
        OPEN_AI_CLIP_IMAGE_TEXT_EMBEDDINGS_VIT_BASE_PATCH32 = "OpenAI-CLIP-Image-Text-Embeddings-vit-base-patch32"
        OPEN_AI_CLIP_IMAGE_TEXT_EMBEDDINGS_VIT_LARGE_PATCH14_336 = "OpenAI-CLIP-Image-Text-Embeddings-ViT-Large-Patch14-336"


    class azure.search.documents.indexes.models.AIServicesAccountIdentity(CognitiveServicesAccount, discriminator='#Microsoft.Azure.Search.AIServicesByIdentity'):
        description: str
        identity: Optional[SearchIndexerDataIdentity]
        odata_type: Literal["#AIServicesByIdentity"]
        subdomain_url: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                subdomain_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AIServicesAccountKey(CognitiveServicesAccount, discriminator='#Microsoft.Azure.Search.AIServicesByKey'):
        description: str
        key: str
        odata_type: Literal["#AIServicesByKey"]
        subdomain_url: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                key: str, 
                subdomain_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AIServicesVisionParameters(_Model):
        api_key: Optional[str]
        auth_identity: Optional[SearchIndexerDataIdentity]
        model_version: str
        resource_uri: str

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                auth_identity: Optional[SearchIndexerDataIdentity] = ..., 
                model_version: str, 
                resource_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AIServicesVisionVectorizer(VectorSearchVectorizer, discriminator='aiServicesVision'):
        ai_services_vision_parameters: Optional[AIServicesVisionParameters]
        kind: Literal[VectorSearchVectorizerKind.AI_SERVICES_VISION]
        vectorizer_name: str

        @overload
        def __init__(
                self, 
                *, 
                ai_services_vision_parameters: Optional[AIServicesVisionParameters] = ..., 
                vectorizer_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AnalyzeResult(_Model):
        tokens: list[AnalyzedTokenInfo]

        @overload
        def __init__(
                self, 
                *, 
                tokens: list[AnalyzedTokenInfo]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AnalyzeTextOptions(_Model):
        analyzer_name: Optional[Union[str, LexicalAnalyzerName]]
        char_filters: Optional[list[Union[str, CharFilterName]]]
        normalizer_name: Optional[Union[str, LexicalNormalizerName]]
        text: str
        token_filters: Optional[list[Union[str, TokenFilterName]]]
        tokenizer_name: Optional[Union[str, LexicalTokenizerName]]

        @overload
        def __init__(
                self, 
                *, 
                analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = ..., 
                char_filters: Optional[list[Union[str, CharFilterName]]] = ..., 
                normalizer_name: Optional[Union[str, LexicalNormalizerName]] = ..., 
                text: str, 
                token_filters: Optional[list[Union[str, TokenFilterName]]] = ..., 
                tokenizer_name: Optional[Union[str, LexicalTokenizerName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AnalyzedTokenInfo(_Model):
        end_offset: int
        position: int
        start_offset: int
        token: str


    class azure.search.documents.indexes.models.AsciiFoldingTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.AsciiFoldingTokenFilter'):
        name: str
        odata_type: Literal["#AsciiFoldingTokenFilter"]
        preserve_original: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                preserve_original: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureActiveDirectoryApplicationCredentials(_Model):
        application_id: str
        application_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: str, 
                application_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureBlobKnowledgeSource(KnowledgeSource, discriminator='azureBlob'):
        azure_blob_parameters: AzureBlobKnowledgeSourceParameters
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Literal[KnowledgeSourceKind.AZURE_BLOB]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_parameters: AzureBlobKnowledgeSourceParameters, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureBlobKnowledgeSourceParameters(_Model):
        connection_string: str
        container_name: str
        created_resources: Optional[CreatedResources]
        folder_path: Optional[str]
        ingestion_parameters: Optional[KnowledgeSourceIngestionParameters]
        is_adls_gen2: Optional[bool]
        query_hints: Optional[SearchIndexKnowledgeSourceQueryHints]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                container_name: str, 
                folder_path: Optional[str] = ..., 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                is_adls_gen2: Optional[bool] = ..., 
                query_hints: Optional[SearchIndexKnowledgeSourceQueryHints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureMachineLearningParameters(_Model):
        authentication_key: Optional[str]
        model_name: Optional[Union[str, AIFoundryModelCatalogName]]
        region: Optional[str]
        resource_id: Optional[str]
        scoring_uri: str
        timeout: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                authentication_key: Optional[str] = ..., 
                model_name: Optional[Union[str, AIFoundryModelCatalogName]] = ..., 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                scoring_uri: str, 
                timeout: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureMachineLearningSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Custom.AmlSkill'):
        authentication_key: Optional[str]
        context: str
        degree_of_parallelism: Optional[int]
        description: str
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#AmlSkill"]
        outputs: list[OutputFieldMappingEntry]
        region: Optional[str]
        resource_id: Optional[str]
        scoring_uri: Optional[str]
        timeout: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                authentication_key: Optional[str] = ..., 
                context: Optional[str] = ..., 
                degree_of_parallelism: Optional[int] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                scoring_uri: Optional[str] = ..., 
                timeout: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureMachineLearningVectorizer(VectorSearchVectorizer, discriminator='aml'):
        aml_parameters: Optional[AzureMachineLearningParameters]
        kind: Literal[VectorSearchVectorizerKind.AML]
        vectorizer_name: str

        @overload
        def __init__(
                self, 
                *, 
                aml_parameters: Optional[AzureMachineLearningParameters] = ..., 
                vectorizer_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureOpenAIEmbeddingSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill'):
        api_key: Optional[str]
        auth_identity: Optional[SearchIndexerDataIdentity]
        context: str
        deployment_name: Optional[str]
        description: str
        dimensions: Optional[int]
        inputs: list[InputFieldMappingEntry]
        model_name: Optional[Union[str, AzureOpenAIModelName]]
        name: str
        odata_type: Literal["#AzureOpenAIEmbeddingSkill"]
        outputs: list[OutputFieldMappingEntry]
        resource_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                auth_identity: Optional[SearchIndexerDataIdentity] = ..., 
                context: Optional[str] = ..., 
                deployment_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                dimensions: Optional[int] = ..., 
                inputs: list[InputFieldMappingEntry], 
                model_name: Optional[Union[str, AzureOpenAIModelName]] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                resource_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureOpenAIModelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GPT41 = "gpt-4.1"
        GPT41_MINI = "gpt-4.1-mini"
        GPT41_NANO = "gpt-4.1-nano"
        GPT4_O = "gpt-4o"
        GPT4_O_MINI = "gpt-4o-mini"
        GPT5 = "gpt-5"
        GPT51 = "gpt-5.1"
        GPT52 = "gpt-5.2"
        GPT54 = "gpt-5.4"
        GPT55 = "gpt-5.5"
        GPT56_LUNA = "gpt-5.6-luna"
        GPT56_SOL = "gpt-5.6-sol"
        GPT56_TERRA = "gpt-5.6-terra"
        GPT5_4_MINI = "gpt-5.4-mini"
        GPT5_4_NANO = "gpt-5.4-nano"
        GPT5_MINI = "gpt-5-mini"
        GPT5_NANO = "gpt-5-nano"
        TEXT_EMBEDDING3_LARGE = "text-embedding-3-large"
        TEXT_EMBEDDING3_SMALL = "text-embedding-3-small"
        TEXT_EMBEDDING_ADA002 = "text-embedding-ada-002"


    class azure.search.documents.indexes.models.AzureOpenAITokenizerParameters(_Model):
        allowed_special_tokens: Optional[list[str]]
        encoder_model_name: Optional[Union[str, SplitSkillEncoderModelName]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_special_tokens: Optional[list[str]] = ..., 
                encoder_model_name: Optional[Union[str, SplitSkillEncoderModelName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureOpenAIVectorizer(VectorSearchVectorizer, discriminator='azureOpenAI'):
        kind: Literal[VectorSearchVectorizerKind.AZURE_OPEN_AI]
        parameters: Optional[AzureOpenAIVectorizerParameters]
        vectorizer_name: str

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[AzureOpenAIVectorizerParameters] = ..., 
                vectorizer_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.AzureOpenAIVectorizerParameters(_Model):
        api_key: Optional[str]
        auth_identity: Optional[SearchIndexerDataIdentity]
        deployment_name: Optional[str]
        model_name: Optional[Union[str, AzureOpenAIModelName]]
        resource_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                auth_identity: Optional[SearchIndexerDataIdentity] = ..., 
                deployment_name: Optional[str] = ..., 
                model_name: Optional[Union[str, AzureOpenAIModelName]] = ..., 
                resource_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.BM25SimilarityAlgorithm(SimilarityAlgorithm, discriminator='#Microsoft.Azure.Search.BM25Similarity'):
        b: Optional[float]
        k1: Optional[float]
        odata_type: Literal["#BM25Similarity"]

        @overload
        def __init__(
                self, 
                *, 
                b: Optional[float] = ..., 
                k1: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.BinaryQuantizationCompression(VectorSearchCompression, discriminator='binaryQuantization'):
        compression_name: str
        kind: Literal[VectorSearchCompressionKind.BINARY_QUANTIZATION]
        rescoring_options: RescoringOptions
        truncation_dimension: int

        @overload
        def __init__(
                self, 
                *, 
                compression_name: str, 
                rescoring_options: Optional[RescoringOptions] = ..., 
                truncation_dimension: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.BlobIndexerDataToExtract(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_METADATA = "allMetadata"
        CONTENT_AND_METADATA = "contentAndMetadata"
        STORAGE_METADATA = "storageMetadata"


    class azure.search.documents.indexes.models.BlobIndexerImageAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERATE_NORMALIZED_IMAGES = "generateNormalizedImages"
        GENERATE_NORMALIZED_IMAGE_PER_PAGE = "generateNormalizedImagePerPage"
        NONE = "none"


    class azure.search.documents.indexes.models.BlobIndexerPDFTextRotationAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETECT_ANGLES = "detectAngles"
        NONE = "none"


    class azure.search.documents.indexes.models.BlobIndexerParsingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        DELIMITED_TEXT = "delimitedText"
        JSON = "json"
        JSON_ARRAY = "jsonArray"
        JSON_LINES = "jsonLines"
        MARKDOWN = "markdown"
        TEXT = "text"


    class azure.search.documents.indexes.models.CharFilter(_Model):
        name: str
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CharFilterName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTML_STRIP = "html_strip"


    class azure.search.documents.indexes.models.ChatCompletionCommonModelParameters(_Model):
        frequency_penalty: Optional[float]
        max_tokens: Optional[int]
        model_name: Optional[str]
        presence_penalty: Optional[float]
        seed: Optional[int]
        stop: Optional[list[str]]
        temperature: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                frequency_penalty: Optional[float] = ..., 
                max_tokens: Optional[int] = ..., 
                model_name: Optional[str] = ..., 
                presence_penalty: Optional[float] = ..., 
                seed: Optional[int] = ..., 
                stop: Optional[list[str]] = ..., 
                temperature: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ChatCompletionExtraParametersBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DROP = "drop"
        ERROR = "error"
        PASS_THROUGH = "passThrough"


    class azure.search.documents.indexes.models.ChatCompletionResponseFormat(_Model):
        json_schema_properties: Optional[ChatCompletionSchemaProperties]
        type: Optional[Union[str, ChatCompletionResponseFormatType]]

        @overload
        def __init__(
                self, 
                *, 
                json_schema_properties: Optional[ChatCompletionSchemaProperties] = ..., 
                type: Optional[Union[str, ChatCompletionResponseFormatType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ChatCompletionResponseFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON_OBJECT = "jsonObject"
        JSON_SCHEMA = "jsonSchema"
        TEXT = "text"


    class azure.search.documents.indexes.models.ChatCompletionSchema(_Model):
        additional_properties: Optional[bool]
        properties: Optional[str]
        required: Optional[list[str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_properties: Optional[bool] = ..., 
                properties: Optional[str] = ..., 
                required: Optional[list[str]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ChatCompletionSchemaProperties(_Model):
        description: Optional[str]
        name: Optional[str]
        schema: Optional[ChatCompletionSchema]
        strict: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                schema: Optional[ChatCompletionSchema] = ..., 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ChatCompletionSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Custom.ChatCompletionSkill'):
        api_key: Optional[str]
        auth_identity: Optional[SearchIndexerDataIdentity]
        common_model_parameters: Optional[ChatCompletionCommonModelParameters]
        context: str
        description: str
        extra_parameters: Optional[dict[str, Any]]
        extra_parameters_behavior: Optional[Union[str, ChatCompletionExtraParametersBehavior]]
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#ChatCompletionSkill"]
        outputs: list[OutputFieldMappingEntry]
        response_format: Optional[ChatCompletionResponseFormat]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                auth_identity: Optional[SearchIndexerDataIdentity] = ..., 
                common_model_parameters: Optional[ChatCompletionCommonModelParameters] = ..., 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                extra_parameters: Optional[dict[str, Any]] = ..., 
                extra_parameters_behavior: Optional[Union[str, ChatCompletionExtraParametersBehavior]] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                response_format: Optional[ChatCompletionResponseFormat] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CjkBigramTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.CjkBigramTokenFilter'):
        ignore_scripts: Optional[list[Union[str, CjkBigramTokenFilterScripts]]]
        name: str
        odata_type: Literal["#CjkBigramTokenFilter"]
        output_unigrams: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                ignore_scripts: Optional[list[Union[str, CjkBigramTokenFilterScripts]]] = ..., 
                name: str, 
                output_unigrams: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CjkBigramTokenFilterScripts(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HAN = "han"
        HANGUL = "hangul"
        HIRAGANA = "hiragana"
        KATAKANA = "katakana"


    class azure.search.documents.indexes.models.ClassicSimilarityAlgorithm(SimilarityAlgorithm, discriminator='#Microsoft.Azure.Search.ClassicSimilarity'):
        odata_type: Literal["#ClassicSimilarity"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ClassicTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.ClassicTokenizer'):
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#ClassicTokenizer"]

        @overload
        def __init__(
                self, 
                *, 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CognitiveServicesAccount(_Model):
        description: Optional[str]
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CognitiveServicesAccountKey(CognitiveServicesAccount, discriminator='#Microsoft.Azure.Search.CognitiveServicesByKey'):
        description: str
        key: str
        odata_type: Literal["#CognitiveServicesByKey"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CommonGramTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.CommonGramTokenFilter'):
        common_words: list[str]
        ignore_case: Optional[bool]
        name: str
        odata_type: Literal["#CommonGramTokenFilter"]
        use_query_mode: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                common_words: list[str], 
                ignore_case: Optional[bool] = ..., 
                name: str, 
                use_query_mode: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ConditionalSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Util.ConditionalSkill'):
        context: str
        description: str
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#ConditionalSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ContentColumnMapping(_Model):
        name: str
        search_field_type: str
        source_field: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                search_field_type: str, 
                source_field: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ContentUnderstandingSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Util.ContentUnderstandingSkill'):
        chunking_properties: Optional[ContentUnderstandingSkillChunkingProperties]
        context: str
        description: str
        extraction_options: Optional[list[Union[str, ContentUnderstandingSkillExtractionOptions]]]
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#ContentUnderstandingSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                chunking_properties: Optional[ContentUnderstandingSkillChunkingProperties] = ..., 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                extraction_options: Optional[list[Union[str, ContentUnderstandingSkillExtractionOptions]]] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_SIZE = "fixedSize"
        SEMANTIC = "semantic"


    class azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingProperties(_Model):
        maximum_length: Optional[int]
        method: Optional[Union[str, ContentUnderstandingSkillChunkingMethod]]
        overlap_length: Optional[int]
        unit: Optional[Union[str, ContentUnderstandingSkillChunkingUnit]]

        @overload
        def __init__(
                self, 
                *, 
                maximum_length: Optional[int] = ..., 
                method: Optional[Union[str, ContentUnderstandingSkillChunkingMethod]] = ..., 
                overlap_length: Optional[int] = ..., 
                unit: Optional[Union[str, ContentUnderstandingSkillChunkingUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHARACTERS = "characters"
        TOKENS = "tokens"


    class azure.search.documents.indexes.models.ContentUnderstandingSkillExtractionOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGES = "images"
        LOCATION_METADATA = "locationMetadata"


    class azure.search.documents.indexes.models.CorsOptions(_Model):
        allowed_origins: list[str]
        max_age_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_origins: list[str], 
                max_age_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CreatedResources(_Model):


    class azure.search.documents.indexes.models.CustomAnalyzer(LexicalAnalyzer, discriminator='#Microsoft.Azure.Search.CustomAnalyzer'):
        char_filters: Optional[list[Union[str, CharFilterName]]]
        name: str
        odata_type: Literal["#CustomAnalyzer"]
        token_filters: Optional[list[Union[str, TokenFilterName]]]
        tokenizer_name: Union[str, LexicalTokenizerName]

        @overload
        def __init__(
                self, 
                *, 
                char_filters: Optional[list[Union[str, CharFilterName]]] = ..., 
                name: str, 
                token_filters: Optional[list[Union[str, TokenFilterName]]] = ..., 
                tokenizer_name: Union[str, LexicalTokenizerName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CustomEntity(_Model):
        accent_sensitive: Optional[bool]
        aliases: Optional[list[CustomEntityAlias]]
        case_sensitive: Optional[bool]
        default_accent_sensitive: Optional[bool]
        default_case_sensitive: Optional[bool]
        default_fuzzy_edit_distance: Optional[int]
        description: Optional[str]
        fuzzy_edit_distance: Optional[int]
        id: Optional[str]
        name: str
        subtype: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accent_sensitive: Optional[bool] = ..., 
                aliases: Optional[list[CustomEntityAlias]] = ..., 
                case_sensitive: Optional[bool] = ..., 
                default_accent_sensitive: Optional[bool] = ..., 
                default_case_sensitive: Optional[bool] = ..., 
                default_fuzzy_edit_distance: Optional[int] = ..., 
                description: Optional[str] = ..., 
                fuzzy_edit_distance: Optional[int] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                subtype: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CustomEntityAlias(_Model):
        accent_sensitive: Optional[bool]
        case_sensitive: Optional[bool]
        fuzzy_edit_distance: Optional[int]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                accent_sensitive: Optional[bool] = ..., 
                case_sensitive: Optional[bool] = ..., 
                fuzzy_edit_distance: Optional[int] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CustomEntityLookupSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.CustomEntityLookupSkill'):
        context: str
        default_language_code: Optional[Union[str, CustomEntityLookupSkillLanguage]]
        description: str
        entities_definition_uri: Optional[str]
        global_default_accent_sensitive: Optional[bool]
        global_default_case_sensitive: Optional[bool]
        global_default_fuzzy_edit_distance: Optional[int]
        inline_entities_definition: Optional[list[CustomEntity]]
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#CustomEntityLookupSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, CustomEntityLookupSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                entities_definition_uri: Optional[str] = ..., 
                global_default_accent_sensitive: Optional[bool] = ..., 
                global_default_case_sensitive: Optional[bool] = ..., 
                global_default_fuzzy_edit_distance: Optional[int] = ..., 
                inline_entities_definition: Optional[list[CustomEntity]] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.CustomEntityLookupSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DA = "da"
        DE = "de"
        EN = "en"
        ES = "es"
        FI = "fi"
        FR = "fr"
        IT = "it"
        KO = "ko"
        PT = "pt"


    class azure.search.documents.indexes.models.CustomNormalizer(LexicalNormalizer, discriminator='#Microsoft.Azure.Search.CustomNormalizer'):
        char_filters: Optional[list[Union[str, CharFilterName]]]
        name: str
        odata_type: Literal["#CustomNormalizer"]
        token_filters: Optional[list[Union[str, TokenFilterName]]]

        @overload
        def __init__(
                self, 
                *, 
                char_filters: Optional[list[Union[str, CharFilterName]]] = ..., 
                name: str, 
                token_filters: Optional[list[Union[str, TokenFilterName]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DataChangeDetectionPolicy(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DataDeletionDetectionPolicy(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DataSourceCredentials(_Model):
        connection_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DefaultCognitiveServicesAccount(CognitiveServicesAccount, discriminator='#Microsoft.Azure.Search.DefaultCognitiveServices'):
        description: str
        odata_type: Literal["#DefaultCognitiveServices"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DictionaryDecompounderTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.DictionaryDecompounderTokenFilter'):
        max_subword_size: Optional[int]
        min_subword_size: Optional[int]
        min_word_size: Optional[int]
        name: str
        odata_type: Literal["#DictionaryDecompounderTokenFilter"]
        only_longest_match: Optional[bool]
        word_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                max_subword_size: Optional[int] = ..., 
                min_subword_size: Optional[int] = ..., 
                min_word_size: Optional[int] = ..., 
                name: str, 
                only_longest_match: Optional[bool] = ..., 
                word_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DistanceScoringFunction(ScoringFunction, discriminator='distance'):
        boost: float
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: DistanceScoringParameters
        type: Literal["distance"]

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                field_name: str, 
                interpolation: Optional[Union[str, ScoringFunctionInterpolation]] = ..., 
                parameters: DistanceScoringParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DistanceScoringParameters(_Model):
        boosting_distance: float
        reference_point_parameter: str

        @overload
        def __init__(
                self, 
                *, 
                boosting_distance: float, 
                reference_point_parameter: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DocumentExtractionSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Util.DocumentExtractionSkill'):
        configuration: Optional[dict[str, Any]]
        context: str
        data_to_extract: Optional[str]
        description: str
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#DocumentExtractionSkill"]
        outputs: list[OutputFieldMappingEntry]
        parsing_mode: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, Any]] = ..., 
                context: Optional[str] = ..., 
                data_to_extract: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                parsing_mode: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Util.DocumentIntelligenceLayoutSkill'):
        chunking_properties: Optional[DocumentIntelligenceLayoutSkillChunkingProperties]
        context: str
        description: str
        extraction_options: Optional[list[Union[str, DocumentIntelligenceLayoutSkillExtractionOptions]]]
        inputs: list[InputFieldMappingEntry]
        markdown_header_depth: Optional[Union[str, DocumentIntelligenceLayoutSkillMarkdownHeaderDepth]]
        name: str
        odata_type: Literal["#DocumentIntelligenceLayoutSkill"]
        output_format: Optional[Union[str, DocumentIntelligenceLayoutSkillOutputFormat]]
        output_mode: Optional[Union[str, DocumentIntelligenceLayoutSkillOutputMode]]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                chunking_properties: Optional[DocumentIntelligenceLayoutSkillChunkingProperties] = ..., 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                extraction_options: Optional[list[Union[str, DocumentIntelligenceLayoutSkillExtractionOptions]]] = ..., 
                inputs: list[InputFieldMappingEntry], 
                markdown_header_depth: Optional[Union[str, DocumentIntelligenceLayoutSkillMarkdownHeaderDepth]] = ..., 
                name: Optional[str] = ..., 
                output_format: Optional[Union[str, DocumentIntelligenceLayoutSkillOutputFormat]] = ..., 
                output_mode: Optional[Union[str, DocumentIntelligenceLayoutSkillOutputMode]] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillChunkingProperties(_Model):
        maximum_length: Optional[int]
        overlap_length: Optional[int]
        unit: Optional[Union[str, DocumentIntelligenceLayoutSkillChunkingUnit]]

        @overload
        def __init__(
                self, 
                *, 
                maximum_length: Optional[int] = ..., 
                overlap_length: Optional[int] = ..., 
                unit: Optional[Union[str, DocumentIntelligenceLayoutSkillChunkingUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillChunkingUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHARACTERS = "characters"


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillExtractionOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGES = "images"
        LOCATION_METADATA = "locationMetadata"


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillMarkdownHeaderDepth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        H1 = "h1"
        H2 = "h2"
        H3 = "h3"
        H4 = "h4"
        H5 = "h5"
        H6 = "h6"


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillOutputFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MARKDOWN = "markdown"
        TEXT = "text"


    class azure.search.documents.indexes.models.DocumentIntelligenceLayoutSkillOutputMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_TO_MANY = "oneToMany"


    class azure.search.documents.indexes.models.DocumentKeysOrIds(_Model):
        datasource_document_ids: Optional[list[str]]
        document_keys: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                datasource_document_ids: Optional[list[str]] = ..., 
                document_keys: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EdgeNGramTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.EdgeNGramTokenFilter'):
        max_gram: Optional[int]
        min_gram: Optional[int]
        name: str
        odata_type: Literal["#EdgeNGramTokenFilter"]
        side: Optional[Union[str, EdgeNGramTokenFilterSide]]

        @overload
        def __init__(
                self, 
                *, 
                max_gram: Optional[int] = ..., 
                min_gram: Optional[int] = ..., 
                name: str, 
                side: Optional[Union[str, EdgeNGramTokenFilterSide]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EdgeNGramTokenFilterSide(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACK = "back"
        FRONT = "front"


    class azure.search.documents.indexes.models.EdgeNGramTokenFilterV2(TokenFilter, discriminator='#Microsoft.Azure.Search.EdgeNGramTokenFilterV2'):
        max_gram: Optional[int]
        min_gram: Optional[int]
        name: str
        odata_type: Literal["#EdgeNGramTokenFilterV2"]
        side: Optional[Union[str, EdgeNGramTokenFilterSide]]

        @overload
        def __init__(
                self, 
                *, 
                max_gram: Optional[int] = ..., 
                min_gram: Optional[int] = ..., 
                name: str, 
                side: Optional[Union[str, EdgeNGramTokenFilterSide]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EdgeNGramTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.EdgeNGramTokenizer'):
        max_gram: Optional[int]
        min_gram: Optional[int]
        name: str
        odata_type: Literal["#EdgeNGramTokenizer"]
        token_chars: Optional[list[Union[str, TokenCharacterKind]]]

        @overload
        def __init__(
                self, 
                *, 
                max_gram: Optional[int] = ..., 
                min_gram: Optional[int] = ..., 
                name: str, 
                token_chars: Optional[list[Union[str, TokenCharacterKind]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ElisionTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.ElisionTokenFilter'):
        articles: Optional[list[str]]
        name: str
        odata_type: Literal["#ElisionTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                articles: Optional[list[str]] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EmbeddingColumnMapping(_Model):
        name: str
        source_field: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                source_field: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EntityCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATETIME = "datetime"
        EMAIL = "email"
        LOCATION = "location"
        ORGANIZATION = "organization"
        PERSON = "person"
        QUANTITY = "quantity"
        URL = "url"


    class azure.search.documents.indexes.models.EntityLinkingSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.V3.EntityLinkingSkill'):
        context: str
        default_language_code: Optional[str]
        description: str
        inputs: list[InputFieldMappingEntry]
        minimum_precision: Optional[float]
        model_version: Optional[str]
        name: str
        odata_type: Literal["#EntityLinkingSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                minimum_precision: Optional[float] = ..., 
                model_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EntityRecognitionSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AR = "ar"
        CS = "cs"
        DA = "da"
        DE = "de"
        EL = "el"
        EN = "en"
        ES = "es"
        FI = "fi"
        FR = "fr"
        HU = "hu"
        IT = "it"
        JA = "ja"
        KO = "ko"
        NL = "nl"
        NO = "no"
        PL = "pl"
        PT_BR = "pt-BR"
        PT_PT = "pt-PT"
        RU = "ru"
        SV = "sv"
        TR = "tr"
        ZH_HANS = "zh-Hans"
        ZH_HANT = "zh-Hant"


    class azure.search.documents.indexes.models.EntityRecognitionSkillV3(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.V3.EntityRecognitionSkill'):
        categories: Optional[list[Union[str, EntityCategory]]]
        context: str
        default_language_code: Optional[Union[str, EntityRecognitionSkillLanguage]]
        description: str
        inputs: list[InputFieldMappingEntry]
        minimum_precision: Optional[float]
        model_version: Optional[str]
        name: str
        odata_type: Literal["#EntityRecognitionSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[Union[str, EntityCategory]]] = ..., 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, EntityRecognitionSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                minimum_precision: Optional[float] = ..., 
                model_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.EntraAppAuthentication(_Model):
        application_id: str
        federated_credential_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: str, 
                federated_credential_id: str, 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ExhaustiveKnnAlgorithmConfiguration(VectorSearchAlgorithmConfiguration, discriminator='exhaustiveKnn'):
        kind: Literal[VectorSearchAlgorithmKind.EXHAUSTIVE_KNN]
        name: str
        parameters: Optional[ExhaustiveKnnParameters]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                parameters: Optional[ExhaustiveKnnParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ExhaustiveKnnParameters(_Model):
        metric: Optional[Union[str, VectorSearchAlgorithmMetric]]

        @overload
        def __init__(
                self, 
                *, 
                metric: Optional[Union[str, VectorSearchAlgorithmMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FabricDataAgentKnowledgeSource(KnowledgeSource, discriminator='fabricDataAgent'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        fabric_data_agent_parameters: FabricDataAgentKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.FABRIC_DATA_AGENT]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                fabric_data_agent_parameters: FabricDataAgentKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FabricDataAgentKnowledgeSourceParameters(_Model):
        data_agent_id: str
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_agent_id: str, 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FabricOntologyKnowledgeSource(KnowledgeSource, discriminator='fabricOntology'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        fabric_ontology_parameters: FabricOntologyKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.FABRIC_ONTOLOGY]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                fabric_ontology_parameters: FabricOntologyKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FabricOntologyKnowledgeSourceParameters(_Model):
        ontology_id: str
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                ontology_id: str, 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FieldMapping(_Model):
        mapping_function: Optional[FieldMappingFunction]
        source_field_name: str
        target_field_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mapping_function: Optional[FieldMappingFunction] = ..., 
                source_field_name: str, 
                target_field_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FieldMappingFunction(_Model):
        name: str
        parameters: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                parameters: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FileKnowledgeSource(KnowledgeSource, discriminator='file'):
        cors_options: Optional[CorsOptions]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        file_parameters: FileKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.FILE]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                cors_options: Optional[CorsOptions] = ..., 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                file_parameters: FileKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FileKnowledgeSourceExtractionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MINIMAL = "minimal"
        STANDARD = "standard"


    class azure.search.documents.indexes.models.FileKnowledgeSourceParameters(_Model):
        created_resources: Optional[CreatedResources]
        ingestion_parameters: Optional[KnowledgeSourceIngestionParameters]
        query_hints: Optional[SearchIndexKnowledgeSourceQueryHints]

        @overload
        def __init__(
                self, 
                *, 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                query_hints: Optional[SearchIndexKnowledgeSourceQueryHints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FileUploadMetadata(_Model):
        file_name: Optional[str]
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                file_name: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FreshnessScoringFunction(ScoringFunction, discriminator='freshness'):
        boost: float
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: FreshnessScoringParameters
        type: Literal["freshness"]

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                field_name: str, 
                interpolation: Optional[Union[str, ScoringFunctionInterpolation]] = ..., 
                parameters: FreshnessScoringParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.FreshnessScoringParameters(_Model):
        boosting_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                boosting_duration: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.GetIndexStatisticsResult(_Model):
        document_count: int
        storage_size: int
        vector_index_size: int


    class azure.search.documents.indexes.models.HighWaterMarkChangeDetectionPolicy(DataChangeDetectionPolicy, discriminator='#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy'):
        high_water_mark_column_name: str
        odata_type: Literal["#HighWaterMarkChangeDetectionPolicy"]

        @overload
        def __init__(
                self, 
                *, 
                high_water_mark_column_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.HnswAlgorithmConfiguration(VectorSearchAlgorithmConfiguration, discriminator='hnsw'):
        kind: Literal[VectorSearchAlgorithmKind.HNSW]
        name: str
        parameters: Optional[HnswParameters]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                parameters: Optional[HnswParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.HnswParameters(_Model):
        ef_construction: Optional[int]
        ef_search: Optional[int]
        m: Optional[int]
        metric: Optional[Union[str, VectorSearchAlgorithmMetric]]

        @overload
        def __init__(
                self, 
                *, 
                ef_construction: Optional[int] = ..., 
                ef_search: Optional[int] = ..., 
                m: Optional[int] = ..., 
                metric: Optional[Union[str, VectorSearchAlgorithmMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ImageAnalysisSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Vision.ImageAnalysisSkill'):
        context: str
        default_language_code: Optional[Union[str, ImageAnalysisSkillLanguage]]
        description: str
        details: Optional[list[Union[str, ImageDetail]]]
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#ImageAnalysisSkill"]
        outputs: list[OutputFieldMappingEntry]
        visual_features: Optional[list[Union[str, VisualFeature]]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, ImageAnalysisSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                details: Optional[list[Union[str, ImageDetail]]] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                visual_features: Optional[list[Union[str, VisualFeature]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ImageAnalysisSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AR = "ar"
        AZ = "az"
        BG = "bg"
        BS = "bs"
        CA = "ca"
        CS = "cs"
        CY = "cy"
        DA = "da"
        DE = "de"
        EL = "el"
        EN = "en"
        ES = "es"
        ET = "et"
        EU = "eu"
        FI = "fi"
        FR = "fr"
        GA = "ga"
        GL = "gl"
        HE = "he"
        HI = "hi"
        HR = "hr"
        HU = "hu"
        ID = "id"
        IT = "it"
        JA = "ja"
        KK = "kk"
        KO = "ko"
        LT = "lt"
        LV = "lv"
        MK = "mk"
        MS = "ms"
        NB = "nb"
        NL = "nl"
        PL = "pl"
        PRS = "prs"
        PT = "pt"
        PT_BR = "pt-BR"
        PT_PT = "pt-PT"
        RO = "ro"
        RU = "ru"
        SK = "sk"
        SL = "sl"
        SR_CYRL = "sr-Cyrl"
        SR_LATN = "sr-Latn"
        SV = "sv"
        TH = "th"
        TR = "tr"
        UK = "uk"
        VI = "vi"
        ZH = "zh"
        ZH_HANS = "zh-Hans"
        ZH_HANT = "zh-Hant"


    class azure.search.documents.indexes.models.ImageDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CELEBRITIES = "celebrities"
        LANDMARKS = "landmarks"


    class azure.search.documents.indexes.models.IndexProjectionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCLUDE_INDEXING_PARENT_DOCUMENTS = "includeIndexingParentDocuments"
        SKIP_INDEXING_PARENT_DOCUMENTS = "skipIndexingParentDocuments"


    class azure.search.documents.indexes.models.IndexStatisticsSummary(_Model):
        document_count: int
        name: str
        storage_size: int
        vector_index_size: int

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSource(KnowledgeSource, discriminator='indexedOneLake'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexed_one_lake_parameters: IndexedOneLakeKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.INDEXED_ONELAKE]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                indexed_one_lake_parameters: IndexedOneLakeKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSourceParameters(_Model):
        created_resources: Optional[CreatedResources]
        fabric_workspace_id: str
        ingestion_parameters: Optional[KnowledgeSourceIngestionParameters]
        lakehouse_id: str
        query_hints: Optional[SearchIndexKnowledgeSourceQueryHints]
        target_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_workspace_id: str, 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                lakehouse_id: str, 
                query_hints: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                target_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedSharePointContainerName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_SITE_LIBRARIES = "allSiteLibraries"
        DEFAULT_SITE_LIBRARY = "defaultSiteLibrary"
        USE_QUERY = "useQuery"


    class azure.search.documents.indexes.models.IndexedSharePointKnowledgeSource(KnowledgeSource, discriminator='indexedSharePoint'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexed_share_point_parameters: IndexedSharePointKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.INDEXED_SHARE_POINT]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                indexed_share_point_parameters: IndexedSharePointKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedSharePointKnowledgeSourceParameters(_Model):
        connection_string: str
        container_name: Union[str, IndexedSharePointContainerName]
        created_resources: Optional[CreatedResources]
        ingestion_parameters: Optional[KnowledgeSourceIngestionParameters]
        query: Optional[str]
        query_hints: Optional[SearchIndexKnowledgeSourceQueryHints]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                container_name: Union[str, IndexedSharePointContainerName], 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                query: Optional[str] = ..., 
                query_hints: Optional[SearchIndexKnowledgeSourceQueryHints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedSqlKnowledgeSource(KnowledgeSource, discriminator='indexedSql'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexed_sql_parameters: IndexedSqlKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.INDEXED_SQL]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                indexed_sql_parameters: IndexedSqlKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedSqlKnowledgeSourceParameters(_Model):
        connection_string: str
        content_columns: Optional[list[ContentColumnMapping]]
        created_resources: Optional[CreatedResources]
        embedding_columns: Optional[list[EmbeddingColumnMapping]]
        high_water_mark_column_name: Optional[str]
        ingestion_parameters: Optional[KnowledgeSourceIngestionParameters]
        query_hints: Optional[SearchIndexKnowledgeSourceQueryHints]
        table_or_view: str

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                content_columns: Optional[list[ContentColumnMapping]] = ..., 
                embedding_columns: Optional[list[EmbeddingColumnMapping]] = ..., 
                high_water_mark_column_name: Optional[str] = ..., 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                query_hints: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                table_or_view: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexerCurrentState(_Model):
        all_docs_final_tracking_state: Optional[str]
        all_docs_initial_tracking_state: Optional[str]
        mode: Optional[Union[str, IndexingMode]]
        reset_datasource_document_ids: Optional[list[str]]
        reset_docs_final_tracking_state: Optional[str]
        reset_docs_initial_tracking_state: Optional[str]
        reset_document_keys: Optional[list[str]]
        resync_final_tracking_state: Optional[str]
        resync_initial_tracking_state: Optional[str]


    class azure.search.documents.indexes.models.IndexerExecutionEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "private"
        STANDARD = "standard"


    class azure.search.documents.indexes.models.IndexerExecutionResult(_Model):
        end_time: Optional[datetime]
        error_message: Optional[str]
        errors: list[SearchIndexerError]
        failed_item_count: int
        final_tracking_state: Optional[str]
        initial_tracking_state: Optional[str]
        item_count: int
        mode: Optional[Union[str, IndexingMode]]
        start_time: Optional[datetime]
        status: Union[str, IndexerExecutionStatus]
        status_detail: Optional[Union[str, IndexerExecutionStatusDetail]]
        warnings: list[SearchIndexerWarning]


    class azure.search.documents.indexes.models.IndexerExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_PROGRESS = "inProgress"
        RESET = "reset"
        SUCCESS = "success"
        TRANSIENT_FAILURE = "transientFailure"


    class azure.search.documents.indexes.models.IndexerExecutionStatusDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESET_DOCS = "resetDocs"
        RESYNC = "resync"


    class azure.search.documents.indexes.models.IndexerPermissionOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP_IDS = "groupIds"
        RBAC_SCOPE = "rbacScope"
        USER_IDS = "userIds"


    class azure.search.documents.indexes.models.IndexerResyncBody(_Model):
        options: Optional[list[Union[str, IndexerResyncOption]]]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[list[Union[str, IndexerResyncOption]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexerResyncOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERMISSIONS = "permissions"


    class azure.search.documents.indexes.models.IndexerRuntime(_Model):
        beginning_time: datetime
        ending_time: datetime
        remaining_seconds: Optional[int]
        used_seconds: int

        @overload
        def __init__(
                self, 
                *, 
                beginning_time: datetime, 
                ending_time: datetime, 
                remaining_seconds: Optional[int] = ..., 
                used_seconds: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        RUNNING = "running"
        UNKNOWN = "unknown"


    class azure.search.documents.indexes.models.IndexingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDEXING_ALL_DOCS = "indexingAllDocs"
        INDEXING_RESET_DOCS = "indexingResetDocs"
        INDEXING_RESYNC = "indexingResync"


    class azure.search.documents.indexes.models.IndexingParameters(_Model):
        batch_size: Optional[int]
        configuration: Optional[IndexingParametersConfiguration]
        max_failed_items: Optional[int]
        max_failed_items_per_batch: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                batch_size: Optional[int] = ..., 
                configuration: Optional[IndexingParametersConfiguration] = ..., 
                max_failed_items: Optional[int] = ..., 
                max_failed_items_per_batch: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexingParametersConfiguration(_Model):
        allow_skillset_to_read_file_data: Optional[bool]
        data_to_extract: Optional[Union[str, BlobIndexerDataToExtract]]
        delimited_text_delimiter: Optional[str]
        delimited_text_headers: Optional[str]
        document_root: Optional[str]
        excluded_file_name_extensions: Optional[str]
        execution_environment: Optional[Union[str, IndexerExecutionEnvironment]]
        fail_on_unprocessable_document: Optional[bool]
        fail_on_unsupported_content_type: Optional[bool]
        first_line_contains_headers: Optional[bool]
        image_action: Optional[Union[str, BlobIndexerImageAction]]
        index_storage_metadata_only_for_oversized_documents: Optional[bool]
        indexed_file_name_extensions: Optional[str]
        markdown_header_depth: Optional[Union[str, MarkdownHeaderDepth]]
        markdown_parsing_submode: Optional[Union[str, MarkdownParsingSubmode]]
        parsing_mode: Optional[Union[str, BlobIndexerParsingMode]]
        pdf_text_rotation_algorithm: Optional[Union[str, BlobIndexerPDFTextRotationAlgorithm]]
        query_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_skillset_to_read_file_data: Optional[bool] = ..., 
                data_to_extract: Optional[Union[str, BlobIndexerDataToExtract]] = ..., 
                delimited_text_delimiter: Optional[str] = ..., 
                delimited_text_headers: Optional[str] = ..., 
                document_root: Optional[str] = ..., 
                excluded_file_name_extensions: Optional[str] = ..., 
                execution_environment: Optional[Union[str, IndexerExecutionEnvironment]] = ..., 
                fail_on_unprocessable_document: Optional[bool] = ..., 
                fail_on_unsupported_content_type: Optional[bool] = ..., 
                first_line_contains_headers: Optional[bool] = ..., 
                image_action: Optional[Union[str, BlobIndexerImageAction]] = ..., 
                index_storage_metadata_only_for_oversized_documents: Optional[bool] = ..., 
                indexed_file_name_extensions: Optional[str] = ..., 
                markdown_header_depth: Optional[Union[str, MarkdownHeaderDepth]] = ..., 
                markdown_parsing_submode: Optional[Union[str, MarkdownParsingSubmode]] = ..., 
                parsing_mode: Optional[Union[str, BlobIndexerParsingMode]] = ..., 
                pdf_text_rotation_algorithm: Optional[Union[str, BlobIndexerPDFTextRotationAlgorithm]] = ..., 
                query_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexingSchedule(_Model):
        interval: timedelta
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                interval: timedelta, 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.InputFieldMappingEntry(_Model):
        inputs: Optional[list[InputFieldMappingEntry]]
        name: str
        source: Optional[str]
        source_context: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[list[InputFieldMappingEntry]] = ..., 
                name: str, 
                source: Optional[str] = ..., 
                source_context: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KeepTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.KeepTokenFilter'):
        keep_words: list[str]
        lower_case_keep_words: Optional[bool]
        name: str
        odata_type: Literal["#KeepTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                keep_words: list[str], 
                lower_case_keep_words: Optional[bool] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KeyPhraseExtractionSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.KeyPhraseExtractionSkill'):
        context: str
        default_language_code: Optional[Union[str, KeyPhraseExtractionSkillLanguage]]
        description: str
        inputs: list[InputFieldMappingEntry]
        max_key_phrase_count: Optional[int]
        model_version: Optional[str]
        name: str
        odata_type: Literal["#KeyPhraseExtractionSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, KeyPhraseExtractionSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                max_key_phrase_count: Optional[int] = ..., 
                model_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KeyPhraseExtractionSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DA = "da"
        DE = "de"
        EN = "en"
        ES = "es"
        FI = "fi"
        FR = "fr"
        IT = "it"
        JA = "ja"
        KO = "ko"
        NL = "nl"
        NO = "no"
        PL = "pl"
        PT_BR = "pt-BR"
        PT_PT = "pt-PT"
        RU = "ru"
        SV = "sv"


    class azure.search.documents.indexes.models.KeywordMarkerTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.KeywordMarkerTokenFilter'):
        ignore_case: Optional[bool]
        keywords: list[str]
        name: str
        odata_type: Literal["#KeywordMarkerTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                ignore_case: Optional[bool] = ..., 
                keywords: list[str], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KeywordTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.KeywordTokenizer'):
        buffer_size: Optional[int]
        name: str
        odata_type: Literal["#KeywordTokenizer"]

        @overload
        def __init__(
                self, 
                *, 
                buffer_size: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KeywordTokenizerV2(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.KeywordTokenizerV2'):
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#KeywordTokenizerV2"]

        @overload
        def __init__(
                self, 
                *, 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeBase(_KnowledgeBase):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeBaseAzureOpenAIModel(KnowledgeBaseModel, discriminator='azureOpenAI'):
        azure_open_ai_parameters: AzureOpenAIVectorizerParameters
        kind: Literal[KnowledgeBaseModelKind.AZURE_OPEN_AI]

        @overload
        def __init__(
                self, 
                *, 
                azure_open_ai_parameters: AzureOpenAIVectorizerParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeBaseModel(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeBaseModelKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_OPEN_AI = "azureOpenAI"


    class azure.search.documents.indexes.models.KnowledgeBaseRetrieveDefaults(_Model):
        max_output_documents: Optional[int]
        max_output_size_in_tokens: Optional[int]
        max_runtime_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_output_documents: Optional[int] = ..., 
                max_output_size_in_tokens: Optional[int] = ..., 
                max_runtime_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeSource(_Model):
        description: Optional[str]
        e_tag: Optional[str]
        encryption_key: Optional[SearchResourceEncryptionKey]
        kind: str
        name: str
        results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                kind: str, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeSourceContentExtractionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MINIMAL = "minimal"
        STANDARD = "standard"


    class azure.search.documents.indexes.models.KnowledgeSourceFile(_Model):
        created_at: Optional[datetime]
        error_message: Optional[str]
        extraction_mode: Optional[Union[str, FileKnowledgeSourceExtractionMode]]
        file_id: Optional[str]
        file_name: Optional[str]
        file_size_bytes: Optional[int]
        last_updated_at: Optional[datetime]
        metadata: Optional[dict[str, str]]
        parsing_mode: Optional[Union[str, BlobIndexerParsingMode]]
        prefix: Optional[str]


    class azure.search.documents.indexes.models.KnowledgeSourceIngestionPermissionOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP_IDS = "groupIds"
        RBAC_SCOPE = "rbacScope"
        SENSITIVITY_LABELS = "sensitivityLabels"
        USER_IDS = "userIds"


    class azure.search.documents.indexes.models.KnowledgeSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "azureBlob"
        FABRIC_DATA_AGENT = "fabricDataAgent"
        FABRIC_ONTOLOGY = "fabricOntology"
        FILE = "file"
        INDEXED_ONELAKE = "indexedOneLake"
        INDEXED_SHARE_POINT = "indexedSharePoint"
        INDEXED_SQL = "indexedSql"
        MCP_SERVER = "mcpServer"
        REMOTE_SHARE_POINT = "remoteSharePoint"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"
        WORK_IQ = "workIQ"


    class azure.search.documents.indexes.models.KnowledgeSourceReference(_Model):
        enable_freshness: Optional[bool]
        enable_image_serving: Optional[bool]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                enable_freshness: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeSourceResultsProcessing(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        RERANK = "rerank"


    class azure.search.documents.indexes.models.KnowledgeSourceSynchronizationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        CREATING = "creating"
        DELETING = "deleting"


    class azure.search.documents.indexes.models.LanguageDetectionSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.LanguageDetectionSkill'):
        context: str
        default_country_hint: Optional[str]
        description: str
        inputs: list[InputFieldMappingEntry]
        model_version: Optional[str]
        name: str
        odata_type: Literal["#LanguageDetectionSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_country_hint: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                model_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LengthTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.LengthTokenFilter'):
        max_length: Optional[int]
        min_length: Optional[int]
        name: str
        odata_type: Literal["#LengthTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                max_length: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LexicalAnalyzer(_Model):
        name: str
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LexicalAnalyzerName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AR_LUCENE = "ar.lucene"
        AR_MICROSOFT = "ar.microsoft"
        BG_LUCENE = "bg.lucene"
        BG_MICROSOFT = "bg.microsoft"
        BN_MICROSOFT = "bn.microsoft"
        CA_LUCENE = "ca.lucene"
        CA_MICROSOFT = "ca.microsoft"
        CS_LUCENE = "cs.lucene"
        CS_MICROSOFT = "cs.microsoft"
        DA_LUCENE = "da.lucene"
        DA_MICROSOFT = "da.microsoft"
        DE_LUCENE = "de.lucene"
        DE_MICROSOFT = "de.microsoft"
        EL_LUCENE = "el.lucene"
        EL_MICROSOFT = "el.microsoft"
        EN_LUCENE = "en.lucene"
        EN_MICROSOFT = "en.microsoft"
        ES_LUCENE = "es.lucene"
        ES_MICROSOFT = "es.microsoft"
        ET_MICROSOFT = "et.microsoft"
        EU_LUCENE = "eu.lucene"
        FA_LUCENE = "fa.lucene"
        FI_LUCENE = "fi.lucene"
        FI_MICROSOFT = "fi.microsoft"
        FR_LUCENE = "fr.lucene"
        FR_MICROSOFT = "fr.microsoft"
        GA_LUCENE = "ga.lucene"
        GL_LUCENE = "gl.lucene"
        GU_MICROSOFT = "gu.microsoft"
        HE_MICROSOFT = "he.microsoft"
        HI_LUCENE = "hi.lucene"
        HI_MICROSOFT = "hi.microsoft"
        HR_MICROSOFT = "hr.microsoft"
        HU_LUCENE = "hu.lucene"
        HU_MICROSOFT = "hu.microsoft"
        HY_LUCENE = "hy.lucene"
        ID_LUCENE = "id.lucene"
        ID_MICROSOFT = "id.microsoft"
        IS_MICROSOFT = "is.microsoft"
        IT_LUCENE = "it.lucene"
        IT_MICROSOFT = "it.microsoft"
        JA_LUCENE = "ja.lucene"
        JA_MICROSOFT = "ja.microsoft"
        KEYWORD = "keyword"
        KN_MICROSOFT = "kn.microsoft"
        KO_LUCENE = "ko.lucene"
        KO_MICROSOFT = "ko.microsoft"
        LT_MICROSOFT = "lt.microsoft"
        LV_LUCENE = "lv.lucene"
        LV_MICROSOFT = "lv.microsoft"
        ML_MICROSOFT = "ml.microsoft"
        MR_MICROSOFT = "mr.microsoft"
        MS_MICROSOFT = "ms.microsoft"
        NB_MICROSOFT = "nb.microsoft"
        NL_LUCENE = "nl.lucene"
        NL_MICROSOFT = "nl.microsoft"
        NO_LUCENE = "no.lucene"
        PATTERN = "pattern"
        PA_MICROSOFT = "pa.microsoft"
        PL_LUCENE = "pl.lucene"
        PL_MICROSOFT = "pl.microsoft"
        PT_BR_LUCENE = "pt-BR.lucene"
        PT_BR_MICROSOFT = "pt-BR.microsoft"
        PT_PT_LUCENE = "pt-PT.lucene"
        PT_PT_MICROSOFT = "pt-PT.microsoft"
        RO_LUCENE = "ro.lucene"
        RO_MICROSOFT = "ro.microsoft"
        RU_LUCENE = "ru.lucene"
        RU_MICROSOFT = "ru.microsoft"
        SIMPLE = "simple"
        SK_MICROSOFT = "sk.microsoft"
        SL_MICROSOFT = "sl.microsoft"
        SR_CYRILLIC_MICROSOFT = "sr-cyrillic.microsoft"
        SR_LATIN_MICROSOFT = "sr-latin.microsoft"
        STANDARD_ASCII_FOLDING_LUCENE = "standardasciifolding.lucene"
        STANDARD_LUCENE = "standard.lucene"
        STOP = "stop"
        SV_LUCENE = "sv.lucene"
        SV_MICROSOFT = "sv.microsoft"
        TA_MICROSOFT = "ta.microsoft"
        TE_MICROSOFT = "te.microsoft"
        TH_LUCENE = "th.lucene"
        TH_MICROSOFT = "th.microsoft"
        TR_LUCENE = "tr.lucene"
        TR_MICROSOFT = "tr.microsoft"
        UK_MICROSOFT = "uk.microsoft"
        UR_MICROSOFT = "ur.microsoft"
        VI_MICROSOFT = "vi.microsoft"
        WHITESPACE = "whitespace"
        ZH_HANS_LUCENE = "zh-Hans.lucene"
        ZH_HANS_MICROSOFT = "zh-Hans.microsoft"
        ZH_HANT_LUCENE = "zh-Hant.lucene"
        ZH_HANT_MICROSOFT = "zh-Hant.microsoft"


    class azure.search.documents.indexes.models.LexicalNormalizer(_Model):
        name: str
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LexicalNormalizerName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCII_FOLDING = "asciifolding"
        ELISION = "elision"
        LOWERCASE = "lowercase"
        STANDARD = "standard"
        UPPERCASE = "uppercase"


    class azure.search.documents.indexes.models.LexicalTokenizer(_Model):
        name: str
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LexicalTokenizerName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIC = "classic"
        EDGE_N_GRAM = "edgeNGram"
        KEYWORD = "keyword_v2"
        LETTER = "letter"
        LOWERCASE = "lowercase"
        MICROSOFT_LANGUAGE_STEMMING_TOKENIZER = "microsoft_language_stemming_tokenizer"
        MICROSOFT_LANGUAGE_TOKENIZER = "microsoft_language_tokenizer"
        N_GRAM = "nGram"
        PATH_HIERARCHY = "path_hierarchy_v2"
        PATTERN = "pattern"
        STANDARD = "standard_v2"
        UAX_URL_EMAIL = "uax_url_email"
        WHITESPACE = "whitespace"


    class azure.search.documents.indexes.models.LimitTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.LimitTokenFilter'):
        consume_all_tokens: Optional[bool]
        max_token_count: Optional[int]
        name: str
        odata_type: Literal["#LimitTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                consume_all_tokens: Optional[bool] = ..., 
                max_token_count: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ListingSearchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREFIX = "prefix"


    class azure.search.documents.indexes.models.LuceneStandardAnalyzer(LexicalAnalyzer, discriminator='#Microsoft.Azure.Search.StandardAnalyzer'):
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#StandardAnalyzer"]
        stopwords: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                max_token_length: Optional[int] = ..., 
                name: str, 
                stopwords: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LuceneStandardTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.StandardTokenizer'):
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#StandardTokenizer"]

        @overload
        def __init__(
                self, 
                *, 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.LuceneStandardTokenizerV2(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.StandardTokenizerV2'):
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#StandardTokenizerV2"]

        @overload
        def __init__(
                self, 
                *, 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MagnitudeScoringFunction(ScoringFunction, discriminator='magnitude'):
        boost: float
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: MagnitudeScoringParameters
        type: Literal["magnitude"]

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                field_name: str, 
                interpolation: Optional[Union[str, ScoringFunctionInterpolation]] = ..., 
                parameters: MagnitudeScoringParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MagnitudeScoringParameters(_Model):
        boosting_range_end: float
        boosting_range_start: float
        should_boost_beyond_range_by_constant: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                boosting_range_end: float, 
                boosting_range_start: float, 
                should_boost_beyond_range_by_constant: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MappingCharFilter(CharFilter, discriminator='#Microsoft.Azure.Search.MappingCharFilter'):
        mappings: list[str]
        name: str
        odata_type: Literal["#MappingCharFilter"]

        @overload
        def __init__(
                self, 
                *, 
                mappings: list[str], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MarkdownHeaderDepth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        H1 = "h1"
        H2 = "h2"
        H3 = "h3"
        H4 = "h4"
        H5 = "h5"
        H6 = "h6"


    class azure.search.documents.indexes.models.MarkdownParsingSubmode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_TO_MANY = "oneToMany"
        ONE_TO_ONE = "oneToOne"


    class azure.search.documents.indexes.models.McpServerAuthentication(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerAuthenticationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUNDRY_CONNECTION = "foundryConnection"
        STORED_HEADERS = "storedHeaders"


    class azure.search.documents.indexes.models.McpServerAutoOutputParsing(McpServerOutputParsing, discriminator='auto'):
        kind: Literal[McpServerOutputParsingKind.AUTO]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerFoundryConnectionAuthentication(McpServerAuthentication, discriminator='foundryConnection'):
        foundry_connection_parameters: McpServerFoundryConnectionParameters
        kind: Literal[McpServerAuthenticationKind.FOUNDRY_CONNECTION]

        @overload
        def __init__(
                self, 
                *, 
                foundry_connection_parameters: McpServerFoundryConnectionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerFoundryConnectionParameters(_Model):
        connection_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerHeaders(_Model):


    class azure.search.documents.indexes.models.McpServerJsonOutputParsing(McpServerOutputParsing, discriminator='json'):
        json_parameters: McpServerOutputParsingJsonParameters
        kind: Literal[McpServerOutputParsingKind.JSON]

        @overload
        def __init__(
                self, 
                *, 
                json_parameters: McpServerOutputParsingJsonParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerKnowledgeSource(KnowledgeSource, discriminator='mcpServer'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Literal[KnowledgeSourceKind.MCP_SERVER]
        mcp_server_parameters: McpServerKnowledgeSourceParameters
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                mcp_server_parameters: McpServerKnowledgeSourceParameters, 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerKnowledgeSourceParameters(_Model):
        authentication: Optional[McpServerAuthentication]
        server_url: str
        tools: list[McpServerTool]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[McpServerAuthentication] = ..., 
                server_url: str, 
                tools: list[McpServerTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerNoneOutputParsing(McpServerOutputParsing, discriminator='none'):
        kind: Literal[McpServerOutputParsingKind.NONE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerOutputParsing(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerOutputParsingJsonParameters(_Model):
        documents_path: str
        include_context: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                documents_path: str, 
                include_context: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerOutputParsingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        JSON = "json"
        NONE = "none"
        SPLIT = "split"


    class azure.search.documents.indexes.models.McpServerOutputParsingSplitParameters(_Model):
        default_language_code: Optional[Union[str, SplitSkillLanguage]]
        maximum_page_length: Optional[int]
        maximum_pages_to_take: Optional[int]
        page_overlap_length: Optional[int]
        text_split_mode: Optional[Union[str, TextSplitMode]]

        @overload
        def __init__(
                self, 
                *, 
                default_language_code: Optional[Union[str, SplitSkillLanguage]] = ..., 
                maximum_page_length: Optional[int] = ..., 
                maximum_pages_to_take: Optional[int] = ..., 
                page_overlap_length: Optional[int] = ..., 
                text_split_mode: Optional[Union[str, TextSplitMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerSplitOutputParsing(McpServerOutputParsing, discriminator='split'):
        kind: Literal[McpServerOutputParsingKind.SPLIT]
        split_parameters: Optional[McpServerOutputParsingSplitParameters]

        @overload
        def __init__(
                self, 
                *, 
                split_parameters: Optional[McpServerOutputParsingSplitParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerStoredHeadersAuthentication(McpServerAuthentication, discriminator='storedHeaders'):
        kind: Literal[McpServerAuthenticationKind.STORED_HEADERS]
        stored_headers_parameters: McpServerStoredHeadersParameters

        @overload
        def __init__(
                self, 
                *, 
                stored_headers_parameters: McpServerStoredHeadersParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerStoredHeadersParameters(_Model):
        headers: Optional[McpServerHeaders]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[McpServerHeaders] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.McpServerTool(_Model):
        max_output_tokens: Optional[int]
        name: Optional[str]
        output_parsing: Optional[McpServerOutputParsing]
        results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]]

        @overload
        def __init__(
                self, 
                *, 
                max_output_tokens: Optional[int] = ..., 
                name: Optional[str] = ..., 
                output_parsing: Optional[McpServerOutputParsing] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MergeSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.MergeSkill'):
        context: str
        description: str
        inputs: list[InputFieldMappingEntry]
        insert_post_tag: Optional[str]
        insert_pre_tag: Optional[str]
        name: str
        odata_type: Literal["#MergeSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                insert_post_tag: Optional[str] = ..., 
                insert_pre_tag: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MicrosoftLanguageStemmingTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.MicrosoftLanguageStemmingTokenizer'):
        is_search_tokenizer: Optional[bool]
        language: Optional[Union[str, MicrosoftStemmingTokenizerLanguage]]
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#MicrosoftLanguageStemmingTokenizer"]

        @overload
        def __init__(
                self, 
                *, 
                is_search_tokenizer: Optional[bool] = ..., 
                language: Optional[Union[str, MicrosoftStemmingTokenizerLanguage]] = ..., 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MicrosoftLanguageTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.MicrosoftLanguageTokenizer'):
        is_search_tokenizer: Optional[bool]
        language: Optional[Union[str, MicrosoftTokenizerLanguage]]
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#MicrosoftLanguageTokenizer"]

        @overload
        def __init__(
                self, 
                *, 
                is_search_tokenizer: Optional[bool] = ..., 
                language: Optional[Union[str, MicrosoftTokenizerLanguage]] = ..., 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.MicrosoftStemmingTokenizerLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARABIC = "arabic"
        BANGLA = "bangla"
        BULGARIAN = "bulgarian"
        CATALAN = "catalan"
        CROATIAN = "croatian"
        CZECH = "czech"
        DANISH = "danish"
        DUTCH = "dutch"
        ENGLISH = "english"
        ESTONIAN = "estonian"
        FINNISH = "finnish"
        FRENCH = "french"
        GERMAN = "german"
        GREEK = "greek"
        GUJARATI = "gujarati"
        HEBREW = "hebrew"
        HINDI = "hindi"
        HUNGARIAN = "hungarian"
        ICELANDIC = "icelandic"
        INDONESIAN = "indonesian"
        ITALIAN = "italian"
        KANNADA = "kannada"
        LATVIAN = "latvian"
        LITHUANIAN = "lithuanian"
        MALAY = "malay"
        MALAYALAM = "malayalam"
        MARATHI = "marathi"
        NORWEGIAN_BOKMAAL = "norwegianBokmaal"
        POLISH = "polish"
        PORTUGUESE = "portuguese"
        PORTUGUESE_BRAZILIAN = "portugueseBrazilian"
        PUNJABI = "punjabi"
        ROMANIAN = "romanian"
        RUSSIAN = "russian"
        SERBIAN_CYRILLIC = "serbianCyrillic"
        SERBIAN_LATIN = "serbianLatin"
        SLOVAK = "slovak"
        SLOVENIAN = "slovenian"
        SPANISH = "spanish"
        SWEDISH = "swedish"
        TAMIL = "tamil"
        TELUGU = "telugu"
        TURKISH = "turkish"
        UKRAINIAN = "ukrainian"
        URDU = "urdu"


    class azure.search.documents.indexes.models.MicrosoftTokenizerLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BANGLA = "bangla"
        BULGARIAN = "bulgarian"
        CATALAN = "catalan"
        CHINESE_SIMPLIFIED = "chineseSimplified"
        CHINESE_TRADITIONAL = "chineseTraditional"
        CROATIAN = "croatian"
        CZECH = "czech"
        DANISH = "danish"
        DUTCH = "dutch"
        ENGLISH = "english"
        FRENCH = "french"
        GERMAN = "german"
        GREEK = "greek"
        GUJARATI = "gujarati"
        HINDI = "hindi"
        ICELANDIC = "icelandic"
        INDONESIAN = "indonesian"
        ITALIAN = "italian"
        JAPANESE = "japanese"
        KANNADA = "kannada"
        KOREAN = "korean"
        MALAY = "malay"
        MALAYALAM = "malayalam"
        MARATHI = "marathi"
        NORWEGIAN_BOKMAAL = "norwegianBokmaal"
        POLISH = "polish"
        PORTUGUESE = "portuguese"
        PORTUGUESE_BRAZILIAN = "portugueseBrazilian"
        PUNJABI = "punjabi"
        ROMANIAN = "romanian"
        RUSSIAN = "russian"
        SERBIAN_CYRILLIC = "serbianCyrillic"
        SERBIAN_LATIN = "serbianLatin"
        SLOVENIAN = "slovenian"
        SPANISH = "spanish"
        SWEDISH = "swedish"
        TAMIL = "tamil"
        TELUGU = "telugu"
        THAI = "thai"
        UKRAINIAN = "ukrainian"
        URDU = "urdu"
        VIETNAMESE = "vietnamese"


    class azure.search.documents.indexes.models.NGramTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.NGramTokenFilter'):
        max_gram: Optional[int]
        min_gram: Optional[int]
        name: str
        odata_type: Literal["#NGramTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                max_gram: Optional[int] = ..., 
                min_gram: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.NGramTokenFilterV2(TokenFilter, discriminator='#Microsoft.Azure.Search.NGramTokenFilterV2'):
        max_gram: Optional[int]
        min_gram: Optional[int]
        name: str
        odata_type: Literal["#NGramTokenFilterV2"]

        @overload
        def __init__(
                self, 
                *, 
                max_gram: Optional[int] = ..., 
                min_gram: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.NGramTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.NGramTokenizer'):
        max_gram: Optional[int]
        min_gram: Optional[int]
        name: str
        odata_type: Literal["#NGramTokenizer"]
        token_chars: Optional[list[Union[str, TokenCharacterKind]]]

        @overload
        def __init__(
                self, 
                *, 
                max_gram: Optional[int] = ..., 
                min_gram: Optional[int] = ..., 
                name: str, 
                token_chars: Optional[list[Union[str, TokenCharacterKind]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.NativeBlobSoftDeleteDeletionDetectionPolicy(DataDeletionDetectionPolicy, discriminator='#Microsoft.Azure.Search.NativeBlobSoftDeleteDeletionDetectionPolicy'):
        odata_type: Literal["#NativeBlobSoftDeleteDeletionDetectionPolicy"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.OcrLineEnding(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CARRIAGE_RETURN = "carriageReturn"
        CARRIAGE_RETURN_LINE_FEED = "carriageReturnLineFeed"
        LINE_FEED = "lineFeed"
        SPACE = "space"


    class azure.search.documents.indexes.models.OcrSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Vision.OcrSkill'):
        context: str
        default_language_code: Optional[Union[str, OcrSkillLanguage]]
        description: str
        inputs: list[InputFieldMappingEntry]
        line_ending: Optional[Union[str, OcrLineEnding]]
        name: str
        odata_type: Literal["#OcrSkill"]
        outputs: list[OutputFieldMappingEntry]
        should_detect_orientation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, OcrSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                line_ending: Optional[Union[str, OcrLineEnding]] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                should_detect_orientation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.OcrSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AF = "af"
        ANP = "anp"
        AR = "ar"
        AST = "ast"
        AWA = "awa"
        AZ = "az"
        BE = "be"
        BE_CYRL = "be-cyrl"
        BE_LATN = "be-latn"
        BFY = "bfy"
        BFZ = "bfz"
        BG = "bg"
        BGC = "bgc"
        BHO = "bho"
        BI = "bi"
        BNS = "bns"
        BR = "br"
        BRA = "bra"
        BRX = "brx"
        BS = "bs"
        BUA = "bua"
        CA = "ca"
        CEB = "ceb"
        CH = "ch"
        CNR_CYRL = "cnr-cyrl"
        CNR_LATN = "cnr-latn"
        CO = "co"
        CRH = "crh"
        CS = "cs"
        CSB = "csb"
        CY = "cy"
        DA = "da"
        DE = "de"
        DHI = "dhi"
        DOI = "doi"
        DSB = "dsb"
        EL = "el"
        EN = "en"
        ES = "es"
        ET = "et"
        EU = "eu"
        FA = "fa"
        FI = "fi"
        FIL = "fil"
        FJ = "fj"
        FO = "fo"
        FR = "fr"
        FUR = "fur"
        FY = "fy"
        GA = "ga"
        GAG = "gag"
        GD = "gd"
        GIL = "gil"
        GL = "gl"
        GON = "gon"
        GV = "gv"
        GVR = "gvr"
        HAW = "haw"
        HI = "hi"
        HLB = "hlb"
        HNE = "hne"
        HNI = "hni"
        HOC = "hoc"
        HR = "hr"
        HSB = "hsb"
        HT = "ht"
        HU = "hu"
        IA = "ia"
        ID = "id"
        IS = "is"
        IT = "it"
        IU = "iu"
        JA = "ja"
        JNS = "Jns"
        JV = "jv"
        KAA = "kaa"
        KAA_CYRL = "kaa-cyrl"
        KAC = "kac"
        KEA = "kea"
        KFQ = "kfq"
        KHA = "kha"
        KK_CYRL = "kk-cyrl"
        KK_LATN = "kk-latn"
        KL = "kl"
        KLR = "klr"
        KMJ = "kmj"
        KO = "ko"
        KOS = "kos"
        KPY = "kpy"
        KRC = "krc"
        KRU = "kru"
        KSH = "ksh"
        KUM = "kum"
        KU_ARAB = "ku-arab"
        KU_LATN = "ku-latn"
        KW = "kw"
        KY = "ky"
        LA = "la"
        LB = "lb"
        LKT = "lkt"
        LT = "lt"
        MI = "mi"
        MN = "mn"
        MR = "mr"
        MS = "ms"
        MT = "mt"
        MWW = "mww"
        MYV = "myv"
        NAP = "nap"
        NB = "nb"
        NE = "ne"
        NIU = "niu"
        NL = "nl"
        NO = "no"
        NOG = "nog"
        OC = "oc"
        OS = "os"
        PA = "pa"
        PL = "pl"
        PRS = "prs"
        PS = "ps"
        PT = "pt"
        QUC = "quc"
        RAB = "rab"
        RM = "rm"
        RO = "ro"
        RU = "ru"
        SA = "sa"
        SAT = "sat"
        SCK = "sck"
        SCO = "sco"
        SK = "sk"
        SL = "sl"
        SM = "sm"
        SMA = "sma"
        SME = "sme"
        SMJ = "smj"
        SMN = "smn"
        SMS = "sms"
        SO = "so"
        SQ = "sq"
        SR = "sr"
        SRX = "srx"
        SR_CYRL = "sr-Cyrl"
        SR_LATN = "sr-Latn"
        SV = "sv"
        SW = "sw"
        TET = "tet"
        TG = "tg"
        THF = "thf"
        TK = "tk"
        TO = "to"
        TR = "tr"
        TT = "tt"
        TYV = "tyv"
        UG = "ug"
        UNK = "unk"
        UR = "ur"
        UZ = "uz"
        UZ_ARAB = "uz-arab"
        UZ_CYRL = "uz-cyrl"
        VO = "vo"
        WAE = "wae"
        XNR = "xnr"
        XSR = "xsr"
        YUA = "yua"
        ZA = "za"
        ZH_HANS = "zh-Hans"
        ZH_HANT = "zh-Hant"
        ZU = "zu"


    class azure.search.documents.indexes.models.OutputFieldMappingEntry(_Model):
        name: str
        target_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                target_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PIIDetectionSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.PIIDetectionSkill'):
        context: str
        default_language_code: Optional[str]
        description: str
        domain: Optional[str]
        inputs: list[InputFieldMappingEntry]
        mask: Optional[str]
        masking_mode: Optional[Union[str, PIIDetectionSkillMaskingMode]]
        minimum_precision: Optional[float]
        model_version: Optional[str]
        name: str
        odata_type: Literal["#PIIDetectionSkill"]
        outputs: list[OutputFieldMappingEntry]
        pii_categories: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[str] = ..., 
                description: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                mask: Optional[str] = ..., 
                masking_mode: Optional[Union[str, PIIDetectionSkillMaskingMode]] = ..., 
                minimum_precision: Optional[float] = ..., 
                model_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                pii_categories: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PIIDetectionSkillMaskingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        REPLACE = "replace"


    class azure.search.documents.indexes.models.PathHierarchyTokenizerV2(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.PathHierarchyTokenizerV2'):
        delimiter: Optional[str]
        max_token_length: Optional[int]
        name: str
        number_of_tokens_to_skip: Optional[int]
        odata_type: Literal["#PathHierarchyTokenizerV2"]
        replacement: Optional[str]
        reverse_token_order: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                delimiter: Optional[str] = ..., 
                max_token_length: Optional[int] = ..., 
                name: str, 
                number_of_tokens_to_skip: Optional[int] = ..., 
                replacement: Optional[str] = ..., 
                reverse_token_order: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PatternAnalyzer(LexicalAnalyzer, discriminator='#Microsoft.Azure.Search.PatternAnalyzer'):
        flags: Optional[list[Union[str, RegexFlags]]]
        lower_case_terms: Optional[bool]
        name: str
        odata_type: Literal["#PatternAnalyzer"]
        pattern: Optional[str]
        stopwords: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[list[Union[str, RegexFlags]]] = ..., 
                lower_case_terms: Optional[bool] = ..., 
                name: str, 
                pattern: Optional[str] = ..., 
                stopwords: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PatternCaptureTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.PatternCaptureTokenFilter'):
        name: str
        odata_type: Literal["#PatternCaptureTokenFilter"]
        patterns: list[str]
        preserve_original: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                patterns: list[str], 
                preserve_original: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PatternReplaceCharFilter(CharFilter, discriminator='#Microsoft.Azure.Search.PatternReplaceCharFilter'):
        name: str
        odata_type: Literal["#PatternReplaceCharFilter"]
        pattern: str
        replacement: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                pattern: str, 
                replacement: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PatternReplaceTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.PatternReplaceTokenFilter'):
        name: str
        odata_type: Literal["#PatternReplaceTokenFilter"]
        pattern: str
        replacement: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                pattern: str, 
                replacement: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PatternTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.PatternTokenizer'):
        flags: Optional[list[Union[str, RegexFlags]]]
        group: Optional[int]
        name: str
        odata_type: Literal["#PatternTokenizer"]
        pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[list[Union[str, RegexFlags]]] = ..., 
                group: Optional[int] = ..., 
                name: str, 
                pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.PermissionFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP_IDS = "groupIds"
        RBAC_SCOPE = "rbacScope"
        USER_IDS = "userIds"


    class azure.search.documents.indexes.models.PhoneticEncoder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEIDER_MORSE = "beiderMorse"
        CAVERPHONE1 = "caverphone1"
        CAVERPHONE2 = "caverphone2"
        COLOGNE = "cologne"
        DOUBLE_METAPHONE = "doubleMetaphone"
        HAASE_PHONETIK = "haasePhonetik"
        KOELNER_PHONETIK = "koelnerPhonetik"
        METAPHONE = "metaphone"
        NYSIIS = "nysiis"
        REFINED_SOUNDEX = "refinedSoundex"
        SOUNDEX = "soundex"


    class azure.search.documents.indexes.models.PhoneticTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.PhoneticTokenFilter'):
        encoder: Optional[Union[str, PhoneticEncoder]]
        name: str
        odata_type: Literal["#PhoneticTokenFilter"]
        replace_original_tokens: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                encoder: Optional[Union[str, PhoneticEncoder]] = ..., 
                name: str, 
                replace_original_tokens: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.RankingOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOSTED_RERANKER_SCORE = "BoostedRerankerScore"
        RERANKER_SCORE = "RerankerScore"


    class azure.search.documents.indexes.models.RegexFlags(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANON_EQ = "CANON_EQ"
        CASE_INSENSITIVE = "CASE_INSENSITIVE"
        COMMENTS = "COMMENTS"
        DOT_ALL = "DOTALL"
        LITERAL = "LITERAL"
        MULTILINE = "MULTILINE"
        UNICODE_CASE = "UNICODE_CASE"
        UNIX_LINES = "UNIX_LINES"


    class azure.search.documents.indexes.models.RemoteSharePointKnowledgeSource(KnowledgeSource, discriminator='remoteSharePoint'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Literal[KnowledgeSourceKind.REMOTE_SHARE_POINT]
        name: str
        remote_share_point_parameters: Optional[RemoteSharePointKnowledgeSourceParameters]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                remote_share_point_parameters: Optional[RemoteSharePointKnowledgeSourceParameters] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.RemoteSharePointKnowledgeSourceParameters(_Model):
        container_type_id: Optional[str]
        filter_expression: Optional[str]
        resource_metadata: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                container_type_id: Optional[str] = ..., 
                filter_expression: Optional[str] = ..., 
                resource_metadata: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.RescoringOptions(_Model):
        default_oversampling: Optional[float]
        enable_rescoring: Optional[bool]
        rescore_storage_method: Optional[Union[str, VectorSearchCompressionRescoreStorageMethod]]

        @overload
        def __init__(
                self, 
                *, 
                default_oversampling: Optional[float] = ..., 
                enable_rescoring: Optional[bool] = ..., 
                rescore_storage_method: Optional[Union[str, VectorSearchCompressionRescoreStorageMethod]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ResourceCounter(_Model):
        quota: Optional[int]
        usage: int

        @overload
        def __init__(
                self, 
                *, 
                quota: Optional[int] = ..., 
                usage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ScalarQuantizationCompression(VectorSearchCompression, discriminator='scalarQuantization'):
        compression_name: str
        kind: Literal[VectorSearchCompressionKind.SCALAR_QUANTIZATION]
        parameters: Optional[ScalarQuantizationParameters]
        rescoring_options: RescoringOptions
        truncation_dimension: int

        @overload
        def __init__(
                self, 
                *, 
                compression_name: str, 
                parameters: Optional[ScalarQuantizationParameters] = ..., 
                rescoring_options: Optional[RescoringOptions] = ..., 
                truncation_dimension: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ScalarQuantizationParameters(_Model):
        quantized_data_type: Optional[Union[str, VectorSearchCompressionTarget]]

        @overload
        def __init__(
                self, 
                *, 
                quantized_data_type: Optional[Union[str, VectorSearchCompressionTarget]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ScoringFunction(_Model):
        boost: float
        field_name: str
        interpolation: Optional[Union[str, ScoringFunctionInterpolation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                field_name: str, 
                interpolation: Optional[Union[str, ScoringFunctionInterpolation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ScoringFunctionAggregation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "average"
        FIRST_MATCHING = "firstMatching"
        MAXIMUM = "maximum"
        MINIMUM = "minimum"
        PRODUCT = "product"
        SUM = "sum"


    class azure.search.documents.indexes.models.ScoringFunctionInterpolation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSTANT = "constant"
        LINEAR = "linear"
        LOGARITHMIC = "logarithmic"
        QUADRATIC = "quadratic"


    class azure.search.documents.indexes.models.ScoringProfile(_Model):
        function_aggregation: Optional[Union[str, ScoringFunctionAggregation]]
        functions: Optional[list[ScoringFunction]]
        name: str
        text_weights: Optional[TextWeights]

        @overload
        def __init__(
                self, 
                *, 
                function_aggregation: Optional[Union[str, ScoringFunctionAggregation]] = ..., 
                functions: Optional[list[ScoringFunction]] = ..., 
                name: str, 
                text_weights: Optional[TextWeights] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchAlias(_Model):
        e_tag: Optional[str]
        indexes: list[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                indexes: list[str], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchField(_SearchField):
        property hidden: Optional[bool]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.search.documents.indexes.models.SearchFieldDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Edm.Boolean"
        BYTE = "Edm.Byte"
        COMPLEX = "Edm.ComplexType"
        DATE_TIME_OFFSET = "Edm.DateTimeOffset"
        DOUBLE = "Edm.Double"
        GEOGRAPHY_POINT = "Edm.GeographyPoint"
        HALF = "Edm.Half"
        INT16 = "Edm.Int16"
        INT32 = "Edm.Int32"
        INT64 = "Edm.Int64"
        SINGLE = "Edm.Single"
        STRING = "Edm.String"
        S_BYTE = "Edm.SByte"


    class azure.search.documents.indexes.models.SearchIndex(_Model):
        analyzers: Optional[list[LexicalAnalyzer]]
        char_filters: Optional[list[CharFilter]]
        cors_options: Optional[CorsOptions]
        default_scoring_profile: Optional[str]
        description: Optional[str]
        e_tag: Optional[str]
        encryption_key: Optional[SearchResourceEncryptionKey]
        fields: list[SearchField]
        name: str
        normalizers: Optional[list[LexicalNormalizer]]
        permission_filter_option: Optional[Union[str, SearchIndexPermissionFilterOption]]
        purview_enabled: Optional[bool]
        scoring_profiles: Optional[list[ScoringProfile]]
        semantic_search: Optional[SemanticSearch]
        share_point_connector_app_registration: Optional[SharePointConnectorAppRegistration]
        similarity: Optional[SimilarityAlgorithm]
        suggesters: Optional[list[SearchSuggester]]
        token_filters: Optional[list[TokenFilter]]
        tokenizers: Optional[list[LexicalTokenizer]]
        vector_search: Optional[VectorSearch]

        @overload
        def __init__(
                self, 
                *, 
                analyzers: Optional[list[LexicalAnalyzer]] = ..., 
                char_filters: Optional[list[CharFilter]] = ..., 
                cors_options: Optional[CorsOptions] = ..., 
                default_scoring_profile: Optional[str] = ..., 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                fields: list[SearchField], 
                name: str, 
                normalizers: Optional[list[LexicalNormalizer]] = ..., 
                permission_filter_option: Optional[Union[str, SearchIndexPermissionFilterOption]] = ..., 
                purview_enabled: Optional[bool] = ..., 
                scoring_profiles: Optional[list[ScoringProfile]] = ..., 
                semantic_search: Optional[SemanticSearch] = ..., 
                share_point_connector_app_registration: Optional[SharePointConnectorAppRegistration] = ..., 
                similarity: Optional[SimilarityAlgorithm] = ..., 
                suggesters: Optional[list[SearchSuggester]] = ..., 
                token_filters: Optional[list[TokenFilter]] = ..., 
                tokenizers: Optional[list[LexicalTokenizer]] = ..., 
                vector_search: Optional[VectorSearch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexFieldReference(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSource(KnowledgeSource, discriminator='searchIndex'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Literal[KnowledgeSourceKind.SEARCH_INDEX]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]
        search_index_parameters: SearchIndexKnowledgeSourceParameters

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ..., 
                search_index_parameters: SearchIndexKnowledgeSourceParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceBoost(_Model):
        boost_instructions: Optional[str]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                boost_instructions: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceBoostKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIELD_VALUE = "fieldValue"
        MULTI_WORD_EXPRESSION = "multiWordExpression"


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceFieldValueBoost(SearchIndexKnowledgeSourceBoost, discriminator='fieldValue'):
        boost: float
        boost_instructions: str
        field: str
        field_values: Optional[list[str]]
        kind: Literal[SearchIndexKnowledgeSourceBoostKind.FIELD_VALUE]

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                boost_instructions: Optional[str] = ..., 
                field: str, 
                field_values: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceFilterHint(_Model):
        field: str
        field_values: list[str]
        filter_instructions: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                field: str, 
                field_values: list[str], 
                filter_instructions: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceMultiWordExpressionBoost(SearchIndexKnowledgeSourceBoost, discriminator='multiWordExpression'):
        boost: float
        boost_instructions: str
        field_values: Optional[list[str]]
        kind: Literal[SearchIndexKnowledgeSourceBoostKind.MULTI_WORD_EXPRESSION]

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                boost_instructions: Optional[str] = ..., 
                field_values: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters(_Model):
        base_filter: Optional[str]
        query_hints: Optional[SearchIndexKnowledgeSourceQueryHints]
        search_fields: Optional[list[SearchIndexFieldReference]]
        search_index_name: str
        semantic_configuration_name: Optional[str]
        source_data_fields: Optional[list[SearchIndexFieldReference]]

        @overload
        def __init__(
                self, 
                *, 
                base_filter: Optional[str] = ..., 
                query_hints: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                search_fields: Optional[list[SearchIndexFieldReference]] = ..., 
                search_index_name: str, 
                semantic_configuration_name: Optional[str] = ..., 
                source_data_fields: Optional[list[SearchIndexFieldReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceQueryHints(_Model):
        boosts: Optional[list[SearchIndexKnowledgeSourceBoost]]
        filters: Optional[list[SearchIndexKnowledgeSourceFilterHint]]

        @overload
        def __init__(
                self, 
                *, 
                boosts: Optional[list[SearchIndexKnowledgeSourceBoost]] = ..., 
                filters: Optional[list[SearchIndexKnowledgeSourceFilterHint]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexPermissionFilterOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.search.documents.indexes.models.SearchIndexer(_Model):
        cache: Optional[SearchIndexerCache]
        data_source_name: str
        description: Optional[str]
        e_tag: Optional[str]
        encryption_key: Optional[SearchResourceEncryptionKey]
        field_mappings: Optional[list[FieldMapping]]
        is_disabled: Optional[bool]
        name: str
        output_field_mappings: Optional[list[FieldMapping]]
        parameters: Optional[IndexingParameters]
        schedule: Optional[IndexingSchedule]
        skillset_name: Optional[str]
        target_index_name: str

        @overload
        def __init__(
                self, 
                *, 
                cache: Optional[SearchIndexerCache] = ..., 
                data_source_name: str, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                field_mappings: Optional[list[FieldMapping]] = ..., 
                is_disabled: Optional[bool] = ..., 
                name: str, 
                output_field_mappings: Optional[list[FieldMapping]] = ..., 
                parameters: Optional[IndexingParameters] = ..., 
                schedule: Optional[IndexingSchedule] = ..., 
                skillset_name: Optional[str] = ..., 
                target_index_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerCache(_Model):
        enable_reprocessing: Optional[bool]
        id: Optional[str]
        identity: Optional[SearchIndexerDataIdentity]
        storage_connection_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_reprocessing: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                storage_connection_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerDataContainer(_Model):
        name: str
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerDataIdentity(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerDataNoneIdentity(SearchIndexerDataIdentity, discriminator='#Microsoft.Azure.Search.DataNoneIdentity'):
        odata_type: Literal["#DataNoneIdentity"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerDataSourceConnection(_SearchIndexerDataSourceConnection):

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                container: SearchIndexerDataContainer, 
                credentials: DataSourceCredentials, 
                data_change_detection_policy: Optional[DataChangeDetectionPolicy] = ..., 
                data_deletion_detection_policy: Optional[DataDeletionDetectionPolicy] = ..., 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                name: str, 
                type: Union[str, SearchIndexerDataSourceType]
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                container: SearchIndexerDataContainer, 
                data_change_detection_policy: Optional[DataChangeDetectionPolicy] = ..., 
                data_deletion_detection_policy: Optional[DataDeletionDetectionPolicy] = ..., 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                name: str, 
                type: Union[str, SearchIndexerDataSourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerDataSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADLS_GEN2 = "adlsgen2"
        AZURE_BLOB = "azureblob"
        AZURE_SQL = "azuresql"
        AZURE_TABLE = "azuretable"
        COSMOS_DB = "cosmosdb"
        MYSQL = "mysql"
        ONELAKE = "onelake"
        SHAREPOINT = "sharepoint"


    class azure.search.documents.indexes.models.SearchIndexerDataUserAssignedIdentity(SearchIndexerDataIdentity, discriminator='#Microsoft.Azure.Search.DataUserAssignedIdentity'):
        federated_identity_client_id: Optional[str]
        odata_type: Literal["#DataUserAssignedIdentity"]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                federated_identity_client_id: Optional[str] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerError(_Model):
        details: Optional[str]
        documentation_link: Optional[str]
        error_message: str
        key: Optional[str]
        name: Optional[str]
        status_code: int


    class azure.search.documents.indexes.models.SearchIndexerIndexProjection(_Model):
        parameters: Optional[SearchIndexerIndexProjectionsParameters]
        selectors: list[SearchIndexerIndexProjectionSelector]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[SearchIndexerIndexProjectionsParameters] = ..., 
                selectors: list[SearchIndexerIndexProjectionSelector]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerIndexProjectionSelector(_Model):
        mappings: list[InputFieldMappingEntry]
        parent_key_field_name: str
        source_context: str
        target_index_name: str

        @overload
        def __init__(
                self, 
                *, 
                mappings: list[InputFieldMappingEntry], 
                parent_key_field_name: str, 
                source_context: str, 
                target_index_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerIndexProjectionsParameters(_Model):
        projection_mode: Optional[Union[str, IndexProjectionMode]]

        @overload
        def __init__(
                self, 
                *, 
                projection_mode: Optional[Union[str, IndexProjectionMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStore(_Model):
        identity: Optional[SearchIndexerDataIdentity]
        parameters: Optional[SearchIndexerKnowledgeStoreParameters]
        projections: list[SearchIndexerKnowledgeStoreProjection]
        storage_connection_string: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                parameters: Optional[SearchIndexerKnowledgeStoreParameters] = ..., 
                projections: list[SearchIndexerKnowledgeStoreProjection], 
                storage_connection_string: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreBlobProjectionSelector(SearchIndexerKnowledgeStoreProjectionSelector):
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        storage_container: str

        @overload
        def __init__(
                self, 
                *, 
                generated_key_name: Optional[str] = ..., 
                inputs: Optional[list[InputFieldMappingEntry]] = ..., 
                reference_key_name: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_context: Optional[str] = ..., 
                storage_container: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreFileProjectionSelector(SearchIndexerKnowledgeStoreBlobProjectionSelector):
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        storage_container: str

        @overload
        def __init__(
                self, 
                *, 
                generated_key_name: Optional[str] = ..., 
                inputs: Optional[list[InputFieldMappingEntry]] = ..., 
                reference_key_name: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_context: Optional[str] = ..., 
                storage_container: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreObjectProjectionSelector(SearchIndexerKnowledgeStoreBlobProjectionSelector):
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        storage_container: str

        @overload
        def __init__(
                self, 
                *, 
                generated_key_name: Optional[str] = ..., 
                inputs: Optional[list[InputFieldMappingEntry]] = ..., 
                reference_key_name: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_context: Optional[str] = ..., 
                storage_container: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreParameters(_Model):
        synthesize_generated_key_name: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                synthesize_generated_key_name: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreProjection(_Model):
        files: Optional[list[SearchIndexerKnowledgeStoreFileProjectionSelector]]
        objects: Optional[list[SearchIndexerKnowledgeStoreObjectProjectionSelector]]
        tables: Optional[list[SearchIndexerKnowledgeStoreTableProjectionSelector]]

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[list[SearchIndexerKnowledgeStoreFileProjectionSelector]] = ..., 
                objects: Optional[list[SearchIndexerKnowledgeStoreObjectProjectionSelector]] = ..., 
                tables: Optional[list[SearchIndexerKnowledgeStoreTableProjectionSelector]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreProjectionSelector(_Model):
        generated_key_name: Optional[str]
        inputs: Optional[list[InputFieldMappingEntry]]
        reference_key_name: Optional[str]
        source: Optional[str]
        source_context: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                generated_key_name: Optional[str] = ..., 
                inputs: Optional[list[InputFieldMappingEntry]] = ..., 
                reference_key_name: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_context: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerKnowledgeStoreTableProjectionSelector(SearchIndexerKnowledgeStoreProjectionSelector):
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        table_name: str

        @overload
        def __init__(
                self, 
                *, 
                generated_key_name: str, 
                inputs: Optional[list[InputFieldMappingEntry]] = ..., 
                reference_key_name: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_context: Optional[str] = ..., 
                table_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerLimits(_Model):
        max_document_content_characters_to_extract: Optional[int]
        max_document_extraction_size: Optional[int]
        max_run_time: Optional[timedelta]


    class azure.search.documents.indexes.models.SearchIndexerSkill(_Model):
        context: Optional[str]
        description: Optional[str]
        inputs: list[InputFieldMappingEntry]
        name: Optional[str]
        odata_type: str
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                odata_type: str, 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerSkillset(_Model):
        cognitive_services_account: Optional[CognitiveServicesAccount]
        description: Optional[str]
        e_tag: Optional[str]
        encryption_key: Optional[SearchResourceEncryptionKey]
        index_projection: Optional[SearchIndexerIndexProjection]
        knowledge_store: Optional[SearchIndexerKnowledgeStore]
        name: str
        skills: list[SearchIndexerSkill]

        @overload
        def __init__(
                self, 
                *, 
                cognitive_services_account: Optional[CognitiveServicesAccount] = ..., 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                index_projection: Optional[SearchIndexerIndexProjection] = ..., 
                knowledge_store: Optional[SearchIndexerKnowledgeStore] = ..., 
                name: str, 
                skills: list[SearchIndexerSkill]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexerStatus(_Model):
        current_state: Optional[IndexerCurrentState]
        execution_history: list[IndexerExecutionResult]
        last_result: Optional[IndexerExecutionResult]
        limits: SearchIndexerLimits
        name: str
        runtime: IndexerRuntime
        status: Union[str, IndexerStatus]


    class azure.search.documents.indexes.models.SearchIndexerWarning(_Model):
        details: Optional[str]
        documentation_link: Optional[str]
        key: Optional[str]
        message: str
        name: Optional[str]


    class azure.search.documents.indexes.models.SearchResourceEncryptionKey(_SearchResourceEncryptionKey):

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                access_credentials: Optional[AzureActiveDirectoryApplicationCredentials] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                is_service_level_key: Optional[bool] = ..., 
                key_name: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                vault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.search.documents.indexes.models.SearchServiceCounters(_Model):
        alias_counter: ResourceCounter
        data_source_counter: ResourceCounter
        document_counter: ResourceCounter
        index_counter: ResourceCounter
        indexer_counter: ResourceCounter
        knowledge_base_counter: ResourceCounter
        knowledge_source_counter: ResourceCounter
        skillset_counter: ResourceCounter
        storage_size_counter: ResourceCounter
        synonym_map_counter: ResourceCounter
        vector_index_size_counter: ResourceCounter

        @overload
        def __init__(
                self, 
                *, 
                alias_counter: ResourceCounter, 
                data_source_counter: ResourceCounter, 
                document_counter: ResourceCounter, 
                index_counter: ResourceCounter, 
                indexer_counter: ResourceCounter, 
                knowledge_base_counter: ResourceCounter, 
                knowledge_source_counter: ResourceCounter, 
                skillset_counter: ResourceCounter, 
                storage_size_counter: ResourceCounter, 
                synonym_map_counter: ResourceCounter, 
                vector_index_size_counter: ResourceCounter
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchServiceLimits(_Model):
        max_complex_collection_fields_per_index: Optional[int]
        max_complex_objects_in_collections_per_document: Optional[int]
        max_cumulative_indexer_runtime_seconds: Optional[int]
        max_field_nesting_depth_per_index: Optional[int]
        max_fields_per_index: Optional[int]
        max_storage_per_index_in_bytes: Optional[int]
        max_vector_index_size_per_index_in_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_complex_collection_fields_per_index: Optional[int] = ..., 
                max_complex_objects_in_collections_per_document: Optional[int] = ..., 
                max_cumulative_indexer_runtime_seconds: Optional[int] = ..., 
                max_field_nesting_depth_per_index: Optional[int] = ..., 
                max_fields_per_index: Optional[int] = ..., 
                max_storage_per_index_in_bytes: Optional[int] = ..., 
                max_vector_index_size_per_index_in_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchServiceStatistics(_Model):
        counters: SearchServiceCounters
        indexers_runtime: ServiceIndexersRuntime
        limits: SearchServiceLimits

        @overload
        def __init__(
                self, 
                *, 
                counters: SearchServiceCounters, 
                indexers_runtime: ServiceIndexersRuntime, 
                limits: SearchServiceLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchSuggester(_Model):
        name: str
        search_mode: Literal["analyzingInfixMatching"]
        source_fields: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                source_fields: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SemanticConfiguration(_Model):
        flighting_opt_in: Optional[bool]
        name: str
        prioritized_fields: SemanticPrioritizedFields
        ranking_order: Optional[Union[str, RankingOrder]]

        @overload
        def __init__(
                self, 
                *, 
                flighting_opt_in: Optional[bool] = ..., 
                name: str, 
                prioritized_fields: SemanticPrioritizedFields, 
                ranking_order: Optional[Union[str, RankingOrder]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SemanticField(_Model):
        field_name: str

        @overload
        def __init__(
                self, 
                *, 
                field_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SemanticPrioritizedFields(_Model):
        content_fields: Optional[list[SemanticField]]
        keywords_fields: Optional[list[SemanticField]]
        title_field: Optional[SemanticField]

        @overload
        def __init__(
                self, 
                *, 
                content_fields: Optional[list[SemanticField]] = ..., 
                keywords_fields: Optional[list[SemanticField]] = ..., 
                title_field: Optional[SemanticField] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SemanticSearch(_Model):
        configurations: Optional[list[SemanticConfiguration]]
        default_configuration_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Optional[list[SemanticConfiguration]] = ..., 
                default_configuration_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SentimentSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DA = "da"
        DE = "de"
        EL = "el"
        EN = "en"
        ES = "es"
        FI = "fi"
        FR = "fr"
        IT = "it"
        NL = "nl"
        NO = "no"
        PL = "pl"
        PT_PT = "pt-PT"
        RU = "ru"
        SV = "sv"
        TR = "tr"


    class azure.search.documents.indexes.models.SentimentSkillV3(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.V3.SentimentSkill'):
        context: str
        default_language_code: Optional[Union[str, SentimentSkillLanguage]]
        description: str
        include_opinion_mining: Optional[bool]
        inputs: list[InputFieldMappingEntry]
        model_version: Optional[str]
        name: str
        odata_type: Literal["#SentimentSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, SentimentSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                include_opinion_mining: Optional[bool] = ..., 
                inputs: list[InputFieldMappingEntry], 
                model_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ServiceIndexersRuntime(_Model):
        beginning_time: datetime
        ending_time: datetime
        remaining_seconds: Optional[int]
        used_seconds: int

        @overload
        def __init__(
                self, 
                *, 
                beginning_time: datetime, 
                ending_time: datetime, 
                remaining_seconds: Optional[int] = ..., 
                used_seconds: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ShaperSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Util.ShaperSkill'):
        context: str
        description: str
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#ShaperSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SharePointConnectorAppRegistration(_Model):
        application_id: str
        federated_credential_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: str, 
                federated_credential_id: str, 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ShingleTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.ShingleTokenFilter'):
        filter_token: Optional[str]
        max_shingle_size: Optional[int]
        min_shingle_size: Optional[int]
        name: str
        odata_type: Literal["#ShingleTokenFilter"]
        output_unigrams: Optional[bool]
        output_unigrams_if_no_shingles: Optional[bool]
        token_separator: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filter_token: Optional[str] = ..., 
                max_shingle_size: Optional[int] = ..., 
                min_shingle_size: Optional[int] = ..., 
                name: str, 
                output_unigrams: Optional[bool] = ..., 
                output_unigrams_if_no_shingles: Optional[bool] = ..., 
                token_separator: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SimilarityAlgorithm(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SkillNames(_Model):
        skill_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                skill_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SnowballTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.SnowballTokenFilter'):
        language: Union[str, SnowballTokenFilterLanguage]
        name: str
        odata_type: Literal["#SnowballTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                language: Union[str, SnowballTokenFilterLanguage], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SnowballTokenFilterLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARMENIAN = "armenian"
        BASQUE = "basque"
        CATALAN = "catalan"
        DANISH = "danish"
        DUTCH = "dutch"
        ENGLISH = "english"
        FINNISH = "finnish"
        FRENCH = "french"
        GERMAN = "german"
        GERMAN2 = "german2"
        HUNGARIAN = "hungarian"
        ITALIAN = "italian"
        KP = "kp"
        LOVINS = "lovins"
        NORWEGIAN = "norwegian"
        PORTER = "porter"
        PORTUGUESE = "portuguese"
        ROMANIAN = "romanian"
        RUSSIAN = "russian"
        SPANISH = "spanish"
        SWEDISH = "swedish"
        TURKISH = "turkish"


    class azure.search.documents.indexes.models.SoftDeleteColumnDeletionDetectionPolicy(DataDeletionDetectionPolicy, discriminator='#Microsoft.Azure.Search.SoftDeleteColumnDeletionDetectionPolicy'):
        odata_type: Literal["#SoftDeleteColumnDeletionDetectionPolicy"]
        soft_delete_column_name: Optional[str]
        soft_delete_marker_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                soft_delete_column_name: Optional[str] = ..., 
                soft_delete_marker_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SplitSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.SplitSkill'):
        azure_open_ai_tokenizer_parameters: Optional[AzureOpenAITokenizerParameters]
        context: str
        default_language_code: Optional[Union[str, SplitSkillLanguage]]
        description: str
        inputs: list[InputFieldMappingEntry]
        maximum_page_length: Optional[int]
        maximum_pages_to_take: Optional[int]
        name: str
        odata_type: Literal["#SplitSkill"]
        outputs: list[OutputFieldMappingEntry]
        page_overlap_length: Optional[int]
        text_split_mode: Optional[Union[str, TextSplitMode]]
        unit: Optional[Union[str, SplitSkillUnit]]

        @overload
        def __init__(
                self, 
                *, 
                azure_open_ai_tokenizer_parameters: Optional[AzureOpenAITokenizerParameters] = ..., 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, SplitSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                maximum_page_length: Optional[int] = ..., 
                maximum_pages_to_take: Optional[int] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                page_overlap_length: Optional[int] = ..., 
                text_split_mode: Optional[Union[str, TextSplitMode]] = ..., 
                unit: Optional[Union[str, SplitSkillUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SplitSkillEncoderModelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CL100_K_BASE = "cl100k_base"
        P50_K_BASE = "p50k_base"
        P50_K_EDIT = "p50k_edit"
        R50_K_BASE = "r50k_base"


    class azure.search.documents.indexes.models.SplitSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AM = "am"
        BS = "bs"
        CS = "cs"
        DA = "da"
        DE = "de"
        EN = "en"
        ES = "es"
        ET = "et"
        FI = "fi"
        FR = "fr"
        HE = "he"
        HI = "hi"
        HR = "hr"
        HU = "hu"
        ID = "id"
        IS = "is"
        IT = "it"
        JA = "ja"
        KO = "ko"
        LV = "lv"
        NB = "nb"
        NL = "nl"
        PL = "pl"
        PT = "pt"
        PT_BR = "pt-br"
        RU = "ru"
        SK = "sk"
        SL = "sl"
        SR = "sr"
        SV = "sv"
        TR = "tr"
        UR = "ur"
        ZH = "zh"


    class azure.search.documents.indexes.models.SplitSkillUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_OPEN_AI_TOKENS = "azureOpenAITokens"
        CHARACTERS = "characters"


    class azure.search.documents.indexes.models.SqlIntegratedChangeTrackingPolicy(DataChangeDetectionPolicy, discriminator='#Microsoft.Azure.Search.SqlIntegratedChangeTrackingPolicy'):
        odata_type: Literal["#SqlIntegratedChangeTrackingPolicy"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.StemmerOverrideTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.StemmerOverrideTokenFilter'):
        name: str
        odata_type: Literal["#StemmerOverrideTokenFilter"]
        rules: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                rules: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.StemmerTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.StemmerTokenFilter'):
        language: Union[str, StemmerTokenFilterLanguage]
        name: str
        odata_type: Literal["#StemmerTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                language: Union[str, StemmerTokenFilterLanguage], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.StemmerTokenFilterLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARABIC = "arabic"
        ARMENIAN = "armenian"
        BASQUE = "basque"
        BRAZILIAN = "brazilian"
        BULGARIAN = "bulgarian"
        CATALAN = "catalan"
        CZECH = "czech"
        DANISH = "danish"
        DUTCH = "dutch"
        DUTCH_KP = "dutchKp"
        ENGLISH = "english"
        FINNISH = "finnish"
        FRENCH = "french"
        GALICIAN = "galician"
        GERMAN = "german"
        GERMAN2 = "german2"
        GREEK = "greek"
        HINDI = "hindi"
        HUNGARIAN = "hungarian"
        INDONESIAN = "indonesian"
        IRISH = "irish"
        ITALIAN = "italian"
        LATVIAN = "latvian"
        LIGHT_ENGLISH = "lightEnglish"
        LIGHT_FINNISH = "lightFinnish"
        LIGHT_FRENCH = "lightFrench"
        LIGHT_GERMAN = "lightGerman"
        LIGHT_HUNGARIAN = "lightHungarian"
        LIGHT_ITALIAN = "lightItalian"
        LIGHT_NORWEGIAN = "lightNorwegian"
        LIGHT_NYNORSK = "lightNynorsk"
        LIGHT_PORTUGUESE = "lightPortuguese"
        LIGHT_RUSSIAN = "lightRussian"
        LIGHT_SPANISH = "lightSpanish"
        LIGHT_SWEDISH = "lightSwedish"
        LOVINS = "lovins"
        MINIMAL_ENGLISH = "minimalEnglish"
        MINIMAL_FRENCH = "minimalFrench"
        MINIMAL_GALICIAN = "minimalGalician"
        MINIMAL_GERMAN = "minimalGerman"
        MINIMAL_NORWEGIAN = "minimalNorwegian"
        MINIMAL_NYNORSK = "minimalNynorsk"
        MINIMAL_PORTUGUESE = "minimalPortuguese"
        NORWEGIAN = "norwegian"
        PORTER2 = "porter2"
        PORTUGUESE = "portuguese"
        PORTUGUESE_RSLP = "portugueseRslp"
        POSSESSIVE_ENGLISH = "possessiveEnglish"
        ROMANIAN = "romanian"
        RUSSIAN = "russian"
        SORANI = "sorani"
        SPANISH = "spanish"
        SWEDISH = "swedish"
        TURKISH = "turkish"


    class azure.search.documents.indexes.models.StopAnalyzer(LexicalAnalyzer, discriminator='#Microsoft.Azure.Search.StopAnalyzer'):
        name: str
        odata_type: Literal["#StopAnalyzer"]
        stopwords: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                stopwords: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.StopwordsList(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARABIC = "arabic"
        ARMENIAN = "armenian"
        BASQUE = "basque"
        BRAZILIAN = "brazilian"
        BULGARIAN = "bulgarian"
        CATALAN = "catalan"
        CZECH = "czech"
        DANISH = "danish"
        DUTCH = "dutch"
        ENGLISH = "english"
        FINNISH = "finnish"
        FRENCH = "french"
        GALICIAN = "galician"
        GERMAN = "german"
        GREEK = "greek"
        HINDI = "hindi"
        HUNGARIAN = "hungarian"
        INDONESIAN = "indonesian"
        IRISH = "irish"
        ITALIAN = "italian"
        LATVIAN = "latvian"
        NORWEGIAN = "norwegian"
        PERSIAN = "persian"
        PORTUGUESE = "portuguese"
        ROMANIAN = "romanian"
        RUSSIAN = "russian"
        SORANI = "sorani"
        SPANISH = "spanish"
        SWEDISH = "swedish"
        THAI = "thai"
        TURKISH = "turkish"


    class azure.search.documents.indexes.models.StopwordsTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.StopwordsTokenFilter'):
        ignore_case: Optional[bool]
        name: str
        odata_type: Literal["#StopwordsTokenFilter"]
        remove_trailing_stop_words: Optional[bool]
        stopwords: Optional[list[str]]
        stopwords_list: Optional[Union[str, StopwordsList]]

        @overload
        def __init__(
                self, 
                *, 
                ignore_case: Optional[bool] = ..., 
                name: str, 
                remove_trailing_stop_words: Optional[bool] = ..., 
                stopwords: Optional[list[str]] = ..., 
                stopwords_list: Optional[Union[str, StopwordsList]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SynonymMap(_Model):
        e_tag: Optional[str]
        encryption_key: Optional[SearchResourceEncryptionKey]
        format: Literal["solr"]
        name: str
        synonyms: list[str]

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                synonyms: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SynonymTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.SynonymTokenFilter'):
        expand: Optional[bool]
        ignore_case: Optional[bool]
        name: str
        odata_type: Literal["#SynonymTokenFilter"]
        synonyms: list[str]

        @overload
        def __init__(
                self, 
                *, 
                expand: Optional[bool] = ..., 
                ignore_case: Optional[bool] = ..., 
                name: str, 
                synonyms: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.TagScoringFunction(ScoringFunction, discriminator='tag'):
        boost: float
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: TagScoringParameters
        type: Literal["tag"]

        @overload
        def __init__(
                self, 
                *, 
                boost: float, 
                field_name: str, 
                interpolation: Optional[Union[str, ScoringFunctionInterpolation]] = ..., 
                parameters: TagScoringParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.TagScoringParameters(_Model):
        tags_parameter: str

        @overload
        def __init__(
                self, 
                *, 
                tags_parameter: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.TextSplitMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAGES = "pages"
        SENTENCES = "sentences"


    class azure.search.documents.indexes.models.TextTranslationSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Text.TranslationSkill'):
        context: str
        default_from_language_code: Optional[Union[str, TextTranslationSkillLanguage]]
        default_to_language_code: Union[str, TextTranslationSkillLanguage]
        description: str
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#TranslationSkill"]
        outputs: list[OutputFieldMappingEntry]
        suggested_from: Optional[Union[str, TextTranslationSkillLanguage]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_from_language_code: Optional[Union[str, TextTranslationSkillLanguage]] = ..., 
                default_to_language_code: Union[str, TextTranslationSkillLanguage], 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                suggested_from: Optional[Union[str, TextTranslationSkillLanguage]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.TextTranslationSkillLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AF = "af"
        AR = "ar"
        BG = "bg"
        BN = "bn"
        BS = "bs"
        CA = "ca"
        CS = "cs"
        CY = "cy"
        DA = "da"
        DE = "de"
        EL = "el"
        EN = "en"
        ES = "es"
        ET = "et"
        FA = "fa"
        FI = "fi"
        FIL = "fil"
        FJ = "fj"
        FR = "fr"
        GA = "ga"
        HE = "he"
        HI = "hi"
        HR = "hr"
        HT = "ht"
        HU = "hu"
        ID = "id"
        IS = "is"
        IT = "it"
        JA = "ja"
        KN = "kn"
        KO = "ko"
        LT = "lt"
        LV = "lv"
        MG = "mg"
        MI = "mi"
        ML = "ml"
        MS = "ms"
        MT = "mt"
        MWW = "mww"
        NB = "nb"
        NL = "nl"
        OTQ = "otq"
        PA = "pa"
        PL = "pl"
        PT = "pt"
        PT_BR = "pt-br"
        PT_PT = "pt-PT"
        RO = "ro"
        RU = "ru"
        SK = "sk"
        SL = "sl"
        SM = "sm"
        SR_CYRL = "sr-Cyrl"
        SR_LATN = "sr-Latn"
        SV = "sv"
        SW = "sw"
        TA = "ta"
        TE = "te"
        TH = "th"
        TLH = "tlh"
        TLH_LATN = "tlh-Latn"
        TLH_PIQD = "tlh-Piqd"
        TO = "to"
        TR = "tr"
        TY = "ty"
        UK = "uk"
        UR = "ur"
        VI = "vi"
        YUA = "yua"
        YUE = "yue"
        ZH_HANS = "zh-Hans"
        ZH_HANT = "zh-Hant"


    class azure.search.documents.indexes.models.TextWeights(_Model):
        weights: dict[str, float]

        @overload
        def __init__(
                self, 
                *, 
                weights: dict[str, float]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.TokenCharacterKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIGIT = "digit"
        LETTER = "letter"
        PUNCTUATION = "punctuation"
        SYMBOL = "symbol"
        WHITESPACE = "whitespace"


    class azure.search.documents.indexes.models.TokenFilter(_Model):
        name: str
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.TokenFilterName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APOSTROPHE = "apostrophe"
        ARABIC_NORMALIZATION = "arabic_normalization"
        ASCII_FOLDING = "asciifolding"
        CJK_BIGRAM = "cjk_bigram"
        CJK_WIDTH = "cjk_width"
        CLASSIC = "classic"
        COMMON_GRAM = "common_grams"
        EDGE_N_GRAM = "edgeNGram_v2"
        ELISION = "elision"
        GERMAN_NORMALIZATION = "german_normalization"
        HINDI_NORMALIZATION = "hindi_normalization"
        INDIC_NORMALIZATION = "indic_normalization"
        KEYWORD_REPEAT = "keyword_repeat"
        K_STEM = "kstem"
        LENGTH = "length"
        LIMIT = "limit"
        LOWERCASE = "lowercase"
        N_GRAM = "nGram_v2"
        PERSIAN_NORMALIZATION = "persian_normalization"
        PHONETIC = "phonetic"
        PORTER_STEM = "porter_stem"
        REVERSE = "reverse"
        SCANDINAVIAN_FOLDING_NORMALIZATION = "scandinavian_folding"
        SCANDINAVIAN_NORMALIZATION = "scandinavian_normalization"
        SHINGLE = "shingle"
        SNOWBALL = "snowball"
        SORANI_NORMALIZATION = "sorani_normalization"
        STEMMER = "stemmer"
        STOPWORDS = "stopwords"
        TRIM = "trim"
        TRUNCATE = "truncate"
        UNIQUE = "unique"
        UPPERCASE = "uppercase"
        WORD_DELIMITER = "word_delimiter"


    class azure.search.documents.indexes.models.TruncateTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.TruncateTokenFilter'):
        length: Optional[int]
        name: str
        odata_type: Literal["#TruncateTokenFilter"]

        @overload
        def __init__(
                self, 
                *, 
                length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.UaxUrlEmailTokenizer(LexicalTokenizer, discriminator='#Microsoft.Azure.Search.UaxUrlEmailTokenizer'):
        max_token_length: Optional[int]
        name: str
        odata_type: Literal["#UaxUrlEmailTokenizer"]

        @overload
        def __init__(
                self, 
                *, 
                max_token_length: Optional[int] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.UniqueTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.UniqueTokenFilter'):
        name: str
        odata_type: Literal["#UniqueTokenFilter"]
        only_on_same_position: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                only_on_same_position: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.UpdateKnowledgeSourceFileRequest(_Model):
        content: Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]
        metadata: FileUploadMetadata

        @overload
        def __init__(
                self, 
                *, 
                content: FileType, 
                metadata: FileUploadMetadata
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.UploadKnowledgeSourceFileMultipartRequest(_Model):
        content: Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]
        metadata: FileUploadMetadata

        @overload
        def __init__(
                self, 
                *, 
                content: FileType, 
                metadata: FileUploadMetadata
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VectorEncodingFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PACKED_BIT = "packedBit"


    class azure.search.documents.indexes.models.VectorSearch(_Model):
        algorithms: Optional[list[VectorSearchAlgorithmConfiguration]]
        compressions: Optional[list[VectorSearchCompression]]
        profiles: Optional[list[VectorSearchProfile]]
        vectorizers: Optional[list[VectorSearchVectorizer]]

        @overload
        def __init__(
                self, 
                *, 
                algorithms: Optional[list[VectorSearchAlgorithmConfiguration]] = ..., 
                compressions: Optional[list[VectorSearchCompression]] = ..., 
                profiles: Optional[list[VectorSearchProfile]] = ..., 
                vectorizers: Optional[list[VectorSearchVectorizer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VectorSearchAlgorithmConfiguration(_Model):
        kind: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VectorSearchAlgorithmKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXHAUSTIVE_KNN = "exhaustiveKnn"
        HNSW = "hnsw"


    class azure.search.documents.indexes.models.VectorSearchAlgorithmMetric(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COSINE = "cosine"
        DOT_PRODUCT = "dotProduct"
        EUCLIDEAN = "euclidean"
        HAMMING = "hamming"


    class azure.search.documents.indexes.models.VectorSearchCompression(_Model):
        compression_name: str
        kind: str
        rescoring_options: Optional[RescoringOptions]
        truncation_dimension: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                compression_name: str, 
                kind: str, 
                rescoring_options: Optional[RescoringOptions] = ..., 
                truncation_dimension: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VectorSearchCompressionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY_QUANTIZATION = "binaryQuantization"
        SCALAR_QUANTIZATION = "scalarQuantization"


    class azure.search.documents.indexes.models.VectorSearchCompressionRescoreStorageMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISCARD_ORIGINALS = "discardOriginals"
        PRESERVE_ORIGINALS = "preserveOriginals"


    class azure.search.documents.indexes.models.VectorSearchCompressionTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INT8 = "int8"


    class azure.search.documents.indexes.models.VectorSearchProfile(_Model):
        algorithm_configuration_name: str
        compression_name: Optional[str]
        name: str
        vectorizer_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                algorithm_configuration_name: str, 
                compression_name: Optional[str] = ..., 
                name: str, 
                vectorizer_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VectorSearchVectorizer(_Model):
        kind: str
        vectorizer_name: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                vectorizer_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VectorSearchVectorizerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AI_SERVICES_VISION = "aiServicesVision"
        AML = "aml"
        AZURE_OPEN_AI = "azureOpenAI"
        CUSTOM_WEB_API = "customWebApi"


    class azure.search.documents.indexes.models.VisionVectorizeSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Vision.VectorizeSkill'):
        context: str
        description: str
        inputs: list[InputFieldMappingEntry]
        model_version: str
        name: str
        odata_type: Literal["#VectorizeSkill"]
        outputs: list[OutputFieldMappingEntry]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                model_version: str, 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.VisualFeature(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADULT = "adult"
        BRANDS = "brands"
        CATEGORIES = "categories"
        DESCRIPTION = "description"
        FACES = "faces"
        OBJECTS = "objects"
        TAGS = "tags"


    class azure.search.documents.indexes.models.WebApiHttpHeaders(_Model):


    class azure.search.documents.indexes.models.WebApiSkill(SearchIndexerSkill, discriminator='#Microsoft.Skills.Custom.WebApiSkill'):
        auth_identity: Optional[SearchIndexerDataIdentity]
        auth_resource_id: Optional[str]
        batch_size: Optional[int]
        context: str
        degree_of_parallelism: Optional[int]
        description: str
        http_headers: Optional[WebApiHttpHeaders]
        http_method: Optional[str]
        inputs: list[InputFieldMappingEntry]
        name: str
        odata_type: Literal["#WebApiSkill"]
        outputs: list[OutputFieldMappingEntry]
        timeout: Optional[timedelta]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                auth_identity: Optional[SearchIndexerDataIdentity] = ..., 
                auth_resource_id: Optional[str] = ..., 
                batch_size: Optional[int] = ..., 
                context: Optional[str] = ..., 
                degree_of_parallelism: Optional[int] = ..., 
                description: Optional[str] = ..., 
                http_headers: Optional[WebApiHttpHeaders] = ..., 
                http_method: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                timeout: Optional[timedelta] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WebApiVectorizer(VectorSearchVectorizer, discriminator='customWebApi'):
        kind: Literal[VectorSearchVectorizerKind.CUSTOM_WEB_API]
        vectorizer_name: str
        web_api_parameters: Optional[WebApiVectorizerParameters]

        @overload
        def __init__(
                self, 
                *, 
                vectorizer_name: str, 
                web_api_parameters: Optional[WebApiVectorizerParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WebApiVectorizerParameters(_Model):
        auth_identity: Optional[SearchIndexerDataIdentity]
        auth_resource_id: Optional[str]
        http_headers: Optional[dict[str, str]]
        http_method: Optional[str]
        timeout: Optional[timedelta]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth_identity: Optional[SearchIndexerDataIdentity] = ..., 
                auth_resource_id: Optional[str] = ..., 
                http_headers: Optional[dict[str, str]] = ..., 
                http_method: Optional[str] = ..., 
                timeout: Optional[timedelta] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WebKnowledgeSource(KnowledgeSource, discriminator='web'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Literal[KnowledgeSourceKind.WEB]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]
        web_parameters: Optional[WebKnowledgeSourceParameters]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ..., 
                web_parameters: Optional[WebKnowledgeSourceParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WebKnowledgeSourceDomain(_Model):
        address: str
        include_subpages: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                address: str, 
                include_subpages: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WebKnowledgeSourceDomains(_Model):
        allowed_domains: Optional[list[WebKnowledgeSourceDomain]]
        blocked_domains: Optional[list[WebKnowledgeSourceDomain]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_domains: Optional[list[WebKnowledgeSourceDomain]] = ..., 
                blocked_domains: Optional[list[WebKnowledgeSourceDomain]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WebKnowledgeSourceParameters(_Model):
        count: Optional[int]
        domains: Optional[WebKnowledgeSourceDomains]
        freshness: Optional[str]
        language: Optional[str]
        market: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                domains: Optional[WebKnowledgeSourceDomains] = ..., 
                freshness: Optional[str] = ..., 
                language: Optional[str] = ..., 
                market: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WordDelimiterTokenFilter(TokenFilter, discriminator='#Microsoft.Azure.Search.WordDelimiterTokenFilter'):
        catenate_all: Optional[bool]
        catenate_numbers: Optional[bool]
        catenate_words: Optional[bool]
        generate_number_parts: Optional[bool]
        generate_word_parts: Optional[bool]
        name: str
        odata_type: Literal["#WordDelimiterTokenFilter"]
        preserve_original: Optional[bool]
        protected_words: Optional[list[str]]
        split_on_case_change: Optional[bool]
        split_on_numerics: Optional[bool]
        stem_english_possessive: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                catenate_all: Optional[bool] = ..., 
                catenate_numbers: Optional[bool] = ..., 
                catenate_words: Optional[bool] = ..., 
                generate_number_parts: Optional[bool] = ..., 
                generate_word_parts: Optional[bool] = ..., 
                name: str, 
                preserve_original: Optional[bool] = ..., 
                protected_words: Optional[list[str]] = ..., 
                split_on_case_change: Optional[bool] = ..., 
                split_on_numerics: Optional[bool] = ..., 
                stem_english_possessive: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WorkIQKnowledgeSource(KnowledgeSource, discriminator='workIQ'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Literal[KnowledgeSourceKind.WORK_IQ]
        name: str
        results_processing: Union[str, KnowledgeSourceResultsProcessing]
        work_iq_parameters: WorkIQKnowledgeSourceParameters

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ..., 
                work_iq_parameters: WorkIQKnowledgeSourceParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.WorkIQKnowledgeSourceParameters(_Model):
        entra_app_authentication: EntraAppAuthentication

        @overload
        def __init__(
                self, 
                *, 
                entra_app_authentication: EntraAppAuthentication
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.search.documents.indexes.types

    class azure.search.documents.indexes.types.AIServicesAccountIdentity(TypedDict):
        key "description": str
        key "identity": Optional[SearchIndexerDataIdentity]
        @odata.type: Required[Literal["#AIServicesByIdentity"]]
        description: str
        identity: SearchIndexerDataIdentity
        odata_type: Literal[#AIServicesByIdentity]
        subdomainUrl: Required[str]
        subdomain_url: str


    class azure.search.documents.indexes.types.AIServicesAccountKey(TypedDict):
        key "description": str
        @odata.type: Required[Literal["#AIServicesByKey"]]
        description: str
        key: Required[str]
        odata_type: Literal[#AIServicesByKey]
        subdomainUrl: Required[str]
        subdomain_url: str


    class azure.search.documents.indexes.types.AIServicesVisionParameters(TypedDict, total=False):
        key "apiKey": str
        key "authIdentity": Optional[SearchIndexerDataIdentity]
        api_key: str
        auth_identity: SearchIndexerDataIdentity
        modelVersion: Required[Optional[str]]
        model_version: str
        resourceUri: Required[str]
        resource_uri: str


    class azure.search.documents.indexes.types.AIServicesVisionVectorizer(TypedDict, total=False):
        key "aiServicesVisionParameters": ForwardRef('AIServicesVisionParameters')
        ai_services_vision_parameters: AIServicesVisionParameters
        kind: Required[Literal[VectorSearchVectorizerKind.AI_SERVICES_VISION]]
        name: Required[str]
        vectorizer_name: str


    class azure.search.documents.indexes.types.AnalyzeResult(TypedDict, total=False):
        tokens: Required[list[AnalyzedTokenInfo]]


    class azure.search.documents.indexes.types.AnalyzeTextOptions(TypedDict, total=False):
        key "analyzer": Union[str, LexicalAnalyzerName]
        key "charFilters": list[Union[str, CharFilterName]]
        key "normalizer": Union[str, LexicalNormalizerName]
        key "tokenFilters": list[Union[str, TokenFilterName]]
        key "tokenizer": Union[str, LexicalTokenizerName]
        analyzer_name: Union[str, LexicalAnalyzerName]
        char_filters: list[Union[str, CharFilterName]]
        normalizer_name: Union[str, LexicalNormalizerName]
        text: Required[str]
        token_filters: list[Union[str, TokenFilterName]]
        tokenizer_name: Union[str, LexicalTokenizerName]


    class azure.search.documents.indexes.types.AnalyzedTokenInfo(TypedDict, total=False):
        endOffset: Required[int]
        end_offset: int
        position: Required[int]
        startOffset: Required[int]
        start_offset: int
        token: Required[str]


    class azure.search.documents.indexes.types.AsciiFoldingTokenFilter(TypedDict):
        key "preserveOriginal": bool
        @odata.type: Required[Literal["#AsciiFoldingTokenFilter"]]
        name: Required[str]
        odata_type: Literal[#AsciiFoldingTokenFilter]
        preserve_original: bool


    class azure.search.documents.indexes.types.AzureActiveDirectoryApplicationCredentials(TypedDict, total=False):
        key "applicationSecret": str
        applicationId: Required[str]
        application_id: str
        application_secret: str


    class azure.search.documents.indexes.types.AzureBlobKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        azureBlobParameters: Required[AzureBlobKnowledgeSourceParameters]
        azure_blob_parameters: AzureBlobKnowledgeSourceParameters
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Required[Literal[KnowledgeSourceKind.AZURE_BLOB]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.AzureBlobKnowledgeSourceParameters(TypedDict, total=False):
        key "createdResources": ForwardRef('CreatedResources')
        key "folderPath": Optional[str]
        key "ingestionParameters": Optional[KnowledgeSourceIngestionParameters]
        key "isADLSGen2": bool
        key "queryHints": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        connectionString: Required[str]
        connection_string: str
        containerName: Required[str]
        container_name: str
        created_resources: CreatedResources
        folder_path: str
        ingestion_parameters: KnowledgeSourceIngestionParameters
        is_adls_gen2: bool
        query_hints: SearchIndexKnowledgeSourceQueryHints


    class azure.search.documents.indexes.types.AzureMachineLearningParameters(TypedDict, total=False):
        key "key": Optional[str]
        key "modelName": Union[str, AIFoundryModelCatalogName]
        key "region": Optional[str]
        key "resourceId": Optional[str]
        key "timeout": Optional[str]
        authentication_key: str
        model_name: Union[str, AIFoundryModelCatalogName]
        region: str
        resource_id: str
        scoring_uri: str
        timeout: str
        uri: Required[Optional[str]]


    class azure.search.documents.indexes.types.AzureMachineLearningSkill(TypedDict):
        key "context": str
        key "degreeOfParallelism": Optional[int]
        key "description": str
        key "key": Optional[str]
        key "name": str
        key "region": Optional[str]
        key "resourceId": Optional[str]
        key "timeout": Optional[str]
        key "uri": Optional[str]
        @odata.type: Required[Literal["#AmlSkill"]]
        authentication_key: str
        context: str
        degree_of_parallelism: int
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#AmlSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        region: str
        resource_id: str
        scoring_uri: str
        timeout: str


    class azure.search.documents.indexes.types.AzureMachineLearningVectorizer(TypedDict, total=False):
        key "amlParameters": ForwardRef('AzureMachineLearningParameters')
        aml_parameters: AzureMachineLearningParameters
        kind: Required[Literal[VectorSearchVectorizerKind.AML]]
        name: Required[str]
        vectorizer_name: str


    class azure.search.documents.indexes.types.AzureOpenAIEmbeddingSkill(TypedDict):
        key "apiKey": str
        key "authIdentity": ForwardRef('SearchIndexerDataIdentity')
        key "context": str
        key "deploymentId": str
        key "description": str
        key "dimensions": Optional[int]
        key "modelName": Union[str, AzureOpenAIModelName]
        key "name": str
        key "resourceUri": str
        @odata.type: Required[Literal["#AzureOpenAIEmbeddingSkill"]]
        api_key: str
        auth_identity: SearchIndexerDataIdentity
        context: str
        deployment_name: str
        description: str
        dimensions: int
        inputs: Required[list[InputFieldMappingEntry]]
        model_name: Union[str, AzureOpenAIModelName]
        name: str
        odata_type: Literal[#AzureOpenAIEmbeddingSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        resource_url: str


    class azure.search.documents.indexes.types.AzureOpenAITokenizerParameters(TypedDict, total=False):
        key "allowedSpecialTokens": list[str]
        key "encoderModelName": Optional[Union[str, SplitSkillEncoderModelName]]
        allowed_special_tokens: list[str]
        encoder_model_name: Union[str, SplitSkillEncoderModelName]


    class azure.search.documents.indexes.types.AzureOpenAIVectorizer(TypedDict, total=False):
        key "azureOpenAIParameters": ForwardRef('AzureOpenAIVectorizerParameters')
        kind: Required[Literal[VectorSearchVectorizerKind.AZURE_OPEN_AI]]
        name: Required[str]
        parameters: AzureOpenAIVectorizerParameters
        vectorizer_name: str


    class azure.search.documents.indexes.types.AzureOpenAIVectorizerParameters(TypedDict, total=False):
        key "apiKey": str
        key "authIdentity": ForwardRef('SearchIndexerDataIdentity')
        key "deploymentId": str
        key "modelName": Union[str, AzureOpenAIModelName]
        key "resourceUri": str
        api_key: str
        auth_identity: SearchIndexerDataIdentity
        deployment_name: str
        model_name: Union[str, AzureOpenAIModelName]
        resource_url: str


    class azure.search.documents.indexes.types.BM25SimilarityAlgorithm(TypedDict):
        key "b": Optional[float]
        key "k1": Optional[float]
        @odata.type: Required[Literal["#BM25Similarity"]]
        b: float
        k1: float
        odata_type: Literal[#BM25Similarity]


    class azure.search.documents.indexes.types.BinaryQuantizationCompression(TypedDict, total=False):
        key "rescoringOptions": Optional[RescoringOptions]
        key "truncationDimension": Optional[int]
        compression_name: str
        kind: Required[Literal[VectorSearchCompressionKind.BINARY_QUANTIZATION]]
        name: Required[str]
        rescoring_options: RescoringOptions
        truncation_dimension: int


    class azure.search.documents.indexes.types.ChatCompletionCommonModelParameters(TypedDict, total=False):
        key "frequencyPenalty": Optional[float]
        key "maxTokens": Optional[int]
        key "model": Optional[str]
        key "presencePenalty": Optional[float]
        key "seed": Optional[int]
        key "stop": Optional[list[str]]
        key "temperature": Optional[float]
        frequency_penalty: float
        max_tokens: int
        model_name: str
        presence_penalty: float
        seed: int
        stop: list[str]
        temperature: float


    class azure.search.documents.indexes.types.ChatCompletionResponseFormat(TypedDict, total=False):
        key "jsonSchemaProperties": Optional[ChatCompletionSchemaProperties]
        key "type": Union[str, ChatCompletionResponseFormatType]
        json_schema_properties: ChatCompletionSchemaProperties
        type: Union[str, ChatCompletionResponseFormatType]


    class azure.search.documents.indexes.types.ChatCompletionSchema(TypedDict, total=False):
        key "additionalProperties": bool
        key "properties": str
        key "required": list[str]
        key "type": str
        additional_properties: bool
        properties: str
        required: list[str]
        type: str


    class azure.search.documents.indexes.types.ChatCompletionSchemaProperties(TypedDict, total=False):
        key "description": Optional[str]
        key "name": Optional[str]
        key "schema": ForwardRef('ChatCompletionSchema')
        key "strict": bool
        description: str
        name: str
        schema: ChatCompletionSchema
        strict: bool


    class azure.search.documents.indexes.types.ChatCompletionSkill(TypedDict):
        key "apiKey": str
        key "authIdentity": Optional[SearchIndexerDataIdentity]
        key "commonModelParameters": ForwardRef('ChatCompletionCommonModelParameters')
        key "context": str
        key "description": str
        key "extraParameters": Optional[dict[str, Any]]
        key "extraParametersBehavior": Union[str, ChatCompletionExtraParametersBehavior]
        key "name": str
        key "responseFormat": ForwardRef('ChatCompletionResponseFormat')
        @odata.type: Required[Literal["#ChatCompletionSkill"]]
        api_key: str
        auth_identity: SearchIndexerDataIdentity
        common_model_parameters: ChatCompletionCommonModelParameters
        context: str
        description: str
        extra_parameters: dict[str, Any]
        extra_parameters_behavior: Union[str, ChatCompletionExtraParametersBehavior]
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#ChatCompletionSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        response_format: ChatCompletionResponseFormat
        uri: Required[str]


    class azure.search.documents.indexes.types.CjkBigramTokenFilter(TypedDict):
        key "ignoreScripts": list[Union[str, CjkBigramTokenFilterScripts]]
        key "outputUnigrams": bool
        @odata.type: Required[Literal["#CjkBigramTokenFilter"]]
        ignore_scripts: list[Union[str, CjkBigramTokenFilterScripts]]
        name: Required[str]
        odata_type: Literal[#CjkBigramTokenFilter]
        output_unigrams: bool


    class azure.search.documents.indexes.types.ClassicSimilarityAlgorithm(TypedDict):
        @odata.type: Required[Literal["#ClassicSimilarity"]]
        odata_type: Literal[#ClassicSimilarity]


    class azure.search.documents.indexes.types.ClassicTokenizer(TypedDict):
        key "maxTokenLength": int
        @odata.type: Required[Literal["#ClassicTokenizer"]]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#ClassicTokenizer]


    class azure.search.documents.indexes.types.CognitiveServicesAccountKey(TypedDict):
        key "description": str
        @odata.type: Required[Literal["#CognitiveServicesByKey"]]
        description: str
        key: Required[str]
        odata_type: Literal[#CognitiveServicesByKey]


    class azure.search.documents.indexes.types.CommonGramTokenFilter(TypedDict):
        key "ignoreCase": bool
        key "queryMode": bool
        @odata.type: Required[Literal["#CommonGramTokenFilter"]]
        commonWords: Required[list[str]]
        common_words: list[str]
        ignore_case: bool
        name: Required[str]
        odata_type: Literal[#CommonGramTokenFilter]
        use_query_mode: bool


    class azure.search.documents.indexes.types.ConditionalSkill(TypedDict):
        key "context": str
        key "description": str
        key "name": str
        @odata.type: Required[Literal["#ConditionalSkill"]]
        context: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#ConditionalSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.ContentColumnMapping(TypedDict, total=False):
        name: Required[str]
        searchFieldType: Required[str]
        search_field_type: str
        sourceField: Required[str]
        source_field: str


    class azure.search.documents.indexes.types.ContentUnderstandingSkill(TypedDict):
        key "chunkingProperties": Optional[ContentUnderstandingSkillChunkingProperties]
        key "context": str
        key "description": str
        key "extractionOptions": Optional[list[Union[str, ContentUnderstandingSkillExtractionOptions]]]
        key "name": str
        @odata.type: Required[Literal["#ContentUnderstandingSkill"]]
        chunking_properties: ContentUnderstandingSkillChunkingProperties
        context: str
        description: str
        extraction_options: list[Union[str, ContentUnderstandingSkillExtractionOptions]]
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#ContentUnderstandingSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.ContentUnderstandingSkillChunkingProperties(TypedDict, total=False):
        key "maximumLength": Optional[int]
        key "method": Union[str, ContentUnderstandingSkillChunkingMethod]
        key "overlapLength": Optional[int]
        key "unit": Optional[Union[str, ContentUnderstandingSkillChunkingUnit]]
        maximum_length: int
        method: Union[str, ContentUnderstandingSkillChunkingMethod]
        overlap_length: int
        unit: Union[str, ContentUnderstandingSkillChunkingUnit]


    class azure.search.documents.indexes.types.CorsOptions(TypedDict, total=False):
        key "maxAgeInSeconds": Optional[int]
        allowedOrigins: Required[list[str]]
        allowed_origins: list[str]
        max_age_in_seconds: int


    class azure.search.documents.indexes.types.CreatedResources(TypedDict, total=False):


    class azure.search.documents.indexes.types.CustomAnalyzer(TypedDict):
        key "charFilters": list[Union[str, CharFilterName]]
        key "tokenFilters": list[Union[str, TokenFilterName]]
        @odata.type: Required[Literal["#CustomAnalyzer"]]
        char_filters: list[Union[str, CharFilterName]]
        name: Required[str]
        odata_type: Literal[#CustomAnalyzer]
        token_filters: list[Union[str, TokenFilterName]]
        tokenizer: Required[Union[str, LexicalTokenizerName]]
        tokenizer_name: Union[str, LexicalTokenizerName]


    class azure.search.documents.indexes.types.CustomEntity(TypedDict, total=False):
        key "accentSensitive": Optional[bool]
        key "aliases": Optional[list[CustomEntityAlias]]
        key "caseSensitive": Optional[bool]
        key "defaultAccentSensitive": Optional[bool]
        key "defaultCaseSensitive": Optional[bool]
        key "defaultFuzzyEditDistance": Optional[int]
        key "description": Optional[str]
        key "fuzzyEditDistance": Optional[int]
        key "id": Optional[str]
        key "subtype": Optional[str]
        key "type": Optional[str]
        accent_sensitive: bool
        aliases: list[CustomEntityAlias]
        case_sensitive: bool
        default_accent_sensitive: bool
        default_case_sensitive: bool
        default_fuzzy_edit_distance: int
        description: str
        fuzzy_edit_distance: int
        id: str
        name: Required[str]
        subtype: str
        type: str


    class azure.search.documents.indexes.types.CustomEntityAlias(TypedDict, total=False):
        key "accentSensitive": Optional[bool]
        key "caseSensitive": Optional[bool]
        key "fuzzyEditDistance": Optional[int]
        accent_sensitive: bool
        case_sensitive: bool
        fuzzy_edit_distance: int
        text: Required[str]


    class azure.search.documents.indexes.types.CustomEntityLookupSkill(TypedDict):
        key "context": str
        key "defaultLanguageCode": Optional[Union[str, CustomEntityLookupSkillLanguage]]
        key "description": str
        key "entitiesDefinitionUri": Optional[str]
        key "globalDefaultAccentSensitive": Optional[bool]
        key "globalDefaultCaseSensitive": Optional[bool]
        key "globalDefaultFuzzyEditDistance": Optional[int]
        key "inlineEntitiesDefinition": Optional[list[CustomEntity]]
        key "name": str
        @odata.type: Required[Literal["#CustomEntityLookupSkill"]]
        context: str
        default_language_code: Union[str, CustomEntityLookupSkillLanguage]
        description: str
        entities_definition_uri: str
        global_default_accent_sensitive: bool
        global_default_case_sensitive: bool
        global_default_fuzzy_edit_distance: int
        inline_entities_definition: list[CustomEntity]
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#CustomEntityLookupSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.CustomNormalizer(TypedDict):
        key "charFilters": list[Union[str, CharFilterName]]
        key "tokenFilters": list[Union[str, TokenFilterName]]
        @odata.type: Required[Literal["#CustomNormalizer"]]
        char_filters: list[Union[str, CharFilterName]]
        name: Required[str]
        odata_type: Literal[#CustomNormalizer]
        token_filters: list[Union[str, TokenFilterName]]


    class azure.search.documents.indexes.types.DataSourceCredentials(TypedDict, total=False):
        key "connectionString": str
        connection_string: str


    class azure.search.documents.indexes.types.DefaultCognitiveServicesAccount(TypedDict):
        key "description": str
        @odata.type: Required[Literal["#DefaultCognitiveServices"]]
        description: str
        odata_type: Literal[#DefaultCognitiveServices]


    class azure.search.documents.indexes.types.DictionaryDecompounderTokenFilter(TypedDict):
        key "maxSubwordSize": int
        key "minSubwordSize": int
        key "minWordSize": int
        key "onlyLongestMatch": bool
        @odata.type: Required[Literal["#DictionaryDecompounderTokenFilter"]]
        max_subword_size: int
        min_subword_size: int
        min_word_size: int
        name: Required[str]
        odata_type: Literal[#DictionaryDecompounderTokenFilter]
        only_longest_match: bool
        wordList: Required[list[str]]
        word_list: list[str]


    class azure.search.documents.indexes.types.DistanceScoringFunction(TypedDict, total=False):
        key "interpolation": Union[str, ScoringFunctionInterpolation]
        boost: Required[float]
        distance: Required[DistanceScoringParameters]
        fieldName: Required[str]
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: DistanceScoringParameters
        type: Required[Literal["distance"]]


    class azure.search.documents.indexes.types.DistanceScoringParameters(TypedDict, total=False):
        boostingDistance: Required[float]
        boosting_distance: float
        referencePointParameter: Required[str]
        reference_point_parameter: str


    class azure.search.documents.indexes.types.DocumentExtractionSkill(TypedDict):
        key "configuration": Optional[dict[str, Any]]
        key "context": str
        key "dataToExtract": Optional[str]
        key "description": str
        key "name": str
        key "parsingMode": Optional[str]
        @odata.type: Required[Literal["#DocumentExtractionSkill"]]
        configuration: dict[str, Any]
        context: str
        data_to_extract: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#DocumentExtractionSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        parsing_mode: str


    class azure.search.documents.indexes.types.DocumentIntelligenceLayoutSkill(TypedDict):
        key "chunkingProperties": Optional[DocumentIntelligenceLayoutSkillChunkingProperties]
        key "context": str
        key "description": str
        key "extractionOptions": Optional[list[Union[str, DocumentIntelligenceLayoutSkillExtractionOptions]]]
        key "markdownHeaderDepth": Optional[Union[str, DocumentIntelligenceLayoutSkillMarkdownHeaderDepth]]
        key "name": str
        key "outputFormat": Optional[Union[str, DocumentIntelligenceLayoutSkillOutputFormat]]
        key "outputMode": Optional[Union[str, DocumentIntelligenceLayoutSkillOutputMode]]
        @odata.type: Required[Literal["#DocumentIntelligenceLayoutSkill"]]
        chunking_properties: DocumentIntelligenceLayoutSkillChunkingProperties
        context: str
        description: str
        extraction_options: list[Union[str, DocumentIntelligenceLayoutSkillExtractionOptions]]
        inputs: Required[list[InputFieldMappingEntry]]
        markdown_header_depth: Union[str, DocumentIntelligenceLayoutSkillMarkdownHeaderDepth]
        name: str
        odata_type: Literal[#DocumentIntelligenceLayoutSkill]
        output_format: Union[str, DocumentIntelligenceLayoutSkillOutputFormat]
        output_mode: Union[str, DocumentIntelligenceLayoutSkillOutputMode]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.DocumentIntelligenceLayoutSkillChunkingProperties(TypedDict, total=False):
        key "maximumLength": Optional[int]
        key "overlapLength": Optional[int]
        key "unit": Optional[Union[str, DocumentIntelligenceLayoutSkillChunkingUnit]]
        maximum_length: int
        overlap_length: int
        unit: Union[str, DocumentIntelligenceLayoutSkillChunkingUnit]


    class azure.search.documents.indexes.types.DocumentKeysOrIds(TypedDict, total=False):
        key "datasourceDocumentIds": list[str]
        key "documentKeys": list[str]
        datasource_document_ids: list[str]
        document_keys: list[str]


    class azure.search.documents.indexes.types.EdgeNGramTokenFilter(TypedDict):
        key "maxGram": int
        key "minGram": int
        key "side": Union[str, EdgeNGramTokenFilterSide]
        @odata.type: Required[Literal["#EdgeNGramTokenFilter"]]
        max_gram: int
        min_gram: int
        name: Required[str]
        odata_type: Literal[#EdgeNGramTokenFilter]
        side: Union[str, EdgeNGramTokenFilterSide]


    class azure.search.documents.indexes.types.EdgeNGramTokenFilterV2(TypedDict):
        key "maxGram": int
        key "minGram": int
        key "side": Union[str, EdgeNGramTokenFilterSide]
        @odata.type: Required[Literal["#EdgeNGramTokenFilterV2"]]
        max_gram: int
        min_gram: int
        name: Required[str]
        odata_type: Literal[#EdgeNGramTokenFilterV2]
        side: Union[str, EdgeNGramTokenFilterSide]


    class azure.search.documents.indexes.types.EdgeNGramTokenizer(TypedDict):
        key "maxGram": int
        key "minGram": int
        key "tokenChars": list[Union[str, TokenCharacterKind]]
        @odata.type: Required[Literal["#EdgeNGramTokenizer"]]
        max_gram: int
        min_gram: int
        name: Required[str]
        odata_type: Literal[#EdgeNGramTokenizer]
        token_chars: list[Union[str, TokenCharacterKind]]


    class azure.search.documents.indexes.types.ElisionTokenFilter(TypedDict):
        key "articles": list[str]
        @odata.type: Required[Literal["#ElisionTokenFilter"]]
        articles: list[str]
        name: Required[str]
        odata_type: Literal[#ElisionTokenFilter]


    class azure.search.documents.indexes.types.EmbeddingColumnMapping(TypedDict, total=False):
        name: Required[str]
        sourceField: Required[str]
        source_field: str


    class azure.search.documents.indexes.types.EntityLinkingSkill(TypedDict):
        key "context": str
        key "defaultLanguageCode": Optional[str]
        key "description": str
        key "minimumPrecision": float
        key "modelVersion": Optional[str]
        key "name": str
        @odata.type: Required[Literal["#EntityLinkingSkill"]]
        context: str
        default_language_code: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        minimum_precision: float
        model_version: str
        name: str
        odata_type: Literal[#EntityLinkingSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.EntityRecognitionSkillV3(TypedDict):
        key "categories": list[Union[str, EntityCategory]]
        key "context": str
        key "defaultLanguageCode": Optional[Union[str, EntityRecognitionSkillLanguage]]
        key "description": str
        key "minimumPrecision": float
        key "modelVersion": Optional[str]
        key "name": str
        @odata.type: Required[Literal["#EntityRecognitionSkill"]]
        categories: list[Union[str, EntityCategory]]
        context: str
        default_language_code: Union[str, EntityRecognitionSkillLanguage]
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        minimum_precision: float
        model_version: str
        name: str
        odata_type: Literal[#EntityRecognitionSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.EntraAppAuthentication(TypedDict, total=False):
        key "tenantId": str
        applicationId: Required[str]
        application_id: str
        federatedCredentialId: Required[str]
        federated_credential_id: str
        tenant_id: str


    class azure.search.documents.indexes.types.ExhaustiveKnnAlgorithmConfiguration(TypedDict, total=False):
        key "exhaustiveKnnParameters": ForwardRef('ExhaustiveKnnParameters')
        kind: Required[Literal[VectorSearchAlgorithmKind.EXHAUSTIVE_KNN]]
        name: Required[str]
        parameters: ExhaustiveKnnParameters


    class azure.search.documents.indexes.types.ExhaustiveKnnParameters(TypedDict, total=False):
        key "metric": Optional[Union[str, VectorSearchAlgorithmMetric]]
        metric: Union[str, VectorSearchAlgorithmMetric]


    class azure.search.documents.indexes.types.FabricDataAgentKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        fabricDataAgentParameters: Required[FabricDataAgentKnowledgeSourceParameters]
        fabric_data_agent_parameters: FabricDataAgentKnowledgeSourceParameters
        kind: Required[Literal[KnowledgeSourceKind.FABRIC_DATA_AGENT]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.FabricDataAgentKnowledgeSourceParameters(TypedDict, total=False):
        dataAgentId: Required[str]
        data_agent_id: str
        workspaceId: Required[str]
        workspace_id: str


    class azure.search.documents.indexes.types.FabricOntologyKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        fabricOntologyParameters: Required[FabricOntologyKnowledgeSourceParameters]
        fabric_ontology_parameters: FabricOntologyKnowledgeSourceParameters
        kind: Required[Literal[KnowledgeSourceKind.FABRIC_ONTOLOGY]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.FabricOntologyKnowledgeSourceParameters(TypedDict, total=False):
        ontologyId: Required[str]
        ontology_id: str
        workspaceId: Required[str]
        workspace_id: str


    class azure.search.documents.indexes.types.FieldMapping(TypedDict, total=False):
        key "mappingFunction": Optional[FieldMappingFunction]
        key "targetFieldName": str
        mapping_function: FieldMappingFunction
        sourceFieldName: Required[str]
        source_field_name: str
        target_field_name: str


    class azure.search.documents.indexes.types.FieldMappingFunction(TypedDict, total=False):
        key "parameters": Optional[dict[str, Any]]
        name: Required[str]
        parameters: dict[str, Any]


    class azure.search.documents.indexes.types.FileKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "corsOptions": ForwardRef('CorsOptions')
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        cors_options: CorsOptions
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        fileParameters: Required[FileKnowledgeSourceParameters]
        file_parameters: FileKnowledgeSourceParameters
        kind: Required[Literal[KnowledgeSourceKind.FILE]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.FileKnowledgeSourceParameters(TypedDict, total=False):
        key "createdResources": ForwardRef('CreatedResources')
        key "ingestionParameters": ForwardRef('KnowledgeSourceIngestionParameters')
        key "queryHints": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        created_resources: CreatedResources
        ingestion_parameters: KnowledgeSourceIngestionParameters
        query_hints: SearchIndexKnowledgeSourceQueryHints


    class azure.search.documents.indexes.types.FileUploadMetadata(TypedDict, total=False):
        key "fileName": str
        key "metadata": dict[str, str]
        file_name: str
        metadata: dict[str, str]


    class azure.search.documents.indexes.types.FreshnessScoringFunction(TypedDict, total=False):
        key "interpolation": Union[str, ScoringFunctionInterpolation]
        boost: Required[float]
        fieldName: Required[str]
        field_name: str
        freshness: Required[FreshnessScoringParameters]
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: FreshnessScoringParameters
        type: Required[Literal["freshness"]]


    class azure.search.documents.indexes.types.FreshnessScoringParameters(TypedDict, total=False):
        boostingDuration: Required[str]
        boosting_duration: str


    class azure.search.documents.indexes.types.GetIndexStatisticsResult(TypedDict, total=False):
        documentCount: Required[int]
        document_count: int
        storageSize: Required[int]
        storage_size: int
        vectorIndexSize: Required[int]
        vector_index_size: int


    class azure.search.documents.indexes.types.HighWaterMarkChangeDetectionPolicy(TypedDict):
        @odata.type: Required[Literal["#HighWaterMarkChangeDetectionPolicy"]]
        highWaterMarkColumnName: Required[str]
        high_water_mark_column_name: str
        odata_type: Literal[#HighWaterMarkChangeDetectionPolicy]


    class azure.search.documents.indexes.types.HnswAlgorithmConfiguration(TypedDict, total=False):
        key "hnswParameters": ForwardRef('HnswParameters')
        kind: Required[Literal[VectorSearchAlgorithmKind.HNSW]]
        name: Required[str]
        parameters: HnswParameters


    class azure.search.documents.indexes.types.HnswParameters(TypedDict, total=False):
        key "efConstruction": int
        key "efSearch": int
        key "m": int
        key "metric": Optional[Union[str, VectorSearchAlgorithmMetric]]
        ef_construction: int
        ef_search: int
        m: int
        metric: Union[str, VectorSearchAlgorithmMetric]


    class azure.search.documents.indexes.types.ImageAnalysisSkill(TypedDict):
        key "context": str
        key "defaultLanguageCode": Union[str, ImageAnalysisSkillLanguage]
        key "description": str
        key "details": list[Union[str, ImageDetail]]
        key "name": str
        key "visualFeatures": list[Union[str, VisualFeature]]
        @odata.type: Required[Literal["#ImageAnalysisSkill"]]
        context: str
        default_language_code: Union[str, ImageAnalysisSkillLanguage]
        description: str
        details: list[Union[str, ImageDetail]]
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#ImageAnalysisSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        visual_features: list[Union[str, VisualFeature]]


    class azure.search.documents.indexes.types.IndexedOneLakeKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexedOneLakeParameters: Required[IndexedOneLakeKnowledgeSourceParameters]
        indexed_one_lake_parameters: IndexedOneLakeKnowledgeSourceParameters
        kind: Required[Literal[KnowledgeSourceKind.INDEXED_ONELAKE]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.IndexedOneLakeKnowledgeSourceParameters(TypedDict, total=False):
        key "createdResources": ForwardRef('CreatedResources')
        key "ingestionParameters": ForwardRef('KnowledgeSourceIngestionParameters')
        key "queryHints": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "targetPath": Optional[str]
        created_resources: CreatedResources
        fabricWorkspaceId: Required[str]
        fabric_workspace_id: str
        ingestion_parameters: KnowledgeSourceIngestionParameters
        lakehouseId: Required[str]
        lakehouse_id: str
        query_hints: SearchIndexKnowledgeSourceQueryHints
        target_path: str


    class azure.search.documents.indexes.types.IndexedSharePointKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexedSharePointParameters: Required[IndexedSharePointKnowledgeSourceParameters]
        indexed_share_point_parameters: IndexedSharePointKnowledgeSourceParameters
        kind: Required[Literal[KnowledgeSourceKind.INDEXED_SHARE_POINT]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.IndexedSharePointKnowledgeSourceParameters(TypedDict, total=False):
        key "createdResources": ForwardRef('CreatedResources')
        key "ingestionParameters": Optional[KnowledgeSourceIngestionParameters]
        key "query": Optional[str]
        key "queryHints": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        connectionString: Required[str]
        connection_string: str
        containerName: Required[Union[str, IndexedSharePointContainerName]]
        container_name: Union[str, IndexedSharePointContainerName]
        created_resources: CreatedResources
        ingestion_parameters: KnowledgeSourceIngestionParameters
        query: str
        query_hints: SearchIndexKnowledgeSourceQueryHints


    class azure.search.documents.indexes.types.IndexedSqlKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexedSqlParameters: Required[IndexedSqlKnowledgeSourceParameters]
        indexed_sql_parameters: IndexedSqlKnowledgeSourceParameters
        kind: Required[Literal[KnowledgeSourceKind.INDEXED_SQL]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.IndexedSqlKnowledgeSourceParameters(TypedDict, total=False):
        key "contentColumns": list[ContentColumnMapping]
        key "createdResources": ForwardRef('CreatedResources')
        key "embeddingColumns": list[EmbeddingColumnMapping]
        key "highWaterMarkColumnName": str
        key "ingestionParameters": ForwardRef('KnowledgeSourceIngestionParameters')
        key "queryHints": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        connectionString: Required[str]
        connection_string: str
        content_columns: list[ContentColumnMapping]
        created_resources: CreatedResources
        embedding_columns: list[EmbeddingColumnMapping]
        high_water_mark_column_name: str
        ingestion_parameters: KnowledgeSourceIngestionParameters
        query_hints: SearchIndexKnowledgeSourceQueryHints
        tableOrView: Required[str]
        table_or_view: str


    class azure.search.documents.indexes.types.IndexerResyncBody(TypedDict, total=False):
        key "options": Optional[list[Union[str, IndexerResyncOption]]]
        options: list[Union[str, IndexerResyncOption]]


    class azure.search.documents.indexes.types.IndexingParameters(TypedDict, total=False):
        key "batchSize": Optional[int]
        key "configuration": ForwardRef('IndexingParametersConfiguration')
        key "maxFailedItems": Optional[int]
        key "maxFailedItemsPerBatch": Optional[int]
        batch_size: int
        configuration: IndexingParametersConfiguration
        max_failed_items: int
        max_failed_items_per_batch: int


    class azure.search.documents.indexes.types.IndexingParametersConfiguration(TypedDict, total=False):
        key "allowSkillsetToReadFileData": bool
        key "dataToExtract": Union[str, BlobIndexerDataToExtract]
        key "delimitedTextDelimiter": str
        key "delimitedTextHeaders": str
        key "documentRoot": str
        key "excludedFileNameExtensions": str
        key "executionEnvironment": Union[str, IndexerExecutionEnvironment]
        key "failOnUnprocessableDocument": bool
        key "failOnUnsupportedContentType": bool
        key "firstLineContainsHeaders": bool
        key "imageAction": Union[str, BlobIndexerImageAction]
        key "indexStorageMetadataOnlyForOversizedDocuments": bool
        key "indexedFileNameExtensions": str
        key "markdownHeaderDepth": Optional[Union[str, MarkdownHeaderDepth]]
        key "markdownParsingSubmode": Optional[Union[str, MarkdownParsingSubmode]]
        key "parsingMode": Union[str, BlobIndexerParsingMode]
        key "pdfTextRotationAlgorithm": Union[str, BlobIndexerPDFTextRotationAlgorithm]
        key "queryTimeout": str
        allow_skillset_to_read_file_data: bool
        data_to_extract: Union[str, BlobIndexerDataToExtract]
        delimited_text_delimiter: str
        delimited_text_headers: str
        document_root: str
        excluded_file_name_extensions: str
        execution_environment: Union[str, IndexerExecutionEnvironment]
        fail_on_unprocessable_document: bool
        fail_on_unsupported_content_type: bool
        first_line_contains_headers: bool
        image_action: Union[str, BlobIndexerImageAction]
        index_storage_metadata_only_for_oversized_documents: bool
        indexed_file_name_extensions: str
        markdown_header_depth: Union[str, MarkdownHeaderDepth]
        markdown_parsing_submode: Union[str, MarkdownParsingSubmode]
        parsing_mode: Union[str, BlobIndexerParsingMode]
        pdf_text_rotation_algorithm: Union[str, BlobIndexerPDFTextRotationAlgorithm]
        query_timeout: str


    class azure.search.documents.indexes.types.IndexingSchedule(TypedDict, total=False):
        key "startTime": str
        interval: Required[str]
        start_time: str


    class azure.search.documents.indexes.types.InputFieldMappingEntry(TypedDict, total=False):
        key "inputs": list[InputFieldMappingEntry]
        key "source": str
        key "sourceContext": str
        inputs: list[InputFieldMappingEntry]
        name: Required[str]
        source: str
        source_context: str


    class azure.search.documents.indexes.types.KeepTokenFilter(TypedDict):
        key "keepWordsCase": bool
        @odata.type: Required[Literal["#KeepTokenFilter"]]
        keepWords: Required[list[str]]
        keep_words: list[str]
        lower_case_keep_words: bool
        name: Required[str]
        odata_type: Literal[#KeepTokenFilter]


    class azure.search.documents.indexes.types.KeyPhraseExtractionSkill(TypedDict):
        key "context": str
        key "defaultLanguageCode": Union[str, KeyPhraseExtractionSkillLanguage]
        key "description": str
        key "maxKeyPhraseCount": Optional[int]
        key "modelVersion": Optional[str]
        key "name": str
        @odata.type: Required[Literal["#KeyPhraseExtractionSkill"]]
        context: str
        default_language_code: Union[str, KeyPhraseExtractionSkillLanguage]
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        max_key_phrase_count: int
        model_version: str
        name: str
        odata_type: Literal[#KeyPhraseExtractionSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.KeywordMarkerTokenFilter(TypedDict):
        key "ignoreCase": bool
        @odata.type: Required[Literal["#KeywordMarkerTokenFilter"]]
        ignore_case: bool
        keywords: Required[list[str]]
        name: Required[str]
        odata_type: Literal[#KeywordMarkerTokenFilter]


    class azure.search.documents.indexes.types.KeywordTokenizer(TypedDict):
        key "bufferSize": int
        @odata.type: Required[Literal["#KeywordTokenizer"]]
        buffer_size: int
        name: Required[str]
        odata_type: Literal[#KeywordTokenizer]


    class azure.search.documents.indexes.types.KeywordTokenizerV2(TypedDict):
        key "maxTokenLength": int
        @odata.type: Required[Literal["#KeywordTokenizerV2"]]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#KeywordTokenizerV2]


    class azure.search.documents.indexes.types.KnowledgeBase(TypedDict):
        key "@odata.etag": str
        key "answerInstructions": str
        key "corsOptions": ForwardRef('CorsOptions')
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "models": list[KnowledgeBaseModel]
        key "outputMode": Union[str, KnowledgeRetrievalOutputMode]
        key "retrievalInstructions": str
        key "retrievalReasoningEffort": ForwardRef('KnowledgeRetrievalReasoningEffort')
        key "retrieveDefaults": ForwardRef('KnowledgeBaseRetrieveDefaults')
        key "tags": dict[str, str]
        answer_instructions: str
        cors_options: CorsOptions
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        knowledgeSources: Required[list[KnowledgeSourceReference]]
        knowledge_sources: list[KnowledgeSourceReference]
        models: list[KnowledgeBaseModel]
        name: Required[str]
        output_mode: Union[str, KnowledgeRetrievalOutputMode]
        retrieval_instructions: str
        retrieval_reasoning_effort: KnowledgeRetrievalReasoningEffort
        retrieve_defaults: KnowledgeBaseRetrieveDefaults
        tags: dict[str, str]


    class azure.search.documents.indexes.types.KnowledgeBaseAzureOpenAIModel(TypedDict, total=False):
        azureOpenAIParameters: Required[AzureOpenAIVectorizerParameters]
        azure_open_ai_parameters: AzureOpenAIVectorizerParameters
        kind: Required[Literal[KnowledgeBaseModelKind.AZURE_OPEN_AI]]


    class azure.search.documents.indexes.types.KnowledgeBaseModel(TypedDict, total=False):
        azureOpenAIParameters: Required[AzureOpenAIVectorizerParameters]
        azure_open_ai_parameters: AzureOpenAIVectorizerParameters
        kind: Required[Literal[KnowledgeBaseModelKind.AZURE_OPEN_AI]]


    class azure.search.documents.indexes.types.KnowledgeBaseModelKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_OPEN_AI = "azureOpenAI"


    class azure.search.documents.indexes.types.KnowledgeBaseRetrieveDefaults(TypedDict, total=False):
        key "maxOutputDocuments": int
        key "maxOutputSizeInTokens": int
        key "maxRuntimeInSeconds": int
        max_output_documents: int
        max_output_size_in_tokens: int
        max_runtime_in_seconds: int


    class azure.search.documents.indexes.types.KnowledgeSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "azureBlob"
        FABRIC_DATA_AGENT = "fabricDataAgent"
        FABRIC_ONTOLOGY = "fabricOntology"
        FILE = "file"
        INDEXED_ONELAKE = "indexedOneLake"
        INDEXED_SHARE_POINT = "indexedSharePoint"
        INDEXED_SQL = "indexedSql"
        MCP_SERVER = "mcpServer"
        REMOTE_SHARE_POINT = "remoteSharePoint"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"
        WORK_IQ = "workIQ"


    class azure.search.documents.indexes.types.KnowledgeSourceReference(TypedDict, total=False):
        key "enableFreshness": bool
        key "enableImageServing": bool
        enable_freshness: bool
        enable_image_serving: bool
        name: Required[str]


    class azure.search.documents.indexes.types.LanguageDetectionSkill(TypedDict):
        key "context": str
        key "defaultCountryHint": Optional[str]
        key "description": str
        key "modelVersion": Optional[str]
        key "name": str
        @odata.type: Required[Literal["#LanguageDetectionSkill"]]
        context: str
        default_country_hint: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        model_version: str
        name: str
        odata_type: Literal[#LanguageDetectionSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.LengthTokenFilter(TypedDict):
        key "max": int
        key "min": int
        @odata.type: Required[Literal["#LengthTokenFilter"]]
        max_length: int
        min_length: int
        name: Required[str]
        odata_type: Literal[#LengthTokenFilter]


    class azure.search.documents.indexes.types.LexicalNormalizer(TypedDict):
        key "charFilters": list[Union[str, CharFilterName]]
        key "tokenFilters": list[Union[str, TokenFilterName]]
        @odata.type: Required[Literal["#CustomNormalizer"]]
        char_filters: list[Union[str, CharFilterName]]
        name: Required[str]
        odata_type: Literal[#CustomNormalizer]
        token_filters: list[Union[str, TokenFilterName]]


    class azure.search.documents.indexes.types.LimitTokenFilter(TypedDict):
        key "consumeAllTokens": bool
        key "maxTokenCount": int
        @odata.type: Required[Literal["#LimitTokenFilter"]]
        consume_all_tokens: bool
        max_token_count: int
        name: Required[str]
        odata_type: Literal[#LimitTokenFilter]


    class azure.search.documents.indexes.types.LuceneStandardAnalyzer(TypedDict):
        key "maxTokenLength": int
        key "stopwords": list[str]
        @odata.type: Required[Literal["#StandardAnalyzer"]]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#StandardAnalyzer]
        stopwords: list[str]


    class azure.search.documents.indexes.types.LuceneStandardTokenizer(TypedDict):
        key "maxTokenLength": int
        @odata.type: Required[Literal["#StandardTokenizer"]]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#StandardTokenizer]


    class azure.search.documents.indexes.types.LuceneStandardTokenizerV2(TypedDict):
        key "maxTokenLength": int
        @odata.type: Required[Literal["#StandardTokenizerV2"]]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#StandardTokenizerV2]


    class azure.search.documents.indexes.types.MagnitudeScoringFunction(TypedDict, total=False):
        key "interpolation": Union[str, ScoringFunctionInterpolation]
        boost: Required[float]
        fieldName: Required[str]
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        magnitude: Required[MagnitudeScoringParameters]
        parameters: MagnitudeScoringParameters
        type: Required[Literal["magnitude"]]


    class azure.search.documents.indexes.types.MagnitudeScoringParameters(TypedDict, total=False):
        key "constantBoostBeyondRange": bool
        boostingRangeEnd: Required[float]
        boostingRangeStart: Required[float]
        boosting_range_end: float
        boosting_range_start: float
        should_boost_beyond_range_by_constant: bool


    class azure.search.documents.indexes.types.MappingCharFilter(TypedDict):
        @odata.type: Required[Literal["#MappingCharFilter"]]
        mappings: Required[list[str]]
        name: Required[str]
        odata_type: Literal[#MappingCharFilter]


    class azure.search.documents.indexes.types.McpServerAuthenticationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUNDRY_CONNECTION = "foundryConnection"
        STORED_HEADERS = "storedHeaders"


    class azure.search.documents.indexes.types.McpServerAutoOutputParsing(TypedDict, total=False):
        kind: Required[Literal[McpServerOutputParsingKind.AUTO]]


    class azure.search.documents.indexes.types.McpServerFoundryConnectionAuthentication(TypedDict, total=False):
        foundryConnectionParameters: Required[McpServerFoundryConnectionParameters]
        foundry_connection_parameters: McpServerFoundryConnectionParameters
        kind: Required[Literal[McpServerAuthenticationKind.FOUNDRY_CONNECTION]]


    class azure.search.documents.indexes.types.McpServerFoundryConnectionParameters(TypedDict, total=False):
        key "connectionId": str
        connection_id: str


    class azure.search.documents.indexes.types.McpServerHeaders(TypedDict, total=False):


    class azure.search.documents.indexes.types.McpServerJsonOutputParsing(TypedDict, total=False):
        jsonParameters: Required[McpServerOutputParsingJsonParameters]
        json_parameters: McpServerOutputParsingJsonParameters
        kind: Required[Literal[McpServerOutputParsingKind.JSON]]


    class azure.search.documents.indexes.types.McpServerKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Required[Literal[KnowledgeSourceKind.MCP_SERVER]]
        mcpServerParameters: Required[McpServerKnowledgeSourceParameters]
        mcp_server_parameters: McpServerKnowledgeSourceParameters
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.McpServerKnowledgeSourceParameters(TypedDict, total=False):
        key "authentication": ForwardRef('McpServerAuthentication')
        authentication: McpServerAuthentication
        serverURL: Required[str]
        server_url: str
        tools: Required[list[McpServerTool]]


    class azure.search.documents.indexes.types.McpServerNoneOutputParsing(TypedDict, total=False):
        kind: Required[Literal[McpServerOutputParsingKind.NONE]]


    class azure.search.documents.indexes.types.McpServerOutputParsingJsonParameters(TypedDict, total=False):
        key "includeContext": bool
        documentsPath: Required[str]
        documents_path: str
        include_context: bool


    class azure.search.documents.indexes.types.McpServerOutputParsingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        JSON = "json"
        NONE = "none"
        SPLIT = "split"


    class azure.search.documents.indexes.types.McpServerOutputParsingSplitParameters(TypedDict, total=False):
        key "defaultLanguageCode": Union[str, SplitSkillLanguage]
        key "maximumPageLength": int
        key "maximumPagesToTake": int
        key "pageOverlapLength": int
        key "textSplitMode": Union[str, TextSplitMode]
        default_language_code: Union[str, SplitSkillLanguage]
        maximum_page_length: int
        maximum_pages_to_take: int
        page_overlap_length: int
        text_split_mode: Union[str, TextSplitMode]


    class azure.search.documents.indexes.types.McpServerSplitOutputParsing(TypedDict, total=False):
        key "splitParameters": ForwardRef('McpServerOutputParsingSplitParameters')
        kind: Required[Literal[McpServerOutputParsingKind.SPLIT]]
        split_parameters: McpServerOutputParsingSplitParameters


    class azure.search.documents.indexes.types.McpServerStoredHeadersAuthentication(TypedDict, total=False):
        kind: Required[Literal[McpServerAuthenticationKind.STORED_HEADERS]]
        storedHeadersParameters: Required[McpServerStoredHeadersParameters]
        stored_headers_parameters: McpServerStoredHeadersParameters


    class azure.search.documents.indexes.types.McpServerStoredHeadersParameters(TypedDict, total=False):
        key "headers": ForwardRef('McpServerHeaders')
        headers: McpServerHeaders


    class azure.search.documents.indexes.types.McpServerTool(TypedDict, total=False):
        key "maxOutputTokens": int
        key "name": str
        key "outputParsing": ForwardRef('McpServerOutputParsing')
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        max_output_tokens: int
        name: str
        output_parsing: McpServerOutputParsing
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.MergeSkill(TypedDict):
        key "context": str
        key "description": str
        key "insertPostTag": str
        key "insertPreTag": str
        key "name": str
        @odata.type: Required[Literal["#MergeSkill"]]
        context: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        insert_post_tag: str
        insert_pre_tag: str
        name: str
        odata_type: Literal[#MergeSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.MicrosoftLanguageStemmingTokenizer(TypedDict):
        key "isSearchTokenizer": bool
        key "language": Union[str, MicrosoftStemmingTokenizerLanguage]
        key "maxTokenLength": int
        @odata.type: Required[Literal["#MicrosoftLanguageStemmingTokenizer"]]
        is_search_tokenizer: bool
        language: Union[str, MicrosoftStemmingTokenizerLanguage]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#MicrosoftLanguageStemmingTokenizer]


    class azure.search.documents.indexes.types.MicrosoftLanguageTokenizer(TypedDict):
        key "isSearchTokenizer": bool
        key "language": Union[str, MicrosoftTokenizerLanguage]
        key "maxTokenLength": int
        @odata.type: Required[Literal["#MicrosoftLanguageTokenizer"]]
        is_search_tokenizer: bool
        language: Union[str, MicrosoftTokenizerLanguage]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#MicrosoftLanguageTokenizer]


    class azure.search.documents.indexes.types.NGramTokenFilter(TypedDict):
        key "maxGram": int
        key "minGram": int
        @odata.type: Required[Literal["#NGramTokenFilter"]]
        max_gram: int
        min_gram: int
        name: Required[str]
        odata_type: Literal[#NGramTokenFilter]


    class azure.search.documents.indexes.types.NGramTokenFilterV2(TypedDict):
        key "maxGram": int
        key "minGram": int
        @odata.type: Required[Literal["#NGramTokenFilterV2"]]
        max_gram: int
        min_gram: int
        name: Required[str]
        odata_type: Literal[#NGramTokenFilterV2]


    class azure.search.documents.indexes.types.NGramTokenizer(TypedDict):
        key "maxGram": int
        key "minGram": int
        key "tokenChars": list[Union[str, TokenCharacterKind]]
        @odata.type: Required[Literal["#NGramTokenizer"]]
        max_gram: int
        min_gram: int
        name: Required[str]
        odata_type: Literal[#NGramTokenizer]
        token_chars: list[Union[str, TokenCharacterKind]]


    class azure.search.documents.indexes.types.NativeBlobSoftDeleteDeletionDetectionPolicy(TypedDict):
        @odata.type: Required[Literal["#NativeBlobSoftDeleteDeletionDetectionPolicy"]]
        odata_type: Literal[#NativeBlobSoftDeleteDeletionDetectionPolicy]


    class azure.search.documents.indexes.types.OcrSkill(TypedDict):
        key "context": str
        key "defaultLanguageCode": Union[str, OcrSkillLanguage]
        key "description": str
        key "detectOrientation": bool
        key "lineEnding": Union[str, OcrLineEnding]
        key "name": str
        @odata.type: Required[Literal["#OcrSkill"]]
        context: str
        default_language_code: Union[str, OcrSkillLanguage]
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        line_ending: Union[str, OcrLineEnding]
        name: str
        odata_type: Literal[#OcrSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        should_detect_orientation: bool


    class azure.search.documents.indexes.types.OutputFieldMappingEntry(TypedDict, total=False):
        key "targetName": str
        name: Required[str]
        target_name: str


    class azure.search.documents.indexes.types.PIIDetectionSkill(TypedDict):
        key "context": str
        key "defaultLanguageCode": Optional[str]
        key "description": str
        key "domain": Optional[str]
        key "maskingCharacter": str
        key "maskingMode": Union[str, PIIDetectionSkillMaskingMode]
        key "minimumPrecision": float
        key "modelVersion": Optional[str]
        key "name": str
        key "piiCategories": list[str]
        @odata.type: Required[Literal["#PIIDetectionSkill"]]
        context: str
        default_language_code: str
        description: str
        domain: str
        inputs: Required[list[InputFieldMappingEntry]]
        mask: str
        masking_mode: Union[str, PIIDetectionSkillMaskingMode]
        minimum_precision: float
        model_version: str
        name: str
        odata_type: Literal[#PIIDetectionSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        pii_categories: list[str]


    class azure.search.documents.indexes.types.PathHierarchyTokenizerV2(TypedDict):
        key "delimiter": str
        key "maxTokenLength": int
        key "replacement": str
        key "reverse": bool
        key "skip": int
        @odata.type: Required[Literal["#PathHierarchyTokenizerV2"]]
        delimiter: str
        max_token_length: int
        name: Required[str]
        number_of_tokens_to_skip: int
        odata_type: Literal[#PathHierarchyTokenizerV2]
        replacement: str
        reverse_token_order: bool


    class azure.search.documents.indexes.types.PatternAnalyzer(TypedDict):
        key "flags": list[Union[str, RegexFlags]]
        key "lowercase": bool
        key "pattern": str
        key "stopwords": list[str]
        @odata.type: Required[Literal["#PatternAnalyzer"]]
        flags: list[Union[str, RegexFlags]]
        lower_case_terms: bool
        name: Required[str]
        odata_type: Literal[#PatternAnalyzer]
        pattern: str
        stopwords: list[str]


    class azure.search.documents.indexes.types.PatternCaptureTokenFilter(TypedDict):
        key "preserveOriginal": bool
        @odata.type: Required[Literal["#PatternCaptureTokenFilter"]]
        name: Required[str]
        odata_type: Literal[#PatternCaptureTokenFilter]
        patterns: Required[list[str]]
        preserve_original: bool


    class azure.search.documents.indexes.types.PatternReplaceCharFilter(TypedDict):
        @odata.type: Required[Literal["#PatternReplaceCharFilter"]]
        name: Required[str]
        odata_type: Literal[#PatternReplaceCharFilter]
        pattern: Required[str]
        replacement: Required[str]


    class azure.search.documents.indexes.types.PatternReplaceTokenFilter(TypedDict):
        @odata.type: Required[Literal["#PatternReplaceTokenFilter"]]
        name: Required[str]
        odata_type: Literal[#PatternReplaceTokenFilter]
        pattern: Required[str]
        replacement: Required[str]


    class azure.search.documents.indexes.types.PatternTokenizer(TypedDict):
        key "flags": list[Union[str, RegexFlags]]
        key "group": int
        key "pattern": str
        @odata.type: Required[Literal["#PatternTokenizer"]]
        flags: list[Union[str, RegexFlags]]
        group: int
        name: Required[str]
        odata_type: Literal[#PatternTokenizer]
        pattern: str


    class azure.search.documents.indexes.types.PhoneticTokenFilter(TypedDict):
        key "encoder": Union[str, PhoneticEncoder]
        key "replace": bool
        @odata.type: Required[Literal["#PhoneticTokenFilter"]]
        encoder: Union[str, PhoneticEncoder]
        name: Required[str]
        odata_type: Literal[#PhoneticTokenFilter]
        replace_original_tokens: bool


    class azure.search.documents.indexes.types.RemoteSharePointKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "remoteSharePointParameters": ForwardRef('RemoteSharePointKnowledgeSourceParameters')
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Required[Literal[KnowledgeSourceKind.REMOTE_SHARE_POINT]]
        name: Required[str]
        remote_share_point_parameters: RemoteSharePointKnowledgeSourceParameters
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.indexes.types.RemoteSharePointKnowledgeSourceParameters(TypedDict, total=False):
        key "containerTypeId": str
        key "filterExpression": str
        key "resourceMetadata": list[str]
        container_type_id: str
        filter_expression: str
        resource_metadata: list[str]


    class azure.search.documents.indexes.types.RescoringOptions(TypedDict, total=False):
        key "defaultOversampling": Optional[float]
        key "enableRescoring": Optional[bool]
        key "rescoreStorageMethod": Optional[Union[str, VectorSearchCompressionRescoreStorageMethod]]
        default_oversampling: float
        enable_rescoring: bool
        rescore_storage_method: Union[str, VectorSearchCompressionRescoreStorageMethod]


    class azure.search.documents.indexes.types.ScalarQuantizationCompression(TypedDict, total=False):
        key "rescoringOptions": Optional[RescoringOptions]
        key "scalarQuantizationParameters": ForwardRef('ScalarQuantizationParameters')
        key "truncationDimension": Optional[int]
        compression_name: str
        kind: Required[Literal[VectorSearchCompressionKind.SCALAR_QUANTIZATION]]
        name: Required[str]
        parameters: ScalarQuantizationParameters
        rescoring_options: RescoringOptions
        truncation_dimension: int


    class azure.search.documents.indexes.types.ScalarQuantizationParameters(TypedDict, total=False):
        key "quantizedDataType": Optional[Union[str, VectorSearchCompressionTarget]]
        quantized_data_type: Union[str, VectorSearchCompressionTarget]


    class azure.search.documents.indexes.types.ScoringProfile(TypedDict, total=False):
        key "functionAggregation": Union[str, ScoringFunctionAggregation]
        key "functions": list[ScoringFunction]
        key "text": Optional[TextWeights]
        function_aggregation: Union[str, ScoringFunctionAggregation]
        functions: list[ScoringFunction]
        name: Required[str]
        text_weights: TextWeights


    class azure.search.documents.indexes.types.SearchAlias(TypedDict):
        key "@odata.etag": str
        e_tag: str
        indexes: Required[list[str]]
        name: Required[str]


    class azure.search.documents.indexes.types.SearchField(TypedDict, total=False):
        key "analyzer": Optional[Union[str, LexicalAnalyzerName]]
        key "dimensions": int
        key "facetable": bool
        key "fields": list[SearchField]
        key "filterable": bool
        key "indexAnalyzer": Optional[Union[str, LexicalAnalyzerName]]
        key "key": bool
        key "normalizer": Optional[Union[str, LexicalNormalizerName]]
        key "permissionFilter": Optional[Union[str, PermissionFilter]]
        key "retrievable": bool
        key "searchAnalyzer": Optional[Union[str, LexicalAnalyzerName]]
        key "searchable": bool
        key "sensitivityLabelId": bool
        key "sensitivityLabelName": bool
        key "sharepointSiteUrl": bool
        key "sortable": bool
        key "sourceDocumentId": bool
        key "stored": bool
        key "synonymMaps": list[str]
        key "vectorEncoding": Optional[Union[str, VectorEncodingFormat]]
        key "vectorSearchProfile": Optional[str]
        analyzer_name: Union[str, LexicalAnalyzerName]
        facetable: bool
        fields: list[SearchField]
        filterable: bool
        index_analyzer_name: Union[str, LexicalAnalyzerName]
        key: bool
        name: Required[str]
        normalizer_name: Union[str, LexicalNormalizerName]
        permission_filter: Union[str, PermissionFilter]
        retrievable: bool
        search_analyzer_name: Union[str, LexicalAnalyzerName]
        searchable: bool
        sensitivity_label_id: bool
        sensitivity_label_name: bool
        sharepoint_site_url: bool
        sortable: bool
        source_document_id: bool
        stored: bool
        synonym_map_names: list[str]
        type: Required[Union[str, SearchFieldDataType]]
        vector_encoding_format: Union[str, VectorEncodingFormat]
        vector_search_dimensions: int
        vector_search_profile_name: str


    class azure.search.documents.indexes.types.SearchIndex(TypedDict):
        key "@odata.etag": str
        key "analyzers": list[LexicalAnalyzer]
        key "charFilters": list[CharFilter]
        key "corsOptions": Optional[CorsOptions]
        key "defaultScoringProfile": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "normalizers": list[LexicalNormalizer]
        key "permissionFilterOption": Optional[Union[str, SearchIndexPermissionFilterOption]]
        key "purviewEnabled": Optional[bool]
        key "scoringProfiles": list[ScoringProfile]
        key "semantic": Optional[SemanticSearch]
        key "sharePointConnectorAppRegistration": ForwardRef('SharePointConnectorAppRegistration')
        key "similarity": ForwardRef('SimilarityAlgorithm')
        key "suggesters": list[SearchSuggester]
        key "tokenFilters": list[TokenFilter]
        key "tokenizers": list[LexicalTokenizer]
        key "vectorSearch": Optional[VectorSearch]
        analyzers: list[LexicalAnalyzer]
        char_filters: list[CharFilter]
        cors_options: CorsOptions
        default_scoring_profile: str
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        fields: Required[list[SearchField]]
        name: Required[str]
        normalizers: list[LexicalNormalizer]
        permission_filter_option: Union[str, SearchIndexPermissionFilterOption]
        purview_enabled: bool
        scoring_profiles: list[ScoringProfile]
        semantic_search: SemanticSearch
        share_point_connector_app_registration: SharePointConnectorAppRegistration
        similarity: SimilarityAlgorithm
        suggesters: list[SearchSuggester]
        token_filters: list[TokenFilter]
        tokenizers: list[LexicalTokenizer]
        vector_search: VectorSearch


    class azure.search.documents.indexes.types.SearchIndexFieldReference(TypedDict, total=False):
        name: Required[str]


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Required[Literal[KnowledgeSourceKind.SEARCH_INDEX]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]
        searchIndexParameters: Required[SearchIndexKnowledgeSourceParameters]
        search_index_parameters: SearchIndexKnowledgeSourceParameters


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSourceBoostKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIELD_VALUE = "fieldValue"
        MULTI_WORD_EXPRESSION = "multiWordExpression"


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSourceFieldValueBoost(TypedDict, total=False):
        key "boostInstructions": str
        key "fieldValues": list[str]
        boost: Required[float]
        boost_instructions: str
        field: Required[str]
        field_values: list[str]
        kind: Required[Literal[SearchIndexKnowledgeSourceBoostKind.FIELD_VALUE]]


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSourceFilterHint(TypedDict, total=False):
        key "filterInstructions": str
        field: Required[str]
        fieldValues: Required[list[str]]
        field_values: list[str]
        filter_instructions: str


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSourceMultiWordExpressionBoost(TypedDict, total=False):
        key "boostInstructions": str
        key "fieldValues": list[str]
        boost: Required[float]
        boost_instructions: str
        field_values: list[str]
        kind: Required[Literal[SearchIndexKnowledgeSourceBoostKind.MULTI_WORD_EXPRESSION]]


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSourceParameters(TypedDict, total=False):
        key "baseFilter": str
        key "queryHints": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "searchFields": list[SearchIndexFieldReference]
        key "semanticConfigurationName": str
        key "sourceDataFields": list[SearchIndexFieldReference]
        base_filter: str
        query_hints: SearchIndexKnowledgeSourceQueryHints
        searchIndexName: Required[str]
        search_fields: list[SearchIndexFieldReference]
        search_index_name: str
        semantic_configuration_name: str
        source_data_fields: list[SearchIndexFieldReference]


    class azure.search.documents.indexes.types.SearchIndexKnowledgeSourceQueryHints(TypedDict, total=False):
        key "boosts": list[SearchIndexKnowledgeSourceBoost]
        key "filters": list[SearchIndexKnowledgeSourceFilterHint]
        boosts: list[SearchIndexKnowledgeSourceBoost]
        filters: list[SearchIndexKnowledgeSourceFilterHint]


    class azure.search.documents.indexes.types.SearchIndexer(TypedDict):
        key "@odata.etag": str
        key "cache": Optional[SearchIndexerCache]
        key "description": str
        key "disabled": Optional[bool]
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "fieldMappings": list[FieldMapping]
        key "outputFieldMappings": list[FieldMapping]
        key "parameters": Optional[IndexingParameters]
        key "schedule": Optional[IndexingSchedule]
        key "skillsetName": str
        cache: SearchIndexerCache
        dataSourceName: Required[str]
        data_source_name: str
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        field_mappings: list[FieldMapping]
        is_disabled: bool
        name: Required[str]
        output_field_mappings: list[FieldMapping]
        parameters: IndexingParameters
        schedule: IndexingSchedule
        skillset_name: str
        targetIndexName: Required[str]
        target_index_name: str


    class azure.search.documents.indexes.types.SearchIndexerCache(TypedDict, total=False):
        key "enableReprocessing": Optional[bool]
        key "id": str
        key "identity": Optional[SearchIndexerDataIdentity]
        key "storageConnectionString": str
        enable_reprocessing: bool
        id: str
        identity: SearchIndexerDataIdentity
        storage_connection_string: str


    class azure.search.documents.indexes.types.SearchIndexerDataContainer(TypedDict, total=False):
        key "query": str
        name: Required[str]
        query: str


    class azure.search.documents.indexes.types.SearchIndexerDataNoneIdentity(TypedDict):
        @odata.type: Required[Literal["#DataNoneIdentity"]]
        odata_type: Literal[#DataNoneIdentity]


    class azure.search.documents.indexes.types.SearchIndexerDataSourceConnection(TypedDict):
        key "@odata.etag": str
        key "dataChangeDetectionPolicy": Optional[DataChangeDetectionPolicy]
        key "dataDeletionDetectionPolicy": Optional[DataDeletionDetectionPolicy]
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "identity": Optional[SearchIndexerDataIdentity]
        key "indexerPermissionOptions": Optional[list[Union[str, IndexerPermissionOption]]]
        key "subType": str
        container: Required[SearchIndexerDataContainer]
        credentials: Required[DataSourceCredentials]
        data_change_detection_policy: DataChangeDetectionPolicy
        data_deletion_detection_policy: DataDeletionDetectionPolicy
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        identity: SearchIndexerDataIdentity
        indexer_permission_options: list[Union[str, IndexerPermissionOption]]
        name: Required[str]
        sub_type: str
        type: Required[Union[str, SearchIndexerDataSourceType]]


    class azure.search.documents.indexes.types.SearchIndexerDataUserAssignedIdentity(TypedDict):
        key "federatedIdentityClientId": str
        @odata.type: Required[Literal["#DataUserAssignedIdentity"]]
        federated_identity_client_id: str
        odata_type: Literal[#DataUserAssignedIdentity]
        resource_id: str
        userAssignedIdentity: Required[str]


    class azure.search.documents.indexes.types.SearchIndexerIndexProjection(TypedDict, total=False):
        key "parameters": ForwardRef('SearchIndexerIndexProjectionsParameters')
        parameters: SearchIndexerIndexProjectionsParameters
        selectors: Required[list[SearchIndexerIndexProjectionSelector]]


    class azure.search.documents.indexes.types.SearchIndexerIndexProjectionSelector(TypedDict, total=False):
        mappings: Required[list[InputFieldMappingEntry]]
        parentKeyFieldName: Required[str]
        parent_key_field_name: str
        sourceContext: Required[str]
        source_context: str
        targetIndexName: Required[str]
        target_index_name: str


    class azure.search.documents.indexes.types.SearchIndexerIndexProjectionsParameters(TypedDict, total=False):
        key "projectionMode": Union[str, IndexProjectionMode]
        projection_mode: Union[str, IndexProjectionMode]


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStore(TypedDict, total=False):
        key "identity": Optional[SearchIndexerDataIdentity]
        key "parameters": ForwardRef('SearchIndexerKnowledgeStoreParameters')
        identity: SearchIndexerDataIdentity
        parameters: SearchIndexerKnowledgeStoreParameters
        projections: Required[list[SearchIndexerKnowledgeStoreProjection]]
        storageConnectionString: Required[str]
        storage_connection_string: str


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreBlobProjectionSelector(SearchIndexerKnowledgeStoreProjectionSelector):
        key "generatedKeyName": str
        key "inputs": list[InputFieldMappingEntry]
        key "referenceKeyName": str
        key "source": str
        key "sourceContext": str
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        storageContainer: Required[str]
        storage_container: str


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreFileProjectionSelector(SearchIndexerKnowledgeStoreBlobProjectionSelector):
        key "generatedKeyName": str
        key "inputs": list[InputFieldMappingEntry]
        key "referenceKeyName": str
        key "source": str
        key "sourceContext": str
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        storageContainer: Required[str]
        storage_container: str


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreObjectProjectionSelector(SearchIndexerKnowledgeStoreBlobProjectionSelector):
        key "generatedKeyName": str
        key "inputs": list[InputFieldMappingEntry]
        key "referenceKeyName": str
        key "source": str
        key "sourceContext": str
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        storageContainer: Required[str]
        storage_container: str


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreParameters(TypedDict, total=False):
        key "synthesizeGeneratedKeyName": bool
        synthesize_generated_key_name: bool


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreProjection(TypedDict, total=False):
        key "files": list[SearchIndexerKnowledgeStoreFileProjectionSelector]
        key "objects": list[SearchIndexerKnowledgeStoreObjectProjectionSelector]
        key "tables": list[SearchIndexerKnowledgeStoreTableProjectionSelector]
        files: list[SearchIndexerKnowledgeStoreFileProjectionSelector]
        objects: list[SearchIndexerKnowledgeStoreObjectProjectionSelector]
        tables: list[SearchIndexerKnowledgeStoreTableProjectionSelector]


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreProjectionSelector(TypedDict, total=False):
        key "generatedKeyName": str
        key "inputs": list[InputFieldMappingEntry]
        key "referenceKeyName": str
        key "source": str
        key "sourceContext": str
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str


    class azure.search.documents.indexes.types.SearchIndexerKnowledgeStoreTableProjectionSelector(SearchIndexerKnowledgeStoreProjectionSelector):
        key "inputs": list[InputFieldMappingEntry]
        key "referenceKeyName": str
        key "source": str
        key "sourceContext": str
        generatedKeyName: Required[str]
        generated_key_name: str
        inputs: list[InputFieldMappingEntry]
        reference_key_name: str
        source: str
        source_context: str
        tableName: Required[str]
        table_name: str


    class azure.search.documents.indexes.types.SearchIndexerSkillset(TypedDict):
        key "@odata.etag": str
        key "cognitiveServices": ForwardRef('CognitiveServicesAccount')
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "indexProjections": ForwardRef('SearchIndexerIndexProjection')
        key "knowledgeStore": ForwardRef('SearchIndexerKnowledgeStore')
        cognitive_services_account: CognitiveServicesAccount
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        index_projection: SearchIndexerIndexProjection
        knowledge_store: SearchIndexerKnowledgeStore
        name: Required[str]
        skills: Required[list[SearchIndexerSkill]]


    class azure.search.documents.indexes.types.SearchResourceEncryptionKey(TypedDict, total=False):
        key "accessCredentials": ForwardRef('AzureActiveDirectoryApplicationCredentials')
        key "identity": Optional[SearchIndexerDataIdentity]
        key "isServiceLevelKey": bool
        key "keyVaultKeyVersion": str
        access_credentials: AzureActiveDirectoryApplicationCredentials
        identity: SearchIndexerDataIdentity
        is_service_level_key: bool
        keyVaultKeyName: Required[str]
        keyVaultUri: Required[str]
        key_name: str
        key_version: str
        vault_uri: str


    class azure.search.documents.indexes.types.SearchSuggester(TypedDict, total=False):
        name: Required[str]
        searchMode: Required[Literal["analyzingInfixMatching"]]
        search_mode: Literal[analyzingInfixMatching]
        sourceFields: Required[list[str]]
        source_fields: list[str]


    class azure.search.documents.indexes.types.SemanticConfiguration(TypedDict, total=False):
        key "flightingOptIn": bool
        key "rankingOrder": Optional[Union[str, RankingOrder]]
        flighting_opt_in: bool
        name: Required[str]
        prioritizedFields: Required[SemanticPrioritizedFields]
        prioritized_fields: SemanticPrioritizedFields
        ranking_order: Union[str, RankingOrder]


    class azure.search.documents.indexes.types.SemanticField(TypedDict, total=False):
        fieldName: Required[str]
        field_name: str


    class azure.search.documents.indexes.types.SemanticPrioritizedFields(TypedDict, total=False):
        key "prioritizedContentFields": list[SemanticField]
        key "prioritizedKeywordsFields": list[SemanticField]
        key "titleField": ForwardRef('SemanticField')
        content_fields: list[SemanticField]
        keywords_fields: list[SemanticField]
        title_field: SemanticField


    class azure.search.documents.indexes.types.SemanticSearch(TypedDict, total=False):
        key "configurations": list[SemanticConfiguration]
        key "defaultConfiguration": str
        configurations: list[SemanticConfiguration]
        default_configuration_name: str


    class azure.search.documents.indexes.types.SentimentSkillV3(TypedDict):
        key "context": str
        key "defaultLanguageCode": Optional[Union[str, SentimentSkillLanguage]]
        key "description": str
        key "includeOpinionMining": bool
        key "modelVersion": Optional[str]
        key "name": str
        @odata.type: Required[Literal["#SentimentSkill"]]
        context: str
        default_language_code: Union[str, SentimentSkillLanguage]
        description: str
        include_opinion_mining: bool
        inputs: Required[list[InputFieldMappingEntry]]
        model_version: str
        name: str
        odata_type: Literal[#SentimentSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.ShaperSkill(TypedDict):
        key "context": str
        key "description": str
        key "name": str
        @odata.type: Required[Literal["#ShaperSkill"]]
        context: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#ShaperSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.SharePointConnectorAppRegistration(TypedDict, total=False):
        key "tenantId": str
        applicationId: Required[str]
        application_id: str
        federatedCredentialId: Required[str]
        federated_credential_id: str
        tenant_id: str


    class azure.search.documents.indexes.types.ShingleTokenFilter(TypedDict):
        key "filterToken": str
        key "maxShingleSize": int
        key "minShingleSize": int
        key "outputUnigrams": bool
        key "outputUnigramsIfNoShingles": bool
        key "tokenSeparator": str
        @odata.type: Required[Literal["#ShingleTokenFilter"]]
        filter_token: str
        max_shingle_size: int
        min_shingle_size: int
        name: Required[str]
        odata_type: Literal[#ShingleTokenFilter]
        output_unigrams: bool
        output_unigrams_if_no_shingles: bool
        token_separator: str


    class azure.search.documents.indexes.types.SkillNames(TypedDict, total=False):
        key "skillNames": list[str]
        skill_names: list[str]


    class azure.search.documents.indexes.types.SnowballTokenFilter(TypedDict):
        @odata.type: Required[Literal["#SnowballTokenFilter"]]
        language: Required[Union[str, SnowballTokenFilterLanguage]]
        name: Required[str]
        odata_type: Literal[#SnowballTokenFilter]


    class azure.search.documents.indexes.types.SoftDeleteColumnDeletionDetectionPolicy(TypedDict):
        key "softDeleteColumnName": str
        key "softDeleteMarkerValue": str
        @odata.type: Required[Literal["#SoftDeleteColumnDeletionDetectionPolicy"]]
        odata_type: Literal[#SoftDeleteColumnDeletionDetectionPolicy]
        soft_delete_column_name: str
        soft_delete_marker_value: str


    class azure.search.documents.indexes.types.SplitSkill(TypedDict):
        key "azureOpenAITokenizerParameters": Optional[AzureOpenAITokenizerParameters]
        key "context": str
        key "defaultLanguageCode": Union[str, SplitSkillLanguage]
        key "description": str
        key "maximumPageLength": Optional[int]
        key "maximumPagesToTake": Optional[int]
        key "name": str
        key "pageOverlapLength": Optional[int]
        key "textSplitMode": Union[str, TextSplitMode]
        key "unit": Optional[Union[str, SplitSkillUnit]]
        @odata.type: Required[Literal["#SplitSkill"]]
        azure_open_ai_tokenizer_parameters: AzureOpenAITokenizerParameters
        context: str
        default_language_code: Union[str, SplitSkillLanguage]
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        maximum_page_length: int
        maximum_pages_to_take: int
        name: str
        odata_type: Literal[#SplitSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        page_overlap_length: int
        text_split_mode: Union[str, TextSplitMode]
        unit: Union[str, SplitSkillUnit]


    class azure.search.documents.indexes.types.SqlIntegratedChangeTrackingPolicy(TypedDict):
        @odata.type: Required[Literal["#SqlIntegratedChangeTrackingPolicy"]]
        odata_type: Literal[#SqlIntegratedChangeTrackingPolicy]


    class azure.search.documents.indexes.types.StemmerOverrideTokenFilter(TypedDict):
        @odata.type: Required[Literal["#StemmerOverrideTokenFilter"]]
        name: Required[str]
        odata_type: Literal[#StemmerOverrideTokenFilter]
        rules: Required[list[str]]


    class azure.search.documents.indexes.types.StemmerTokenFilter(TypedDict):
        @odata.type: Required[Literal["#StemmerTokenFilter"]]
        language: Required[Union[str, StemmerTokenFilterLanguage]]
        name: Required[str]
        odata_type: Literal[#StemmerTokenFilter]


    class azure.search.documents.indexes.types.StopAnalyzer(TypedDict):
        key "stopwords": list[str]
        @odata.type: Required[Literal["#StopAnalyzer"]]
        name: Required[str]
        odata_type: Literal[#StopAnalyzer]
        stopwords: list[str]


    class azure.search.documents.indexes.types.StopwordsTokenFilter(TypedDict):
        key "ignoreCase": bool
        key "removeTrailing": bool
        key "stopwords": list[str]
        key "stopwordsList": Union[str, StopwordsList]
        @odata.type: Required[Literal["#StopwordsTokenFilter"]]
        ignore_case: bool
        name: Required[str]
        odata_type: Literal[#StopwordsTokenFilter]
        remove_trailing_stop_words: bool
        stopwords: list[str]
        stopwords_list: Union[str, StopwordsList]


    class azure.search.documents.indexes.types.SynonymMap(TypedDict):
        key "@odata.etag": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        format: Required[Literal["solr"]]
        name: Required[str]
        synonyms: Required[list[str]]


    class azure.search.documents.indexes.types.SynonymTokenFilter(TypedDict):
        key "expand": bool
        key "ignoreCase": bool
        @odata.type: Required[Literal["#SynonymTokenFilter"]]
        expand: bool
        ignore_case: bool
        name: Required[str]
        odata_type: Literal[#SynonymTokenFilter]
        synonyms: Required[list[str]]


    class azure.search.documents.indexes.types.TagScoringFunction(TypedDict, total=False):
        key "interpolation": Union[str, ScoringFunctionInterpolation]
        boost: Required[float]
        fieldName: Required[str]
        field_name: str
        interpolation: Union[str, ScoringFunctionInterpolation]
        parameters: TagScoringParameters
        tag: Required[TagScoringParameters]
        type: Required[Literal["tag"]]


    class azure.search.documents.indexes.types.TagScoringParameters(TypedDict, total=False):
        tagsParameter: Required[str]
        tags_parameter: str


    class azure.search.documents.indexes.types.TextTranslationSkill(TypedDict):
        key "context": str
        key "defaultFromLanguageCode": Union[str, TextTranslationSkillLanguage]
        key "description": str
        key "name": str
        key "suggestedFrom": Optional[Union[str, TextTranslationSkillLanguage]]
        @odata.type: Required[Literal["#TranslationSkill"]]
        context: str
        defaultToLanguageCode: Required[Union[str, TextTranslationSkillLanguage]]
        default_from_language_code: Union[str, TextTranslationSkillLanguage]
        default_to_language_code: Union[str, TextTranslationSkillLanguage]
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#TranslationSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        suggested_from: Union[str, TextTranslationSkillLanguage]


    class azure.search.documents.indexes.types.TextWeights(TypedDict, total=False):
        weights: Required[dict[str, float]]


    class azure.search.documents.indexes.types.TruncateTokenFilter(TypedDict):
        key "length": int
        @odata.type: Required[Literal["#TruncateTokenFilter"]]
        length: int
        name: Required[str]
        odata_type: Literal[#TruncateTokenFilter]


    class azure.search.documents.indexes.types.UaxUrlEmailTokenizer(TypedDict):
        key "maxTokenLength": int
        @odata.type: Required[Literal["#UaxUrlEmailTokenizer"]]
        max_token_length: int
        name: Required[str]
        odata_type: Literal[#UaxUrlEmailTokenizer]


    class azure.search.documents.indexes.types.UniqueTokenFilter(TypedDict):
        key "onlyOnSamePosition": bool
        @odata.type: Required[Literal["#UniqueTokenFilter"]]
        name: Required[str]
        odata_type: Literal[#UniqueTokenFilter]
        only_on_same_position: bool


    class azure.search.documents.indexes.types.UpdateKnowledgeSourceFileRequest(TypedDict, total=False):
        content: Required[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]
        metadata: Required[FileUploadMetadata]


    class azure.search.documents.indexes.types.UploadKnowledgeSourceFileMultipartRequest(TypedDict, total=False):
        content: Required[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]
        metadata: Required[FileUploadMetadata]


    class azure.search.documents.indexes.types.VectorSearch(TypedDict, total=False):
        key "algorithms": list[VectorSearchAlgorithmConfiguration]
        key "compressions": list[VectorSearchCompression]
        key "profiles": list[VectorSearchProfile]
        key "vectorizers": list[VectorSearchVectorizer]
        algorithms: list[VectorSearchAlgorithmConfiguration]
        compressions: list[VectorSearchCompression]
        profiles: list[VectorSearchProfile]
        vectorizers: list[VectorSearchVectorizer]


    class azure.search.documents.indexes.types.VectorSearchAlgorithmKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXHAUSTIVE_KNN = "exhaustiveKnn"
        HNSW = "hnsw"


    class azure.search.documents.indexes.types.VectorSearchCompressionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY_QUANTIZATION = "binaryQuantization"
        SCALAR_QUANTIZATION = "scalarQuantization"


    class azure.search.documents.indexes.types.VectorSearchProfile(TypedDict, total=False):
        key "compression": str
        key "vectorizer": str
        algorithm: Required[str]
        algorithm_configuration_name: str
        compression_name: str
        name: Required[str]
        vectorizer_name: str


    class azure.search.documents.indexes.types.VectorSearchVectorizerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AI_SERVICES_VISION = "aiServicesVision"
        AML = "aml"
        AZURE_OPEN_AI = "azureOpenAI"
        CUSTOM_WEB_API = "customWebApi"


    class azure.search.documents.indexes.types.VisionVectorizeSkill(TypedDict):
        key "context": str
        key "description": str
        key "name": str
        @odata.type: Required[Literal["#VectorizeSkill"]]
        context: str
        description: str
        inputs: Required[list[InputFieldMappingEntry]]
        modelVersion: Required[Optional[str]]
        model_version: str
        name: str
        odata_type: Literal[#VectorizeSkill]
        outputs: Required[list[OutputFieldMappingEntry]]


    class azure.search.documents.indexes.types.WebApiHttpHeaders(TypedDict, total=False):


    class azure.search.documents.indexes.types.WebApiSkill(TypedDict):
        key "authIdentity": Optional[SearchIndexerDataIdentity]
        key "authResourceId": Optional[str]
        key "batchSize": Optional[int]
        key "context": str
        key "degreeOfParallelism": Optional[int]
        key "description": str
        key "httpHeaders": ForwardRef('WebApiHttpHeaders')
        key "httpMethod": str
        key "name": str
        key "timeout": str
        @odata.type: Required[Literal["#WebApiSkill"]]
        auth_identity: SearchIndexerDataIdentity
        auth_resource_id: str
        batch_size: int
        context: str
        degree_of_parallelism: int
        description: str
        http_headers: WebApiHttpHeaders
        http_method: str
        inputs: Required[list[InputFieldMappingEntry]]
        name: str
        odata_type: Literal[#WebApiSkill]
        outputs: Required[list[OutputFieldMappingEntry]]
        timeout: str
        uri: Required[str]


    class azure.search.documents.indexes.types.WebApiVectorizer(TypedDict, total=False):
        key "customWebApiParameters": ForwardRef('WebApiVectorizerParameters')
        kind: Required[Literal[VectorSearchVectorizerKind.CUSTOM_WEB_API]]
        name: Required[str]
        vectorizer_name: str
        web_api_parameters: WebApiVectorizerParameters


    class azure.search.documents.indexes.types.WebApiVectorizerParameters(TypedDict, total=False):
        key "authIdentity": Optional[SearchIndexerDataIdentity]
        key "authResourceId": Optional[str]
        key "httpHeaders": dict[str, str]
        key "httpMethod": str
        key "timeout": str
        key "uri": str
        auth_identity: SearchIndexerDataIdentity
        auth_resource_id: str
        http_headers: dict[str, str]
        http_method: str
        timeout: str
        url: str


    class azure.search.documents.indexes.types.WebKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        key "webParameters": ForwardRef('WebKnowledgeSourceParameters')
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Required[Literal[KnowledgeSourceKind.WEB]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]
        web_parameters: WebKnowledgeSourceParameters


    class azure.search.documents.indexes.types.WebKnowledgeSourceDomain(TypedDict, total=False):
        key "includeSubpages": bool
        address: Required[str]
        include_subpages: bool


    class azure.search.documents.indexes.types.WebKnowledgeSourceDomains(TypedDict, total=False):
        key "allowedDomains": list[WebKnowledgeSourceDomain]
        key "blockedDomains": list[WebKnowledgeSourceDomain]
        allowed_domains: list[WebKnowledgeSourceDomain]
        blocked_domains: list[WebKnowledgeSourceDomain]


    class azure.search.documents.indexes.types.WebKnowledgeSourceParameters(TypedDict, total=False):
        key "count": int
        key "domains": ForwardRef('WebKnowledgeSourceDomains')
        key "freshness": str
        key "language": str
        key "market": str
        count: int
        domains: WebKnowledgeSourceDomains
        freshness: str
        language: str
        market: str


    class azure.search.documents.indexes.types.WordDelimiterTokenFilter(TypedDict):
        key "catenateAll": bool
        key "catenateNumbers": bool
        key "catenateWords": bool
        key "generateNumberParts": bool
        key "generateWordParts": bool
        key "preserveOriginal": bool
        key "protectedWords": list[str]
        key "splitOnCaseChange": bool
        key "splitOnNumerics": bool
        key "stemEnglishPossessive": bool
        @odata.type: Required[Literal["#WordDelimiterTokenFilter"]]
        catenate_all: bool
        catenate_numbers: bool
        catenate_words: bool
        generate_number_parts: bool
        generate_word_parts: bool
        name: Required[str]
        odata_type: Literal[#WordDelimiterTokenFilter]
        preserve_original: bool
        protected_words: list[str]
        split_on_case_change: bool
        split_on_numerics: bool
        stem_english_possessive: bool


    class azure.search.documents.indexes.types.WorkIQKnowledgeSource(TypedDict):
        key "@odata.etag": str
        key "description": str
        key "encryptionKey": Optional[SearchResourceEncryptionKey]
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        kind: Required[Literal[KnowledgeSourceKind.WORK_IQ]]
        name: Required[str]
        results_processing: Union[str, KnowledgeSourceResultsProcessing]
        workIQParameters: Required[WorkIQKnowledgeSourceParameters]
        work_iq_parameters: WorkIQKnowledgeSourceParameters


    class azure.search.documents.indexes.types.WorkIQKnowledgeSourceParameters(TypedDict, total=False):
        entraAppAuthentication: Required[EntraAppAuthentication]
        entra_app_authentication: EntraAppAuthentication


namespace azure.search.documents.knowledgebases

    class azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def retrieve(
                self, 
                retrieval_request: KnowledgeBaseRetrievalRequest, 
                *, 
                content_type: str = "application/json", 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        def retrieve(
                self, 
                retrieval_request: KnowledgeBaseRetrievalRequest, 
                *, 
                content_type: str = "application/json", 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        def retrieve(
                self, 
                retrieval_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        def retrieve_stream(
                self, 
                retrieval_request: Union[KnowledgeBaseRetrievalRequest, dict[str, Any], IO[bytes]], 
                *, 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalStream: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.search.documents.knowledgebases.KnowledgeBaseRetrievalEvent:
        data: Optional[Union[KnowledgeBaseRetrievalStartedEvent, KnowledgeBaseActivityStartedEvent, KnowledgeBaseActivityRecord, KnowledgeBaseAnswerCompletedEvent, list[KnowledgeBaseReference], KnowledgeBaseStreamErrorEvent, KnowledgeBaseResponseCompletedEvent, dict[str, Any], list[Any], str, int, float, bool]]
        event_type: str

        def __init__(
                self, 
                event_type: str, 
                data: KnowledgeBaseRetrievalEventData
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.search.documents.knowledgebases.KnowledgeBaseRetrievalStream(Iterator[KnowledgeBaseRetrievalEvent]): implements ContextManager , Iterator 

        def __init__(
                self, 
                *, 
                raw_stream: Iterator[bytes], 
                response: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.search.documents.knowledgebases.aio

    class azure.search.documents.knowledgebases.aio.AsyncKnowledgeBaseRetrievalStream(AsyncIterator[KnowledgeBaseRetrievalEvent]): implements AsyncContextManager , AsyncIterable , AsyncIterator 

        def __init__(
                self, 
                *, 
                raw_stream: AsyncIterator[bytes], 
                response: Any
            ) -> None: ...

        async def close(self) -> None: ...


    class azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def retrieve(
                self, 
                retrieval_request: KnowledgeBaseRetrievalRequest, 
                *, 
                content_type: str = "application/json", 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        async def retrieve(
                self, 
                retrieval_request: KnowledgeBaseRetrievalRequest, 
                *, 
                content_type: str = "application/json", 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        async def retrieve(
                self, 
                retrieval_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        async def retrieve_stream(
                self, 
                retrieval_request: Union[KnowledgeBaseRetrievalRequest, dict[str, Any], IO[bytes]], 
                *, 
                query_source_authorization: Optional[str] = ..., 
                query_work_iq_source_authorization: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncKnowledgeBaseRetrievalStream: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalEvent:
        data: Optional[Union[KnowledgeBaseRetrievalStartedEvent, KnowledgeBaseActivityStartedEvent, KnowledgeBaseActivityRecord, KnowledgeBaseAnswerCompletedEvent, list[KnowledgeBaseReference], KnowledgeBaseStreamErrorEvent, KnowledgeBaseResponseCompletedEvent, dict[str, Any], list[Any], str, int, float, bool]]
        event_type: str

        def __init__(
                self, 
                event_type: str, 
                data: KnowledgeBaseRetrievalEventData
            ) -> None: ...

        def __repr__(self) -> str: ...


namespace azure.search.documents.knowledgebases.models

    class azure.search.documents.knowledgebases.models.AIServices(_Model):
        api_key: Optional[str]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.AssetStore(_Model):
        connection_string: str
        container_name: str

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                container_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.AzureBlobKnowledgeSourceParams(KnowledgeSourceParams, discriminator='azureBlob'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.AZURE_BLOB]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints]
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.CompletedSynchronizationState(_Model):
        end_time: datetime
        items_skipped: int
        items_updates_failed: int
        items_updates_processed: int
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                end_time: datetime, 
                items_skipped: int, 
                items_updates_failed: int, 
                items_updates_processed: int, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.FabricDataAgentKnowledgeSourceParams(KnowledgeSourceParams, discriminator='fabricDataAgent'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.FABRIC_DATA_AGENT]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.FabricOntologyKnowledgeSourceParams(KnowledgeSourceParams, discriminator='fabricOntology'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.FABRIC_ONTOLOGY]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.FileKnowledgeSourceParams(KnowledgeSourceParams, discriminator='file'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.FILE]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints]
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.FreshnessPolicy(_Model):
        boosting_duration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                boosting_duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.ImageServingStatistics(_Model):
        images_retrieved: Optional[int]
        images_sent_to_model: Optional[int]
        served_images: Optional[list[ServedImage]]
        total_image_size_bytes: Optional[int]
        verbalization_used: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                images_retrieved: Optional[int] = ..., 
                images_sent_to_model: Optional[int] = ..., 
                served_images: Optional[list[ServedImage]] = ..., 
                total_image_size_bytes: Optional[int] = ..., 
                verbalization_used: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.IndexedOneLakeKnowledgeSourceParams(KnowledgeSourceParams, discriminator='indexedOneLake'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.INDEXED_ONELAKE]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints]
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.IndexedSharePointKnowledgeSourceParams(KnowledgeSourceParams, discriminator='indexedSharePoint'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.INDEXED_SHARE_POINT]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints]
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.IndexedSqlKnowledgeSourceParams(KnowledgeSourceParams, discriminator='indexedSql'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.INDEXED_SQL]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints]
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecord(_Model):
        completed_at: Optional[datetime]
        elapsed_ms: Optional[int]
        error: Optional[KnowledgeBaseErrorDetail]
        id: int
        started_at: Optional[datetime]
        type: str
        warning: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                started_at: Optional[datetime] = ..., 
                type: str, 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecordModel(_Model):
        deployment_id: Optional[str]
        model_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deployment_id: Optional[str] = ..., 
                model_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTIC_REASONING = "agenticReasoning"
        AZURE_BLOB = "azureBlob"
        FABRIC_DATA_AGENT = "fabricDataAgent"
        FABRIC_ONTOLOGY = "fabricOntology"
        FILE = "file"
        INDEXED_ONELAKE = "indexedOneLake"
        INDEXED_SHARE_POINT = "indexedSharePoint"
        INDEXED_SQL = "indexedSql"
        MCP_SERVER = "mcpServer"
        MODEL_ANSWER_SYNTHESIS = "modelAnswerSynthesis"
        MODEL_QUERY_PLANNING = "modelQueryPlanning"
        MODEL_WEB_SUMMARIZATION = "modelWebSummarization"
        REMOTE_SHARE_POINT = "remoteSharePoint"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"
        WORK_IQ = "workIQ"


    class azure.search.documents.knowledgebases.models.KnowledgeBaseActivityStartedEvent(_Model):
        id: int
        knowledge_source_name: Optional[str]
        started_at: datetime
        type: Union[str, KnowledgeBaseActivityRecordType]

        @overload
        def __init__(
                self, 
                *, 
                id: int, 
                knowledge_source_name: Optional[str] = ..., 
                started_at: datetime, 
                type: Union[str, KnowledgeBaseActivityRecordType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAgenticReasoningActivityRecord(KnowledgeBaseActivityRecord, discriminator='agenticReasoning'):
        completed_at: datetime
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        logical_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort]
        reasoning_tokens: Optional[int]
        retrieval_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.AGENTIC_REASONING]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                logical_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort] = ..., 
                reasoning_tokens: Optional[int] = ..., 
                retrieval_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAnswerCompletedEvent(_Model):
        message: KnowledgeBaseMessage
        message_index: int

        @overload
        def __init__(
                self, 
                *, 
                message: KnowledgeBaseMessage, 
                message_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAzureBlobActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAzureBlobActivityRecord(KnowledgeBaseActivityRecord, discriminator='azureBlob'):
        azure_blob_arguments: Optional[KnowledgeBaseAzureBlobActivityArguments]
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.AZURE_BLOB]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_arguments: Optional[KnowledgeBaseAzureBlobActivityArguments] = ..., 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAzureBlobReference(KnowledgeBaseReference, discriminator='azureBlob'):
        activity_source: int
        blob_url: Optional[str]
        citation_url: Optional[str]
        id: str
        reranker_score: float
        search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.AZURE_BLOB]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                blob_url: Optional[str] = ..., 
                citation_url: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseErrorAdditionalInfo(_Model):
        info: Optional[dict[str, Any]]
        type: Optional[str]


    class azure.search.documents.knowledgebases.models.KnowledgeBaseErrorDetail(_Model):
        additional_info: Optional[list[KnowledgeBaseErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[KnowledgeBaseErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFabricDataAgentActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFabricDataAgentActivityRecord(KnowledgeBaseActivityRecord, discriminator='fabricDataAgent'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        fabric_data_agent_arguments: Optional[KnowledgeBaseFabricDataAgentActivityArguments]
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.FABRIC_DATA_AGENT]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                fabric_data_agent_arguments: Optional[KnowledgeBaseFabricDataAgentActivityArguments] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFabricDataAgentReference(KnowledgeBaseReference, discriminator='fabricDataAgent'):
        activity_source: int
        data_agent_id: Optional[str]
        id: str
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.FABRIC_DATA_AGENT]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                data_agent_id: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFabricOntologyActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFabricOntologyActivityRecord(KnowledgeBaseActivityRecord, discriminator='fabricOntology'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        fabric_ontology_arguments: Optional[KnowledgeBaseFabricOntologyActivityArguments]
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.FABRIC_ONTOLOGY]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                fabric_ontology_arguments: Optional[KnowledgeBaseFabricOntologyActivityArguments] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFabricOntologyReference(KnowledgeBaseReference, discriminator='fabricOntology'):
        activity_source: int
        id: str
        ontology_id: Optional[str]
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.FABRIC_ONTOLOGY]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                id: str, 
                ontology_id: Optional[str] = ..., 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFileActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFileActivityRecord(KnowledgeBaseActivityRecord, discriminator='file'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        file_arguments: Optional[KnowledgeBaseFileActivityArguments]
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.FILE]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                file_arguments: Optional[KnowledgeBaseFileActivityArguments] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseFileReference(KnowledgeBaseReference, discriminator='file'):
        activity_source: int
        citation_url: Optional[str]
        doc_name: Optional[str]
        id: str
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.FILE]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                citation_url: Optional[str] = ..., 
                doc_name: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseImageContent(_Model):
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedOneLakeActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedOneLakeActivityRecord(KnowledgeBaseActivityRecord, discriminator='indexedOneLake'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        indexed_one_lake_arguments: Optional[KnowledgeBaseIndexedOneLakeActivityArguments]
        knowledge_source_name: Optional[str]
        query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.INDEXED_ONELAKE]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                indexed_one_lake_arguments: Optional[KnowledgeBaseIndexedOneLakeActivityArguments] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedOneLakeReference(KnowledgeBaseReference, discriminator='indexedOneLake'):
        activity_source: int
        citation_url: Optional[str]
        doc_url: Optional[str]
        id: str
        reranker_score: float
        search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.INDEXED_ONELAKE]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                citation_url: Optional[str] = ..., 
                doc_url: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSharePointActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSharePointActivityRecord(KnowledgeBaseActivityRecord, discriminator='indexedSharePoint'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        indexed_share_point_arguments: Optional[KnowledgeBaseIndexedSharePointActivityArguments]
        knowledge_source_name: Optional[str]
        query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.INDEXED_SHARE_POINT]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                indexed_share_point_arguments: Optional[KnowledgeBaseIndexedSharePointActivityArguments] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSharePointReference(KnowledgeBaseReference, discriminator='indexedSharePoint'):
        activity_source: int
        citation_url: Optional[str]
        doc_url: Optional[str]
        id: str
        reranker_score: float
        search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.INDEXED_SHARE_POINT]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                citation_url: Optional[str] = ..., 
                doc_url: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSqlActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSqlActivityRecord(KnowledgeBaseActivityRecord, discriminator='indexedSql'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        indexed_sql_arguments: Optional[KnowledgeBaseIndexedSqlActivityArguments]
        knowledge_source_name: Optional[str]
        query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.INDEXED_SQL]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                indexed_sql_arguments: Optional[KnowledgeBaseIndexedSqlActivityArguments] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedSqlReference(KnowledgeBaseReference, discriminator='indexedSql'):
        activity_source: int
        citation_url: Optional[str]
        doc_url: Optional[str]
        id: str
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.INDEXED_SQL]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                citation_url: Optional[str] = ..., 
                doc_url: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMcpServerActivityArguments(_Model):
        tool_arguments: Optional[dict[str, Any]]
        tool_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                tool_arguments: Optional[dict[str, Any]] = ..., 
                tool_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMcpServerActivityRecord(KnowledgeBaseActivityRecord, discriminator='mcpServer'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        mcp_server_arguments: Optional[KnowledgeBaseMcpServerActivityArguments]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.MCP_SERVER]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                mcp_server_arguments: Optional[KnowledgeBaseMcpServerActivityArguments] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMcpServerReference(KnowledgeBaseReference, discriminator='mcpServer'):
        activity_source: int
        id: str
        reranker_score: float
        source_data: dict[str, any]
        title: Optional[str]
        tool_name: Optional[str]
        type: Literal[KnowledgeBaseReferenceType.MCP_SERVER]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ..., 
                title: Optional[str] = ..., 
                tool_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMessage(_Model):
        content: list[KnowledgeBaseMessageContent]
        role: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: list[KnowledgeBaseMessageContent], 
                role: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMessageContent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMessageContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "image"
        TEXT = "text"


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMessageImageContent(KnowledgeBaseMessageContent, discriminator='image'):
        image: KnowledgeBaseImageContent
        type: Literal[KnowledgeBaseMessageContentType.IMAGE]

        @overload
        def __init__(
                self, 
                *, 
                image: KnowledgeBaseImageContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseMessageTextContent(KnowledgeBaseMessageContent, discriminator='text'):
        text: str
        type: Literal[KnowledgeBaseMessageContentType.TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseModelAnswerSynthesisActivityRecord(KnowledgeBaseActivityRecord, discriminator='modelAnswerSynthesis'):
        completed_at: datetime
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        input_tokens: Optional[int]
        model: Optional[KnowledgeBaseActivityRecordModel]
        output_tokens: Optional[int]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.MODEL_ANSWER_SYNTHESIS]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                input_tokens: Optional[int] = ..., 
                model: Optional[KnowledgeBaseActivityRecordModel] = ..., 
                output_tokens: Optional[int] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseModelQueryPlanningActivityRecord(KnowledgeBaseActivityRecord, discriminator='modelQueryPlanning'):
        completed_at: datetime
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        input_tokens: Optional[int]
        model: Optional[KnowledgeBaseActivityRecordModel]
        output_tokens: Optional[int]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.MODEL_QUERY_PLANNING]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                input_tokens: Optional[int] = ..., 
                model: Optional[KnowledgeBaseActivityRecordModel] = ..., 
                output_tokens: Optional[int] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseModelWebSummarizationActivityRecord(KnowledgeBaseActivityRecord, discriminator='modelWebSummarization'):
        completed_at: datetime
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        input_tokens_count: Optional[int]
        model: Optional[KnowledgeBaseActivityRecordModel]
        output_tokens_count: Optional[int]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.MODEL_WEB_SUMMARIZATION]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                input_tokens_count: Optional[int] = ..., 
                model: Optional[KnowledgeBaseActivityRecordModel] = ..., 
                output_tokens_count: Optional[int] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseQueryHintProcessing(_Model):
        generated_boost: Optional[str]
        generated_filter: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                generated_boost: Optional[str] = ..., 
                generated_filter: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseReference(_Model):
        activity_source: int
        id: str
        reranker_score: Optional[float]
        source_data: Optional[dict[str, Any]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "azureBlob"
        FABRIC_DATA_AGENT = "fabricDataAgent"
        FABRIC_ONTOLOGY = "fabricOntology"
        FILE = "file"
        INDEXED_ONELAKE = "indexedOneLake"
        INDEXED_SHARE_POINT = "indexedSharePoint"
        INDEXED_SQL = "indexedSql"
        MCP_SERVER = "mcpServer"
        REMOTE_SHARE_POINT = "remoteSharePoint"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"
        WORK_IQ = "workIQ"


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRemoteSharePointActivityArguments(_Model):
        filter_expression_add_on: Optional[str]
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filter_expression_add_on: Optional[str] = ..., 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRemoteSharePointActivityRecord(KnowledgeBaseActivityRecord, discriminator='remoteSharePoint'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_time: Optional[datetime]
        remote_share_point_arguments: Optional[KnowledgeBaseRemoteSharePointActivityArguments]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.REMOTE_SHARE_POINT]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_time: Optional[datetime] = ..., 
                remote_share_point_arguments: Optional[KnowledgeBaseRemoteSharePointActivityArguments] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRemoteSharePointReference(KnowledgeBaseReference, discriminator='remoteSharePoint'):
        activity_source: int
        id: str
        reranker_score: float
        search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.REMOTE_SHARE_POINT]
        web_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                id: str, 
                reranker_score: Optional[float] = ..., 
                search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ..., 
                source_data: Optional[dict[str, Any]] = ..., 
                web_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseResponseCompletedEvent(_Model):
        response: KnowledgeBaseRetrievalResponse
        status_code: Union[int, KnowledgeBaseRetrievalStatusCode]

        @overload
        def __init__(
                self, 
                *, 
                response: KnowledgeBaseRetrievalResponse, 
                status_code: Union[int, KnowledgeBaseRetrievalStatusCode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest(_Model):
        include_activity: Optional[bool]
        intents: Optional[list[KnowledgeRetrievalIntent]]
        knowledge_source_params: Optional[list[KnowledgeSourceParams]]
        max_output_documents: Optional[int]
        max_output_size: Optional[int]
        max_output_size_in_tokens: Optional[int]
        max_runtime_in_seconds: Optional[int]
        messages: Optional[list[KnowledgeBaseMessage]]
        output_mode: Optional[Union[str, KnowledgeRetrievalOutputMode]]
        retrieval_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort]

        @overload
        def __init__(
                self, 
                *, 
                include_activity: Optional[bool] = ..., 
                intents: Optional[list[KnowledgeRetrievalIntent]] = ..., 
                knowledge_source_params: Optional[list[KnowledgeSourceParams]] = ..., 
                max_output_documents: Optional[int] = ..., 
                max_output_size: Optional[int] = ..., 
                max_output_size_in_tokens: Optional[int] = ..., 
                max_runtime_in_seconds: Optional[int] = ..., 
                messages: Optional[list[KnowledgeBaseMessage]] = ..., 
                output_mode: Optional[Union[str, KnowledgeRetrievalOutputMode]] = ..., 
                retrieval_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalResponse(_Model):
        activity: Optional[list[KnowledgeBaseActivityRecord]]
        references: Optional[list[KnowledgeBaseReference]]
        response: Optional[list[KnowledgeBaseMessage]]
        response_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]

        @overload
        def __init__(
                self, 
                *, 
                activity: Optional[list[KnowledgeBaseActivityRecord]] = ..., 
                references: Optional[list[KnowledgeBaseReference]] = ..., 
                response: Optional[list[KnowledgeBaseMessage]] = ..., 
                response_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalStartedEvent(_Model):
        knowledge_base_name: str
        output_mode: Union[str, KnowledgeRetrievalOutputMode]
        reasoning_effort: KnowledgeRetrievalReasoningEffort
        request_id: str

        @overload
        def __init__(
                self, 
                *, 
                knowledge_base_name: str, 
                output_mode: Union[str, KnowledgeRetrievalOutputMode], 
                reasoning_effort: KnowledgeRetrievalReasoningEffort, 
                request_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalStatusCode(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        OK = 200
        PARTIAL_CONTENT = 206


    class azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexActivityArguments(_Model):
        filter: Optional[str]
        query_type: Optional[Union[str, QueryType]]
        search: Optional[str]
        search_fields: Optional[list[SearchIndexFieldReference]]
        semantic_configuration_name: Optional[str]
        source_data_fields: Optional[list[SearchIndexFieldReference]]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                query_type: Optional[Union[str, QueryType]] = ..., 
                search: Optional[str] = ..., 
                search_fields: Optional[list[SearchIndexFieldReference]] = ..., 
                semantic_configuration_name: Optional[str] = ..., 
                source_data_fields: Optional[list[SearchIndexFieldReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexActivityRecord(KnowledgeBaseActivityRecord, discriminator='searchIndex'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing]
        query_time: Optional[datetime]
        search_index_arguments: Optional[KnowledgeBaseSearchIndexActivityArguments]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.SEARCH_INDEX]
        warning: str

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_hint_processing: Optional[KnowledgeBaseQueryHintProcessing] = ..., 
                query_time: Optional[datetime] = ..., 
                search_index_arguments: Optional[KnowledgeBaseSearchIndexActivityArguments] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexReference(KnowledgeBaseReference, discriminator='searchIndex'):
        activity_source: int
        citation_url: Optional[str]
        doc_key: Optional[str]
        id: str
        reranker_score: float
        search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.SEARCH_INDEX]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                citation_url: Optional[str] = ..., 
                doc_key: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseStreamErrorEvent(_Model):
        activity: Optional[list[KnowledgeBaseActivityRecord]]
        error: Optional[KnowledgeBaseErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                activity: Optional[list[KnowledgeBaseActivityRecord]] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseWebActivityArguments(_Model):
        count: Optional[int]
        freshness: Optional[str]
        language: Optional[str]
        market: Optional[str]
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                language: Optional[str] = ..., 
                market: Optional[str] = ..., 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseWebActivityRecord(KnowledgeBaseActivityRecord, discriminator='web'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.WEB]
        warning: str
        web_arguments: Optional[KnowledgeBaseWebActivityArguments]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ..., 
                web_arguments: Optional[KnowledgeBaseWebActivityArguments] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseWebReference(KnowledgeBaseReference, discriminator='web'):
        activity_source: int
        id: str
        reranker_score: float
        source_data: dict[str, any]
        title: Optional[str]
        type: Literal[KnowledgeBaseReferenceType.WEB]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ..., 
                title: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseWorkIQActivityArguments(_Model):
        search: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                search: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseWorkIQActivityRecord(KnowledgeBaseActivityRecord, discriminator='workIQ'):
        completed_at: datetime
        count: Optional[int]
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        image_serving: Optional[ImageServingStatistics]
        knowledge_source_name: Optional[str]
        query_time: Optional[datetime]
        started_at: datetime
        type: Literal[KnowledgeBaseActivityRecordType.WORK_IQ]
        warning: str
        work_iq_arguments: Optional[KnowledgeBaseWorkIQActivityArguments]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                count: Optional[int] = ..., 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                image_serving: Optional[ImageServingStatistics] = ..., 
                knowledge_source_name: Optional[str] = ..., 
                query_time: Optional[datetime] = ..., 
                started_at: Optional[datetime] = ..., 
                warning: Optional[str] = ..., 
                work_iq_arguments: Optional[KnowledgeBaseWorkIQActivityArguments] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseWorkIQReference(KnowledgeBaseReference, discriminator='workIQ'):
        activity_source: int
        id: str
        reranker_score: float
        search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo]
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.WORK_IQ]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                id: str, 
                reranker_score: Optional[float] = ..., 
                search_sensitivity_label_info: Optional[PurviewSensitivityLabelInfo] = ..., 
                source_data: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalAutoReasoningEffort(KnowledgeRetrievalReasoningEffort, discriminator='auto'):
        kind: Literal[KnowledgeRetrievalReasoningEffortKind.AUTO]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalIntent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalIntentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC = "semantic"


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalLowReasoningEffort(KnowledgeRetrievalReasoningEffort, discriminator='low'):
        kind: Literal[KnowledgeRetrievalReasoningEffortKind.LOW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalMediumReasoningEffort(KnowledgeRetrievalReasoningEffort, discriminator='medium'):
        kind: Literal[KnowledgeRetrievalReasoningEffortKind.MEDIUM]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalMinimalReasoningEffort(KnowledgeRetrievalReasoningEffort, discriminator='minimal'):
        kind: Literal[KnowledgeRetrievalReasoningEffortKind.MINIMAL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalOutputMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANSWER_SYNTHESIS = "answerSynthesis"
        EXTRACTIVE_DATA = "extractiveData"


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalReasoningEffort(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalReasoningEffortKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalSemanticIntent(KnowledgeRetrievalIntent, discriminator='semantic'):
        search: str
        type: Literal[KnowledgeRetrievalIntentType.SEMANTIC]

        @overload
        def __init__(
                self, 
                *, 
                search: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceAzureOpenAIVectorizer(KnowledgeSourceVectorizer, discriminator='azureOpenAI'):
        azure_open_ai_parameters: Optional[AzureOpenAIVectorizerParameters]
        kind: Literal[VectorSearchVectorizerKind.AZURE_OPEN_AI]

        @overload
        def __init__(
                self, 
                *, 
                azure_open_ai_parameters: Optional[AzureOpenAIVectorizerParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceIngestionParameters(_Model):
        ai_services: Optional[AIServices]
        asset_store: Optional[AssetStore]
        chat_completion_model: Optional[KnowledgeBaseModel]
        content_extraction_mode: Optional[Union[str, KnowledgeSourceContentExtractionMode]]
        disable_image_verbalization: Optional[bool]
        embedding_model: Optional[KnowledgeSourceVectorizer]
        freshness_policy: Optional[FreshnessPolicy]
        identity: Optional[SearchIndexerDataIdentity]
        ingestion_permission_options: Optional[list[Union[str, KnowledgeSourceIngestionPermissionOption]]]
        ingestion_schedule: Optional[IndexingSchedule]
        network_access_mode: Optional[Union[str, KnowledgeSourceNetworkAccessMode]]

        @overload
        def __init__(
                self, 
                *, 
                ai_services: Optional[AIServices] = ..., 
                asset_store: Optional[AssetStore] = ..., 
                chat_completion_model: Optional[KnowledgeBaseModel] = ..., 
                content_extraction_mode: Optional[Union[str, KnowledgeSourceContentExtractionMode]] = ..., 
                disable_image_verbalization: Optional[bool] = ..., 
                embedding_model: Optional[KnowledgeSourceVectorizer] = ..., 
                freshness_policy: Optional[FreshnessPolicy] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                ingestion_permission_options: Optional[list[Union[str, KnowledgeSourceIngestionPermissionOption]]] = ..., 
                ingestion_schedule: Optional[IndexingSchedule] = ..., 
                network_access_mode: Optional[Union[str, KnowledgeSourceNetworkAccessMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceNetworkAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "private"
        PUBLIC = "public"


    class azure.search.documents.knowledgebases.models.KnowledgeSourceParams(_Model):
        always_query_source: Optional[bool]
        enable_image_serving: Optional[bool]
        fail_on_error: Optional[bool]
        include_reference_source_data: Optional[bool]
        include_references: Optional[bool]
        kind: str
        knowledge_source_name: str
        max_output_documents: Optional[int]
        never_query_source: Optional[bool]
        reranker_threshold: Optional[float]
        results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                kind: str, 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceStatistics(_Model):
        average_items_processed_per_synchronization: int
        average_synchronization_duration: str
        total_synchronization: int

        @overload
        def __init__(
                self, 
                *, 
                average_items_processed_per_synchronization: int, 
                average_synchronization_duration: str, 
                total_synchronization: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceStatus(_Model):
        current_synchronization_state: Optional[SynchronizationState]
        kind: Optional[Union[str, KnowledgeSourceKind]]
        last_synchronization_state: Optional[CompletedSynchronizationState]
        statistics: Optional[KnowledgeSourceStatistics]
        synchronization_interval: Optional[str]
        synchronization_status: Union[str, KnowledgeSourceSynchronizationStatus]

        @overload
        def __init__(
                self, 
                *, 
                current_synchronization_state: Optional[SynchronizationState] = ..., 
                kind: Optional[Union[str, KnowledgeSourceKind]] = ..., 
                last_synchronization_state: Optional[CompletedSynchronizationState] = ..., 
                statistics: Optional[KnowledgeSourceStatistics] = ..., 
                synchronization_interval: Optional[str] = ..., 
                synchronization_status: Union[str, KnowledgeSourceSynchronizationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceSynchronizationError(_Model):
        details: Optional[str]
        doc_id: Optional[str]
        documentation_link: Optional[str]
        error_message: str
        name: Optional[str]
        status_code: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[str] = ..., 
                doc_id: Optional[str] = ..., 
                documentation_link: Optional[str] = ..., 
                error_message: str, 
                name: Optional[str] = ..., 
                status_code: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceVectorizer(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.McpServerKnowledgeSourceParams(KnowledgeSourceParams, discriminator='mcpServer'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.MCP_SERVER]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.PurviewSensitivityLabelInfo(_Model):
        color: Optional[str]
        display_name: Optional[str]
        is_encrypted: Optional[bool]
        priority: Optional[int]
        sensitivity_label_id: Optional[str]
        tool_tip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                color: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_encrypted: Optional[bool] = ..., 
                priority: Optional[int] = ..., 
                sensitivity_label_id: Optional[str] = ..., 
                tool_tip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.RemoteSharePointKnowledgeSourceParams(KnowledgeSourceParams, discriminator='remoteSharePoint'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        filter_expression_add_on: Optional[str]
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.REMOTE_SHARE_POINT]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                filter_expression_add_on: Optional[str] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.SearchIndexKnowledgeSourceParams(KnowledgeSourceParams, discriminator='searchIndex'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        filter_add_on: Optional[str]
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.SEARCH_INDEX]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints]
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                filter_add_on: Optional[str] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                query_hint_overrides: Optional[SearchIndexKnowledgeSourceQueryHints] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.ServedImage(_Model):
        image_id: Optional[str]
        image_path: Optional[str]
        size_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                image_id: Optional[str] = ..., 
                image_path: Optional[str] = ..., 
                size_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.SynchronizationState(_Model):
        errors: Optional[list[KnowledgeSourceSynchronizationError]]
        items_skipped: int
        items_updates_failed: int
        items_updates_processed: int
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[KnowledgeSourceSynchronizationError]] = ..., 
                items_skipped: int, 
                items_updates_failed: int, 
                items_updates_processed: int, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.WebKnowledgeSourceParams(KnowledgeSourceParams, discriminator='web'):
        always_query_source: bool
        count: Optional[int]
        enable_image_serving: bool
        fail_on_error: bool
        freshness: Optional[str]
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.WEB]
        knowledge_source_name: str
        language: Optional[str]
        market: Optional[str]
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                count: Optional[int] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                freshness: Optional[str] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                language: Optional[str] = ..., 
                market: Optional[str] = ..., 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.WorkIQKnowledgeSourceParams(KnowledgeSourceParams, discriminator='workIQ'):
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.WORK_IQ]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]

        @overload
        def __init__(
                self, 
                *, 
                always_query_source: Optional[bool] = ..., 
                enable_image_serving: Optional[bool] = ..., 
                fail_on_error: Optional[bool] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                max_output_documents: Optional[int] = ..., 
                never_query_source: Optional[bool] = ..., 
                reranker_threshold: Optional[float] = ..., 
                results_processing: Optional[Union[str, KnowledgeSourceResultsProcessing]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.search.documents.knowledgebases.types

    class azure.search.documents.knowledgebases.types.AIServices(TypedDict, total=False):
        key "apiKey": str
        api_key: str
        uri: Required[str]


    class azure.search.documents.knowledgebases.types.AssetStore(TypedDict, total=False):
        connectionString: Required[str]
        connection_string: str
        containerName: Required[str]
        container_name: str


    class azure.search.documents.knowledgebases.types.AzureBlobKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "queryHintOverrides": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.AZURE_BLOB]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: SearchIndexKnowledgeSourceQueryHints
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.CompletedSynchronizationState(TypedDict, total=False):
        endTime: Required[str]
        end_time: str
        itemsSkipped: Required[int]
        itemsUpdatesFailed: Required[int]
        itemsUpdatesProcessed: Required[int]
        items_skipped: int
        items_updates_failed: int
        items_updates_processed: int
        startTime: Required[str]
        start_time: str


    class azure.search.documents.knowledgebases.types.FabricDataAgentKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.FABRIC_DATA_AGENT]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.FabricOntologyKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.FABRIC_ONTOLOGY]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.FileKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "queryHintOverrides": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.FILE]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: SearchIndexKnowledgeSourceQueryHints
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.FreshnessPolicy(TypedDict, total=False):
        key "boostingDuration": str
        boosting_duration: str


    class azure.search.documents.knowledgebases.types.IndexedOneLakeKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "queryHintOverrides": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.INDEXED_ONELAKE]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: SearchIndexKnowledgeSourceQueryHints
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.IndexedSharePointKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "queryHintOverrides": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.INDEXED_SHARE_POINT]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: SearchIndexKnowledgeSourceQueryHints
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.IndexedSqlKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "queryHintOverrides": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.INDEXED_SQL]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: SearchIndexKnowledgeSourceQueryHints
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.KnowledgeBaseImageContent(TypedDict, total=False):
        url: Required[str]


    class azure.search.documents.knowledgebases.types.KnowledgeBaseMessage(TypedDict, total=False):
        key "role": str
        content: Required[list[KnowledgeBaseMessageContent]]
        role: str


    class azure.search.documents.knowledgebases.types.KnowledgeBaseMessageContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "image"
        TEXT = "text"


    class azure.search.documents.knowledgebases.types.KnowledgeBaseMessageImageContent(TypedDict, total=False):
        image: Required[KnowledgeBaseImageContent]
        type: Required[Literal[KnowledgeBaseMessageContentType.IMAGE]]


    class azure.search.documents.knowledgebases.types.KnowledgeBaseMessageTextContent(TypedDict, total=False):
        text: Required[str]
        type: Required[Literal[KnowledgeBaseMessageContentType.TEXT]]


    class azure.search.documents.knowledgebases.types.KnowledgeBaseRetrievalRequest(TypedDict, total=False):
        key "includeActivity": bool
        key "intents": list[KnowledgeRetrievalIntent]
        key "knowledgeSourceParams": list[KnowledgeSourceParams]
        key "maxOutputDocuments": int
        key "maxOutputSize": int
        key "maxOutputSizeInTokens": int
        key "maxRuntimeInSeconds": int
        key "messages": list[KnowledgeBaseMessage]
        key "outputMode": Union[str, KnowledgeRetrievalOutputMode]
        key "retrievalReasoningEffort": ForwardRef('KnowledgeRetrievalReasoningEffort')
        include_activity: bool
        intents: list[KnowledgeRetrievalIntent]
        knowledge_source_params: list[KnowledgeSourceParams]
        max_output_documents: int
        max_output_size: int
        max_output_size_in_tokens: int
        max_runtime_in_seconds: int
        messages: list[KnowledgeBaseMessage]
        output_mode: Union[str, KnowledgeRetrievalOutputMode]
        retrieval_reasoning_effort: KnowledgeRetrievalReasoningEffort


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalAutoReasoningEffort(TypedDict, total=False):
        kind: Required[Literal[KnowledgeRetrievalReasoningEffortKind.AUTO]]


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalIntent(TypedDict, total=False):
        search: Required[str]
        type: Required[Literal[KnowledgeRetrievalIntentType.SEMANTIC]]


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalIntentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC = "semantic"


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalLowReasoningEffort(TypedDict, total=False):
        kind: Required[Literal[KnowledgeRetrievalReasoningEffortKind.LOW]]


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalMediumReasoningEffort(TypedDict, total=False):
        kind: Required[Literal[KnowledgeRetrievalReasoningEffortKind.MEDIUM]]


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalMinimalReasoningEffort(TypedDict, total=False):
        kind: Required[Literal[KnowledgeRetrievalReasoningEffortKind.MINIMAL]]


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalReasoningEffortKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"


    class azure.search.documents.knowledgebases.types.KnowledgeRetrievalSemanticIntent(TypedDict, total=False):
        search: Required[str]
        type: Required[Literal[KnowledgeRetrievalIntentType.SEMANTIC]]


    class azure.search.documents.knowledgebases.types.KnowledgeSourceAzureOpenAIVectorizer(TypedDict, total=False):
        key "azureOpenAIParameters": ForwardRef('AzureOpenAIVectorizerParameters')
        azure_open_ai_parameters: AzureOpenAIVectorizerParameters
        kind: Required[Literal[VectorSearchVectorizerKind.AZURE_OPEN_AI]]


    class azure.search.documents.knowledgebases.types.KnowledgeSourceIngestionParameters(TypedDict, total=False):
        key "aiServices": Optional[AIServices]
        key "assetStore": ForwardRef('AssetStore')
        key "chatCompletionModel": Optional[KnowledgeBaseModel]
        key "contentExtractionMode": Optional[Union[str, KnowledgeSourceContentExtractionMode]]
        key "disableImageVerbalization": bool
        key "embeddingModel": Optional[KnowledgeSourceVectorizer]
        key "freshnessPolicy": ForwardRef('FreshnessPolicy')
        key "identity": Optional[SearchIndexerDataIdentity]
        key "ingestionPermissionOptions": Optional[list[Union[str, KnowledgeSourceIngestionPermissionOption]]]
        key "ingestionSchedule": Optional[IndexingSchedule]
        key "networkAccessMode": Union[str, KnowledgeSourceNetworkAccessMode]
        ai_services: AIServices
        asset_store: AssetStore
        chat_completion_model: KnowledgeBaseModel
        content_extraction_mode: Union[str, KnowledgeSourceContentExtractionMode]
        disable_image_verbalization: bool
        embedding_model: KnowledgeSourceVectorizer
        freshness_policy: FreshnessPolicy
        identity: SearchIndexerDataIdentity
        ingestion_permission_options: list[Union[str, KnowledgeSourceIngestionPermissionOption]]
        ingestion_schedule: IndexingSchedule
        network_access_mode: Union[str, KnowledgeSourceNetworkAccessMode]


    class azure.search.documents.knowledgebases.types.KnowledgeSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "azureBlob"
        FABRIC_DATA_AGENT = "fabricDataAgent"
        FABRIC_ONTOLOGY = "fabricOntology"
        FILE = "file"
        INDEXED_ONELAKE = "indexedOneLake"
        INDEXED_SHARE_POINT = "indexedSharePoint"
        INDEXED_SQL = "indexedSql"
        MCP_SERVER = "mcpServer"
        REMOTE_SHARE_POINT = "remoteSharePoint"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"
        WORK_IQ = "workIQ"


    class azure.search.documents.knowledgebases.types.KnowledgeSourceStatistics(TypedDict, total=False):
        averageItemsProcessedPerSynchronization: Required[int]
        averageSynchronizationDuration: Required[str]
        average_items_processed_per_synchronization: int
        average_synchronization_duration: str
        totalSynchronization: Required[int]
        total_synchronization: int


    class azure.search.documents.knowledgebases.types.KnowledgeSourceStatus(TypedDict, total=False):
        key "currentSynchronizationState": Optional[SynchronizationState]
        key "kind": Union[str, KnowledgeSourceKind]
        key "lastSynchronizationState": Optional[CompletedSynchronizationState]
        key "statistics": Optional[KnowledgeSourceStatistics]
        key "synchronizationInterval": Optional[str]
        current_synchronization_state: SynchronizationState
        kind: Union[str, KnowledgeSourceKind]
        last_synchronization_state: CompletedSynchronizationState
        statistics: KnowledgeSourceStatistics
        synchronizationStatus: Required[Union[str, KnowledgeSourceSynchronizationStatus]]
        synchronization_interval: str
        synchronization_status: Union[str, KnowledgeSourceSynchronizationStatus]


    class azure.search.documents.knowledgebases.types.KnowledgeSourceSynchronizationError(TypedDict, total=False):
        key "details": str
        key "docId": str
        key "documentationLink": str
        key "name": str
        key "statusCode": int
        details: str
        doc_id: str
        documentation_link: str
        errorMessage: Required[str]
        error_message: str
        name: str
        status_code: int


    class azure.search.documents.knowledgebases.types.KnowledgeSourceVectorizer(TypedDict, total=False):
        key "azureOpenAIParameters": ForwardRef('AzureOpenAIVectorizerParameters')
        azure_open_ai_parameters: AzureOpenAIVectorizerParameters
        kind: Required[Literal[VectorSearchVectorizerKind.AZURE_OPEN_AI]]


    class azure.search.documents.knowledgebases.types.McpServerKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.MCP_SERVER]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.RemoteSharePointKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "filterExpressionAddOn": str
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        filter_expression_add_on: str
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.REMOTE_SHARE_POINT]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.SearchIndexKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "filterAddOn": str
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "queryHintOverrides": ForwardRef('SearchIndexKnowledgeSourceQueryHints')
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        filter_add_on: str
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.SEARCH_INDEX]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        query_hint_overrides: SearchIndexKnowledgeSourceQueryHints
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.SynchronizationState(TypedDict, total=False):
        key "errors": list[KnowledgeSourceSynchronizationError]
        errors: list[KnowledgeSourceSynchronizationError]
        itemsSkipped: Required[int]
        itemsUpdatesFailed: Required[int]
        itemsUpdatesProcessed: Required[int]
        items_skipped: int
        items_updates_failed: int
        items_updates_processed: int
        startTime: Required[str]
        start_time: str


    class azure.search.documents.knowledgebases.types.VectorSearchVectorizerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AI_SERVICES_VISION = "aiServicesVision"
        AML = "aml"
        AZURE_OPEN_AI = "azureOpenAI"
        CUSTOM_WEB_API = "customWebApi"


    class azure.search.documents.knowledgebases.types.WebKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "count": int
        key "enableImageServing": bool
        key "failOnError": bool
        key "freshness": str
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "language": str
        key "market": str
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        count: int
        enable_image_serving: bool
        fail_on_error: bool
        freshness: str
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.WEB]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        language: str
        market: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


    class azure.search.documents.knowledgebases.types.WorkIQKnowledgeSourceParams(TypedDict, total=False):
        key "alwaysQuerySource": bool
        key "enableImageServing": bool
        key "failOnError": bool
        key "includeReferenceSourceData": bool
        key "includeReferences": bool
        key "maxOutputDocuments": int
        key "neverQuerySource": bool
        key "rerankerThreshold": float
        key "resultsProcessing": Union[str, KnowledgeSourceResultsProcessing]
        always_query_source: bool
        enable_image_serving: bool
        fail_on_error: bool
        include_reference_source_data: bool
        include_references: bool
        kind: Required[Literal[KnowledgeSourceKind.WORK_IQ]]
        knowledgeSourceName: Required[str]
        knowledge_source_name: str
        max_output_documents: int
        never_query_source: bool
        reranker_threshold: float
        results_processing: Union[str, KnowledgeSourceResultsProcessing]


namespace azure.search.documents.models

    class azure.search.documents.models.AutocompleteItem(_Model):
        query_plus_text: str
        text: str


    class azure.search.documents.models.AutocompleteMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_TERM = "oneTerm"
        ONE_TERM_WITH_CONTEXT = "oneTermWithContext"
        TWO_TERMS = "twoTerms"


    class azure.search.documents.models.DebugInfo(_Model):
        query_rewrites: Optional[QueryRewritesDebugInfo]


    class azure.search.documents.models.DocumentDebugInfo(_Model):
        inner_hits: Optional[dict[str, list[QueryResultDocumentInnerHit]]]
        semantic: Optional[SemanticDebugInfo]
        vectors: Optional[VectorsDebugInfo]


    class azure.search.documents.models.ErrorAdditionalInfo(_Model):
        info: Optional[dict[str, Any]]
        type: Optional[str]


    class azure.search.documents.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.search.documents.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.FacetResult(_Model):
        avg: Optional[float]
        cardinality: Optional[int]
        count: Optional[int]
        facets: Optional[dict[str, list[FacetResult]]]
        max: Optional[float]
        min: Optional[float]
        sum: Optional[float]


    class azure.search.documents.models.HybridCountAndFacetMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT_ALL_RESULTS = "countAllResults"
        COUNT_RETRIEVABLE_RESULTS = "countRetrievableResults"


    class azure.search.documents.models.HybridSearch(_Model):
        count_and_facet_mode: Optional[Union[str, HybridCountAndFacetMode]]
        max_text_recall_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count_and_facet_mode: Optional[Union[str, HybridCountAndFacetMode]] = ..., 
                max_text_recall_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.IndexAction(_Model):
        action_type: Optional[Union[str, IndexActionType]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, IndexActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.IndexActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "delete"
        MERGE = "merge"
        MERGE_OR_UPLOAD = "mergeOrUpload"
        UPLOAD = "upload"


    class azure.search.documents.models.IndexDocumentsBatch(MutableMapping[str, Any]):
        property actions: List[IndexAction]

        def __init__(
                self, 
                *, 
                actions: Optional[List[IndexAction]] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def add_delete_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def add_merge_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def add_merge_or_upload_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def add_upload_actions(
                self, 
                *documents: Union[List[Dict], List[List[Dict]]], 
                **kwargs: Any
            ) -> List[IndexAction]: ...

        def dequeue_actions(self, **kwargs: Any) -> List[IndexAction]: ...

        def enqueue_actions(
                self, 
                new_actions: Union[IndexAction, List[IndexAction]], 
                **kwargs: Any
            ) -> None: ...


    class azure.search.documents.models.IndexingResult(_Model):
        error_message: Optional[str]
        key: str
        status_code: int
        succeeded: bool


    class azure.search.documents.models.LookupDocument(_Model):


    class azure.search.documents.models.QueryAnswerResult(_Model):
        highlights: Optional[str]
        key: Optional[str]
        score: Optional[float]
        text: Optional[str]


    class azure.search.documents.models.QueryAnswerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACTIVE = "extractive"
        NONE = "none"


    class azure.search.documents.models.QueryCaptionResult(_Model):
        highlights: Optional[str]
        text: Optional[str]


    class azure.search.documents.models.QueryCaptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACTIVE = "extractive"
        NONE = "none"


    class azure.search.documents.models.QueryDebugMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        DISABLED = "disabled"
        INNER_HITS = "innerHits"
        QUERY_REWRITES = "queryRewrites"
        SEMANTIC = "semantic"
        VECTOR = "vector"


    class azure.search.documents.models.QueryLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AR_EG = "ar-eg"
        AR_JO = "ar-jo"
        AR_KW = "ar-kw"
        AR_MA = "ar-ma"
        AR_SA = "ar-sa"
        BG_BG = "bg-bg"
        BN_IN = "bn-in"
        CA_ES = "ca-es"
        CS_CZ = "cs-cz"
        DA_DK = "da-dk"
        DE_DE = "de-de"
        EL_GR = "el-gr"
        EN_AU = "en-au"
        EN_CA = "en-ca"
        EN_GB = "en-gb"
        EN_IN = "en-in"
        EN_US = "en-us"
        ES_ES = "es-es"
        ES_MX = "es-mx"
        ET_EE = "et-ee"
        EU_ES = "eu-es"
        FA_AE = "fa-ae"
        FI_FI = "fi-fi"
        FR_CA = "fr-ca"
        FR_FR = "fr-fr"
        GA_IE = "ga-ie"
        GL_ES = "gl-es"
        GU_IN = "gu-in"
        HE_IL = "he-il"
        HI_IN = "hi-in"
        HR_BA = "hr-ba"
        HR_HR = "hr-hr"
        HU_HU = "hu-hu"
        HY_AM = "hy-am"
        ID_ID = "id-id"
        IS_IS = "is-is"
        IT_IT = "it-it"
        JA_JP = "ja-jp"
        KN_IN = "kn-in"
        KO_KR = "ko-kr"
        LT_LT = "lt-lt"
        LV_LV = "lv-lv"
        ML_IN = "ml-in"
        MR_IN = "mr-in"
        MS_BN = "ms-bn"
        MS_MY = "ms-my"
        NB_NO = "nb-no"
        NL_BE = "nl-be"
        NL_NL = "nl-nl"
        NONE = "none"
        NO_NO = "no-no"
        PA_IN = "pa-in"
        PL_PL = "pl-pl"
        PT_BR = "pt-br"
        PT_PT = "pt-pt"
        RO_RO = "ro-ro"
        RU_RU = "ru-ru"
        SK_SK = "sk-sk"
        SL_SL = "sl-sl"
        SR_BA = "sr-ba"
        SR_ME = "sr-me"
        SR_RS = "sr-rs"
        SV_SE = "sv-se"
        TA_IN = "ta-in"
        TE_IN = "te-in"
        TH_TH = "th-th"
        TR_TR = "tr-tr"
        UK_UA = "uk-ua"
        UR_PK = "ur-pk"
        VI_VN = "vi-vn"
        ZH_CN = "zh-cn"
        ZH_TW = "zh-tw"


    class azure.search.documents.models.QueryResultDocumentInnerHit(_Model):
        ordinal: Optional[int]
        vectors: Optional[list[dict[str, SingleVectorFieldResult]]]


    class azure.search.documents.models.QueryResultDocumentRerankerInput(_Model):
        content: Optional[str]
        keywords: Optional[str]
        title: Optional[str]


    class azure.search.documents.models.QueryResultDocumentSemanticField(_Model):
        name: Optional[str]
        state: Optional[Union[str, SemanticFieldState]]


    class azure.search.documents.models.QueryResultDocumentSubscores(_Model):
        document_boost: Optional[float]
        text: Optional[TextResult]
        vectors: Optional[list[dict[str, SingleVectorFieldResult]]]


    class azure.search.documents.models.QueryRewritesDebugInfo(_Model):
        text: Optional[QueryRewritesValuesDebugInfo]
        vectors: Optional[list[QueryRewritesValuesDebugInfo]]


    class azure.search.documents.models.QueryRewritesType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERATIVE = "generative"
        NONE = "none"


    class azure.search.documents.models.QueryRewritesValuesDebugInfo(_Model):
        input_query: Optional[str]
        rewrites: Optional[list[str]]


    class azure.search.documents.models.QuerySpellerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEXICON = "lexicon"
        NONE = "none"


    class azure.search.documents.models.QueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "full"
        SEMANTIC = "semantic"
        SIMPLE = "simple"


    class azure.search.documents.models.ScoringStatistics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "global"
        LOCAL = "local"


    class azure.search.documents.models.SearchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        ANY = "any"


    class azure.search.documents.models.SearchResult(_Model):
        captions: Optional[list[QueryCaptionResult]]
        document_debug_info: Optional[DocumentDebugInfo]
        highlights: Optional[dict[str, list[str]]]
        reranker_boosted_score: Optional[float]
        reranker_score: Optional[float]
        score: float


    class azure.search.documents.models.SearchScoreThreshold(VectorThreshold, discriminator='searchScore'):
        kind: Literal[VectorThresholdKind.SEARCH_SCORE]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.SemanticDebugInfo(_Model):
        content_fields: Optional[list[QueryResultDocumentSemanticField]]
        keyword_fields: Optional[list[QueryResultDocumentSemanticField]]
        reranker_input: Optional[QueryResultDocumentRerankerInput]
        title_field: Optional[QueryResultDocumentSemanticField]


    class azure.search.documents.models.SemanticErrorMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL = "fail"
        PARTIAL = "partial"


    class azure.search.documents.models.SemanticErrorReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_OVERLOADED = "capacityOverloaded"
        MAX_WAIT_EXCEEDED = "maxWaitExceeded"
        TRANSIENT = "transient"


    class azure.search.documents.models.SemanticFieldState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PARTIAL = "partial"
        UNUSED = "unused"
        USED = "used"


    class azure.search.documents.models.SemanticSearchResultsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE_RESULTS = "baseResults"
        RERANKED_RESULTS = "rerankedResults"


    class azure.search.documents.models.SingleVectorFieldResult(_Model):
        search_score: Optional[float]
        vector_similarity: Optional[float]


    class azure.search.documents.models.SuggestResult(_Model):
        text: str


    class azure.search.documents.models.TextResult(_Model):
        search_score: Optional[float]


    class azure.search.documents.models.VectorFilterMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POST_FILTER = "postFilter"
        PRE_FILTER = "preFilter"
        STRICT_POST_FILTER = "strictPostFilter"


    class azure.search.documents.models.VectorQuery(_Model):
        exhaustive: Optional[bool]
        fields: Optional[str]
        filter_override: Optional[str]
        k_nearest_neighbors: Optional[int]
        kind: str
        oversampling: Optional[float]
        per_document_vector_limit: Optional[int]
        threshold: Optional[VectorThreshold]
        weight: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                filter_override: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                kind: str, 
                oversampling: Optional[float] = ..., 
                per_document_vector_limit: Optional[int] = ..., 
                threshold: Optional[VectorThreshold] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE_BINARY = "imageBinary"
        IMAGE_URL = "imageUrl"
        TEXT = "text"
        VECTOR = "vector"


    class azure.search.documents.models.VectorSimilarityThreshold(VectorThreshold, discriminator='vectorSimilarity'):
        kind: Literal[VectorThresholdKind.VECTOR_SIMILARITY]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorThreshold(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorThresholdKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEARCH_SCORE = "searchScore"
        VECTOR_SIMILARITY = "vectorSimilarity"


    class azure.search.documents.models.VectorizableImageBinaryQuery(VectorQuery, discriminator='imageBinary'):
        base64_image: Optional[str]
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.IMAGE_BINARY]
        oversampling: float
        per_document_vector_limit: int
        threshold: VectorThreshold
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                base64_image: Optional[str] = ..., 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                filter_override: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                per_document_vector_limit: Optional[int] = ..., 
                threshold: Optional[VectorThreshold] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorizableImageUrlQuery(VectorQuery, discriminator='imageUrl'):
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.IMAGE_URL]
        oversampling: float
        per_document_vector_limit: int
        threshold: VectorThreshold
        url: Optional[str]
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                filter_override: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                per_document_vector_limit: Optional[int] = ..., 
                threshold: Optional[VectorThreshold] = ..., 
                url: Optional[str] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorizableTextQuery(VectorQuery, discriminator='text'):
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.TEXT]
        oversampling: float
        per_document_vector_limit: int
        query_rewrites: Optional[Union[str, QueryRewritesType]]
        text: str
        threshold: VectorThreshold
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                filter_override: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                per_document_vector_limit: Optional[int] = ..., 
                query_rewrites: Optional[Union[str, QueryRewritesType]] = ..., 
                text: str, 
                threshold: Optional[VectorThreshold] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorizedQuery(VectorQuery, discriminator='vector'):
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.VECTOR]
        oversampling: float
        per_document_vector_limit: int
        threshold: VectorThreshold
        vector: list[float]
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                filter_override: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                per_document_vector_limit: Optional[int] = ..., 
                threshold: Optional[VectorThreshold] = ..., 
                vector: list[float], 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorsDebugInfo(_Model):
        subscores: Optional[QueryResultDocumentSubscores]


namespace azure.search.documents.types

    class azure.search.documents.types.AutocompleteItem(TypedDict, total=False):
        queryPlusText: Required[str]
        query_plus_text: str
        text: Required[str]


    class azure.search.documents.types.AutocompletePostRequest(TypedDict, total=False):
        key "autocompleteMode": Union[str, AutocompleteMode]
        key "filter": str
        key "fuzzy": bool
        key "highlightPostTag": str
        key "highlightPreTag": str
        key "minimumCoverage": float
        key "searchFields": list[str]
        key "top": int
        autocomplete_mode: Union[str, AutocompleteMode]
        filter: str
        highlight_post_tag: str
        highlight_pre_tag: str
        minimum_coverage: float
        search: Required[str]
        search_fields: list[str]
        search_text: str
        suggesterName: Required[str]
        suggester_name: str
        top: int
        use_fuzzy_matching: bool


    class azure.search.documents.types.DebugInfo(TypedDict, total=False):
        key "queryRewrites": ForwardRef('QueryRewritesDebugInfo')
        query_rewrites: QueryRewritesDebugInfo


    class azure.search.documents.types.DocumentDebugInfo(TypedDict, total=False):
        key "innerHits": dict[str, list[QueryResultDocumentInnerHit]]
        key "semantic": ForwardRef('SemanticDebugInfo')
        key "vectors": ForwardRef('VectorsDebugInfo')
        inner_hits: dict[str, list[QueryResultDocumentInnerHit]]
        semantic: SemanticDebugInfo
        vectors: VectorsDebugInfo


    class azure.search.documents.types.FacetResult(TypedDict):
        key "@search.facets": dict[str, list[FacetResult]]
        key "avg": float
        key "cardinality": int
        key "count": int
        key "max": float
        key "min": float
        key "sum": float
        avg: float
        cardinality: int
        count: int
        facets: dict[str, list[FacetResult]]
        max: float
        min: float
        sum: float


    class azure.search.documents.types.HybridSearch(TypedDict, total=False):
        key "countAndFacetMode": Union[str, HybridCountAndFacetMode]
        key "maxTextRecallSize": int
        count_and_facet_mode: Union[str, HybridCountAndFacetMode]
        max_text_recall_size: int


    class azure.search.documents.types.IndexAction(TypedDict):
        key "@search.action": Union[str, IndexActionType]
        action_type: Union[str, IndexActionType]


    class azure.search.documents.types.IndexDocumentsBatch(TypedDict, total=False):
        actions: list[IndexAction]
        value: Required[list[IndexAction]]


    class azure.search.documents.types.IndexingResult(TypedDict, total=False):
        key "errorMessage": str
        error_message: str
        key: Required[str]
        status: Required[bool]
        statusCode: Required[int]
        status_code: int
        succeeded: bool


    class azure.search.documents.types.QueryAnswerResult(TypedDict, total=False):
        key "highlights": Optional[str]
        key "key": str
        key "score": float
        key "text": str
        highlights: str
        key: str
        score: float
        text: str


    class azure.search.documents.types.QueryCaptionResult(TypedDict, total=False):
        key "highlights": Optional[str]
        key "text": str
        highlights: str
        text: str


    class azure.search.documents.types.QueryResultDocumentInnerHit(TypedDict, total=False):
        key "ordinal": int
        key "vectors": list[dict[str, SingleVectorFieldResult]]
        ordinal: int
        vectors: list[dict[str, SingleVectorFieldResult]]


    class azure.search.documents.types.QueryResultDocumentRerankerInput(TypedDict, total=False):
        key "content": str
        key "keywords": str
        key "title": str
        content: str
        keywords: str
        title: str


    class azure.search.documents.types.QueryResultDocumentSemanticField(TypedDict, total=False):
        key "name": str
        key "state": Union[str, SemanticFieldState]
        name: str
        state: Union[str, SemanticFieldState]


    class azure.search.documents.types.QueryResultDocumentSubscores(TypedDict, total=False):
        key "documentBoost": float
        key "text": ForwardRef('TextResult')
        key "vectors": list[dict[str, SingleVectorFieldResult]]
        document_boost: float
        text: TextResult
        vectors: list[dict[str, SingleVectorFieldResult]]


    class azure.search.documents.types.QueryRewritesDebugInfo(TypedDict, total=False):
        key "text": ForwardRef('QueryRewritesValuesDebugInfo')
        key "vectors": list[QueryRewritesValuesDebugInfo]
        text: QueryRewritesValuesDebugInfo
        vectors: list[QueryRewritesValuesDebugInfo]


    class azure.search.documents.types.QueryRewritesValuesDebugInfo(TypedDict, total=False):
        key "inputQuery": str
        key "rewrites": list[str]
        input_query: str
        rewrites: list[str]


    class azure.search.documents.types.SearchDocumentsResult(TypedDict):
        key "@odata.count": int
        key "@odata.nextLink": str
        key "@search.answers": Optional[list[QueryAnswerResult]]
        key "@search.coverage": float
        key "@search.debug": Optional[DebugInfo]
        key "@search.facets": dict[str, list[FacetResult]]
        key "@search.nextPageParameters": ForwardRef('SearchRequest')
        key "@search.semanticPartialResponseReason": Union[str, SemanticErrorReason]
        key "@search.semanticPartialResponseType": Union[str, SemanticSearchResultsType]
        key "@search.semanticQueryRewritesResultType": Union[str, SemanticQueryRewritesResultType]
        answers: list[QueryAnswerResult]
        count: int
        coverage: float
        debug_info: DebugInfo
        facets: dict[str, list[FacetResult]]
        next_link: str
        next_page_parameters: SearchRequest
        results: list[SearchResult]
        semantic_partial_response_reason: Union[str, SemanticErrorReason]
        semantic_partial_response_type: Union[str, SemanticSearchResultsType]
        semantic_query_rewrites_result_type: Union[str, SemanticQueryRewritesResultType]
        value: Required[list[SearchResult]]


    class azure.search.documents.types.SearchPostRequest(TypedDict, total=False):
        key "answers": Union[str, QueryAnswerType]
        key "captions": Union[str, QueryCaptionType]
        key "count": bool
        key "debug": Union[str, QueryDebugMode]
        key "facets": list[str]
        key "filter": str
        key "highlight": list[str]
        key "highlightPostTag": str
        key "highlightPreTag": str
        key "hybridSearch": ForwardRef('HybridSearch')
        key "minimumCoverage": float
        key "orderby": list[str]
        key "queryLanguage": Union[str, QueryLanguage]
        key "queryRewrites": Union[str, QueryRewritesType]
        key "queryType": Union[str, QueryType]
        key "scoringParameters": list[str]
        key "scoringProfile": str
        key "scoringStatistics": Union[str, ScoringStatistics]
        key "search": str
        key "searchFields": list[str]
        key "searchMode": Union[str, SearchMode]
        key "select": list[str]
        key "semanticConfiguration": str
        key "semanticErrorHandling": Union[str, SemanticErrorMode]
        key "semanticFields": list[str]
        key "semanticMaxWaitInMilliseconds": int
        key "semanticQuery": str
        key "sessionId": str
        key "skip": int
        key "speller": Union[str, QuerySpellerType]
        key "top": int
        key "vectorFilterMode": Union[str, VectorFilterMode]
        key "vectorQueries": list[VectorQuery]
        answers: Union[str, QueryAnswerType]
        captions: Union[str, QueryCaptionType]
        debug: Union[str, QueryDebugMode]
        facets: list[str]
        filter: str
        highlight_fields: list[str]
        highlight_post_tag: str
        highlight_pre_tag: str
        hybrid_search: HybridSearch
        include_total_count: bool
        minimum_coverage: float
        order_by: list[str]
        query_language: Union[str, QueryLanguage]
        query_rewrites: Union[str, QueryRewritesType]
        query_speller: Union[str, QuerySpellerType]
        query_type: Union[str, QueryType]
        scoring_parameters: list[str]
        scoring_profile: str
        scoring_statistics: Union[str, ScoringStatistics]
        search_fields: list[str]
        search_mode: Union[str, SearchMode]
        search_text: str
        select: list[str]
        semantic_configuration_name: str
        semantic_error_handling: Union[str, SemanticErrorMode]
        semantic_fields: list[str]
        semantic_max_wait_in_milliseconds: int
        semantic_query: str
        session_id: str
        skip: int
        top: int
        vector_filter_mode: Union[str, VectorFilterMode]
        vector_queries: list[VectorQuery]


    class azure.search.documents.types.SearchRequest(TypedDict, total=False):
        key "answers": Union[str, QueryAnswerType]
        key "captions": Union[str, QueryCaptionType]
        key "count": bool
        key "debug": Union[str, QueryDebugMode]
        key "facets": list[str]
        key "filter": str
        key "highlight": list[str]
        key "highlightPostTag": str
        key "highlightPreTag": str
        key "hybridSearch": ForwardRef('HybridSearch')
        key "minimumCoverage": float
        key "orderby": list[str]
        key "queryLanguage": Union[str, QueryLanguage]
        key "queryRewrites": Union[str, QueryRewritesType]
        key "queryType": Union[str, QueryType]
        key "scoringParameters": list[str]
        key "scoringProfile": str
        key "scoringStatistics": Union[str, ScoringStatistics]
        key "search": str
        key "searchFields": list[str]
        key "searchMode": Union[str, SearchMode]
        key "select": list[str]
        key "semanticConfiguration": str
        key "semanticErrorHandling": Union[str, SemanticErrorMode]
        key "semanticFields": list[str]
        key "semanticMaxWaitInMilliseconds": int
        key "semanticQuery": str
        key "sessionId": str
        key "skip": int
        key "speller": Union[str, QuerySpellerType]
        key "top": int
        key "vectorFilterMode": Union[str, VectorFilterMode]
        key "vectorQueries": list[VectorQuery]
        answers: Union[str, QueryAnswerType]
        captions: Union[str, QueryCaptionType]
        debug: Union[str, QueryDebugMode]
        facets: list[str]
        filter: str
        highlight_fields: list[str]
        highlight_post_tag: str
        highlight_pre_tag: str
        hybrid_search: HybridSearch
        include_total_count: bool
        minimum_coverage: float
        order_by: list[str]
        query_language: Union[str, QueryLanguage]
        query_rewrites: Union[str, QueryRewritesType]
        query_speller: Union[str, QuerySpellerType]
        query_type: Union[str, QueryType]
        scoring_parameters: list[str]
        scoring_profile: str
        scoring_statistics: Union[str, ScoringStatistics]
        search_fields: list[str]
        search_mode: Union[str, SearchMode]
        search_text: str
        select: list[str]
        semantic_configuration_name: str
        semantic_error_handling: Union[str, SemanticErrorMode]
        semantic_fields: list[str]
        semantic_max_wait_in_milliseconds: int
        semantic_query: str
        session_id: str
        skip: int
        top: int
        vector_filter_mode: Union[str, VectorFilterMode]
        vector_queries: list[VectorQuery]


    class azure.search.documents.types.SearchResult(TypedDict):
        key "@search.captions": Optional[list[QueryCaptionResult]]
        key "@search.documentDebugInfo": Optional[DocumentDebugInfo]
        key "@search.highlights": dict[str, list[str]]
        key "@search.rerankerBoostedScore": Optional[float]
        key "@search.rerankerScore": Optional[float]
        @search.score: Required[float]
        captions: list[QueryCaptionResult]
        document_debug_info: DocumentDebugInfo
        highlights: dict[str, list[str]]
        reranker_boosted_score: float
        reranker_score: float
        score: float


    class azure.search.documents.types.SearchScoreThreshold(TypedDict, total=False):
        kind: Required[Literal[VectorThresholdKind.SEARCH_SCORE]]
        value: Required[float]


    class azure.search.documents.types.SemanticDebugInfo(TypedDict, total=False):
        key "contentFields": list[QueryResultDocumentSemanticField]
        key "keywordFields": list[QueryResultDocumentSemanticField]
        key "rerankerInput": ForwardRef('QueryResultDocumentRerankerInput')
        key "titleField": ForwardRef('QueryResultDocumentSemanticField')
        content_fields: list[QueryResultDocumentSemanticField]
        keyword_fields: list[QueryResultDocumentSemanticField]
        reranker_input: QueryResultDocumentRerankerInput
        title_field: QueryResultDocumentSemanticField


    class azure.search.documents.types.SingleVectorFieldResult(TypedDict, total=False):
        key "searchScore": float
        key "vectorSimilarity": float
        search_score: float
        vector_similarity: float


    class azure.search.documents.types.SuggestPostRequest(TypedDict, total=False):
        key "filter": str
        key "fuzzy": bool
        key "highlightPostTag": str
        key "highlightPreTag": str
        key "minimumCoverage": float
        key "orderby": list[str]
        key "searchFields": list[str]
        key "select": list[str]
        key "top": int
        filter: str
        highlight_post_tag: str
        highlight_pre_tag: str
        minimum_coverage: float
        order_by: list[str]
        search: Required[str]
        search_fields: list[str]
        search_text: str
        select: list[str]
        suggesterName: Required[str]
        suggester_name: str
        top: int
        use_fuzzy_matching: bool


    class azure.search.documents.types.SuggestResult(TypedDict):
        @search.text: Required[str]
        text: str


    class azure.search.documents.types.TextResult(TypedDict, total=False):
        key "searchScore": float
        search_score: float


    class azure.search.documents.types.VectorQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE_BINARY = "imageBinary"
        IMAGE_URL = "imageUrl"
        TEXT = "text"
        VECTOR = "vector"


    class azure.search.documents.types.VectorSimilarityThreshold(TypedDict, total=False):
        kind: Required[Literal[VectorThresholdKind.VECTOR_SIMILARITY]]
        value: Required[float]


    class azure.search.documents.types.VectorThresholdKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEARCH_SCORE = "searchScore"
        VECTOR_SIMILARITY = "vectorSimilarity"


    class azure.search.documents.types.VectorizableImageBinaryQuery(TypedDict, total=False):
        key "base64Image": str
        key "exhaustive": bool
        key "fields": str
        key "filterOverride": str
        key "k": int
        key "oversampling": float
        key "perDocumentVectorLimit": int
        key "threshold": ForwardRef('VectorThreshold')
        key "weight": float
        base64_image: str
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Required[Literal[VectorQueryKind.IMAGE_BINARY]]
        oversampling: float
        per_document_vector_limit: int
        threshold: VectorThreshold
        weight: float


    class azure.search.documents.types.VectorizableImageUrlQuery(TypedDict, total=False):
        key "exhaustive": bool
        key "fields": str
        key "filterOverride": str
        key "k": int
        key "oversampling": float
        key "perDocumentVectorLimit": int
        key "threshold": ForwardRef('VectorThreshold')
        key "url": str
        key "weight": float
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Required[Literal[VectorQueryKind.IMAGE_URL]]
        oversampling: float
        per_document_vector_limit: int
        threshold: VectorThreshold
        url: str
        weight: float


    class azure.search.documents.types.VectorizableTextQuery(TypedDict, total=False):
        key "exhaustive": bool
        key "fields": str
        key "filterOverride": str
        key "k": int
        key "oversampling": float
        key "perDocumentVectorLimit": int
        key "queryRewrites": Union[str, QueryRewritesType]
        key "threshold": ForwardRef('VectorThreshold')
        key "weight": float
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Required[Literal[VectorQueryKind.TEXT]]
        oversampling: float
        per_document_vector_limit: int
        query_rewrites: Union[str, QueryRewritesType]
        text: Required[str]
        threshold: VectorThreshold
        weight: float


    class azure.search.documents.types.VectorizedQuery(TypedDict, total=False):
        key "exhaustive": bool
        key "fields": str
        key "filterOverride": str
        key "k": int
        key "oversampling": float
        key "perDocumentVectorLimit": int
        key "threshold": ForwardRef('VectorThreshold')
        key "weight": float
        exhaustive: bool
        fields: str
        filter_override: str
        k_nearest_neighbors: int
        kind: Required[Literal[VectorQueryKind.VECTOR]]
        oversampling: float
        per_document_vector_limit: int
        threshold: VectorThreshold
        vector: Required[list[float]]
        weight: float


    class azure.search.documents.types.VectorsDebugInfo(TypedDict, total=False):
        key "subscores": ForwardRef('QueryResultDocumentSubscores')
        subscores: QueryResultDocumentSubscores


```