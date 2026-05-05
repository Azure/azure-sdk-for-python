```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.search.documents

    class azure.search.documents.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2020_06_30 = "2020-06-30"
        V2023_11_01 = "2023-11-01"
        V2024_07_01 = "2024-07-01"
        V2025_09_01 = "2025-09-01"
        V2026_04_01 = "2026-04-01"


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
                api_version: str = ..., 
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
        def get_document(
                self, 
                key: str, 
                *, 
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
                facets: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                highlight_fields: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                include_total_count: Optional[bool] = ..., 
                minimum_coverage: Optional[float] = ..., 
                order_by: Optional[List[str]] = ..., 
                query_answer: Optional[Union[str, QueryAnswerType]] = ..., 
                query_answer_count: Optional[int] = ..., 
                query_answer_threshold: Optional[float] = ..., 
                query_caption: Optional[Union[str, QueryCaptionType]] = ..., 
                query_caption_highlight_enabled: Optional[bool] = ..., 
                query_type: Optional[Union[str, QueryType]] = ..., 
                scoring_parameters: Optional[List[str]] = ..., 
                scoring_profile: Optional[str] = ..., 
                scoring_statistics: Optional[Union[str, ScoringStatistics]] = ..., 
                search_fields: Optional[List[str]] = ..., 
                search_mode: Optional[Union[str, SearchMode]] = ..., 
                select: Optional[List[str]] = ..., 
                semantic_configuration_name: Optional[str] = ..., 
                semantic_error_mode: Optional[Union[str, SemanticErrorMode]] = ..., 
                semantic_max_wait_in_milliseconds: Optional[int] = ..., 
                semantic_query: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
                skip: Optional[int] = ..., 
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

        async def get_facets(self) -> Optional[Dict]: ...


    class azure.search.documents.aio.SearchClient(_SearchClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                index_name: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
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
        async def get_document(
                self, 
                key: str, 
                *, 
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
                facets: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                highlight_fields: Optional[str] = ..., 
                highlight_post_tag: Optional[str] = ..., 
                highlight_pre_tag: Optional[str] = ..., 
                include_total_count: Optional[bool] = ..., 
                minimum_coverage: Optional[float] = ..., 
                order_by: Optional[List[str]] = ..., 
                query_answer: Optional[Union[str, QueryAnswerType]] = ..., 
                query_answer_count: Optional[int] = ..., 
                query_answer_threshold: Optional[float] = ..., 
                query_caption: Optional[Union[str, QueryCaptionType]] = ..., 
                query_caption_highlight_enabled: Optional[bool] = ..., 
                query_type: Optional[Union[str, QueryType]] = ..., 
                scoring_parameters: Optional[List[str]] = ..., 
                scoring_profile: Optional[str] = ..., 
                scoring_statistics: Optional[Union[str, ScoringStatistics]] = ..., 
                search_fields: Optional[List[str]] = ..., 
                search_mode: Optional[Union[str, SearchMode]] = ..., 
                select: Optional[List[str]] = ..., 
                semantic_configuration_name: Optional[str] = ..., 
                semantic_error_mode: Optional[Union[str, SemanticErrorMode]] = ..., 
                semantic_max_wait_in_milliseconds: Optional[int] = ..., 
                semantic_query: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
                skip: Optional[int] = ..., 
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
                api_version: str = ..., 
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
                alias: JSON, 
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
                index: JSON, 
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
                knowledge_base: JSON, 
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
                knowledge_source: JSON, 
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
                synonym_map: JSON, 
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
        def list_aliases(self, **kwargs: Any) -> ItemPaged[SearchAlias]: ...

        @distributed_trace
        def list_index_names(self, **kwargs: Any) -> ItemPaged[str]: ...

        @distributed_trace
        def list_indexes(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SearchIndex]: ...

        @distributed_trace
        def list_knowledge_bases(self, **kwargs: Any) -> ItemPaged[KnowledgeBase]: ...

        @distributed_trace
        def list_knowledge_sources(self, **kwargs: Any) -> ItemPaged[KnowledgeSource]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.search.documents.indexes.SearchIndexerClient(_SearchIndexerClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
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
                data_source_connection: JSON, 
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
                indexer: JSON, 
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
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @distributed_trace
        def create_or_update_indexer(
                self, 
                indexer: Union[SearchIndexer, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace
        def create_or_update_skillset(
                self, 
                skillset: Union[SearchIndexerSkillset, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
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
                skillset: JSON, 
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
        def reset_indexer(
                self, 
                name: str, 
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
                api_version: str = ..., 
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
                alias: JSON, 
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
                index: JSON, 
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
                knowledge_base: JSON, 
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
                knowledge_source: JSON, 
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
                synonym_map: JSON, 
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
        def list_aliases(self, **kwargs: Any) -> AsyncItemPaged[SearchAlias]: ...

        @distributed_trace
        def list_index_names(self, **kwargs: Any) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_indexes(
                self, 
                *, 
                select: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SearchIndex]: ...

        @distributed_trace
        def list_knowledge_bases(self, **kwargs: Any) -> AsyncItemPaged[KnowledgeBase]: ...

        @distributed_trace
        def list_knowledge_sources(self, **kwargs: Any) -> AsyncItemPaged[KnowledgeSource]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.search.documents.indexes.aio.SearchIndexerClient(_SearchIndexerClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
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
                data_source_connection: JSON, 
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
                indexer: JSON, 
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
                **kwargs: Any
            ) -> SearchIndexerDataSourceConnection: ...

        @distributed_trace_async
        async def create_or_update_indexer(
                self, 
                indexer: Union[SearchIndexer, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> SearchIndexer: ...

        @distributed_trace_async
        async def create_or_update_skillset(
                self, 
                skillset: Union[SearchIndexerSkillset, JSON], 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
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
                skillset: JSON, 
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
        async def reset_indexer(
                self, 
                name: str, 
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

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_parameters: AzureBlobKnowledgeSourceParameters, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str
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

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                container_name: str, 
                folder_path: Optional[str] = ..., 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                is_adls_gen2: Optional[bool] = ...
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
        GPT_5_4_MINI = "gpt-5.4-mini"
        GPT_5_4_NANO = "gpt-5.4-nano"
        GPT_5_MINI = "gpt-5-mini"
        GPT_5_NANO = "gpt-5-nano"
        TEXT_EMBEDDING3_LARGE = "text-embedding-3-large"
        TEXT_EMBEDDING3_SMALL = "text-embedding-3-small"
        TEXT_EMBEDDING_ADA002 = "text-embedding-ada-002"


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


    class azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingProperties(_Model):
        maximum_length: Optional[int]
        overlap_length: Optional[int]
        unit: Optional[Union[str, ContentUnderstandingSkillChunkingUnit]]

        @overload
        def __init__(
                self, 
                *, 
                maximum_length: Optional[int] = ..., 
                overlap_length: Optional[int] = ..., 
                unit: Optional[Union[str, ContentUnderstandingSkillChunkingUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.ContentUnderstandingSkillChunkingUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHARACTERS = "characters"


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


    class azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSource(KnowledgeSource, discriminator='indexedOneLake'):
        description: str
        e_tag: str
        encryption_key: SearchResourceEncryptionKey
        indexed_one_lake_parameters: IndexedOneLakeKnowledgeSourceParameters
        kind: Literal[KnowledgeSourceKind.INDEXED_ONELAKE]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                indexed_one_lake_parameters: IndexedOneLakeKnowledgeSourceParameters, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.IndexedOneLakeKnowledgeSourceParameters(_Model):
        created_resources: Optional[CreatedResources]
        fabric_workspace_id: str
        ingestion_parameters: Optional[KnowledgeSourceIngestionParameters]
        lakehouse_id: str
        target_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_workspace_id: str, 
                ingestion_parameters: Optional[KnowledgeSourceIngestionParameters] = ..., 
                lakehouse_id: str, 
                target_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        start_time: Optional[datetime]
        status: Union[str, IndexerExecutionStatus]
        warnings: list[SearchIndexerWarning]


    class azure.search.documents.indexes.models.IndexerExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_PROGRESS = "inProgress"
        RESET = "reset"
        SUCCESS = "success"
        TRANSIENT_FAILURE = "transientFailure"


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


    class azure.search.documents.indexes.models.IndexerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        RUNNING = "running"
        UNKNOWN = "unknown"


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


    class azure.search.documents.indexes.models.KnowledgeSource(_Model):
        description: Optional[str]
        e_tag: Optional[str]
        encryption_key: Optional[SearchResourceEncryptionKey]
        kind: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                kind: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.KnowledgeSourceContentExtractionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MINIMAL = "minimal"
        STANDARD = "standard"


    class azure.search.documents.indexes.models.KnowledgeSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "azureBlob"
        INDEXED_ONELAKE = "indexedOneLake"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"


    class azure.search.documents.indexes.models.KnowledgeSourceReference(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        scoring_profiles: Optional[list[ScoringProfile]]
        semantic_search: Optional[SemanticSearch]
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
                scoring_profiles: Optional[list[ScoringProfile]] = ..., 
                semantic_search: Optional[SemanticSearch] = ..., 
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
        search_index_parameters: SearchIndexKnowledgeSourceParameters

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
                search_index_parameters: SearchIndexKnowledgeSourceParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters(_Model):
        search_fields: Optional[list[SearchIndexFieldReference]]
        search_index_name: str
        semantic_configuration_name: Optional[str]
        source_data_fields: Optional[list[SearchIndexFieldReference]]

        @overload
        def __init__(
                self, 
                *, 
                search_fields: Optional[list[SearchIndexFieldReference]] = ..., 
                search_index_name: str, 
                semantic_configuration_name: Optional[str] = ..., 
                source_data_fields: Optional[list[SearchIndexFieldReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchIndexer(_Model):
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
        odata_type: Literal["#DataUserAssignedIdentity"]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
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
        projections: list[SearchIndexerKnowledgeStoreProjection]
        storage_connection_string: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
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
        execution_history: list[IndexerExecutionResult]
        last_result: Optional[IndexerExecutionResult]
        limits: SearchIndexerLimits
        name: str
        status: Union[str, IndexerStatus]


    class azure.search.documents.indexes.models.SearchIndexerWarning(_Model):
        details: Optional[str]
        documentation_link: Optional[str]
        key: Optional[str]
        message: str
        name: Optional[str]


    class azure.search.documents.indexes.models.SearchResourceEncryptionKey(_Model):
        access_credentials: Optional[AzureActiveDirectoryApplicationCredentials]
        identity: Optional[SearchIndexerDataIdentity]
        key_name: str
        key_version: Optional[str]
        vault_uri: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                access_credentials: Optional[AzureActiveDirectoryApplicationCredentials] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                key_name: str, 
                key_version: Optional[str] = ..., 
                vault_uri: str
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

        @overload
        def __init__(
                self, 
                *, 
                max_complex_collection_fields_per_index: Optional[int] = ..., 
                max_complex_objects_in_collections_per_document: Optional[int] = ..., 
                max_cumulative_indexer_runtime_seconds: Optional[int] = ..., 
                max_field_nesting_depth_per_index: Optional[int] = ..., 
                max_fields_per_index: Optional[int] = ..., 
                max_storage_per_index_in_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.indexes.models.SearchServiceStatistics(_Model):
        counters: SearchServiceCounters
        limits: SearchServiceLimits

        @overload
        def __init__(
                self, 
                *, 
                counters: SearchServiceCounters, 
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
        name: str
        prioritized_fields: SemanticPrioritizedFields
        ranking_order: Optional[Union[str, RankingOrder]]

        @overload
        def __init__(
                self, 
                *, 
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

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                default_language_code: Optional[Union[str, SplitSkillLanguage]] = ..., 
                description: Optional[str] = ..., 
                inputs: list[InputFieldMappingEntry], 
                maximum_page_length: Optional[int] = ..., 
                maximum_pages_to_take: Optional[int] = ..., 
                name: Optional[str] = ..., 
                outputs: list[OutputFieldMappingEntry], 
                page_overlap_length: Optional[int] = ..., 
                text_split_mode: Optional[Union[str, TextSplitMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        web_parameters: Optional[WebKnowledgeSourceParameters]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                encryption_key: Optional[SearchResourceEncryptionKey] = ..., 
                name: str, 
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
        domains: Optional[WebKnowledgeSourceDomains]

        @overload
        def __init__(
                self, 
                *, 
                domains: Optional[WebKnowledgeSourceDomains] = ...
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


namespace azure.search.documents.knowledgebases

    class azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
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
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        def retrieve(
                self, 
                retrieval_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        def retrieve(
                self, 
                retrieval_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.search.documents.knowledgebases.aio

    class azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
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
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        async def retrieve(
                self, 
                retrieval_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        @overload
        async def retrieve(
                self, 
                retrieval_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KnowledgeBaseRetrievalResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


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


    class azure.search.documents.knowledgebases.models.AzureBlobKnowledgeSourceParams(KnowledgeSourceParams, discriminator='azureBlob'):
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.AZURE_BLOB]
        knowledge_source_name: str
        reranker_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                reranker_threshold: Optional[float] = ...
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


    class azure.search.documents.knowledgebases.models.IndexedOneLakeKnowledgeSourceParams(KnowledgeSourceParams, discriminator='indexedOneLake'):
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.INDEXED_ONELAKE]
        knowledge_source_name: str
        reranker_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                reranker_threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecord(_Model):
        elapsed_ms: Optional[int]
        error: Optional[KnowledgeBaseErrorDetail]
        id: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseActivityRecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTIC_REASONING = "agenticReasoning"
        AZURE_BLOB = "azureBlob"
        INDEXED_ONELAKE = "indexedOneLake"
        MODEL_WEB_SUMMARIZATION = "modelWebSummarization"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAgenticReasoningActivityRecord(KnowledgeBaseActivityRecord, discriminator='agenticReasoning'):
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        reasoning_tokens: Optional[int]
        retrieval_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort]
        type: Literal[KnowledgeBaseActivityRecordType.AGENTIC_REASONING]

        @overload
        def __init__(
                self, 
                *, 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                reasoning_tokens: Optional[int] = ..., 
                retrieval_reasoning_effort: Optional[KnowledgeRetrievalReasoningEffort] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseAzureBlobReference(KnowledgeBaseReference, discriminator='azureBlob'):
        activity_source: int
        blob_url: Optional[str]
        id: str
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.AZURE_BLOB]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                blob_url: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
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


    class azure.search.documents.knowledgebases.models.KnowledgeBaseIndexedOneLakeReference(KnowledgeBaseReference, discriminator='indexedOneLake'):
        activity_source: int
        doc_url: Optional[str]
        id: str
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.INDEXED_ONELAKE]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                doc_url: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ...
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


    class azure.search.documents.knowledgebases.models.KnowledgeBaseModelWebSummarizationActivityRecord(KnowledgeBaseActivityRecord, discriminator='modelWebSummarization'):
        elapsed_ms: int
        error: KnowledgeBaseErrorDetail
        id: int
        input_tokens_count: Optional[int]
        output_tokens_count: Optional[int]
        type: Literal[KnowledgeBaseActivityRecordType.MODEL_WEB_SUMMARIZATION]

        @overload
        def __init__(
                self, 
                *, 
                elapsed_ms: Optional[int] = ..., 
                error: Optional[KnowledgeBaseErrorDetail] = ..., 
                id: int, 
                input_tokens_count: Optional[int] = ..., 
                output_tokens_count: Optional[int] = ...
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
        INDEXED_ONELAKE = "indexedOneLake"
        SEARCH_INDEX = "searchIndex"
        WEB = "web"


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest(_Model):
        include_activity: Optional[bool]
        intents: Optional[list[KnowledgeRetrievalIntent]]
        knowledge_source_params: Optional[list[KnowledgeSourceParams]]
        max_output_size_in_tokens: Optional[int]
        max_runtime_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                include_activity: Optional[bool] = ..., 
                intents: Optional[list[KnowledgeRetrievalIntent]] = ..., 
                knowledge_source_params: Optional[list[KnowledgeSourceParams]] = ..., 
                max_output_size_in_tokens: Optional[int] = ..., 
                max_runtime_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalResponse(_Model):
        activity: Optional[list[KnowledgeBaseActivityRecord]]
        references: Optional[list[KnowledgeBaseReference]]
        response: Optional[list[KnowledgeBaseMessage]]

        @overload
        def __init__(
                self, 
                *, 
                activity: Optional[list[KnowledgeBaseActivityRecord]] = ..., 
                references: Optional[list[KnowledgeBaseReference]] = ..., 
                response: Optional[list[KnowledgeBaseMessage]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexReference(KnowledgeBaseReference, discriminator='searchIndex'):
        activity_source: int
        doc_key: Optional[str]
        id: str
        reranker_score: float
        source_data: dict[str, any]
        type: Literal[KnowledgeBaseReferenceType.SEARCH_INDEX]

        @overload
        def __init__(
                self, 
                *, 
                activity_source: int, 
                doc_key: Optional[str] = ..., 
                id: str, 
                reranker_score: Optional[float] = ..., 
                source_data: Optional[dict[str, Any]] = ...
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


    class azure.search.documents.knowledgebases.models.KnowledgeRetrievalMinimalReasoningEffort(KnowledgeRetrievalReasoningEffort, discriminator='minimal'):
        kind: Literal[KnowledgeRetrievalReasoningEffortKind.MINIMAL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        chat_completion_model: Optional[KnowledgeBaseModel]
        content_extraction_mode: Optional[Union[str, KnowledgeSourceContentExtractionMode]]
        disable_image_verbalization: Optional[bool]
        embedding_model: Optional[KnowledgeSourceVectorizer]
        identity: Optional[SearchIndexerDataIdentity]
        ingestion_schedule: Optional[IndexingSchedule]

        @overload
        def __init__(
                self, 
                *, 
                ai_services: Optional[AIServices] = ..., 
                chat_completion_model: Optional[KnowledgeBaseModel] = ..., 
                content_extraction_mode: Optional[Union[str, KnowledgeSourceContentExtractionMode]] = ..., 
                disable_image_verbalization: Optional[bool] = ..., 
                embedding_model: Optional[KnowledgeSourceVectorizer] = ..., 
                identity: Optional[SearchIndexerDataIdentity] = ..., 
                ingestion_schedule: Optional[IndexingSchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.knowledgebases.models.KnowledgeSourceParams(_Model):
        include_reference_source_data: Optional[bool]
        include_references: Optional[bool]
        kind: str
        knowledge_source_name: str
        reranker_threshold: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                kind: str, 
                knowledge_source_name: str, 
                reranker_threshold: Optional[float] = ...
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


    class azure.search.documents.knowledgebases.models.SearchIndexKnowledgeSourceParams(KnowledgeSourceParams, discriminator='searchIndex'):
        filter_add_on: Optional[str]
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.SEARCH_INDEX]
        knowledge_source_name: str
        reranker_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                filter_add_on: Optional[str] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                reranker_threshold: Optional[float] = ...
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
        count: Optional[int]
        freshness: Optional[str]
        include_reference_source_data: bool
        include_references: bool
        kind: Literal[KnowledgeSourceKind.WEB]
        knowledge_source_name: str
        language: Optional[str]
        market: Optional[str]
        reranker_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                include_reference_source_data: Optional[bool] = ..., 
                include_references: Optional[bool] = ..., 
                knowledge_source_name: str, 
                language: Optional[str] = ..., 
                market: Optional[str] = ..., 
                reranker_threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.search.documents.models

    class azure.search.documents.models.AutocompleteItem(_Model):
        query_plus_text: str
        text: str


    class azure.search.documents.models.AutocompleteMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_TERM = "oneTerm"
        ONE_TERM_WITH_CONTEXT = "oneTermWithContext"
        TWO_TERMS = "twoTerms"


    class azure.search.documents.models.DocumentDebugInfo(_Model):
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
        count: Optional[int]


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


    class azure.search.documents.models.QueryResultDocumentSubscores(_Model):
        document_boost: Optional[float]
        text: Optional[TextResult]
        vectors: Optional[list[dict[str, SingleVectorFieldResult]]]


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


    class azure.search.documents.models.SemanticErrorMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL = "fail"
        PARTIAL = "partial"


    class azure.search.documents.models.SemanticErrorReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_OVERLOADED = "capacityOverloaded"
        MAX_WAIT_EXCEEDED = "maxWaitExceeded"
        TRANSIENT = "transient"


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
        k_nearest_neighbors: Optional[int]
        kind: str
        oversampling: Optional[float]
        weight: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                kind: str, 
                oversampling: Optional[float] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE_BINARY = "imageBinary"
        IMAGE_URL = "imageUrl"
        TEXT = "text"
        VECTOR = "vector"


    class azure.search.documents.models.VectorizableImageBinaryQuery(VectorQuery, discriminator='imageBinary'):
        base64_image: Optional[str]
        exhaustive: bool
        fields: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.IMAGE_BINARY]
        oversampling: float
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                base64_image: Optional[str] = ..., 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorizableImageUrlQuery(VectorQuery, discriminator='imageUrl'):
        exhaustive: bool
        fields: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.IMAGE_URL]
        oversampling: float
        url: Optional[str]
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                url: Optional[str] = ..., 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorizableTextQuery(VectorQuery, discriminator='text'):
        exhaustive: bool
        fields: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.TEXT]
        oversampling: float
        text: str
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                text: str, 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorizedQuery(VectorQuery, discriminator='vector'):
        exhaustive: bool
        fields: str
        k_nearest_neighbors: int
        kind: Literal[VectorQueryKind.VECTOR]
        oversampling: float
        vector: list[float]
        weight: float

        @overload
        def __init__(
                self, 
                *, 
                exhaustive: Optional[bool] = ..., 
                fields: Optional[str] = ..., 
                k_nearest_neighbors: Optional[int] = ..., 
                oversampling: Optional[float] = ..., 
                vector: list[float], 
                weight: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.search.documents.models.VectorsDebugInfo(_Model):
        subscores: Optional[QueryResultDocumentSubscores]


```