```py
namespace azure.mgmt.loganalytics

    class azure.mgmt.loganalytics.LogAnalyticsManagementClient: implements ContextManager 
        available_service_tiers: AvailableServiceTiersOperations
        clusters: ClustersOperations
        data_exports: DataExportsOperations
        data_sources: DataSourcesOperations
        deleted_workspaces: DeletedWorkspacesOperations
        gateways: GatewaysOperations
        intelligence_packs: IntelligencePacksOperations
        linked_services: LinkedServicesOperations
        linked_storage_accounts: LinkedStorageAccountsOperations
        management_groups: ManagementGroupsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        queries: QueriesOperations
        query_packs: QueryPacksOperations
        saved_searches: SavedSearchesOperations
        schema: SchemaOperations
        shared_keys: SharedKeysOperations
        storage_insight_configs: StorageInsightConfigsOperations
        summary_logs: SummaryLogsOperations
        tables: TablesOperations
        usages: UsagesOperations
        workspace_purge: WorkspacePurgeOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.loganalytics.aio

    class azure.mgmt.loganalytics.aio.LogAnalyticsManagementClient: implements AsyncContextManager 
        available_service_tiers: AvailableServiceTiersOperations
        clusters: ClustersOperations
        data_exports: DataExportsOperations
        data_sources: DataSourcesOperations
        deleted_workspaces: DeletedWorkspacesOperations
        gateways: GatewaysOperations
        intelligence_packs: IntelligencePacksOperations
        linked_services: LinkedServicesOperations
        linked_storage_accounts: LinkedStorageAccountsOperations
        management_groups: ManagementGroupsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        queries: QueriesOperations
        query_packs: QueryPacksOperations
        saved_searches: SavedSearchesOperations
        schema: SchemaOperations
        shared_keys: SharedKeysOperations
        storage_insight_configs: StorageInsightConfigsOperations
        summary_logs: SummaryLogsOperations
        tables: TablesOperations
        usages: UsagesOperations
        workspace_purge: WorkspacePurgeOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.loganalytics.aio.operations

    class azure.mgmt.loganalytics.aio.operations.AvailableServiceTiersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> List[AvailableServiceTier]: ...


    class azure.mgmt.loganalytics.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...


    class azure.mgmt.loganalytics.aio.operations.DataExportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                parameters: DataExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataExport: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                parameters: DataExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataExport: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataExport: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                **kwargs: Any
            ) -> DataExport: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataExport]: ...


    class azure.mgmt.loganalytics.aio.operations.DataSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                parameters: DataSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                parameters: DataSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                **kwargs: Any
            ) -> DataSource: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: str, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DataSource]: ...


    class azure.mgmt.loganalytics.aio.operations.DeletedWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...


    class azure.mgmt.loganalytics.aio.operations.GatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                gateway_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.aio.operations.IntelligencePacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def disable(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                intelligence_pack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                intelligence_pack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> List[IntelligencePack]: ...


    class azure.mgmt.loganalytics.aio.operations.LinkedServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                parameters: LinkedService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkedService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                parameters: LinkedService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkedService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkedService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkedService]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                **kwargs: Any
            ) -> LinkedService: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LinkedService]: ...


    class azure.mgmt.loganalytics.aio.operations.LinkedStorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                parameters: LinkedStorageAccountsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                parameters: LinkedStorageAccountsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LinkedStorageAccountsResource]: ...


    class azure.mgmt.loganalytics.aio.operations.ManagementGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagementGroup]: ...


    class azure.mgmt.loganalytics.aio.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                async_operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.loganalytics.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.loganalytics.aio.operations.QueriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                *, 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        def search(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_search_properties: LogAnalyticsQueryPackQuerySearchProperties, 
                *, 
                content_type: str = "application/json", 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        def search(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_search_properties: LogAnalyticsQueryPackQuerySearchProperties, 
                *, 
                content_type: str = "application/json", 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        def search(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_search_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...


    class azure.mgmt.loganalytics.aio.operations.QueryPacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                log_analytics_query_pack_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def create_or_update_without_name(
                self, 
                resource_group_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def create_or_update_without_name(
                self, 
                resource_group_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def create_or_update_without_name(
                self, 
                resource_group_name: str, 
                log_analytics_query_pack_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[LogAnalyticsQueryPack]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LogAnalyticsQueryPack]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_pack_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_pack_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_pack_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...


    class azure.mgmt.loganalytics.aio.operations.SavedSearchesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                parameters: SavedSearch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavedSearch: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                parameters: SavedSearch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavedSearch: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavedSearch: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                **kwargs: Any
            ) -> SavedSearch: ...

        @distributed_trace_async
        async def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SavedSearchesListResult: ...


    class azure.mgmt.loganalytics.aio.operations.SchemaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SearchGetSchemaResponse: ...


    class azure.mgmt.loganalytics.aio.operations.SharedKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_shared_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SharedKeys: ...

        @distributed_trace_async
        async def regenerate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SharedKeys: ...


    class azure.mgmt.loganalytics.aio.operations.StorageInsightConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                parameters: StorageInsight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageInsight: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                parameters: StorageInsight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageInsight: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageInsight: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                **kwargs: Any
            ) -> StorageInsight: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageInsight]: ...


    class azure.mgmt.loganalytics.aio.operations.SummaryLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SummaryLogs]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SummaryLogs]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SummaryLogs]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_retry_bin(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogsRetryBin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_retry_bin(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogsRetryBin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_retry_bin(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> SummaryLogs: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SummaryLogs]: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.aio.operations.TablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Table]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Table]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Table]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Table]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Table]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Table]: ...

        @distributed_trace_async
        async def cancel_search(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> Table: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Table]: ...

        @distributed_trace_async
        async def migrate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UsageMetric]: ...


    class azure.mgmt.loganalytics.aio.operations.WorkspacePurgeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_purge_lake_data(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeLakeDataBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_lake_data(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeLakeDataBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_lake_data(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_purge_status(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                purge_id: str, 
                **kwargs: Any
            ) -> WorkspacePurgeStatusResponse: ...

        @overload
        async def purge(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspacePurgeResponse: ...

        @overload
        async def purge(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspacePurgeResponse: ...

        @overload
        async def purge(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspacePurgeResponse: ...


    class azure.mgmt.loganalytics.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_failback(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_failover(
                self, 
                resource_group_name: str, 
                location: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace_async
        async def get_nsp(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        def list_nsp(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


namespace azure.mgmt.loganalytics.models

    class azure.mgmt.loganalytics.models.AccessRule(_Model):
        name: Optional[str]
        properties: Optional[AccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[AccessRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.AccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.loganalytics.models.AccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, AccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[AccessRulePropertiesSubscriptionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, AccessRuleDirection]] = ..., 
                email_addresses: Optional[list[str]] = ..., 
                fully_qualified_domain_names: Optional[list[str]] = ..., 
                network_security_perimeters: Optional[list[NetworkSecurityPerimeter]] = ..., 
                phone_numbers: Optional[list[str]] = ..., 
                subscriptions: Optional[list[AccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.AccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.AssociatedWorkspace(_Model):
        associate_date: Optional[datetime]
        resource_id: Optional[str]
        workspace_id: Optional[str]
        workspace_name: Optional[str]


    class azure.mgmt.loganalytics.models.AvailableServiceTier(_Model):
        capacity_reservation_level: Optional[int]
        default_retention: Optional[int]
        enabled: Optional[bool]
        last_sku_update: Optional[str]
        maximum_retention: Optional[int]
        minimum_retention: Optional[int]
        service_tier: Optional[Union[str, SkuNameEnum]]


    class azure.mgmt.loganalytics.models.AzureEntityResource(Resource):
        etag: Optional[str]
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.loganalytics.models.BillingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        WORKSPACES = "Workspaces"


    class azure.mgmt.loganalytics.models.CapacityReservationProperties(_Model):
        last_sku_update: Optional[datetime]
        min_capacity: Optional[int]


    class azure.mgmt.loganalytics.models.Cluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ClusterProperties]
        sku: Optional[ClusterSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ClusterProperties] = ..., 
                sku: Optional[ClusterSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.ClusterEntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING_ACCOUNT = "ProvisioningAccount"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.loganalytics.models.ClusterPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ClusterPatchProperties]
        sku: Optional[ClusterSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ClusterPatchProperties] = ..., 
                sku: Optional[ClusterSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.ClusterPatchProperties(_Model):
        billing_type: Optional[Union[str, BillingType]]
        key_vault_properties: Optional[KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                billing_type: Optional[Union[str, BillingType]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ClusterProperties(_Model):
        associated_workspaces: Optional[list[AssociatedWorkspace]]
        billing_type: Optional[Union[str, BillingType]]
        capacity_reservation_properties: Optional[CapacityReservationProperties]
        cluster_id: Optional[str]
        created_date: Optional[datetime]
        is_availability_zones_enabled: Optional[bool]
        is_double_encryption_enabled: Optional[bool]
        key_vault_properties: Optional[KeyVaultProperties]
        last_modified_date: Optional[datetime]
        provisioning_state: Optional[Union[str, ClusterEntityStatus]]
        replication: Optional[ClusterReplicationProperties]

        @overload
        def __init__(
                self, 
                *, 
                associated_workspaces: Optional[list[AssociatedWorkspace]] = ..., 
                billing_type: Optional[Union[str, BillingType]] = ..., 
                capacity_reservation_properties: Optional[CapacityReservationProperties] = ..., 
                is_availability_zones_enabled: Optional[bool] = ..., 
                is_double_encryption_enabled: Optional[bool] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                replication: Optional[ClusterReplicationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ClusterReplicationProperties(_Model):
        created_date: Optional[datetime]
        enabled: Optional[bool]
        is_availability_zones_enabled: Optional[bool]
        last_modified_date: Optional[datetime]
        location: Optional[str]
        provisioning_state: Optional[Union[str, ClusterReplicationState]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                is_availability_zones_enabled: Optional[bool] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ClusterReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DISABLE_REQUESTED = "DisableRequested"
        DISABLING = "Disabling"
        ENABLE_REQUESTED = "EnableRequested"
        ENABLING = "Enabling"
        FAILED = "Failed"
        ROLLBACK_REQUESTED = "RollbackRequested"
        ROLLING_BACK = "RollingBack"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.loganalytics.models.ClusterSku(_Model):
        capacity: Optional[int]
        name: Optional[Union[str, ClusterSkuNameEnum]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, ClusterSkuNameEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ClusterSkuNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_RESERVATION = "CapacityReservation"


    class azure.mgmt.loganalytics.models.Column(_Model):
        data_type_hint: Optional[Union[str, ColumnDataTypeHintEnum]]
        description: Optional[str]
        display_name: Optional[str]
        is_default_display: Optional[bool]
        is_hidden: Optional[bool]
        name: Optional[str]
        type: Optional[Union[str, ColumnTypeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                data_type_hint: Optional[Union[str, ColumnDataTypeHintEnum]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ColumnTypeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ColumnDataTypeHintEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_PATH = "armPath"
        GUID = "guid"
        IP = "ip"
        URI = "uri"
        VECTOR16 = "vector16"


    class azure.mgmt.loganalytics.models.ColumnTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        DATE_TIME = "dateTime"
        DYNAMIC = "dynamic"
        GUID = "guid"
        INT = "int"
        LONG = "long"
        REAL = "real"
        STRING = "string"


    class azure.mgmt.loganalytics.models.CoreSummary(_Model):
        number_of_documents: int
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                number_of_documents: int, 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.loganalytics.models.DataExport(ProxyResource):
        id: str
        name: str
        properties: Optional[DataExportProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataExportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.DataExportProperties(_Model):
        created_date: Optional[str]
        data_export_id: Optional[str]
        destination: Optional[Destination]
        enable: Optional[bool]
        last_modified_date: Optional[str]
        table_names: list[str]

        @overload
        def __init__(
                self, 
                *, 
                created_date: Optional[str] = ..., 
                data_export_id: Optional[str] = ..., 
                destination: Optional[Destination] = ..., 
                enable: Optional[bool] = ..., 
                last_modified_date: Optional[str] = ..., 
                table_names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.DataIngestionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROACHING_QUOTA = "ApproachingQuota"
        FORCE_OFF = "ForceOff"
        FORCE_ON = "ForceOn"
        OVER_QUOTA = "OverQuota"
        RESPECT_QUOTA = "RespectQuota"
        SUBSCRIPTION_SUSPENDED = "SubscriptionSuspended"


    class azure.mgmt.loganalytics.models.DataSource(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Union[str, DataSourceKind]
        name: str
        properties: Any
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Union[str, DataSourceKind], 
                properties: Any, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.DataSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_INSIGHTS = "ApplicationInsights"
        AZURE_ACTIVITY_LOG = "AzureActivityLog"
        AZURE_AUDIT_LOG = "AzureAuditLog"
        CHANGE_TRACKING_CONTENT_LOCATION = "ChangeTrackingContentLocation"
        CHANGE_TRACKING_CUSTOM_PATH = "ChangeTrackingCustomPath"
        CHANGE_TRACKING_DATA_TYPE_CONFIGURATION = "ChangeTrackingDataTypeConfiguration"
        CHANGE_TRACKING_DEFAULT_REGISTRY = "ChangeTrackingDefaultRegistry"
        CHANGE_TRACKING_LINUX_PATH = "ChangeTrackingLinuxPath"
        CHANGE_TRACKING_PATH = "ChangeTrackingPath"
        CHANGE_TRACKING_REGISTRY = "ChangeTrackingRegistry"
        CHANGE_TRACKING_SERVICES = "ChangeTrackingServices"
        CUSTOM_LOG = "CustomLog"
        CUSTOM_LOG_COLLECTION = "CustomLogCollection"
        DNS_ANALYTICS = "DnsAnalytics"
        GENERIC_DATA_SOURCE = "GenericDataSource"
        IIS_LOGS = "IISLogs"
        IMPORT_COMPUTER_GROUP = "ImportComputerGroup"
        ITSM = "Itsm"
        LINUX_CHANGE_TRACKING_PATH = "LinuxChangeTrackingPath"
        LINUX_PERFORMANCE_COLLECTION = "LinuxPerformanceCollection"
        LINUX_PERFORMANCE_OBJECT = "LinuxPerformanceObject"
        LINUX_SYSLOG = "LinuxSyslog"
        LINUX_SYSLOG_COLLECTION = "LinuxSyslogCollection"
        NETWORK_MONITORING = "NetworkMonitoring"
        OFFICE365 = "Office365"
        SECURITY_CENTER_SECURITY_WINDOWS_BASELINE_CONFIGURATION = "SecurityCenterSecurityWindowsBaselineConfiguration"
        SECURITY_EVENT_COLLECTION_CONFIGURATION = "SecurityEventCollectionConfiguration"
        SECURITY_INSIGHTS_SECURITY_EVENT_COLLECTION_CONFIGURATION = "SecurityInsightsSecurityEventCollectionConfiguration"
        SECURITY_WINDOWS_BASELINE_CONFIGURATION = "SecurityWindowsBaselineConfiguration"
        SQL_DATA_CLASSIFICATION = "SqlDataClassification"
        WINDOWS_EVENT = "WindowsEvent"
        WINDOWS_PERFORMANCE_COUNTER = "WindowsPerformanceCounter"
        WINDOWS_TELEMETRY = "WindowsTelemetry"


    class azure.mgmt.loganalytics.models.DataSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        AZURE_WATSON = "AzureWatson"
        CUSTOM_LOGS = "CustomLogs"
        INGESTION = "Ingestion"
        QUERY = "Query"


    class azure.mgmt.loganalytics.models.Destination(_Model):
        meta_data: Optional[DestinationMetaData]
        resource_id: str
        type: Optional[Union[str, Type]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                meta_data: Optional[DestinationMetaData] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.DestinationMetaData(_Model):
        event_hub_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.loganalytics.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.loganalytics.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, UserIdentityProperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserIdentityProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.loganalytics.models.IntelligencePack(_Model):
        display_name: Optional[str]
        enabled: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        UNKNOWN = "Unknown"


    class azure.mgmt.loganalytics.models.KeyVaultProperties(_Model):
        key_name: Optional[str]
        key_rsa_size: Optional[int]
        key_vault_uri: Optional[str]
        key_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_rsa_size: Optional[int] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.LinkedService(ProxyResource):
        id: str
        name: str
        properties: LinkedServiceProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: LinkedServiceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.LinkedServiceEntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        PROVISIONING_ACCOUNT = "ProvisioningAccount"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.loganalytics.models.LinkedServiceProperties(_Model):
        provisioning_state: Optional[Union[str, LinkedServiceEntityStatus]]
        resource_id: Optional[str]
        write_access_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, LinkedServiceEntityStatus]] = ..., 
                resource_id: Optional[str] = ..., 
                write_access_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.LinkedStorageAccountsProperties(_Model):
        data_source_type: Optional[Union[str, DataSourceType]]
        storage_account_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                storage_account_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.LinkedStorageAccountsResource(ProxyResource):
        id: str
        name: str
        properties: LinkedStorageAccountsProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: LinkedStorageAccountsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPack(TrackedResource):
        id: str
        location: str
        name: str
        properties: LogAnalyticsQueryPackProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: LogAnalyticsQueryPackProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPackProperties(_Model):
        provisioning_state: Optional[str]
        query_pack_id: Optional[str]
        time_created: Optional[datetime]
        time_modified: Optional[datetime]


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPackQuery(ProxyResource):
        id: str
        name: str
        properties: Optional[LogAnalyticsQueryPackQueryProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogAnalyticsQueryPackQueryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPackQueryProperties(_Model):
        author: Optional[str]
        body: str
        description: Optional[str]
        display_name: str
        id: Optional[str]
        properties: Optional[Any]
        related: Optional[LogAnalyticsQueryPackQueryPropertiesRelated]
        tags: Optional[dict[str, list[str]]]
        time_created: Optional[datetime]
        time_modified: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                body: str, 
                description: Optional[str] = ..., 
                display_name: str, 
                properties: Optional[Any] = ..., 
                related: Optional[LogAnalyticsQueryPackQueryPropertiesRelated] = ..., 
                tags: Optional[dict[str, list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPackQueryPropertiesRelated(_Model):
        categories: Optional[list[str]]
        resource_types: Optional[list[str]]
        solutions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[str]] = ..., 
                resource_types: Optional[list[str]] = ..., 
                solutions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPackQuerySearchProperties(_Model):
        related: Optional[LogAnalyticsQueryPackQuerySearchPropertiesRelated]
        tags: Optional[dict[str, list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                related: Optional[LogAnalyticsQueryPackQuerySearchPropertiesRelated] = ..., 
                tags: Optional[dict[str, list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.LogAnalyticsQueryPackQuerySearchPropertiesRelated(_Model):
        categories: Optional[list[str]]
        resource_types: Optional[list[str]]
        solutions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[str]] = ..., 
                resource_types: Optional[list[str]] = ..., 
                solutions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.loganalytics.models.ManagementGroup(_Model):
        properties: Optional[ManagementGroupProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagementGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.ManagementGroupProperties(_Model):
        created: Optional[datetime]
        data_received: Optional[datetime]
        id: Optional[str]
        is_gateway: Optional[bool]
        name: Optional[str]
        server_count: Optional[int]
        sku: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                data_received: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                is_gateway: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                server_count: Optional[int] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.MetricName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                profile: Optional[NetworkSecurityProfile] = ..., 
                resource_association: Optional[ResourceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.loganalytics.models.NetworkSecurityProfile(_Model):
        access_rules: Optional[list[AccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[AccessRule]] = ..., 
                access_rules_version: Optional[int] = ..., 
                diagnostic_settings_version: Optional[int] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.OperationStatus(_Model):
        end_time: Optional[str]
        error: Optional[ErrorResponse]
        id: Optional[str]
        name: Optional[str]
        start_time: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                error: Optional[ErrorResponse] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.PrivateLinkScopedResource(_Model):
        resource_id: Optional[str]
        scope_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                scope_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]


    class azure.mgmt.loganalytics.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, IssueType]]
        severity: Optional[Union[str, Severity]]
        suggested_access_rules: Optional[list[AccessRule]]
        suggested_resource_ids: Optional[list[str]]


    class azure.mgmt.loganalytics.models.ProvisioningStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.loganalytics.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.loganalytics.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.loganalytics.models.PurgeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        PENDING = "pending"


    class azure.mgmt.loganalytics.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.loganalytics.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, ResourceAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.loganalytics.models.RestoredLogs(_Model):
        azure_async_operation_id: Optional[str]
        end_restore_time: Optional[datetime]
        source_table: Optional[str]
        start_restore_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_restore_time: Optional[datetime] = ..., 
                source_table: Optional[str] = ..., 
                start_restore_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.ResultStatistics(_Model):
        ingested_records: Optional[int]
        progress: Optional[float]
        scanned_gb: Optional[float]


    class azure.mgmt.loganalytics.models.RuleDefinition(_Model):
        bin_delay: Optional[int]
        bin_size: Optional[int]
        bin_start_time: Optional[datetime]
        destination_table: Optional[str]
        query: Optional[str]
        time_selector: Optional[Union[str, TimeSelectorEnum]]

        @overload
        def __init__(
                self, 
                *, 
                bin_delay: Optional[int] = ..., 
                bin_size: Optional[int] = ..., 
                bin_start_time: Optional[datetime] = ..., 
                destination_table: Optional[str] = ..., 
                query: Optional[str] = ..., 
                time_selector: Optional[Union[str, TimeSelectorEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.RuleTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER = "User"


    class azure.mgmt.loganalytics.models.SavedSearch(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: SavedSearchProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: SavedSearchProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.SavedSearchProperties(_Model):
        category: str
        display_name: str
        function_alias: Optional[str]
        function_parameters: Optional[str]
        query: str
        tags: Optional[list[Tag]]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                display_name: str, 
                function_alias: Optional[str] = ..., 
                function_parameters: Optional[str] = ..., 
                query: str, 
                tags: Optional[list[Tag]] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SavedSearchesListResult(_Model):
        value: Optional[list[SavedSearch]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SavedSearch]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.Schema(_Model):
        categories: Optional[list[str]]
        columns: Optional[list[Column]]
        description: Optional[str]
        display_name: Optional[str]
        labels: Optional[list[str]]
        name: Optional[str]
        solutions: Optional[list[str]]
        source: Optional[Union[str, SourceEnum]]
        standard_columns: Optional[list[Column]]
        table_sub_type: Optional[Union[str, TableSubTypeEnum]]
        table_type: Optional[Union[str, TableTypeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[Column]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchGetSchemaResponse(_Model):
        metadata: Optional[SearchMetadata]
        value: Optional[list[SearchSchemaValue]]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[SearchMetadata] = ..., 
                value: Optional[list[SearchSchemaValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchMetadata(_Model):
        aggregated_grouping_fields: Optional[str]
        aggregated_value_field: Optional[str]
        core_summaries: Optional[list[CoreSummary]]
        e_tag: Optional[str]
        id: Optional[str]
        last_updated: Optional[datetime]
        max: Optional[int]
        request_time: Optional[int]
        result_type: Optional[str]
        schema: Optional[SearchMetadataSchema]
        search_id: Optional[str]
        sort: Optional[list[SearchSort]]
        start_time: Optional[datetime]
        status: Optional[str]
        sum: Optional[int]
        top: Optional[int]
        total: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                aggregated_grouping_fields: Optional[str] = ..., 
                aggregated_value_field: Optional[str] = ..., 
                core_summaries: Optional[list[CoreSummary]] = ..., 
                e_tag: Optional[str] = ..., 
                id: Optional[str] = ..., 
                last_updated: Optional[datetime] = ..., 
                max: Optional[int] = ..., 
                request_time: Optional[int] = ..., 
                result_type: Optional[str] = ..., 
                schema: Optional[SearchMetadataSchema] = ..., 
                search_id: Optional[str] = ..., 
                sort: Optional[list[SearchSort]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                sum: Optional[int] = ..., 
                top: Optional[int] = ..., 
                total: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchMetadataSchema(_Model):
        name: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchResults(_Model):
        azure_async_operation_id: Optional[str]
        description: Optional[str]
        end_search_time: Optional[datetime]
        limit: Optional[int]
        query: Optional[str]
        source_table: Optional[str]
        start_search_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                end_search_time: Optional[datetime] = ..., 
                limit: Optional[int] = ..., 
                query: Optional[str] = ..., 
                start_search_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchSchemaValue(_Model):
        display_name: Optional[str]
        facet: bool
        indexed: bool
        name: Optional[str]
        owner_type: Optional[list[str]]
        stored: bool
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                facet: bool, 
                indexed: bool, 
                name: Optional[str] = ..., 
                owner_type: Optional[list[str]] = ..., 
                stored: bool, 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchSort(_Model):
        name: Optional[str]
        order: Optional[Union[str, SearchSortEnum]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                order: Optional[Union[str, SearchSortEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SearchSortEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.mgmt.loganalytics.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.loganalytics.models.SharedKeys(_Model):
        primary_shared_key: Optional[str]
        secondary_shared_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_shared_key: Optional[str] = ..., 
                secondary_shared_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SkuNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_RESERVATION = "CapacityReservation"
        FREE = "Free"
        PER_GB2018 = "PerGB2018"
        PER_NODE = "PerNode"
        PREMIUM = "Premium"
        STANDALONE = "Standalone"
        STANDARD = "Standard"


    class azure.mgmt.loganalytics.models.SourceEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER = "customer"
        MICROSOFT = "microsoft"


    class azure.mgmt.loganalytics.models.StatusCodeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_PLANE_ERROR = "DataPlaneError"
        USER_ACTION = "UserAction"


    class azure.mgmt.loganalytics.models.StorageAccount(_Model):
        id: str
        key: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.StorageInsight(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[StorageInsightProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[StorageInsightProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.StorageInsightProperties(_Model):
        containers: Optional[list[str]]
        status: Optional[StorageInsightStatus]
        storage_account: StorageAccount
        tables: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[str]] = ..., 
                storage_account: StorageAccount, 
                tables: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.StorageInsightState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "ERROR"
        OK = "OK"


    class azure.mgmt.loganalytics.models.StorageInsightStatus(_Model):
        description: Optional[str]
        state: Union[str, StorageInsightState]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                state: Union[str, StorageInsightState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SummaryLogs(ProxyResource):
        id: str
        identity: Optional[SummaryLogsIdentity]
        name: str
        properties: Optional[SummaryLogsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SummaryLogsIdentity] = ..., 
                properties: Optional[SummaryLogsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.SummaryLogsIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, SummaryLogsIdentityType]
        user_assigned_identities: Optional[dict[str, SummaryLogsUserIdentityProperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, SummaryLogsIdentityType], 
                user_assigned_identities: Optional[dict[str, SummaryLogsUserIdentityProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SummaryLogsIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.loganalytics.models.SummaryLogsProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        is_active: Optional[bool]
        provisioning_state: Optional[Union[str, SummaryLogsProvisioningState]]
        rule_definition: Optional[RuleDefinition]
        rule_type: Optional[Union[str, RuleTypeEnum]]
        status_code: Optional[Union[str, StatusCodeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                rule_definition: Optional[RuleDefinition] = ..., 
                rule_type: Optional[Union[str, RuleTypeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SummaryLogsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.loganalytics.models.SummaryLogsRetryBin(_Model):
        properties: Optional[SummaryLogsRetryBinProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SummaryLogsRetryBinProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SummaryLogsRetryBinProperties(_Model):
        retry_bin_start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                retry_bin_start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.SummaryLogsUserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.loganalytics.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.Table(ProxyResource):
        id: str
        name: str
        properties: Optional[TableProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.TablePlanEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYTICS = "Analytics"
        AUXILIARY = "Auxiliary"
        BASIC = "Basic"


    class azure.mgmt.loganalytics.models.TableProperties(_Model):
        archive_retention_in_days: Optional[int]
        last_plan_modified_date: Optional[str]
        plan: Optional[Union[str, TablePlanEnum]]
        protection_level: Optional[Union[str, TableProtectionLevelEnum]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        restored_logs: Optional[RestoredLogs]
        result_statistics: Optional[ResultStatistics]
        retention_in_days: Optional[int]
        retention_in_days_as_default: Optional[bool]
        schema: Optional[Schema]
        search_results: Optional[SearchResults]
        total_retention_in_days: Optional[int]
        total_retention_in_days_as_default: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                plan: Optional[Union[str, TablePlanEnum]] = ..., 
                protection_level: Optional[Union[str, TableProtectionLevelEnum]] = ..., 
                restored_logs: Optional[RestoredLogs] = ..., 
                retention_in_days: Optional[int] = ..., 
                schema: Optional[Schema] = ..., 
                search_results: Optional[SearchResults] = ..., 
                total_retention_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.TableProtectionLevelEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERAL = "General"
        PROTECTED = "Protected"


    class azure.mgmt.loganalytics.models.TableSubTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        CLASSIC = "Classic"
        DATA_COLLECTION_RULE_BASED = "DataCollectionRuleBased"


    class azure.mgmt.loganalytics.models.TableTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOG = "CustomLog"
        MICROSOFT = "Microsoft"
        RESTORED_LOGS = "RestoredLogs"
        SEARCH_RESULTS = "SearchResults"


    class azure.mgmt.loganalytics.models.Tag(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.TimeSelectorEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TIME_GENERATED = "TimeGenerated"


    class azure.mgmt.loganalytics.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"
        STORAGE_ACCOUNT = "StorageAccount"


    class azure.mgmt.loganalytics.models.UsageMetric(_Model):
        current_value: Optional[float]
        limit: Optional[float]
        name: Optional[MetricName]
        next_reset_time: Optional[datetime]
        quota_period: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[float] = ..., 
                limit: Optional[float] = ..., 
                name: Optional[MetricName] = ..., 
                next_reset_time: Optional[datetime] = ..., 
                quota_period: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.loganalytics.models.UserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.loganalytics.models.Workspace(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[WorkspaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: Optional[WorkspaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspaceCapping(_Model):
        daily_quota_gb: Optional[float]
        data_ingestion_status: Optional[Union[str, DataIngestionStatus]]
        quota_next_reset_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                daily_quota_gb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspaceEntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING_ACCOUNT = "ProvisioningAccount"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.loganalytics.models.WorkspaceFailoverProperties(_Model):
        last_modified_date: Optional[datetime]
        state: Optional[Union[str, WorkspaceFailoverState]]


    class azure.mgmt.loganalytics.models.WorkspaceFailoverState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATING = "Activating"
        ACTIVE = "Active"
        DEACTIVATING = "Deactivating"
        FAILED = "Failed"
        INACTIVE = "Inactive"


    class azure.mgmt.loganalytics.models.WorkspaceFeatures(_Model):
        associations: Optional[list[str]]
        cluster_resource_id: Optional[str]
        data_authorization_mode: Optional[bool]
        disable_local_auth: Optional[bool]
        enable_data_export: Optional[bool]
        enable_log_access_using_only_resource_permissions: Optional[bool]
        immediate_purge_data_on30_days: Optional[bool]
        unified_sentinel_billing_only: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: Optional[str] = ..., 
                data_authorization_mode: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_data_export: Optional[bool] = ..., 
                enable_log_access_using_only_resource_permissions: Optional[bool] = ..., 
                immediate_purge_data_on30_days: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePatch(AzureEntityResource):
        etag: str
        id: str
        identity: Optional[Identity]
        name: str
        properties: Optional[WorkspaceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[WorkspaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspaceProperties(_Model):
        created_date: Optional[datetime]
        customer_id: Optional[str]
        default_data_collection_rule_resource_id: Optional[str]
        failover: Optional[WorkspaceFailoverProperties]
        features: Optional[WorkspaceFeatures]
        force_cmk_for_query: Optional[bool]
        modified_date: Optional[datetime]
        private_link_scoped_resources: Optional[list[PrivateLinkScopedResource]]
        provisioning_state: Optional[Union[str, WorkspaceEntityStatus]]
        public_network_access_for_ingestion: Optional[Union[str, PublicNetworkAccessType]]
        public_network_access_for_query: Optional[Union[str, PublicNetworkAccessType]]
        replication: Optional[WorkspaceReplicationProperties]
        retention_in_days: Optional[int]
        sku: Optional[WorkspaceSku]
        workspace_capping: Optional[WorkspaceCapping]

        @overload
        def __init__(
                self, 
                *, 
                default_data_collection_rule_resource_id: Optional[str] = ..., 
                failover: Optional[WorkspaceFailoverProperties] = ..., 
                features: Optional[WorkspaceFeatures] = ..., 
                force_cmk_for_query: Optional[bool] = ..., 
                public_network_access_for_ingestion: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                public_network_access_for_query: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                replication: Optional[WorkspaceReplicationProperties] = ..., 
                retention_in_days: Optional[int] = ..., 
                sku: Optional[WorkspaceSku] = ..., 
                workspace_capping: Optional[WorkspaceCapping] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePurgeBody(_Model):
        filters: list[WorkspacePurgeBodyFilters]
        table: str

        @overload
        def __init__(
                self, 
                *, 
                filters: list[WorkspacePurgeBodyFilters], 
                table: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePurgeBodyFilters(_Model):
        column: Optional[str]
        key: Optional[str]
        operator: Optional[str]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                column: Optional[str] = ..., 
                key: Optional[str] = ..., 
                operator: Optional[str] = ..., 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePurgeLakeDataBody(_Model):
        table: str
        time_range: WorkspacePurgeLakeDataTimeRange

        @overload
        def __init__(
                self, 
                *, 
                table: str, 
                time_range: WorkspacePurgeLakeDataTimeRange
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePurgeLakeDataTimeRange(_Model):
        end_time: datetime
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                end_time: datetime, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePurgeResponse(_Model):
        operation_id: str

        @overload
        def __init__(
                self, 
                *, 
                operation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspacePurgeStatusResponse(_Model):
        status: Union[str, PurgeState]

        @overload
        def __init__(
                self, 
                *, 
                status: Union[str, PurgeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspaceReplicationProperties(_Model):
        created_date: Optional[datetime]
        enabled: Optional[bool]
        last_modified_date: Optional[datetime]
        location: Optional[str]
        provisioning_state: Optional[Union[str, WorkspaceReplicationState]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspaceReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DISABLE_REQUESTED = "DisableRequested"
        DISABLING = "Disabling"
        ENABLE_REQUESTED = "EnableRequested"
        ENABLING = "Enabling"
        FAILED = "Failed"
        ROLLBACK_REQUESTED = "RollbackRequested"
        ROLLING_BACK = "RollingBack"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.loganalytics.models.WorkspaceSku(_Model):
        capacity_reservation_level: Optional[int]
        last_sku_update: Optional[datetime]
        name: Union[str, WorkspaceSkuNameEnum]

        @overload
        def __init__(
                self, 
                *, 
                capacity_reservation_level: Optional[int] = ..., 
                name: Union[str, WorkspaceSkuNameEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.loganalytics.models.WorkspaceSkuNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_RESERVATION = "CapacityReservation"
        FREE = "Free"
        LA_CLUSTER = "LACluster"
        PER_GB2018 = "PerGB2018"
        PER_NODE = "PerNode"
        PREMIUM = "Premium"
        STANDALONE = "Standalone"
        STANDARD = "Standard"


namespace azure.mgmt.loganalytics.operations

    class azure.mgmt.loganalytics.operations.AvailableServiceTiersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> List[AvailableServiceTier]: ...


    class azure.mgmt.loganalytics.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...


    class azure.mgmt.loganalytics.operations.DataExportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                parameters: DataExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataExport: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                parameters: DataExport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataExport: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataExport: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_export_name: str, 
                **kwargs: Any
            ) -> DataExport: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataExport]: ...


    class azure.mgmt.loganalytics.operations.DataSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                parameters: DataSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                parameters: DataSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataSource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_name: str, 
                **kwargs: Any
            ) -> DataSource: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: str, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DataSource]: ...


    class azure.mgmt.loganalytics.operations.DeletedWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...


    class azure.mgmt.loganalytics.operations.GatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                gateway_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.operations.IntelligencePacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def disable(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                intelligence_pack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                intelligence_pack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> List[IntelligencePack]: ...


    class azure.mgmt.loganalytics.operations.LinkedServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                parameters: LinkedService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkedService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                parameters: LinkedService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkedService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkedService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[LinkedService]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                linked_service_name: str, 
                **kwargs: Any
            ) -> LinkedService: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LinkedService]: ...


    class azure.mgmt.loganalytics.operations.LinkedStorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                parameters: LinkedStorageAccountsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                parameters: LinkedStorageAccountsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_source_type: Union[str, DataSourceType], 
                **kwargs: Any
            ) -> LinkedStorageAccountsResource: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LinkedStorageAccountsResource]: ...


    class azure.mgmt.loganalytics.operations.ManagementGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagementGroup]: ...


    class azure.mgmt.loganalytics.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                async_operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.loganalytics.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.loganalytics.operations.QueriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                *, 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        def search(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_search_properties: LogAnalyticsQueryPackQuerySearchProperties, 
                *, 
                content_type: str = "application/json", 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        def search(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_search_properties: LogAnalyticsQueryPackQuerySearchProperties, 
                *, 
                content_type: str = "application/json", 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        def search(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_search_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_body: Optional[bool] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LogAnalyticsQueryPackQuery]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: LogAnalyticsQueryPackQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                id: str, 
                query_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPackQuery: ...


    class azure.mgmt.loganalytics.operations.QueryPacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                log_analytics_query_pack_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def create_or_update_without_name(
                self, 
                resource_group_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def create_or_update_without_name(
                self, 
                resource_group_name: str, 
                log_analytics_query_pack_payload: LogAnalyticsQueryPack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def create_or_update_without_name(
                self, 
                resource_group_name: str, 
                log_analytics_query_pack_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[LogAnalyticsQueryPack]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LogAnalyticsQueryPack]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_pack_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_pack_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                query_pack_name: str, 
                query_pack_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogAnalyticsQueryPack: ...


    class azure.mgmt.loganalytics.operations.SavedSearchesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                parameters: SavedSearch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavedSearch: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                parameters: SavedSearch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavedSearch: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SavedSearch: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                saved_search_id: str, 
                **kwargs: Any
            ) -> SavedSearch: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SavedSearchesListResult: ...


    class azure.mgmt.loganalytics.operations.SchemaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SearchGetSchemaResponse: ...


    class azure.mgmt.loganalytics.operations.SharedKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_shared_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SharedKeys: ...

        @distributed_trace
        def regenerate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SharedKeys: ...


    class azure.mgmt.loganalytics.operations.StorageInsightConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                parameters: StorageInsight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageInsight: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                parameters: StorageInsight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageInsight: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageInsight: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                storage_insight_name: str, 
                **kwargs: Any
            ) -> StorageInsight: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageInsight]: ...


    class azure.mgmt.loganalytics.operations.SummaryLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SummaryLogs]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SummaryLogs]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SummaryLogs]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_retry_bin(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogsRetryBin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_retry_bin(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: SummaryLogsRetryBin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_retry_bin(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> SummaryLogs: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SummaryLogs]: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                summary_logs_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.operations.TablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Table]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Table]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Table]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Table]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: Table, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Table]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Table]: ...

        @distributed_trace
        def cancel_search(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> Table: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Table]: ...

        @distributed_trace
        def migrate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.loganalytics.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UsageMetric]: ...


    class azure.mgmt.loganalytics.operations.WorkspacePurgeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_purge_lake_data(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeLakeDataBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_lake_data(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeLakeDataBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_lake_data(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_purge_status(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                purge_id: str, 
                **kwargs: Any
            ) -> WorkspacePurgeStatusResponse: ...

        @overload
        def purge(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspacePurgeResponse: ...

        @overload
        def purge(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: WorkspacePurgeBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspacePurgeResponse: ...

        @overload
        def purge(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspacePurgeResponse: ...


    class azure.mgmt.loganalytics.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_failback(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_failover(
                self, 
                resource_group_name: str, 
                location: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def get_nsp(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...

        @distributed_trace
        def list_nsp(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


namespace azure.mgmt.loganalytics.types

    class azure.mgmt.loganalytics.types.AssociatedWorkspace(TypedDict, total=False):
        key "associateDate": str
        key "resourceId": str
        key "workspaceId": str
        key "workspaceName": str
        associateDate: str
        resourceId: str
        workspaceId: str
        workspaceName: str


    class azure.mgmt.loganalytics.types.AzureEntityResource(Resource):
        key "etag": str
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.CapacityReservationProperties(TypedDict, total=False):
        key "lastSkuUpdate": str
        key "minCapacity": int
        lastSkuUpdate: str
        minCapacity: int


    class azure.mgmt.loganalytics.types.Cluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ClusterProperties', module='types')
        key "sku": ForwardRef('ClusterSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ClusterProperties
        sku: ClusterSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.ClusterPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ClusterPatchProperties', module='types')
        key "sku": ForwardRef('ClusterSku', module='types')
        identity: ManagedServiceIdentity
        properties: ClusterPatchProperties
        sku: ClusterSku
        tags: dict[str, str]


    class azure.mgmt.loganalytics.types.ClusterPatchProperties(TypedDict, total=False):
        key "billingType": Union[str, BillingType]
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        billingType: Union[str, BillingType]
        keyVaultProperties: KeyVaultProperties


    class azure.mgmt.loganalytics.types.ClusterProperties(TypedDict, total=False):
        key "billingType": Union[str, BillingType]
        key "capacityReservationProperties": ForwardRef('CapacityReservationProperties', module='types')
        key "clusterId": str
        key "createdDate": str
        key "isAvailabilityZonesEnabled": bool
        key "isDoubleEncryptionEnabled": bool
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        key "lastModifiedDate": str
        key "provisioningState": Union[str, ClusterEntityStatus]
        key "replication": ForwardRef('ClusterReplicationProperties', module='types')
        associatedWorkspaces: list[AssociatedWorkspace]
        billingType: Union[str, BillingType]
        capacityReservationProperties: CapacityReservationProperties
        clusterId: str
        createdDate: str
        isAvailabilityZonesEnabled: bool
        isDoubleEncryptionEnabled: bool
        keyVaultProperties: KeyVaultProperties
        lastModifiedDate: str
        provisioningState: Union[str, ClusterEntityStatus]
        replication: ClusterReplicationProperties


    class azure.mgmt.loganalytics.types.ClusterReplicationProperties(TypedDict, total=False):
        key "createdDate": str
        key "enabled": bool
        key "isAvailabilityZonesEnabled": bool
        key "lastModifiedDate": str
        key "location": str
        key "provisioningState": Union[str, ClusterReplicationState]
        createdDate: str
        enabled: bool
        isAvailabilityZonesEnabled: bool
        lastModifiedDate: str
        location: str
        provisioningState: Union[str, ClusterReplicationState]


    class azure.mgmt.loganalytics.types.ClusterSku(TypedDict, total=False):
        key "capacity": Optional[int]
        key "name": Union[str, ClusterSkuNameEnum]
        capacity: int
        name: Union[str, ClusterSkuNameEnum]


    class azure.mgmt.loganalytics.types.Column(TypedDict, total=False):
        key "dataTypeHint": Union[str, ColumnDataTypeHintEnum]
        key "description": str
        key "displayName": str
        key "isDefaultDisplay": bool
        key "isHidden": bool
        key "name": str
        key "type": Union[str, ColumnTypeEnum]
        dataTypeHint: Union[str, ColumnDataTypeHintEnum]
        description: str
        displayName: str
        isDefaultDisplay: bool
        isHidden: bool
        name: str
        type: Union[str, ColumnTypeEnum]


    class azure.mgmt.loganalytics.types.DataExport(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataExportProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DataExportProperties
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.DataExportProperties(TypedDict, total=False):
        key "createdDate": str
        key "dataExportId": str
        key "destination": ForwardRef('Destination', module='types')
        key "enable": bool
        key "lastModifiedDate": str
        key "tableNames": Required[list[str]]
        createdDate: str
        dataExportId: str
        destination: Destination
        enable: bool
        lastModifiedDate: str
        tableNames: list[str]


    class azure.mgmt.loganalytics.types.DataSource(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": Required[Union[str, DataSourceKind]]
        key "name": str
        key "properties": Required[Any]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Union[str, DataSourceKind]
        name: str
        properties: Any
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.Destination(TypedDict, total=False):
        key "metaData": ForwardRef('DestinationMetaData', module='types')
        key "resourceId": Required[str]
        key "type": Union[str, Type]
        metaData: DestinationMetaData
        resourceId: str
        type: Union[str, Type]


    class azure.mgmt.loganalytics.types.DestinationMetaData(TypedDict, total=False):
        key "eventHubName": str
        eventHubName: str


    class azure.mgmt.loganalytics.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, IdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, IdentityType]
        userAssignedIdentities: dict[str, UserIdentityProperties]


    class azure.mgmt.loganalytics.types.KeyVaultProperties(TypedDict, total=False):
        key "keyName": str
        key "keyRsaSize": int
        key "keyVaultUri": str
        key "keyVersion": str
        keyName: str
        keyRsaSize: int
        keyVaultUri: str
        keyVersion: str


    class azure.mgmt.loganalytics.types.LinkedService(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[LinkedServiceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: LinkedServiceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.LinkedServiceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, LinkedServiceEntityStatus]
        key "resourceId": str
        key "writeAccessResourceId": str
        provisioningState: Union[str, LinkedServiceEntityStatus]
        resourceId: str
        writeAccessResourceId: str


    class azure.mgmt.loganalytics.types.LinkedStorageAccountsProperties(TypedDict, total=False):
        key "dataSourceType": Union[str, DataSourceType]
        dataSourceType: Union[str, DataSourceType]
        storageAccountIds: list[str]


    class azure.mgmt.loganalytics.types.LinkedStorageAccountsResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[LinkedStorageAccountsProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: LinkedStorageAccountsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPack(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[LogAnalyticsQueryPackProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: LogAnalyticsQueryPackProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPackProperties(TypedDict, total=False):
        key "provisioningState": str
        key "queryPackId": str
        key "timeCreated": str
        key "timeModified": str
        provisioningState: str
        queryPackId: str
        timeCreated: str
        timeModified: str


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPackQuery(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('LogAnalyticsQueryPackQueryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: LogAnalyticsQueryPackQueryProperties
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPackQueryProperties(TypedDict, total=False):
        key "author": str
        key "body": Required[str]
        key "description": str
        key "displayName": Required[str]
        key "id": str
        key "properties": Any
        key "related": ForwardRef('LogAnalyticsQueryPackQueryPropertiesRelated', module='types')
        key "timeCreated": str
        key "timeModified": str
        author: str
        body: str
        description: str
        displayName: str
        id: str
        properties: Any
        related: LogAnalyticsQueryPackQueryPropertiesRelated
        tags: dict[str, list[str]]
        timeCreated: str
        timeModified: str


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPackQueryPropertiesRelated(TypedDict, total=False):
        categories: list[str]
        resourceTypes: list[str]
        solutions: list[str]


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPackQuerySearchProperties(TypedDict, total=False):
        key "related": ForwardRef('LogAnalyticsQueryPackQuerySearchPropertiesRelated', module='types')
        related: LogAnalyticsQueryPackQuerySearchPropertiesRelated
        tags: dict[str, list[str]]


    class azure.mgmt.loganalytics.types.LogAnalyticsQueryPackQuerySearchPropertiesRelated(TypedDict, total=False):
        categories: list[str]
        resourceTypes: list[str]
        solutions: list[str]


    class azure.mgmt.loganalytics.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.loganalytics.types.PrivateLinkScopedResource(TypedDict, total=False):
        key "resourceId": str
        key "scopeId": str
        resourceId: str
        scopeId: str


    class azure.mgmt.loganalytics.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.RestoredLogs(TypedDict, total=False):
        key "azureAsyncOperationId": str
        key "endRestoreTime": str
        key "sourceTable": str
        key "startRestoreTime": str
        azureAsyncOperationId: str
        endRestoreTime: str
        sourceTable: str
        startRestoreTime: str


    class azure.mgmt.loganalytics.types.ResultStatistics(TypedDict, total=False):
        key "ingestedRecords": int
        key "progress": float
        key "scannedGb": float
        ingestedRecords: int
        progress: float
        scannedGb: float


    class azure.mgmt.loganalytics.types.RuleDefinition(TypedDict, total=False):
        key "binDelay": int
        key "binSize": int
        key "binStartTime": str
        key "destinationTable": str
        key "query": str
        key "timeSelector": Union[str, TimeSelectorEnum]
        binDelay: int
        binSize: int
        binStartTime: str
        destinationTable: str
        query: str
        timeSelector: Union[str, TimeSelectorEnum]


    class azure.mgmt.loganalytics.types.SavedSearch(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": Required[SavedSearchProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: SavedSearchProperties
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.SavedSearchProperties(TypedDict, total=False):
        key "category": Required[str]
        key "displayName": Required[str]
        key "functionAlias": str
        key "functionParameters": str
        key "query": Required[str]
        key "version": int
        category: str
        displayName: str
        functionAlias: str
        functionParameters: str
        query: str
        tags: list[Tag]
        version: int


    class azure.mgmt.loganalytics.types.Schema(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "name": str
        key "source": Union[str, SourceEnum]
        key "tableSubType": Union[str, TableSubTypeEnum]
        key "tableType": Union[str, TableTypeEnum]
        categories: list[str]
        columns: list[Column]
        description: str
        displayName: str
        labels: list[str]
        name: str
        solutions: list[str]
        source: Union[str, SourceEnum]
        standardColumns: list[Column]
        tableSubType: Union[str, TableSubTypeEnum]
        tableType: Union[str, TableTypeEnum]


    class azure.mgmt.loganalytics.types.SearchResults(TypedDict, total=False):
        key "azureAsyncOperationId": str
        key "description": str
        key "endSearchTime": str
        key "limit": int
        key "query": str
        key "sourceTable": str
        key "startSearchTime": str
        azureAsyncOperationId: str
        description: str
        endSearchTime: str
        limit: int
        query: str
        sourceTable: str
        startSearchTime: str


    class azure.mgmt.loganalytics.types.StorageAccount(TypedDict, total=False):
        key "id": Required[str]
        key "key": Required[str]
        id: str
        key: str


    class azure.mgmt.loganalytics.types.StorageInsight(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('StorageInsightProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: StorageInsightProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.StorageInsightProperties(TypedDict, total=False):
        key "status": ForwardRef('StorageInsightStatus', module='types')
        key "storageAccount": Required[StorageAccount]
        containers: list[str]
        status: StorageInsightStatus
        storageAccount: StorageAccount
        tables: list[str]


    class azure.mgmt.loganalytics.types.StorageInsightStatus(TypedDict, total=False):
        key "description": str
        key "state": Required[Union[str, StorageInsightState]]
        description: str
        state: Union[str, StorageInsightState]


    class azure.mgmt.loganalytics.types.SummaryLogs(ProxyResource):
        key "id": str
        key "identity": ForwardRef('SummaryLogsIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('SummaryLogsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: SummaryLogsIdentity
        name: str
        properties: SummaryLogsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.SummaryLogsIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, SummaryLogsIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, SummaryLogsIdentityType]
        userAssignedIdentities: dict[str, SummaryLogsUserIdentityProperties]


    class azure.mgmt.loganalytics.types.SummaryLogsProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "isActive": bool
        key "provisioningState": Union[str, SummaryLogsProvisioningState]
        key "ruleDefinition": ForwardRef('RuleDefinition', module='types')
        key "ruleType": Union[str, RuleTypeEnum]
        key "statusCode": Union[str, StatusCodeEnum]
        description: str
        displayName: str
        isActive: bool
        provisioningState: Union[str, SummaryLogsProvisioningState]
        ruleDefinition: RuleDefinition
        ruleType: Union[str, RuleTypeEnum]
        statusCode: Union[str, StatusCodeEnum]


    class azure.mgmt.loganalytics.types.SummaryLogsRetryBin(TypedDict, total=False):
        key "properties": ForwardRef('SummaryLogsRetryBinProperties', module='types')
        properties: SummaryLogsRetryBinProperties


    class azure.mgmt.loganalytics.types.SummaryLogsRetryBinProperties(TypedDict, total=False):
        key "retryBinStartTime": Required[str]
        retryBinStartTime: str


    class azure.mgmt.loganalytics.types.SummaryLogsUserIdentityProperties(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.loganalytics.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.loganalytics.types.Table(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TableProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TableProperties
        systemData: SystemData
        type: str


    class azure.mgmt.loganalytics.types.TableProperties(TypedDict, total=False):
        key "archiveRetentionInDays": int
        key "lastPlanModifiedDate": str
        key "plan": Union[str, TablePlanEnum]
        key "protectionLevel": Union[str, TableProtectionLevelEnum]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "restoredLogs": ForwardRef('RestoredLogs', module='types')
        key "resultStatistics": ForwardRef('ResultStatistics', module='types')
        key "retentionInDays": int
        key "retentionInDaysAsDefault": bool
        key "schema": ForwardRef('Schema', module='types')
        key "searchResults": ForwardRef('SearchResults', module='types')
        key "totalRetentionInDays": int
        key "totalRetentionInDaysAsDefault": bool
        archiveRetentionInDays: int
        lastPlanModifiedDate: str
        plan: Union[str, TablePlanEnum]
        protectionLevel: Union[str, TableProtectionLevelEnum]
        provisioningState: Union[str, ProvisioningStateEnum]
        restoredLogs: RestoredLogs
        resultStatistics: ResultStatistics
        retentionInDays: int
        retentionInDaysAsDefault: bool
        schema: Schema
        searchResults: SearchResults
        totalRetentionInDays: int
        totalRetentionInDaysAsDefault: bool


    class azure.mgmt.loganalytics.types.Tag(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.loganalytics.types.TagsResource(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.loganalytics.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.loganalytics.types.UserIdentityProperties(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.loganalytics.types.Workspace(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WorkspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        location: str
        name: str
        properties: WorkspaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.WorkspaceCapping(TypedDict, total=False):
        key "dailyQuotaGb": float
        key "dataIngestionStatus": Union[str, DataIngestionStatus]
        key "quotaNextResetTime": str
        dailyQuotaGb: float
        dataIngestionStatus: Union[str, DataIngestionStatus]
        quotaNextResetTime: str


    class azure.mgmt.loganalytics.types.WorkspaceFailoverProperties(TypedDict, total=False):
        key "lastModifiedDate": str
        key "state": Union[str, WorkspaceFailoverState]
        lastModifiedDate: str
        state: Union[str, WorkspaceFailoverState]


    class azure.mgmt.loganalytics.types.WorkspaceFeatures(TypedDict, total=False):
        key "clusterResourceId": Optional[str]
        key "dataAuthorizationMode": Optional[bool]
        key "disableLocalAuth": Optional[bool]
        key "enableDataExport": Optional[bool]
        key "enableLogAccessUsingOnlyResourcePermissions": Optional[bool]
        key "immediatePurgeDataOn30Days": Optional[bool]
        key "unifiedSentinelBillingOnly": Optional[bool]
        associations: list[str]
        clusterResourceId: str
        dataAuthorizationMode: bool
        disableLocalAuth: bool
        enableDataExport: bool
        enableLogAccessUsingOnlyResourcePermissions: bool
        immediatePurgeDataOn30Days: bool
        unifiedSentinelBillingOnly: bool


    class azure.mgmt.loganalytics.types.WorkspacePatch(AzureEntityResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "name": str
        key "properties": ForwardRef('WorkspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        name: str
        properties: WorkspaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.loganalytics.types.WorkspaceProperties(TypedDict, total=False):
        key "createdDate": str
        key "customerId": str
        key "defaultDataCollectionRuleResourceId": str
        key "failover": ForwardRef('WorkspaceFailoverProperties', module='types')
        key "features": ForwardRef('WorkspaceFeatures', module='types')
        key "forceCmkForQuery": bool
        key "modifiedDate": str
        key "provisioningState": Union[str, WorkspaceEntityStatus]
        key "publicNetworkAccessForIngestion": Union[str, PublicNetworkAccessType]
        key "publicNetworkAccessForQuery": Union[str, PublicNetworkAccessType]
        key "replication": ForwardRef('WorkspaceReplicationProperties', module='types')
        key "retentionInDays": Optional[int]
        key "sku": ForwardRef('WorkspaceSku', module='types')
        key "workspaceCapping": ForwardRef('WorkspaceCapping', module='types')
        createdDate: str
        customerId: str
        defaultDataCollectionRuleResourceId: str
        failover: WorkspaceFailoverProperties
        features: WorkspaceFeatures
        forceCmkForQuery: bool
        modifiedDate: str
        privateLinkScopedResources: list[PrivateLinkScopedResource]
        provisioningState: Union[str, WorkspaceEntityStatus]
        publicNetworkAccessForIngestion: Union[str, PublicNetworkAccessType]
        publicNetworkAccessForQuery: Union[str, PublicNetworkAccessType]
        replication: WorkspaceReplicationProperties
        retentionInDays: int
        sku: WorkspaceSku
        workspaceCapping: WorkspaceCapping


    class azure.mgmt.loganalytics.types.WorkspacePurgeBody(TypedDict, total=False):
        key "filters": Required[list[WorkspacePurgeBodyFilters]]
        key "table": Required[str]
        filters: list[WorkspacePurgeBodyFilters]
        table: str


    class azure.mgmt.loganalytics.types.WorkspacePurgeBodyFilters(TypedDict, total=False):
        key "column": str
        key "key": str
        key "operator": str
        key "value": Any
        column: str
        key: str
        operator: str
        value: Any


    class azure.mgmt.loganalytics.types.WorkspacePurgeLakeDataBody(TypedDict, total=False):
        key "table": Required[str]
        key "timeRange": Required[WorkspacePurgeLakeDataTimeRange]
        table: str
        timeRange: WorkspacePurgeLakeDataTimeRange


    class azure.mgmt.loganalytics.types.WorkspacePurgeLakeDataTimeRange(TypedDict, total=False):
        key "endTime": Required[str]
        key "startTime": Required[str]
        endTime: str
        startTime: str


    class azure.mgmt.loganalytics.types.WorkspaceReplicationProperties(TypedDict, total=False):
        key "createdDate": str
        key "enabled": bool
        key "lastModifiedDate": str
        key "location": str
        key "provisioningState": Union[str, WorkspaceReplicationState]
        createdDate: str
        enabled: bool
        lastModifiedDate: str
        location: str
        provisioningState: Union[str, WorkspaceReplicationState]


    class azure.mgmt.loganalytics.types.WorkspaceSku(TypedDict, total=False):
        key "capacityReservationLevel": Optional[int]
        key "lastSkuUpdate": str
        key "name": Required[Union[str, WorkspaceSkuNameEnum]]
        capacityReservationLevel: int
        lastSkuUpdate: str
        name: Union[str, WorkspaceSkuNameEnum]


```