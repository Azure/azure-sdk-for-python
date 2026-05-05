```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.cosmos

    class azure.cosmos.ConnectionRetryPolicy(RetryPolicy):
        BACKOFF_MAX = 120

        def __init__(self, **kwargs): ...

        def send(self, request: PipelineRequest) -> PipelineResponse: ...


    class azure.cosmos.ConsistencyLevel:
        BoundedStaleness: Literal["BoundedStaleness"] = BoundedStaleness
        ConsistentPrefix: Literal["ConsistentPrefix"] = ConsistentPrefix
        Eventual: Literal["Eventual"] = Eventual
        Session: Literal["Session"] = Session
        Strong: Literal["Strong"] = Strong


    class azure.cosmos.ContainerProxy:
        property is_system_key: bool    # Read-only
        property scripts: ScriptsProxy    # Read-only
        container_link: str
        id: str

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                database_link: str, 
                id: str, 
                properties: Optional[dict[str, Any]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace
        def create_item(
                self, 
                body: dict[str, Any], 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                indexing_directive: Optional[int] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                enable_automatic_id_generation: bool = False, 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                no_response: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def delete_all_items_by_partition_key(
                self, 
                partition_key: PartitionKeyType, 
                *, 
                excluded_locations: Optional[Sequence[str]] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], None], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_conflict(
                self, 
                conflict: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_item(
                self, 
                item: Union[Mapping[str, Any], str], 
                partition_key: PartitionKeyType, 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], None], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def execute_item_batch(
                self, 
                batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ]], Tuple[str, Tuple[Any, ], dict[str, Any]]]], 
                partition_key: PartitionKeyType, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], list[dict[str, Any]]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        def feed_range_from_partition_key(self, partition_key: PartitionKeyType) -> dict[str, Any]: ...

        @distributed_trace
        def get_conflict(
                self, 
                conflict: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        def get_latest_session_token(
                self, 
                feed_ranges_to_session_tokens: list[Tuple[dict[str, Any], str]], 
                target_feed_range: dict[str, Any]
            ) -> str: ...

        @distributed_trace
        def get_throughput(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        def is_feed_range_subset(
                self, 
                parent_feed_range: dict[str, Any], 
                child_feed_range: dict[str, Any]
            ) -> bool: ...

        @distributed_trace
        def list_conflicts(
                self, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def patch_item(
                self, 
                item: Union[str, dict[str, Any]], 
                partition_key: PartitionKeyType, 
                patch_operations: list[dict[str, Any]], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                filter_predicate: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def query_conflicts(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, object]]] = None, 
                enable_cross_partition_query: Optional[bool] = None, 
                partition_key: Optional[PartitionKeyType] = None, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, object]]] = None, 
                partition_key: Optional[PartitionKeyType] = None, 
                enable_cross_partition_query: Optional[bool] = None, 
                max_item_count: Optional[int] = None, 
                enable_scan_in_query: Optional[bool] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosItemPaged: ...

        @overload
        def query_items(
                self, 
                query: str, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                enable_cross_partition_query: Optional[bool] = ..., 
                enable_scan_in_query: Optional[bool] = ..., 
                feed_range: dict[str, Any], 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, object]]] = ..., 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                populate_query_metrics: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosItemPaged: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                partition_key: PartitionKeyType, 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                feed_range: dict[str, Any], 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation: str, 
                max_item_count: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read(
                self, 
                populate_query_metrics: Optional[bool] = None, 
                populate_partition_key_range_statistics: Optional[bool] = None, 
                populate_quota_info: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_all_items(
                self, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read_feed_ranges(
                self, 
                *, 
                force_refresh: bool = False, 
                **kwargs: Any
            ) -> Iterable[dict[str, Any]]: ...

        @distributed_trace
        def read_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                populate_query_metrics: Optional[bool] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_items(
                self, 
                items: Sequence[Tuple[str, PartitionKeyType]], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                consistency_level: Optional[str] = ..., 
                excluded_locations: Optional[list[str]] = ..., 
                executor: Optional[ThreadPoolExecutor] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_concurrency: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        @distributed_trace
        def read_offer(
                self, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def replace_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_throughput(
                self, 
                throughput: Union[int, ThroughputProperties], 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        @distributed_trace
        def semantic_rerank(
                self, 
                *, 
                context: str, 
                documents: list[str], 
                options: Optional[dict[str, Any]] = ...
            ) -> CosmosDict: ...

        @distributed_trace
        def upsert_item(
                self, 
                body: dict[str, Any], 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...


    class azure.cosmos.CosmosClient: implements ContextManager 

        def __init__(
                self, 
                url: str, 
                credential: Union[TokenCredential, str, dict[str, Any]], 
                consistency_level: Optional[str] = None, 
                **kwargs
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[TokenCredential, str, dict[str, Any]]] = None, 
                consistency_level: Optional[str] = None, 
                **kwargs
            ) -> CosmosClient: ...

        def close(self) -> None: ...

        @overload
        def create_database(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[False] = False, 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> DatabaseProxy: ...

        @overload
        def create_database(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[True], 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> tuple[DatabaseProxy, CosmosDict]: ...

        @overload
        def create_database_if_not_exists(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[False] = False, 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> DatabaseProxy: ...

        @overload
        def create_database_if_not_exists(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[True], 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> tuple[DatabaseProxy, CosmosDict]: ...

        @distributed_trace
        def delete_database(
                self, 
                database: Union[str, DatabaseProxy, Mapping[str, Any]], 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_database_account(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                **kwargs
            ) -> DatabaseAccount: ...

        def get_database_client(self, database: Union[str, DatabaseProxy, Mapping[str, Any]]) -> DatabaseProxy: ...

        @distributed_trace
        def list_databases(
                self, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_databases(
                self, 
                query: Optional[str] = None, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                enable_cross_partition_query: Optional[bool] = None, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...


    class azure.cosmos.CosmosDict(dict[str, Any]):

        def __init__(
                self, 
                original_dict: Optional[Mapping[str, Any]], 
                /, 
                *, 
                response_headers: CaseInsensitiveDict
            ) -> None: ...

        def get_response_headers(self) -> CaseInsensitiveDict: ...


    class azure.cosmos.CosmosList(list[dict[str, Any]]):

        def __init__(
                self, 
                original_list: Optional[Iterable[dict[str, Any]]], 
                /, 
                *, 
                response_headers: CaseInsensitiveDict
            ) -> None: ...

        def get_response_headers(self) -> CaseInsensitiveDict: ...


    class azure.cosmos.DataType:
        LineString: Literal["LineString"] = LineString
        MultiPolygon: Literal["MultiPolygon"] = MultiPolygon
        Number: Literal["Number"] = Number
        Point: Literal["Point"] = Point
        Polygon: Literal["Polygon"] = Polygon
        String: Literal["String"] = String


    class azure.cosmos.DatabaseAccount:
        property ReadableLocations: list[dict[str, str]]    # Read-only
        property WritableLocations: list[dict[str, str]]    # Read-only
        ConsistencyPolicy: dict[str, Any]
        CurrentMediaStorageUsageInMB: int
        DatabaseLink: str
        EnableMultipleWritableLocations: boolean
        MaxMediaStorageUsageInMB: int
        MediaLink: str

        def __init__(self) -> None: ...


    class azure.cosmos.DatabaseProxy:
        id

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                id: str, 
                properties: Optional[dict[str, Any]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @overload
        def create_container(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        def create_container(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @overload
        def create_container_if_not_exists(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        def create_container_if_not_exists(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @distributed_trace
        def create_user(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...

        @distributed_trace
        def delete_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                etag: Optional[str] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                response_hook: Optional[Callable] = ..., 
                session_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user(
                self, 
                user: Union[str, UserProxy, Mapping[str, Any]], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_container_client(self, container: Union[str, ContainerProxy, Mapping[str, Any]]) -> ContainerProxy: ...

        @distributed_trace
        def get_throughput(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        def get_user_client(self, user: Union[str, UserProxy, Mapping[str, Any]]) -> UserProxy: ...

        @distributed_trace
        def list_containers(
                self, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                session_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_users(
                self, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_containers(
                self, 
                query: Optional[str] = None, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_users(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read(
                self, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_offer(
                self, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def replace_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        def replace_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @distributed_trace
        def replace_throughput(
                self, 
                throughput: Union[int, ThroughputProperties], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        @distributed_trace
        def replace_user(
                self, 
                user: Union[str, UserProxy, Mapping[str, Any]], 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...

        @distributed_trace
        def upsert_user(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...


    class azure.cosmos.IndexKind:
        Hash: Literal["Hash"] = Hash
        MultiHash: Literal["MultiHash"] = MultiHash
        Range: Literal["Range"] = Range


    class azure.cosmos.IndexingMode:
        Consistent: Literal["consistent"] = consistent
        Lazy: Literal["lazy"] = lazy
        NoIndex: Literal["none"] = none


    class azure.cosmos.Offer:

        def __init__(
                self, 
                *args, 
                *, 
                auto_scale_increment_percent: Optional[int] = ..., 
                auto_scale_max_throughput: Optional[int] = ..., 
                offer_throughput: Optional[int] = ..., 
                **kwargs
            ) -> None: ...

        def get_response_headers(self) -> Mapping[str, Any]: ...


    class azure.cosmos.PartitionKey(dict):
        property kind: Literal["MultiHash", "Hash"]
        property path: str
        property version: int
        kind: str
        path: str
        version: int

        @overload
        def __init__(
                self, 
                path: list[str], 
                *, 
                kind: Literal["MultiHash"] = "MultiHash", 
                version: int = _PartitionKeyVersion.V2
            ) -> None: ...

        @overload
        def __init__(
                self, 
                path: str, 
                *, 
                kind: Literal["Hash"] = "Hash", 
                version: int = _PartitionKeyVersion.V2
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.cosmos.Permission:

        def __init__(
                self, 
                id: str, 
                user_link: str, 
                permission_mode: str, 
                resource_link: str, 
                properties: Mapping[str, Any]
            ) -> None: ...


    class azure.cosmos.PermissionMode:
        All: Literal["all"] = all
        NoneMode: Literal["none"] = none
        Read: Literal["read"] = read


    class azure.cosmos.ProxyConfiguration:
        Host: str
        Port: int

        def __init__(self) -> None: ...


    class azure.cosmos.SSLConfiguration:
        SSLCaCerts: Union[str, bool]
        SSLCertFile: str
        SSLKeyFIle: str

        def __init__(self) -> None: ...


    class azure.cosmos.ScriptsProxy:

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                container_link: str, 
                is_system_key: bool
            ) -> None: ...

        @distributed_trace
        def create_stored_procedure(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def create_trigger(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def create_user_defined_function(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def delete_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def execute_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                partition_key: Optional[PartitionKeyType] = None, 
                params: Optional[list[dict[str, Any]]] = None, 
                enable_script_logging: Optional[bool] = None, 
                **kwargs: Any
            ) -> Any: ...

        @distributed_trace
        def get_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def get_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def get_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def list_stored_procedures(
                self, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_triggers(
                self, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_user_defined_functions(
                self, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_stored_procedures(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_triggers(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_user_defined_functions(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def replace_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...


    class azure.cosmos.ThroughputProperties:

        def __init__(
                self, 
                *args, 
                *, 
                auto_scale_increment_percent: Optional[int] = ..., 
                auto_scale_max_throughput: Optional[int] = ..., 
                offer_throughput: Optional[int] = ..., 
                **kwargs
            ) -> None: ...

        def get_response_headers(self) -> Mapping[str, Any]: ...


    class azure.cosmos.TriggerOperation:
        All: Literal["all"] = all
        Create: Literal["create"] = create
        Delete: Literal["delete"] = delete
        Replace: Literal["replace"] = replace
        Update: Literal["update"] = update


    class azure.cosmos.TriggerType:
        Post: Literal["post"] = post
        Pre: Literal["pre"] = pre


    class azure.cosmos.UserProxy:
        id: str
        user_link: str

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                id: str, 
                database_link: str, 
                properties: Optional[CosmosDict] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace
        def create_permission(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace
        def delete_permission(
                self, 
                permission: Union[str, Permission, Mapping[str, Any]], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_permission(
                self, 
                permission: Union[str, Permission, Mapping[str, Any]], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace
        def list_permissions(
                self, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_permissions(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read(
                self, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_permission(
                self, 
                permission: Union[str, Permission, Mapping[str, Any]], 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs
            ) -> Permission: ...

        @distributed_trace
        def upsert_permission(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Permission: ...


namespace azure.cosmos.aio

    class azure.cosmos.aio.ContainerProxy:
        property is_system_key: bool    # Read-only
        property scripts: ScriptsProxy    # Read-only
        id: str
        session_token: str

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                database_link: str, 
                id: str, 
                properties: Optional[dict[str, Any]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace_async
        async def create_item(
                self, 
                body: dict[str, Any], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                enable_automatic_id_generation: bool = False, 
                excluded_locations: Optional[Sequence[str]] = ..., 
                indexing_directive: Optional[int] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                no_response: Optional[bool] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def delete_all_items_by_partition_key(
                self, 
                partition_key: PartitionKeyType, 
                *, 
                excluded_locations: Optional[Sequence[str]] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                response_hook: Optional[Callable] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_conflict(
                self, 
                conflict: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                response_hook: Callable[[dict[str, str], None], None] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], None], None] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def execute_item_batch(
                self, 
                batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ]], Tuple[str, Tuple[Any, ], dict[str, Any]]]], 
                partition_key: PartitionKeyType, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        async def feed_range_from_partition_key(self, partition_key: PartitionKeyType) -> dict[str, Any]: ...

        @distributed_trace_async
        async def get_conflict(
                self, 
                conflict: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        async def get_latest_session_token(
                self, 
                feed_ranges_to_session_tokens: list[Tuple[dict[str, Any], str]], 
                target_feed_range: dict[str, Any]
            ) -> str: ...

        @distributed_trace_async
        async def get_throughput(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        async def is_feed_range_subset(
                self, 
                parent_feed_range: dict[str, Any], 
                child_feed_range: dict[str, Any]
            ) -> bool: ...

        @distributed_trace
        def list_conflicts(
                self, 
                *, 
                max_item_count: Optional[int] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace_async
        async def patch_item(
                self, 
                item: Union[str, dict[str, Any]], 
                partition_key: PartitionKeyType, 
                patch_operations: list[dict[str, Any]], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                filter_predicate: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def query_conflicts(
                self, 
                query: str, 
                *, 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, object]]] = ..., 
                partition_key: Optional[PartitionKeyType] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @overload
        def query_items(
                self, 
                query: str, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                enable_scan_in_query: Optional[bool] = ..., 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, object]]] = ..., 
                partition_key: PartitionKeyType, 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                populate_query_metrics: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosAsyncItemPaged: ...

        @overload
        def query_items(
                self, 
                query: str, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                enable_scan_in_query: Optional[bool] = ..., 
                feed_range: dict[str, Any], 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, object]]] = ..., 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                populate_query_metrics: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosAsyncItemPaged: ...

        @overload
        def query_items(
                self, 
                query: str, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                enable_scan_in_query: Optional[bool] = ..., 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, object]]] = ..., 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                populate_query_metrics: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosAsyncItemPaged: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                partition_key: PartitionKeyType, 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                feed_range: dict[str, Any], 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation: str, 
                max_item_count: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace_async
        async def read(
                self, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                populate_partition_key_range_statistics: Optional[bool] = ..., 
                populate_quota_info: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_all_items(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                max_item_count: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read_feed_ranges(
                self, 
                *, 
                force_refresh: bool = False, 
                **kwargs: Any
            ) -> AsyncIterable[dict[str, Any]]: ...

        @distributed_trace_async
        async def read_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                post_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def read_items(
                self, 
                items: Sequence[Tuple[str, PartitionKeyType]], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                consistency_level: Optional[str] = ..., 
                excluded_locations: Optional[list[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_concurrency: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        @distributed_trace_async
        async def replace_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def replace_throughput(
                self, 
                throughput: Union[int, ThroughputProperties], 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        @distributed_trace_async
        async def semantic_rerank(
                self, 
                *, 
                context: str, 
                documents: list[str], 
                options: Optional[dict[str, Any]] = ...
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def upsert_item(
                self, 
                body: dict[str, Any], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...


    class azure.cosmos.aio.CosmosClient: implements AsyncContextManager 

        def __init__(
                self, 
                url: str, 
                credential: Union[str, dict[str, str], AsyncTokenCredential], 
                *, 
                availability_strategy: Union[bool, dict[str, Any]] = False, 
                availability_strategy_max_concurrency: Optional[int] = ..., 
                consistency_level: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                consistency_level: Optional[str] = ..., 
                credential: Optional[Union[str, dict[str, str]]] = ..., 
                **kwargs: Any
            ) -> CosmosClient: ...

        async def close(self) -> None: ...

        @overload
        async def create_database(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[False] = False, 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> DatabaseProxy: ...

        @overload
        async def create_database(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[True], 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> tuple[DatabaseProxy, CosmosDict]: ...

        @overload
        async def create_database_if_not_exists(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[False] = False, 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> DatabaseProxy: ...

        @overload
        async def create_database_if_not_exists(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[True], 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> tuple[DatabaseProxy, CosmosDict]: ...

        @distributed_trace_async
        async def delete_database(
                self, 
                database: Union[str, DatabaseProxy, dict[str, Any]], 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_database_client(self, database: Union[str, DatabaseProxy, dict[str, Any]]) -> DatabaseProxy: ...

        @distributed_trace
        def list_databases(
                self, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_item_count: Optional[int] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_databases(
                self, 
                query: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...


    class azure.cosmos.aio.DatabaseProxy:
        id

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                id: str, 
                properties: Optional[dict[str, Any]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @overload
        async def create_container(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                conflict_resolution_policy: Optional[dict[str, str]] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                indexing_policy: Optional[dict[str, str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                return_properties: Literal[False] = False, 
                unique_key_policy: Optional[dict[str, str]] = ..., 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        async def create_container(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                conflict_resolution_policy: Optional[dict[str, str]] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                indexing_policy: Optional[dict[str, str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                return_properties: Literal[True], 
                unique_key_policy: Optional[dict[str, str]] = ..., 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @overload
        async def create_container_if_not_exists(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                conflict_resolution_policy: Optional[dict[str, str]] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                indexing_policy: Optional[dict[str, str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                return_properties: Literal[False] = False, 
                unique_key_policy: Optional[dict[str, str]] = ..., 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        async def create_container_if_not_exists(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                conflict_resolution_policy: Optional[dict[str, str]] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                indexing_policy: Optional[dict[str, str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                return_properties: Literal[True], 
                unique_key_policy: Optional[dict[str, str]] = ..., 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @distributed_trace_async
        async def create_user(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...

        @distributed_trace_async
        async def delete_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Callable[[Mapping[str, str], None], None] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_user(
                self, 
                user: Union[str, UserProxy, Mapping[str, Any]], 
                *, 
                response_hook: Callable[[dict[str, str], None], None] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_container_client(self, container: Union[str, ContainerProxy, dict[str, Any]]) -> ContainerProxy: ...

        @distributed_trace_async
        async def get_throughput(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        def get_user_client(self, user: Union[str, UserProxy, Mapping[str, Any]]) -> UserProxy: ...

        @distributed_trace
        def list_containers(
                self, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_item_count: Optional[int] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_users(
                self, 
                *, 
                max_item_count: Optional[int] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_containers(
                self, 
                query: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_users(
                self, 
                query: str, 
                *, 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace_async
        async def read(
                self, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Callable[[Mapping[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @overload
        async def replace_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                partition_key: PartitionKey, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                conflict_resolution_policy: Optional[dict[str, str]] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                indexing_policy: Optional[dict[str, str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        async def replace_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                partition_key: PartitionKey, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                conflict_resolution_policy: Optional[dict[str, str]] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                indexing_policy: Optional[dict[str, str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @distributed_trace_async
        async def replace_throughput(
                self, 
                throughput: Union[int, ThroughputProperties], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        @distributed_trace_async
        async def replace_user(
                self, 
                user: Union[str, UserProxy, Mapping[str, Any]], 
                body: dict[str, Any], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...

        @distributed_trace_async
        async def upsert_user(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...


    class azure.cosmos.aio.ScriptsProxy:

        def __init__(
                self, 
                container: ContainerProxy, 
                client_connection: _CosmosClientConnection, 
                container_link: str
            ) -> None: ...

        @distributed_trace_async
        async def create_stored_procedure(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def create_trigger(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> dict[str, Any]: ...

        @distributed_trace_async
        async def create_user_defined_function(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> dict[str, Any]: ...

        @distributed_trace_async
        async def delete_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def execute_stored_procedure(
                self, 
                sproc: Union[str, dict[str, Any]], 
                *, 
                enable_script_logging: Optional[bool] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                partition_key: Optional[PartitionKeyType] = ..., 
                **kwargs: Any
            ) -> Any: ...

        @distributed_trace_async
        async def get_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def get_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> dict[str, Any]: ...

        @distributed_trace_async
        async def get_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> dict[str, Any]: ...

        @distributed_trace
        def list_stored_procedures(
                self, 
                *, 
                max_item_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_triggers(
                self, 
                *, 
                max_item_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_user_defined_functions(
                self, 
                *, 
                max_item_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_stored_procedures(
                self, 
                query: str, 
                *, 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_triggers(
                self, 
                query: str, 
                *, 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_user_defined_functions(
                self, 
                query: str, 
                *, 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace_async
        async def replace_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def replace_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> dict[str, Any]: ...

        @distributed_trace_async
        async def replace_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> dict[str, Any]: ...


    class azure.cosmos.aio.UserProxy:
        id: str
        user_link: str

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                id: str, 
                database_link: str, 
                properties: Optional[CosmosDict] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace_async
        async def create_permission(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace_async
        async def delete_permission(
                self, 
                permission: Union[str, Mapping[str, Any], Permission], 
                *, 
                response_hook: Callable[[dict[str, str], None], None] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_permission(
                self, 
                permission: Union[str, Mapping[str, Any], Permission], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace
        def list_permissions(
                self, 
                *, 
                max_item_count: Optional[int] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_permissions(
                self, 
                query: str, 
                *, 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, Any]]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], AsyncItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[dict[str, Any]]: ...

        @distributed_trace_async
        async def read(
                self, 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace_async
        async def replace_permission(
                self, 
                permission: Union[str, Mapping[str, Any], Permission], 
                body: dict[str, Any], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace_async
        async def upsert_permission(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Callable[[dict[str, str], dict[str, Any]], None] = ..., 
                **kwargs: Any
            ) -> Permission: ...


namespace azure.cosmos.auth

    def azure.cosmos.auth.GetAuthorizationHeader(
            cosmos_client_connection, 
            verb, 
            path, 
            resource_id_or_fullname, 
            is_name_based, 
            resource_type, 
            headers
        ): ...


namespace azure.cosmos.container

    class azure.cosmos.container.ContainerProxy:
        property is_system_key: bool    # Read-only
        property scripts: ScriptsProxy    # Read-only
        container_link: str
        id: str

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                database_link: str, 
                id: str, 
                properties: Optional[dict[str, Any]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace
        def create_item(
                self, 
                body: dict[str, Any], 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                indexing_directive: Optional[int] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                enable_automatic_id_generation: bool = False, 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                no_response: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def delete_all_items_by_partition_key(
                self, 
                partition_key: PartitionKeyType, 
                *, 
                excluded_locations: Optional[Sequence[str]] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], None], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_conflict(
                self, 
                conflict: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_item(
                self, 
                item: Union[Mapping[str, Any], str], 
                partition_key: PartitionKeyType, 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], None], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def execute_item_batch(
                self, 
                batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ]], Tuple[str, Tuple[Any, ], dict[str, Any]]]], 
                partition_key: PartitionKeyType, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], list[dict[str, Any]]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        def feed_range_from_partition_key(self, partition_key: PartitionKeyType) -> dict[str, Any]: ...

        @distributed_trace
        def get_conflict(
                self, 
                conflict: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        def get_latest_session_token(
                self, 
                feed_ranges_to_session_tokens: list[Tuple[dict[str, Any], str]], 
                target_feed_range: dict[str, Any]
            ) -> str: ...

        @distributed_trace
        def get_throughput(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        def is_feed_range_subset(
                self, 
                parent_feed_range: dict[str, Any], 
                child_feed_range: dict[str, Any]
            ) -> bool: ...

        @distributed_trace
        def list_conflicts(
                self, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def patch_item(
                self, 
                item: Union[str, dict[str, Any]], 
                partition_key: PartitionKeyType, 
                patch_operations: list[dict[str, Any]], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                filter_predicate: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                post_trigger_include: Optional[str] = ..., 
                pre_trigger_include: Optional[str] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def query_conflicts(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, object]]] = None, 
                enable_cross_partition_query: Optional[bool] = None, 
                partition_key: Optional[PartitionKeyType] = None, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, object]]] = None, 
                partition_key: Optional[PartitionKeyType] = None, 
                enable_cross_partition_query: Optional[bool] = None, 
                max_item_count: Optional[int] = None, 
                enable_scan_in_query: Optional[bool] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosItemPaged: ...

        @overload
        def query_items(
                self, 
                query: str, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation_token_limit: Optional[int] = ..., 
                enable_cross_partition_query: Optional[bool] = ..., 
                enable_scan_in_query: Optional[bool] = ..., 
                feed_range: dict[str, Any], 
                full_text_score_scope: Optional[Literal[Local, Global]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                max_item_count: Optional[int] = ..., 
                parameters: Optional[list[dict[str, object]]] = ..., 
                populate_index_metrics: Optional[bool] = ..., 
                populate_query_advice: Optional[bool] = ..., 
                populate_query_metrics: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosItemPaged: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                partition_key: PartitionKeyType, 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                feed_range: dict[str, Any], 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                continuation: str, 
                max_item_count: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @overload
        def query_items_change_feed(
                self, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                max_item_count: Optional[int] = ..., 
                mode: Optional[Literal[LatestVersion, AllVersionsAndDeletes]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                start_time: Optional[Union[datetime, Literal[Now, Beginning]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read(
                self, 
                populate_query_metrics: Optional[bool] = None, 
                populate_partition_key_range_statistics: Optional[bool] = None, 
                populate_quota_info: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_all_items(
                self, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read_feed_ranges(
                self, 
                *, 
                force_refresh: bool = False, 
                **kwargs: Any
            ) -> Iterable[dict[str, Any]]: ...

        @distributed_trace
        def read_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                partition_key: PartitionKeyType, 
                populate_query_metrics: Optional[bool] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_integrated_cache_staleness_in_ms: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_items(
                self, 
                items: Sequence[Tuple[str, PartitionKeyType]], 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                consistency_level: Optional[str] = ..., 
                excluded_locations: Optional[list[str]] = ..., 
                executor: Optional[ThreadPoolExecutor] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                max_concurrency: Optional[int] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        @distributed_trace
        def read_offer(
                self, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def replace_item(
                self, 
                item: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_throughput(
                self, 
                throughput: Union[int, ThroughputProperties], 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        @distributed_trace
        def semantic_rerank(
                self, 
                *, 
                context: str, 
                documents: list[str], 
                options: Optional[dict[str, Any]] = ...
            ) -> CosmosDict: ...

        @distributed_trace
        def upsert_item(
                self, 
                body: dict[str, Any], 
                populate_query_metrics: Optional[bool] = None, 
                pre_trigger_include: Optional[str] = None, 
                post_trigger_include: Optional[str] = None, 
                *, 
                availability_strategy: Optional[Union[bool, dict[str, Any]]] = ..., 
                etag: Optional[str] = ..., 
                excluded_locations: Optional[Sequence[str]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                no_response: Optional[bool] = ..., 
                priority: Optional[Literal[High, Low]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = ..., 
                retry_write: Optional[int] = ..., 
                session_token: Optional[str] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...


namespace azure.cosmos.cosmos_client

    class azure.cosmos.cosmos_client.CosmosClient: implements ContextManager 

        def __init__(
                self, 
                url: str, 
                credential: Union[TokenCredential, str, dict[str, Any]], 
                consistency_level: Optional[str] = None, 
                **kwargs
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[TokenCredential, str, dict[str, Any]]] = None, 
                consistency_level: Optional[str] = None, 
                **kwargs
            ) -> CosmosClient: ...

        def close(self) -> None: ...

        @overload
        def create_database(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[False] = False, 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> DatabaseProxy: ...

        @overload
        def create_database(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[True], 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> tuple[DatabaseProxy, CosmosDict]: ...

        @overload
        def create_database_if_not_exists(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[False] = False, 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> DatabaseProxy: ...

        @overload
        def create_database_if_not_exists(
                self, 
                id: str, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                return_properties: Literal[True], 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> tuple[DatabaseProxy, CosmosDict]: ...

        @distributed_trace
        def delete_database(
                self, 
                database: Union[str, DatabaseProxy, Mapping[str, Any]], 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_database_account(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                **kwargs
            ) -> DatabaseAccount: ...

        def get_database_client(self, database: Union[str, DatabaseProxy, Mapping[str, Any]]) -> DatabaseProxy: ...

        @distributed_trace
        def list_databases(
                self, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_databases(
                self, 
                query: Optional[str] = None, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                enable_cross_partition_query: Optional[bool] = None, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any]], None]] = ..., 
                throughput_bucket: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...


namespace azure.cosmos.database

    class azure.cosmos.database.DatabaseProxy:
        id

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                id: str, 
                properties: Optional[dict[str, Any]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @overload
        def create_container(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        def create_container(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @overload
        def create_container_if_not_exists(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        def create_container_if_not_exists(
                self, 
                id: str, 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                offer_throughput: Optional[Union[int, ThroughputProperties]] = None, 
                unique_key_policy: Optional[dict[str, Any]] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                change_feed_policy: Optional[dict[str, Any]] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @distributed_trace
        def create_user(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...

        @distributed_trace
        def delete_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                etag: Optional[str] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                response_hook: Optional[Callable] = ..., 
                session_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user(
                self, 
                user: Union[str, UserProxy, Mapping[str, Any]], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_container_client(self, container: Union[str, ContainerProxy, Mapping[str, Any]]) -> ContainerProxy: ...

        @distributed_trace
        def get_throughput(
                self, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        def get_user_client(self, user: Union[str, UserProxy, Mapping[str, Any]]) -> UserProxy: ...

        @distributed_trace
        def list_containers(
                self, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                session_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_users(
                self, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_containers(
                self, 
                query: Optional[str] = None, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_users(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read(
                self, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                initial_headers: Optional[dict[str, str]] = ..., 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def read_offer(
                self, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Offer: ...

        @overload
        def replace_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[False] = False, 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> ContainerProxy: ...

        @overload
        def replace_container(
                self, 
                container: Union[str, ContainerProxy, Mapping[str, Any]], 
                partition_key: PartitionKey, 
                indexing_policy: Optional[dict[str, Any]] = None, 
                default_ttl: Optional[int] = None, 
                conflict_resolution_policy: Optional[dict[str, Any]] = None, 
                populate_query_metrics: Optional[bool] = None, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                computed_properties: Optional[list[dict[str, str]]] = ..., 
                full_text_policy: Optional[dict[str, Any]] = ..., 
                initial_headers: Optional[dict[str, str]] = ..., 
                return_properties: Literal[True], 
                vector_embedding_policy: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> tuple[ContainerProxy, CosmosDict]: ...

        @distributed_trace
        def replace_throughput(
                self, 
                throughput: Union[int, ThroughputProperties], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> ThroughputProperties: ...

        @distributed_trace
        def replace_user(
                self, 
                user: Union[str, UserProxy, Mapping[str, Any]], 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...

        @distributed_trace
        def upsert_user(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> UserProxy: ...


namespace azure.cosmos.documents

    class azure.cosmos.documents.ConnectionMode:
        Gateway: int = 0


    class azure.cosmos.documents.ConnectionPolicy:
        ConnectionMode: ConnectionMode
        ConnectionRetryConfiguration: Union[int, ConnectionRetryPolicy]
        DisableSSLVerification: boolean
        EnableEndpointDiscovery: boolean
        ExcludedLocations: list[str]
        PreferredLocations: list[str]
        ProxyConfiguration: ProxyConfiguration
        RequestTimeout: int
        ResponsePayloadOnWriteDisabled: boolean
        RetryNonIdempotentWrites: int
        RetryOptions: RetryOptions
        SSLConfiguration: SSLConfiguration
        UseMultipleWriteLocations: boolean

        def __init__(self) -> None: ...


    class azure.cosmos.documents.ConsistencyLevel:
        BoundedStaleness: Literal["BoundedStaleness"] = BoundedStaleness
        ConsistentPrefix: Literal["ConsistentPrefix"] = ConsistentPrefix
        Eventual: Literal["Eventual"] = Eventual
        Session: Literal["Session"] = Session
        Strong: Literal["Strong"] = Strong


    class azure.cosmos.documents.DataType:
        LineString: Literal["LineString"] = LineString
        MultiPolygon: Literal["MultiPolygon"] = MultiPolygon
        Number: Literal["Number"] = Number
        Point: Literal["Point"] = Point
        Polygon: Literal["Polygon"] = Polygon
        String: Literal["String"] = String


    class azure.cosmos.documents.DatabaseAccount:
        property ReadableLocations: list[dict[str, str]]    # Read-only
        property WritableLocations: list[dict[str, str]]    # Read-only
        ConsistencyPolicy: dict[str, Any]
        CurrentMediaStorageUsageInMB: int
        DatabaseLink: str
        EnableMultipleWritableLocations: boolean
        MaxMediaStorageUsageInMB: int
        MediaLink: str

        def __init__(self) -> None: ...


    class azure.cosmos.documents.IndexKind:
        Hash: Literal["Hash"] = Hash
        MultiHash: Literal["MultiHash"] = MultiHash
        Range: Literal["Range"] = Range


    class azure.cosmos.documents.IndexingDirective:
        Default: int = 0
        Exclude: int = 1
        Include: int = 2


    class azure.cosmos.documents.IndexingMode:
        Consistent: Literal["consistent"] = consistent
        Lazy: Literal["lazy"] = lazy
        NoIndex: Literal["none"] = none


    class azure.cosmos.documents.PartitionKind:
        Hash: Literal["Hash"] = Hash
        MultiHash: Literal["MultiHash"] = MultiHash


    class azure.cosmos.documents.PermissionMode:
        All: Literal["all"] = all
        NoneMode: Literal["none"] = none
        Read: Literal["read"] = read


    class azure.cosmos.documents.ProxyConfiguration:
        Host: str
        Port: int

        def __init__(self) -> None: ...


    class azure.cosmos.documents.RetryOptions:
        property FixedRetryIntervalInMilliseconds: Optional[int]    # Read-only
        property MaxRetryAttemptCount: int    # Read-only
        property MaxWaitTimeInSeconds: int    # Read-only
        FixedRetryIntervalInMilliseconds: int
        MaxRetryAttemptCount: int
        MaxWaitTimeInSeconds: int

        def __init__(
                self, 
                max_retry_attempt_count: int = 9, 
                fixed_retry_interval_in_milliseconds: Optional[int] = None, 
                max_wait_time_in_seconds: int = 30
            ): ...


    class azure.cosmos.documents.SSLConfiguration:
        SSLCaCerts: Union[str, bool]
        SSLCertFile: str
        SSLKeyFIle: str

        def __init__(self) -> None: ...


    class azure.cosmos.documents.TriggerOperation:
        All: Literal["all"] = all
        Create: Literal["create"] = create
        Delete: Literal["delete"] = delete
        Replace: Literal["replace"] = replace
        Update: Literal["update"] = update


    class azure.cosmos.documents.TriggerType:
        Post: Literal["post"] = post
        Pre: Literal["pre"] = pre


    class azure.cosmos.documents.UserConsistencyPolicy(TypedDict, total=False):
        key "defaultConsistencyLevel": str
        key "maxStalenessIntervalInSeconds": int
        key "maxStalenessPrefix": int


namespace azure.cosmos.errors

    class azure.cosmos.errors.CosmosAccessConditionFailedError(CosmosHttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


    class azure.cosmos.errors.CosmosBatchOperationError(HttpResponseError):
        error_index: int
        headers: dict[str, Any]
        message: str
        operation_responses: List[dict[str, Any]]
        status_code: int

        def __init__(
                self, 
                error_index: int = None, 
                headers: dict[str, Any] = None, 
                status_code: int = None, 
                message: str = None, 
                operation_responses: List[dict[str, Any]] = None, 
                **kwargs
            ): ...


    class azure.cosmos.errors.CosmosClientTimeoutError(AzureError):

        def __init__(
                self, 
                message = None, 
                **kwargs
            ): ...


    class azure.cosmos.errors.CosmosHttpResponseError(HttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


    class azure.cosmos.errors.CosmosResourceExistsError(ResourceExistsError, CosmosHttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


    class azure.cosmos.errors.CosmosResourceNotFoundError(ResourceNotFoundError, CosmosHttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


namespace azure.cosmos.exceptions

    class azure.cosmos.exceptions.CosmosAccessConditionFailedError(CosmosHttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


    class azure.cosmos.exceptions.CosmosBatchOperationError(HttpResponseError):
        error_index: int
        headers: dict[str, Any]
        message: str
        operation_responses: List[dict[str, Any]]
        status_code: int

        def __init__(
                self, 
                error_index: int = None, 
                headers: dict[str, Any] = None, 
                status_code: int = None, 
                message: str = None, 
                operation_responses: List[dict[str, Any]] = None, 
                **kwargs
            ): ...


    class azure.cosmos.exceptions.CosmosClientTimeoutError(AzureError):

        def __init__(
                self, 
                message = None, 
                **kwargs
            ): ...


    class azure.cosmos.exceptions.CosmosHttpResponseError(HttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


    class azure.cosmos.exceptions.CosmosResourceExistsError(ResourceExistsError, CosmosHttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


    class azure.cosmos.exceptions.CosmosResourceNotFoundError(ResourceNotFoundError, CosmosHttpResponseError):

        def __init__(
                self, 
                status_code: int = None, 
                message: str = None, 
                response = None, 
                **kwargs
            ): ...

        def __str__(self): ...


namespace azure.cosmos.http_constants

    class azure.cosmos.http_constants.CookieHeaders:
        SessionToken = x-ms-session-token


    class azure.cosmos.http_constants.Delimiters:
        ClientContinuationDelimiter = !!
        ClientContinuationFormat = {0}!!{1}


    class azure.cosmos.http_constants.HttpContextProperties:
        SubscriptionId = SubscriptionId


    class azure.cosmos.http_constants.HttpHeaderPreferenceTokens:
        PreferUnfilteredQueryResponse = PreferUnfilteredQueryResponse


    class azure.cosmos.http_constants.HttpHeaders:
        AIM = A-IM
        Accept = Accept
        AcceptCharset = Accept-Charset
        AcceptEncoding = Accept-Encoding
        AcceptLanguage = Accept-Language
        AcceptRanges = Accept-Ranges
        AccessControlAllowHeaders = Access-Control-Allow-Headers
        AccessControlAllowOrigin = Access-Control-Allow-Origin
        ActivityId = x-ms-activity-id
        AllowTentativeWrites = x-ms-cosmos-allow-tentative-writes
        AlternateContentPath = x-ms-alt-content-path
        Authorization = authorization
        AutoscaleSettings = x-ms-cosmos-offer-autopilot-settings
        CacheControl = Cache-Control
        ChangeFeedWireFormatVersion = x-ms-cosmos-changefeed-wire-format-version
        CharacterSet = CharacterSet
        ClientId = x-ms-client-id
        CollectionCurrentUsageInMb = x-ms-collection-usage-mb
        CollectionPartitionInfo = x-ms-collection-partition-info
        CollectionQuotaInMb = x-ms-collection-quota-mb
        CollectionServiceInfo = x-ms-collection-service-info
        ConsistencyLevel = x-ms-consistency-level
        ContentEncoding = Content-Encoding
        ContentLanguage = Content-Language
        ContentLength = Content-Length
        ContentLocation = Content-Location
        ContentMd5 = Content-Md5
        ContentPath = x-ms-content-path
        ContentRange = Content-Range
        ContentType = Content-Type
        Continuation = x-ms-continuation
        CorrelatedActivityId = x-ms-cosmos-correlated-activityid
        CosmosItemLsn = x-ms-cosmos-item-llsn
        CosmosLsn = x-ms-cosmos-llsn
        CosmosQuorumAckedLsn = x-ms-cosmos-quorum-acked-llsn
        CurrentEntityCount = x-ms-root-entity-current-count
        CurrentMediaStorageUsageInMB = x-ms-media-storage-usage-mb
        CurrentReplicaSetSize = x-ms-current-replica-set-size
        CurrentWriteQuorum = x-ms-current-write-quorum
        DedicatedGatewayCacheStaleness = x-ms-dedicatedgateway-max-age
        DisableRUPerMinuteUsage = x-ms-documentdb-disable-ru-per-minute-usage
        ETag = etag
        EmitVerboseTracesInQuery = x-ms-documentdb-query-emit-traces
        EnableCrossPartitionQuery = x-ms-documentdb-query-enablecrosspartition
        EnableScanInQuery = x-ms-documentdb-query-enable-scan
        EnableScriptLogging = x-ms-documentdb-script-enable-logging
        EndEpkString = x-ms-end-epk
        ForceRefresh = x-ms-force-refresh
        FullFidelityFeedHeaderValue = Full-Fidelity Feed
        FullUpgrade = x-ms-force-full-upgrade
        GatewayVersion = x-ms-gatewayversion
        GlobalCommittedLsn = x-ms-global-committed-lsn
        Host = Host
        HttpDate = date
        IfMatch = If-Match
        IfModified_since = If-Modified-Since
        IfNoneMatch = If-None-Match
        IfRange = If-Range
        IfUnmodifiedSince = If-Unmodified-Since
        IgnoreInProgressUpgrade = x-ms-ignore-inprogress-upgrade
        IncrementalFeedHeaderValue = Incremental feed
        IndexTransformationProgress = x-ms-documentdb-collection-index-transformation-progress
        IndexUtilization = x-ms-cosmos-index-utilization
        IndexingDirective = x-ms-indexing-directive
        IntegratedCacheHit = x-ms-cosmos-cachehit
        IntendedCollectionRID = x-ms-cosmos-intended-collection-rid
        IsBatchAtomic = x-ms-cosmos-batch-atomic
        IsBatchRequest = x-ms-cosmos-is-batch-request
        IsCanary = x-ms-iscanary
        IsContinuationExpected = x-ms-documentdb-query-iscontinuationexpected
        IsFeedUnfiltered = x-ms-is-feed-unfiltered
        IsQuery = x-ms-documentdb-isquery
        IsQueryPlanRequest = x-ms-cosmos-is-query-plan-request
        IsRUPerMinuteUsed = x-ms-documentdb-is-ru-per-minute-used
        IsUpsert = x-ms-documentdb-is-upsert
        ItemCount = x-ms-item-count
        ItemLsn = x-ms-item-lsn
        KeepAlive = Keep-Alive
        KeyValueEncodingFormat = application/x-www-form-urlencoded
        LSN = lsn
        LastModified = Last-Modified
        LastStateChangeUtc = x-ms-last-state-change-utc
        LazyIndexingProgress = x-ms-documentdb-collection-lazy-indexing-progress
        Location = Location
        MaxEntityCount = x-ms-root-entity-max-count
        MaxForwards = Max-Forwards
        MaxMediaStorageUsageInMB = x-ms-max-media-storage-usage-mb
        MethodOverride = X-HTTP-Method
        NewResourceId = x-ms-new-resource-id
        NumberOfReadRegions = x-ms-number-of-read-regions
        OcpResourceProviderRegisteredUri = ocp-resourceprovider-registered-uri
        OfferIsRUPerMinuteThroughputEnabled = x-ms-offer-is-ru-per-minute-throughput-enabled
        OfferThroughput = x-ms-offer-throughput
        OfferType = x-ms-offer-type
        OnlyUpgradeNonSystemApplications = x-ms-only-upgrade-non-system-applications
        OnlyUpgradeSystemApplications = x-ms-only-upgrade-system-applications
        Origin = Origin
        PageSize = x-ms-max-item-count
        PartitionKey = x-ms-documentdb-partitionkey
        PartitionKeyDeletePending = x-ms-cosmos-is-partition-key-delete-pending
        PartitionKeyRangeID = x-ms-documentdb-partitionkeyrangeid
        PhysicalPartitionId = x-ms-cosmos-physical-partition-id
        PopulateIndexMetrics = x-ms-cosmos-populateindexmetrics
        PopulatePartitionKeyRangeStatistics = x-ms-documentdb-populatepartitionstatistics
        PopulateQueryAdvice = x-ms-cosmos-populatequeryadvice
        PopulateQueryMetrics = x-ms-documentdb-populatequerymetrics
        PopulateQuotaInfo = x-ms-documentdb-populatequotainfo
        PostTriggerExclude = x-ms-documentdb-post-trigger-exclude
        PostTriggerInclude = x-ms-documentdb-post-trigger-include
        Pragma = Pragma
        PreTriggerExclude = x-ms-documentdb-pre-trigger-exclude
        PreTriggerInclude = x-ms-documentdb-pre-trigger-include
        Prefer = Prefer
        PriorityLevel = x-ms-cosmos-priority-level
        ProxyAuthenticate = Proxy-Authenticate
        ProxyAuthorization = Proxy-Authorization
        Query = x-ms-documentdb-query
        QueryAdvice = x-ms-cosmos-query-advice
        QueryExecutionInfo = x-ms-cosmos-query-execution-info
        QueryMetrics = x-ms-documentdb-query-metrics
        QueryVersion = x-ms-cosmos-query-version
        QuorumAckedLsn = x-ms-quorum-acked-lsn
        ReadFeedKeyType = x-ms-read-key-type
        Referer = referer
        RequestCharge = x-ms-request-charge
        RequestDurationMs = x-ms-request-duration-ms
        RequestId = x-ms-request-id
        ResourceQuota = x-ms-resource-quota
        ResourceTokenExpiry = x-ms-documentdb-expiry-seconds
        ResourceUsage = x-ms-resource-usage
        ResponseContinuationTokenLimitInKb = x-ms-documentdb-responsecontinuationtokenlimitinkb
        RetryAfter = Retry-After
        RetryAfterInMilliseconds = x-ms-retry-after-ms
        SDKSupportedCapabilities = x-ms-cosmos-sdk-supportedcapabilities
        SchemaVersion = x-ms-schemaversion
        ScriptLogResults = x-ms-documentdb-script-log-results
        SeparateMetaWithCrts = 2021-09-15
        Server = Server
        ServiceVersion = x-ms-serviceversion
        SessionToken = x-ms-session-token
        SetCookie = Set-Cookie
        ShouldBatchContinueOnError = x-ms-cosmos-batch-continue-on-error
        SimpleToken = SWT
        Slug = Slug
        StartEpkString = x-ms-start-epk
        StrictTransportSecurity = Strict-Transport-Security
        SubStatus = x-ms-substatus
        SupportedQueryFeatures = x-ms-cosmos-supported-query-features
        ThinClientProxyOperationType = x-ms-thinclient-proxy-operation-type
        ThinClientProxyResourceType = x-ms-thinclient-proxy-resource-type
        ThrottleRetryCount = x-ms-throttle-retry-count
        ThrottleRetryWaitTimeInMs = x-ms-throttle-retry-wait-time-ms
        ThroughputBucket = x-ms-cosmos-throughput-bucket
        TransferEncoding = Transfer-Encoding
        TransportRequestId = x-ms-transport-request-id
        UpgradeFabricRingCodeAndConfig = x-ms-upgrade-fabric-code-config
        UpgradeVerificationKind = x-ms-upgrade-verification-kind
        UseMasterCollectionResolver = x-ms-use-master-collection-resolver
        UserAgent = User-Agent
        Version = x-ms-version
        WrapAssertion = wrap_assertion
        WrapAssertionFormat = wrap_assertion_format
        WrapScope = wrap_scope
        WwwAuthenticate = Www-Authenticate
        XDate = x-ms-date
        XpRole = x-ms-xp-role


    class azure.cosmos.http_constants.HttpListenerErrorCodes:
        ERROR_CONNECTION_INVALID = 1229
        ERROR_OPERATION_ABORTED = 995


    class azure.cosmos.http_constants.HttpMethods:
        Delete = DELETE
        Get = GET
        Head = HEAD
        Options = OPTIONS
        Post = POST
        Put = PUT


    class azure.cosmos.http_constants.HttpStatusDescriptions:
        Accepted = Accepted
        BadGateway = Bad Gateway
        BadRequest = Bad Request
        Conflict = Conflict
        Created = Created
        Forbidden = Forbidden
        GatewayTimeout = Gateway timed out
        Gone = Gone
        InternalServerError = Internal Server Error
        LengthRequired = Length Required
        MethodNotAllowed = MethodNotAllowed
        NoContent = No Content
        NotAcceptable = Not Acceptable
        NotFound = Not Found
        NotModified = Not Modified
        OK = Ok
        PreconditionFailed = Precondition Failed
        RequestEntityTooLarge = Request Entity Too Large
        RequestTimeout = Request timed out
        RetryWith = Retry the request
        ServiceUnavailable = Service Unavailable
        TooManyRequests = Too Many Requests
        Unauthorized = Unauthorized
        UnsupportedMediaType = Unsupported Media Type


    class azure.cosmos.http_constants.QueryStrings:
        ContentView = contentview
        Filter = $filter
        GenerateId = $generateFor
        GenerateIdBatchSize = $batchSize
        Generic = generic
        GetChildResourcePartitions = $getChildResourcePartitions
        Query = query
        RootIndex = $rootIndex
        SQLQueryType = sql
        Url = $resolveFor


    class azure.cosmos.http_constants.ResourceType:
        Attachment = attachments
        Collection = colls
        Conflict = conflicts
        Database = dbs
        DatabaseAccount = databaseaccount
        Document = docs
        Offer = offers
        PartitionKey = partitionkey
        PartitionKeyRange = pkranges
        Permission = permissions
        Schema = schemas
        StoredProcedure = sprocs
        Topology = topology
        Trigger = triggers
        User = users
        UserDefinedFunction = udfs

        @staticmethod
        def IsCollectionChild(resourceType: str) -> bool: ...


    class azure.cosmos.http_constants.SDKSupportedCapabilities:
        NONE = 0
        PARTITION_MERGE = 1


    class azure.cosmos.http_constants.StatusCodes:
        ACCEPTED = 202
        BAD_REQUEST = 400
        CONFLICT = 409
        CREATED = 201
        FAILED_DEPENDENCY = 424
        FORBIDDEN = 403
        GONE = 410
        INTERNAL_SERVER_ERROR = 500
        METHOD_NOT_ALLOWED = 405
        NOT_FOUND = 404
        NOT_MODIFIED = 304
        NO_CONTENT = 204
        OK = 200
        OPERATION_CANCELLED = 1201
        OPERATION_PAUSED = 1200
        PRECONDITION_FAILED = 412
        REQUEST_ENTITY_TOO_LARGE = 413
        REQUEST_TIMEOUT = 408
        RETRY_WITH = 449
        SERVICE_UNAVAILABLE = 503
        TOO_MANY_REQUESTS = 429
        UNAUTHORIZED = 401


    class azure.cosmos.http_constants.SubStatusCodes:
        AAD_REQUEST_NOT_AUTHORIZED = 5300
        COLLECTION_RID_MISMATCH = 1024
        COMPLETING_PARTITION_MIGRATION = 1008
        COMPLETING_SPLIT = 1007
        CONFLICT_WITH_CONTROL_PLANE = 1006
        CONTAINER_CREATE_IN_PROGRESS = 1013
        CROSS_PARTITION_QUERY_NOT_SERVABLE = 1004
        DATABASE_ACCOUNT_NOT_FOUND = 1008
        INSUFFICIENT_BINDABLE_PARTITIONS = 1007
        NAME_CACHE_IS_STALE = 1000
        OWNER_RESOURCE_NOT_FOUND = 1003
        PARTITION_KEY_MISMATCH = 1001
        PARTITION_KEY_RANGE_GONE = 1002
        PROVISION_LIMIT_REACHED = 1005
        READ_SESSION_NOTAVAILABLE = 1002
        REDUNDANT_COLLECTION_PUT = 1009
        SHARED_THROUGHPUT_DATABASE_QUOTA_EXCEEDED = 1010
        SHARED_THROUGHPUT_OFFER_GROW_NOT_NEEDED = 1011
        THROUGHPUT_OFFER_NOT_FOUND = 10004
        UNKNOWN = 0
        WRITE_FORBIDDEN = 3


    class azure.cosmos.http_constants.Versions:
        CurrentVersion = 2020-07-15
        QueryVersion = 1.0
        SDKName = azure-cosmos


namespace azure.cosmos.offer

    class azure.cosmos.offer.Offer:

        def __init__(
                self, 
                *args, 
                *, 
                auto_scale_increment_percent: Optional[int] = ..., 
                auto_scale_max_throughput: Optional[int] = ..., 
                offer_throughput: Optional[int] = ..., 
                **kwargs
            ) -> None: ...

        def get_response_headers(self) -> Mapping[str, Any]: ...


    class azure.cosmos.offer.ThroughputProperties:

        def __init__(
                self, 
                *args, 
                *, 
                auto_scale_increment_percent: Optional[int] = ..., 
                auto_scale_max_throughput: Optional[int] = ..., 
                offer_throughput: Optional[int] = ..., 
                **kwargs
            ) -> None: ...

        def get_response_headers(self) -> Mapping[str, Any]: ...


namespace azure.cosmos.partition_key

    class azure.cosmos.partition_key.NonePartitionKeyValue:


    class azure.cosmos.partition_key.NullPartitionKeyValue:


    class azure.cosmos.partition_key.PartitionKey(dict):
        property kind: Literal["MultiHash", "Hash"]
        property path: str
        property version: int
        kind: str
        path: str
        version: int

        @overload
        def __init__(
                self, 
                path: list[str], 
                *, 
                kind: Literal["MultiHash"] = "MultiHash", 
                version: int = _PartitionKeyVersion.V2
            ) -> None: ...

        @overload
        def __init__(
                self, 
                path: str, 
                *, 
                kind: Literal["Hash"] = "Hash", 
                version: int = _PartitionKeyVersion.V2
            ) -> None: ...

        def __repr__(self) -> str: ...


namespace azure.cosmos.permission

    class azure.cosmos.permission.Permission:

        def __init__(
                self, 
                id: str, 
                user_link: str, 
                permission_mode: str, 
                resource_link: str, 
                properties: Mapping[str, Any]
            ) -> None: ...


    class azure.cosmos.permission.PermissionMode:
        All: Literal["all"] = all
        NoneMode: Literal["none"] = none
        Read: Literal["read"] = read


namespace azure.cosmos.scripts

    def azure.cosmos.scripts.build_options(kwargs: dict[str, Any]) -> dict[str, Any]: ...


    class azure.cosmos.scripts.Constants:
        AAD_DEFAULT_SCOPE: str = "https://cosmos.azure.com/.default"
        AAD_SCOPE_OVERRIDE: str = "AZURE_COSMOS_AAD_SCOPE_OVERRIDE"
        AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES: str = "AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES"
        AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES_DEFAULT: int = 3
        AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS: str = "AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS"
        AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS_DEFAULT: int = 500
        CIRCUIT_BREAKER_ENABLED_CONFIG: str = "AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"
        CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT: str = "False"
        CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ: str = "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ"
        CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ_DEFAULT: int = 10
        CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE: str = "AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE"
        CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE_DEFAULT: int = 5
        ContainerRID: Literal["containerRID"] = containerRID
        DatabaseAccountEndpoint: Literal["databaseAccountEndpoint"] = databaseAccountEndpoint
        DefaultConsistencyLevel: Literal["defaultConsistencyLevel"] = defaultConsistencyLevel
        DefaultEndpointsRefreshTime: int = 300000
        ERROR_TRANSLATIONS: dict[int, str] = {400: 'BAD_REQUEST - Request being sent is invalid.', 401: "UNAUTHORIZED - The input authorization token can't serve the request.", 403: 'FORBIDDEN', 404: 'NOT_FOUND - Entity with the specified id does not exist in the system.', 405: 'METHOD_NOT_ALLOWED', 408: 'REQUEST_TIMEOUT', 409: 'CONFLICT - Entity with the specified id already exists in the system.', 410: 'GONE', 412: 'PRECONDITION_FAILED - Operation cannot be performed because one of the specified precondition is not met', 413: 'REQUEST_ENTITY_TOO_LARGE - Document size exceeds limit.', 424: 'FAILED_DEPENDENCY - There is a failure in the transactional batch.', 429: 'TOO_MANY_REQUESTS', 449: 'RETRY_WITH - Conflicting request to resource has been attempted. Retry to avoid conflicts.'}
        EnableMultipleWritableLocations: Literal["enableMultipleWriteLocations"] = enableMultipleWriteLocations
        EnablePerPartitionFailoverBehavior: Literal["enablePerPartitionFailoverBehavior"] = enablePerPartitionFailoverBehavior
        FAILURE_PERCENTAGE_TOLERATED = AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED
        FAILURE_PERCENTAGE_TOLERATED_DEFAULT: int = 90
        HS_MAX_ITEMS_CONFIG: str = "AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"
        HS_MAX_ITEMS_CONFIG_DEFAULT: int = 1000
        INFERENCE_SERVICE_DEFAULT_SCOPE = https://dbinference.azure.com/.default
        MAX_ITEM_BUFFER_VS_CONFIG: str = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
        MAX_ITEM_BUFFER_VS_CONFIG_DEFAULT: int = 50000
        Name: Literal["name"] = name
        OperationStartTime: Literal["operationStartTime"] = operationStartTime
        ReadableLocations: Literal["readableLocations"] = readableLocations
        SEMANTIC_RERANKER_INFERENCE_ENDPOINT: str = "AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT"
        SESSION_TOKEN_FALSE_PROGRESS_MERGE_CONFIG: str = "AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE"
        SESSION_TOKEN_FALSE_PROGRESS_MERGE_CONFIG_DEFAULT: str = "True"
        TIMEOUT_ERROR_THRESHOLD_PPAF = AZURE_COSMOS_TIMEOUT_ERROR_THRESHOLD_FOR_PPAF
        TIMEOUT_ERROR_THRESHOLD_PPAF_DEFAULT: int = 10
        TimeoutScope: Literal["timeoutScope"] = timeoutScope
        UserConsistencyPolicy: Literal["userConsistencyPolicy"] = userConsistencyPolicy
        WritableLocations: Literal["writableLocations"] = writableLocations


    class azure.cosmos.scripts.CosmosClientConnection:
        property ReadEndpoint: str    # Read-only
        property Session: Optional[Session]
        property WriteEndpoint: str    # Read-only
        PartitionResolverErrorMessage = Couldn't find any partition resolvers for the database link provided. Ensure that the link you used when registering the partition resolvers matches the link provided or you need to register both types of database link(self link as well as ID based link).

        def __init__(
                self, 
                url_connection: str, 
                auth: CredentialDict, 
                connection_policy: Optional[ConnectionPolicy] = None, 
                consistency_level: Optional[str] = None, 
                availability_strategy: Union[bool, dict[str, Any]] = False, 
                availability_strategy_executor: Optional[ThreadPoolExecutor] = None, 
                **kwargs: Any
            ) -> None: ...

        def Batch(
                self, 
                collection_link: str, 
                batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ]], Tuple[str, Tuple[Any, ], dict[str, Any]]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosList: ...

        def Create(
                self, 
                body: dict[str, Any], 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateContainer(
                self, 
                database_link: str, 
                collection: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateDatabase(
                self, 
                database: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateItem(
                self, 
                database_or_container_link: str, 
                document: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreatePermission(
                self, 
                user_link: str, 
                permission: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateStoredProcedure(
                self, 
                collection_link: str, 
                sproc: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateTrigger(
                self, 
                collection_link: str, 
                trigger: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateUser(
                self, 
                database_link: str, 
                user: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateUserDefinedFunction(
                self, 
                collection_link: str, 
                udf: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def DeleteAllItemsByPartitionKey(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteConflict(
                self, 
                conflict_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteContainer(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteDatabase(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteItem(
                self, 
                document_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeletePermission(
                self, 
                permission_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteResource(
                self, 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteStoredProcedure(
                self, 
                sproc_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteTrigger(
                self, 
                trigger_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteUser(
                self, 
                user_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteUserDefinedFunction(
                self, 
                udf_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def ExecuteStoredProcedure(
                self, 
                sproc_link: str, 
                params: Optional[Union[dict[str, Any], list[dict[str, Any]]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> Any: ...

        def GetDatabaseAccount(
                self, 
                url_connection: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseAccount: ...

        def GetPartitionResolver(self, database_link: str) -> Optional[RangePartitionResolver]: ...

        def PatchItem(
                self, 
                document_link: str, 
                operations: list[dict[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def QueryConflicts(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryContainers(
                self, 
                database_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryDatabases(
                self, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryFeed(
                self, 
                path: str, 
                collection_id: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Mapping[str, Any], 
                partition_key_range_id: Optional[str] = None, 
                **kwargs: Any
            ) -> Tuple[list[dict[str, Any]], CaseInsensitiveDict]: ...

        def QueryItems(
                self, 
                database_or_container_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                partition_key: Optional[PartitionKeyType] = None, 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = None, 
                **kwargs: Any
            ) -> CosmosItemPaged: ...

        def QueryItemsChangeFeed(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryOffers(
                self, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryPermissions(
                self, 
                user_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryStoredProcedures(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryTriggers(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryUserDefinedFunctions(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryUsers(
                self, 
                database_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def Read(
                self, 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadConflict(
                self, 
                conflict_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadConflicts(
                self, 
                collection_link: str, 
                feed_options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadContainer(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadContainers(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadDatabase(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadDatabases(
                self, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadItem(
                self, 
                document_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs
            ) -> CosmosDict: ...

        def ReadItems(
                self, 
                collection_link: str, 
                feed_options: Optional[Mapping[str, Any]] = None, 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadOffer(
                self, 
                offer_link: str, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadOffers(
                self, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadPermission(
                self, 
                permission_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadPermissions(
                self, 
                user_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadStoredProcedure(
                self, 
                sproc_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadStoredProcedures(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadTrigger(
                self, 
                trigger_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadTriggers(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadUser(
                self, 
                user_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadUserDefinedFunction(
                self, 
                udf_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadUserDefinedFunctions(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadUsers(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def RegisterPartitionResolver(
                self, 
                database_link: str, 
                partition_resolver: RangePartitionResolver
            ) -> None: ...

        def Replace(
                self, 
                resource: dict[str, Any], 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceContainer(
                self, 
                collection_link: str, 
                collection: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceItem(
                self, 
                document_link: str, 
                new_document: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceOffer(
                self, 
                offer_link: str, 
                offer: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplacePermission(
                self, 
                permission_link: str, 
                permission: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceStoredProcedure(
                self, 
                sproc_link: str, 
                sproc: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceTrigger(
                self, 
                trigger_link: str, 
                trigger: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceUser(
                self, 
                user_link: str, 
                user: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceUserDefinedFunction(
                self, 
                udf_link: str, 
                udf: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def Upsert(
                self, 
                body: dict[str, Any], 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertItem(
                self, 
                database_or_container_link: str, 
                document: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertPermission(
                self, 
                user_link: str, 
                permission: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertStoredProcedure(
                self, 
                collection_link: str, 
                sproc: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertTrigger(
                self, 
                collection_link: str, 
                trigger: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertUser(
                self, 
                database_link: str, 
                user: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertUserDefinedFunction(
                self, 
                collection_link: str, 
                udf: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def health_check(
                self, 
                url_connection: Optional[str] = None, 
                **kwargs: Any
            ): ...

        def read_items(
                self, 
                collection_link: str, 
                items: Sequence[Tuple[str, PartitionKeyType]], 
                options: Optional[Mapping[str, Any]] = None, 
                *, 
                executor: Optional[ThreadPoolExecutor] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        def refresh_routing_map_provider(
                self, 
                collection_link: Optional[str] = None, 
                previous_routing_map: Optional[Any] = None, 
                feed_options: Optional[dict[str, Any]] = None
            ) -> None: ...


    class azure.cosmos.scripts.CosmosDict(dict[str, Any]):

        def __init__(
                self, 
                original_dict: Optional[Mapping[str, Any]], 
                /, 
                *, 
                response_headers: CaseInsensitiveDict
            ) -> None: ...

        def get_response_headers(self) -> CaseInsensitiveDict: ...


    class azure.cosmos.scripts.NonePartitionKeyValue:


    class azure.cosmos.scripts.ScriptType:
        StoredProcedure = sprocs
        Trigger = triggers
        UserDefinedFunction = udfs


    class azure.cosmos.scripts.ScriptsProxy:

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                container_link: str, 
                is_system_key: bool
            ) -> None: ...

        @distributed_trace
        def create_stored_procedure(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def create_trigger(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def create_user_defined_function(
                self, 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def delete_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def execute_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                partition_key: Optional[PartitionKeyType] = None, 
                params: Optional[list[dict[str, Any]]] = None, 
                enable_script_logging: Optional[bool] = None, 
                **kwargs: Any
            ) -> Any: ...

        @distributed_trace
        def get_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def get_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def get_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def list_stored_procedures(
                self, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_triggers(
                self, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def list_user_defined_functions(
                self, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_stored_procedures(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_triggers(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_user_defined_functions(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def replace_stored_procedure(
                self, 
                sproc: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_trigger(
                self, 
                trigger: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_user_defined_function(
                self, 
                udf: Union[str, Mapping[str, Any]], 
                body: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...


namespace azure.cosmos.user

    def azure.cosmos.user.build_options(kwargs: dict[str, Any]) -> dict[str, Any]: ...


    class azure.cosmos.user.CosmosClientConnection:
        property ReadEndpoint: str    # Read-only
        property Session: Optional[Session]
        property WriteEndpoint: str    # Read-only
        PartitionResolverErrorMessage = Couldn't find any partition resolvers for the database link provided. Ensure that the link you used when registering the partition resolvers matches the link provided or you need to register both types of database link(self link as well as ID based link).

        def __init__(
                self, 
                url_connection: str, 
                auth: CredentialDict, 
                connection_policy: Optional[ConnectionPolicy] = None, 
                consistency_level: Optional[str] = None, 
                availability_strategy: Union[bool, dict[str, Any]] = False, 
                availability_strategy_executor: Optional[ThreadPoolExecutor] = None, 
                **kwargs: Any
            ) -> None: ...

        def Batch(
                self, 
                collection_link: str, 
                batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ]], Tuple[str, Tuple[Any, ], dict[str, Any]]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosList: ...

        def Create(
                self, 
                body: dict[str, Any], 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateContainer(
                self, 
                database_link: str, 
                collection: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateDatabase(
                self, 
                database: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateItem(
                self, 
                database_or_container_link: str, 
                document: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreatePermission(
                self, 
                user_link: str, 
                permission: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateStoredProcedure(
                self, 
                collection_link: str, 
                sproc: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateTrigger(
                self, 
                collection_link: str, 
                trigger: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateUser(
                self, 
                database_link: str, 
                user: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def CreateUserDefinedFunction(
                self, 
                collection_link: str, 
                udf: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def DeleteAllItemsByPartitionKey(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteConflict(
                self, 
                conflict_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteContainer(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteDatabase(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteItem(
                self, 
                document_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeletePermission(
                self, 
                permission_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteResource(
                self, 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteStoredProcedure(
                self, 
                sproc_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteTrigger(
                self, 
                trigger_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteUser(
                self, 
                user_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def DeleteUserDefinedFunction(
                self, 
                udf_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> None: ...

        def ExecuteStoredProcedure(
                self, 
                sproc_link: str, 
                params: Optional[Union[dict[str, Any], list[dict[str, Any]]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> Any: ...

        def GetDatabaseAccount(
                self, 
                url_connection: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseAccount: ...

        def GetPartitionResolver(self, database_link: str) -> Optional[RangePartitionResolver]: ...

        def PatchItem(
                self, 
                document_link: str, 
                operations: list[dict[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def QueryConflicts(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryContainers(
                self, 
                database_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryDatabases(
                self, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryFeed(
                self, 
                path: str, 
                collection_id: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Mapping[str, Any], 
                partition_key_range_id: Optional[str] = None, 
                **kwargs: Any
            ) -> Tuple[list[dict[str, Any]], CaseInsensitiveDict]: ...

        def QueryItems(
                self, 
                database_or_container_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                partition_key: Optional[PartitionKeyType] = None, 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = None, 
                **kwargs: Any
            ) -> CosmosItemPaged: ...

        def QueryItemsChangeFeed(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryOffers(
                self, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryPermissions(
                self, 
                user_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryStoredProcedures(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryTriggers(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryUserDefinedFunctions(
                self, 
                collection_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def QueryUsers(
                self, 
                database_link: str, 
                query: Optional[Union[str, dict[str, Any]]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def Read(
                self, 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadConflict(
                self, 
                conflict_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadConflicts(
                self, 
                collection_link: str, 
                feed_options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadContainer(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadContainers(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadDatabase(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadDatabases(
                self, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadItem(
                self, 
                document_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs
            ) -> CosmosDict: ...

        def ReadItems(
                self, 
                collection_link: str, 
                feed_options: Optional[Mapping[str, Any]] = None, 
                response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadOffer(
                self, 
                offer_link: str, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadOffers(
                self, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadPermission(
                self, 
                permission_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadPermissions(
                self, 
                user_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadStoredProcedure(
                self, 
                sproc_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadStoredProcedures(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadTrigger(
                self, 
                trigger_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadTriggers(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadUser(
                self, 
                user_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadUserDefinedFunction(
                self, 
                udf_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReadUserDefinedFunctions(
                self, 
                collection_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def ReadUsers(
                self, 
                database_link: str, 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        def RegisterPartitionResolver(
                self, 
                database_link: str, 
                partition_resolver: RangePartitionResolver
            ) -> None: ...

        def Replace(
                self, 
                resource: dict[str, Any], 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceContainer(
                self, 
                collection_link: str, 
                collection: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceItem(
                self, 
                document_link: str, 
                new_document: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceOffer(
                self, 
                offer_link: str, 
                offer: dict[str, Any], 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplacePermission(
                self, 
                permission_link: str, 
                permission: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceStoredProcedure(
                self, 
                sproc_link: str, 
                sproc: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceTrigger(
                self, 
                trigger_link: str, 
                trigger: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceUser(
                self, 
                user_link: str, 
                user: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def ReplaceUserDefinedFunction(
                self, 
                udf_link: str, 
                udf: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def Upsert(
                self, 
                body: dict[str, Any], 
                path: str, 
                resource_type: str, 
                id: Optional[str], 
                initial_headers: Optional[Mapping[str, Any]], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertItem(
                self, 
                database_or_container_link: str, 
                document: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertPermission(
                self, 
                user_link: str, 
                permission: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertStoredProcedure(
                self, 
                collection_link: str, 
                sproc: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertTrigger(
                self, 
                collection_link: str, 
                trigger: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertUser(
                self, 
                database_link: str, 
                user: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def UpsertUserDefinedFunction(
                self, 
                collection_link: str, 
                udf: dict[str, Any], 
                options: Optional[Mapping[str, Any]] = None, 
                **kwargs: Any
            ) -> CosmosDict: ...

        def health_check(
                self, 
                url_connection: Optional[str] = None, 
                **kwargs: Any
            ): ...

        def read_items(
                self, 
                collection_link: str, 
                items: Sequence[Tuple[str, PartitionKeyType]], 
                options: Optional[Mapping[str, Any]] = None, 
                *, 
                executor: Optional[ThreadPoolExecutor] = ..., 
                **kwargs: Any
            ) -> CosmosList: ...

        def refresh_routing_map_provider(
                self, 
                collection_link: Optional[str] = None, 
                previous_routing_map: Optional[Any] = None, 
                feed_options: Optional[dict[str, Any]] = None
            ) -> None: ...


    class azure.cosmos.user.CosmosDict(dict[str, Any]):

        def __init__(
                self, 
                original_dict: Optional[Mapping[str, Any]], 
                /, 
                *, 
                response_headers: CaseInsensitiveDict
            ) -> None: ...

        def get_response_headers(self) -> CaseInsensitiveDict: ...


    class azure.cosmos.user.Permission:

        def __init__(
                self, 
                id: str, 
                user_link: str, 
                permission_mode: str, 
                resource_link: str, 
                properties: Mapping[str, Any]
            ) -> None: ...


    class azure.cosmos.user.UserProxy:
        id: str
        user_link: str

        def __init__(
                self, 
                client_connection: CosmosClientConnection, 
                id: str, 
                database_link: str, 
                properties: Optional[CosmosDict] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace
        def create_permission(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace
        def delete_permission(
                self, 
                permission: Union[str, Permission, Mapping[str, Any]], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_permission(
                self, 
                permission: Union[str, Permission, Mapping[str, Any]], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Permission: ...

        @distributed_trace
        def list_permissions(
                self, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def query_permissions(
                self, 
                query: str, 
                parameters: Optional[list[dict[str, Any]]] = None, 
                max_item_count: Optional[int] = None, 
                *, 
                response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[dict[str, Any]]: ...

        @distributed_trace
        def read(
                self, 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> CosmosDict: ...

        @distributed_trace
        def replace_permission(
                self, 
                permission: Union[str, Permission, Mapping[str, Any]], 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs
            ) -> Permission: ...

        @distributed_trace
        def upsert_permission(
                self, 
                body: dict[str, Any], 
                *, 
                response_hook: Optional[Callable] = ..., 
                **kwargs: Any
            ) -> Permission: ...


```