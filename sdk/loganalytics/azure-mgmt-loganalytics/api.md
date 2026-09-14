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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                query_payload: JSON, 
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
                query_search_properties: JSON, 
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
                query_payload: JSON, 
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
                log_analytics_query_pack_payload: JSON, 
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
                log_analytics_query_pack_payload: JSON, 
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
                query_pack_tags: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                body: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
        name: str
        properties: Optional[SummaryLogsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SummaryLogsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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
                restored_logs: Optional[RestoredLogs] = ..., 
                retention_in_days: Optional[int] = ..., 
                schema: Optional[Schema] = ..., 
                search_results: Optional[SearchResults] = ..., 
                total_retention_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                query_payload: JSON, 
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
                query_search_properties: JSON, 
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
                query_payload: JSON, 
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
                log_analytics_query_pack_payload: JSON, 
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
                log_analytics_query_pack_payload: JSON, 
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
                query_pack_tags: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                body: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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


```