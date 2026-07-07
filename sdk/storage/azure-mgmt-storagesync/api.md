```py
namespace azure.mgmt.storagesync

    class azure.mgmt.storagesync.StorageSyncMgmtClient(_StorageSyncMgmtClientOperationsMixin): implements ContextManager 
        cloud_endpoints: CloudEndpointsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        registered_servers: RegisteredServersOperations
        server_endpoints: ServerEndpointsOperations
        storage_sync_services: StorageSyncServicesOperations
        sync_groups: SyncGroupsOperations
        workflows: WorkflowsOperations

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

        @distributed_trace
        def location_operation_status(
                self, 
                location_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LocationOperationStatus: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.storagesync.aio

    class azure.mgmt.storagesync.aio.StorageSyncMgmtClient(_StorageSyncMgmtClientOperationsMixin): implements AsyncContextManager 
        cloud_endpoints: CloudEndpointsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        registered_servers: RegisteredServersOperations
        server_endpoints: ServerEndpointsOperations
        storage_sync_services: StorageSyncServicesOperations
        sync_groups: SyncGroupsOperations
        workflows: WorkflowsOperations

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

        @distributed_trace_async
        async def location_operation_status(
                self, 
                location_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LocationOperationStatus: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.storagesync.aio.operations

    class azure.mgmt.storagesync.aio.operations.CloudEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def afs_share_metadata_certificate_public_keys(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> CloudEndpointAfsShareMetadataCertificatePublicKeys: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: CloudEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: CloudEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_post_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostBackupResponse]: ...

        @overload
        async def begin_post_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostBackupResponse]: ...

        @overload
        async def begin_post_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostBackupResponse]: ...

        @overload
        async def begin_post_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PostRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_post_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PostRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_post_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PreRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PreRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_change_detection(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: TriggerChangeDetectionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_change_detection(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: TriggerChangeDetectionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_change_detection(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> CloudEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudEndpoint]: ...

        @distributed_trace_async
        async def restore_heartbeat(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.storagesync.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                location_name: str, 
                workflow_id: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.storagesync.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationEntity]: ...


    class azure.mgmt.storagesync.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.storagesync.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.storagesync.aio.operations.RegisteredServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegisteredServer]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegisteredServer]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegisteredServer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rollover(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: TriggerRolloverRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rollover(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: TriggerRolloverRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rollover(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegisteredServer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegisteredServer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegisteredServer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                **kwargs: Any
            ) -> RegisteredServer: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegisteredServer]: ...


    class azure.mgmt.storagesync.aio.operations.ServerEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: ServerEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: ServerEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_recall_action(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: RecallActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_recall_action(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: RecallActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_recall_action(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: Optional[ServerEndpointUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: Optional[ServerEndpointUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                **kwargs: Any
            ) -> ServerEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ServerEndpoint]: ...


    class azure.mgmt.storagesync.aio.operations.StorageSyncServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: StorageSyncServiceCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: StorageSyncServiceCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: Optional[StorageSyncServiceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: Optional[StorageSyncServiceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @overload
        async def check_name_availability(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> StorageSyncService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageSyncService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StorageSyncService]: ...


    class azure.mgmt.storagesync.aio.operations.SyncGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                parameters: SyncGroupCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SyncGroup: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                parameters: SyncGroupCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SyncGroup: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SyncGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> SyncGroup: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SyncGroup]: ...


    class azure.mgmt.storagesync.aio.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def abort(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workflow]: ...


namespace azure.mgmt.storagesync.models

    class azure.mgmt.storagesync.models.BackupRequest(_Model):
        azure_file_share: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_file_share: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.ChangeDetectionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        RECURSIVE = "Recursive"


    class azure.mgmt.storagesync.models.CheckNameAvailabilityParameters(_Model):
        name: str
        type: Union[str, Type]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, Type]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, NameAvailabilityReason]]


    class azure.mgmt.storagesync.models.CloudEndpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[CloudEndpointProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.CloudEndpointAfsShareMetadataCertificatePublicKeys(_Model):
        first_key: Optional[str]
        second_key: Optional[str]


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationActivity(_Model):
        deletes_progress_percent: Optional[int]
        last_updated_timestamp: Optional[datetime]
        minutes_remaining: Optional[int]
        operation_state: Optional[Union[str, CloudEndpointChangeEnumerationActivityState]]
        processed_directories_count: Optional[int]
        processed_files_count: Optional[int]
        progress_percent: Optional[int]
        started_timestamp: Optional[datetime]
        status_code: Optional[int]
        total_counts_state: Optional[Union[str, CloudEndpointChangeEnumerationTotalCountsState]]
        total_directories_count: Optional[int]
        total_files_count: Optional[int]
        total_size_bytes: Optional[int]


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationActivityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUMERATION_IN_PROGRESS = "EnumerationInProgress"
        INITIAL_ENUMERATION_IN_PROGRESS = "InitialEnumerationInProgress"


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationStatus(_Model):
        activity: Optional[CloudEndpointChangeEnumerationActivity]
        last_enumeration_status: Optional[CloudEndpointLastChangeEnumerationStatus]
        last_updated_timestamp: Optional[datetime]


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationTotalCountsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALCULATING = "Calculating"
        FINAL = "Final"


    class azure.mgmt.storagesync.models.CloudEndpointCreateParameters(ProxyResource):
        id: str
        name: str
        properties: Optional[CloudEndpointCreateParametersProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudEndpointCreateParametersProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.CloudEndpointCreateParametersProperties(_Model):
        azure_file_share_name: Optional[str]
        friendly_name: Optional[str]
        storage_account_resource_id: Optional[str]
        storage_account_tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_file_share_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                storage_account_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.CloudEndpointLastChangeEnumerationStatus(_Model):
        completed_timestamp: Optional[datetime]
        namespace_directories_count: Optional[int]
        namespace_files_count: Optional[int]
        namespace_size_bytes: Optional[int]
        next_run_timestamp: Optional[datetime]
        started_timestamp: Optional[datetime]


    class azure.mgmt.storagesync.models.CloudEndpointProperties(_Model):
        azure_file_share_name: Optional[str]
        backup_enabled: Optional[str]
        change_enumeration_status: Optional[CloudEndpointChangeEnumerationStatus]
        friendly_name: Optional[str]
        last_operation_name: Optional[str]
        last_workflow_id: Optional[str]
        partnership_id: Optional[str]
        provisioning_state: Optional[str]
        storage_account_resource_id: Optional[str]
        storage_account_tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_file_share_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                last_operation_name: Optional[str] = ..., 
                last_workflow_id: Optional[str] = ..., 
                partnership_id: Optional[str] = ..., 
                provisioning_state: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                storage_account_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.CloudTieringCachePerformance(_Model):
        cache_hit_bytes: Optional[int]
        cache_hit_bytes_percent: Optional[int]
        cache_miss_bytes: Optional[int]
        last_updated_timestamp: Optional[datetime]


    class azure.mgmt.storagesync.models.CloudTieringDatePolicyStatus(_Model):
        last_updated_timestamp: Optional[datetime]
        tiered_files_most_recent_access_timestamp: Optional[datetime]


    class azure.mgmt.storagesync.models.CloudTieringFilesNotTiering(_Model):
        errors: Optional[list[FilesNotTieringError]]
        last_updated_timestamp: Optional[datetime]
        total_file_count: Optional[int]


    class azure.mgmt.storagesync.models.CloudTieringLowDiskMode(_Model):
        last_updated_timestamp: Optional[datetime]
        state: Optional[Union[str, CloudTieringLowDiskModeState]]


    class azure.mgmt.storagesync.models.CloudTieringLowDiskModeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storagesync.models.CloudTieringSpaceSavings(_Model):
        cached_size_bytes: Optional[int]
        last_updated_timestamp: Optional[datetime]
        space_savings_bytes: Optional[int]
        space_savings_percent: Optional[int]
        total_size_cloud_bytes: Optional[int]
        volume_size_bytes: Optional[int]


    class azure.mgmt.storagesync.models.CloudTieringVolumeFreeSpacePolicyStatus(_Model):
        current_volume_free_space_percent: Optional[int]
        effective_volume_free_space_policy: Optional[int]
        last_updated_timestamp: Optional[datetime]


    class azure.mgmt.storagesync.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storagesync.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.storagesync.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.storagesync.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.FeatureStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "off"
        ON = "on"


    class azure.mgmt.storagesync.models.FilesNotTieringError(_Model):
        error_code: Optional[int]
        file_count: Optional[int]


    class azure.mgmt.storagesync.models.IncomingTrafficPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_ALL_TRAFFIC = "AllowAllTraffic"
        ALLOW_VIRTUAL_NETWORKS_ONLY = "AllowVirtualNetworksOnly"


    class azure.mgmt.storagesync.models.InitialDownloadPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVOID_TIERED_FILES = "AvoidTieredFiles"
        NAMESPACE_ONLY = "NamespaceOnly"
        NAMESPACE_THEN_MODIFIED_FILES = "NamespaceThenModifiedFiles"


    class azure.mgmt.storagesync.models.InitialUploadPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MERGE = "Merge"
        SERVER_AUTHORITATIVE = "ServerAuthoritative"


    class azure.mgmt.storagesync.models.LocalCacheMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD_NEW_AND_MODIFIED_FILES = "DownloadNewAndModifiedFiles"
        UPDATE_LOCALLY_CACHED_FILES = "UpdateLocallyCachedFiles"


    class azure.mgmt.storagesync.models.LocationOperationStatus(_Model):
        end_time: Optional[datetime]
        error: Optional[StorageSyncApiError]
        id: Optional[str]
        name: Optional[str]
        percent_complete: Optional[int]
        start_time: Optional[datetime]
        status: Optional[str]


    class azure.mgmt.storagesync.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.storagesync.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storagesync.models.NameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.storagesync.models.OperationDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "cancel"
        DO = "do"
        UNDO = "undo"


    class azure.mgmt.storagesync.models.OperationDisplayInfo(_Model):
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


    class azure.mgmt.storagesync.models.OperationEntity(_Model):
        display: Optional[OperationDisplayInfo]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.OperationProperties(_Model):
        service_specification: Optional[OperationResourceServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[OperationResourceServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.OperationResourceMetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[OperationResourceMetricSpecificationDimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[bool]
        lock_aggregation_type: Optional[str]
        name: Optional[str]
        supported_aggregation_types: Optional[list[str]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[list[OperationResourceMetricSpecificationDimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                lock_aggregation_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.OperationResourceMetricSpecificationDimension(_Model):
        display_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_shoebox: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.OperationResourceServiceSpecification(_Model):
        metric_specifications: Optional[list[OperationResourceMetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                metric_specifications: Optional[list[OperationResourceMetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.OperationStatus(_Model):
        end_time: Optional[datetime]
        error: Optional[StorageSyncApiError]
        name: Optional[str]
        start_time: Optional[datetime]
        status: Optional[str]


    class azure.mgmt.storagesync.models.PostBackupResponse(_Model):
        backup_metadata: Optional[PostBackupResponseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                backup_metadata: Optional[PostBackupResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.PostBackupResponseProperties(_Model):
        cloud_endpoint_name: Optional[str]


    class azure.mgmt.storagesync.models.PostRestoreRequest(_Model):
        azure_file_share_uri: Optional[str]
        failed_file_list: Optional[str]
        partition: Optional[str]
        replica_group: Optional[str]
        request_id: Optional[str]
        restore_file_spec: Optional[list[RestoreFileSpec]]
        source_azure_file_share_uri: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_file_share_uri: Optional[str] = ..., 
                failed_file_list: Optional[str] = ..., 
                partition: Optional[str] = ..., 
                replica_group: Optional[str] = ..., 
                request_id: Optional[str] = ..., 
                restore_file_spec: Optional[list[RestoreFileSpec]] = ..., 
                source_azure_file_share_uri: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.PreRestoreRequest(_Model):
        azure_file_share_uri: Optional[str]
        backup_metadata_property_bag: Optional[str]
        partition: Optional[str]
        pause_wait_for_sync_drain_time_period_in_seconds: Optional[int]
        replica_group: Optional[str]
        request_id: Optional[str]
        restore_file_spec: Optional[list[RestoreFileSpec]]
        source_azure_file_share_uri: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_file_share_uri: Optional[str] = ..., 
                backup_metadata_property_bag: Optional[str] = ..., 
                partition: Optional[str] = ..., 
                pause_wait_for_sync_drain_time_period_in_seconds: Optional[int] = ..., 
                replica_group: Optional[str] = ..., 
                request_id: Optional[str] = ..., 
                restore_file_spec: Optional[list[RestoreFileSpec]] = ..., 
                source_azure_file_share_uri: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.storagesync.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storagesync.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.storagesync.models.PrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.PrivateLinkResourceListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.models.RecallActionParameters(_Model):
        pattern: Optional[str]
        recall_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                pattern: Optional[str] = ..., 
                recall_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.RegisteredServer(ProxyResource):
        id: str
        name: str
        properties: Optional[RegisteredServerProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegisteredServerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.RegisteredServerAgentVersionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        EXPIRED = "Expired"
        NEAR_EXPIRY = "NearExpiry"
        OK = "Ok"


    class azure.mgmt.storagesync.models.RegisteredServerCreateParameters(ProxyResource):
        id: str
        name: str
        properties: Optional[RegisteredServerCreateParametersProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegisteredServerCreateParametersProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.RegisteredServerCreateParametersProperties(_Model):
        agent_version: Optional[str]
        application_id: Optional[str]
        cluster_id: Optional[str]
        cluster_name: Optional[str]
        friendly_name: Optional[str]
        identity: Optional[bool]
        last_heart_beat: Optional[str]
        server_certificate: Optional[str]
        server_id: Optional[str]
        server_os_version: Optional[str]
        server_role: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                application_id: Optional[str] = ..., 
                cluster_id: Optional[str] = ..., 
                cluster_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                identity: Optional[bool] = ..., 
                last_heart_beat: Optional[str] = ..., 
                server_certificate: Optional[str] = ..., 
                server_id: Optional[str] = ..., 
                server_os_version: Optional[str] = ..., 
                server_role: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.RegisteredServerProperties(_Model):
        active_auth_type: Optional[Union[str, ServerAuthType]]
        agent_version: Optional[str]
        agent_version_expiration_date: Optional[datetime]
        agent_version_status: Optional[Union[str, RegisteredServerAgentVersionStatus]]
        application_id: Optional[str]
        cluster_id: Optional[str]
        cluster_name: Optional[str]
        discovery_endpoint_uri: Optional[str]
        friendly_name: Optional[str]
        identity: Optional[bool]
        last_heart_beat: Optional[str]
        last_operation_name: Optional[str]
        last_workflow_id: Optional[str]
        latest_application_id: Optional[str]
        management_endpoint_uri: Optional[str]
        monitoring_configuration: Optional[str]
        monitoring_endpoint_uri: Optional[str]
        provisioning_state: Optional[str]
        resource_location: Optional[str]
        server_certificate: Optional[str]
        server_id: Optional[str]
        server_management_error_code: Optional[int]
        server_name: Optional[str]
        server_os_version: Optional[str]
        server_role: Optional[str]
        service_location: Optional[str]
        storage_sync_service_uid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                application_id: Optional[str] = ..., 
                cluster_id: Optional[str] = ..., 
                cluster_name: Optional[str] = ..., 
                discovery_endpoint_uri: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                last_heart_beat: Optional[str] = ..., 
                last_operation_name: Optional[str] = ..., 
                last_workflow_id: Optional[str] = ..., 
                latest_application_id: Optional[str] = ..., 
                management_endpoint_uri: Optional[str] = ..., 
                monitoring_configuration: Optional[str] = ..., 
                monitoring_endpoint_uri: Optional[str] = ..., 
                provisioning_state: Optional[str] = ..., 
                resource_location: Optional[str] = ..., 
                server_certificate: Optional[str] = ..., 
                server_id: Optional[str] = ..., 
                server_management_error_code: Optional[int] = ..., 
                server_os_version: Optional[str] = ..., 
                server_role: Optional[str] = ..., 
                service_location: Optional[str] = ..., 
                storage_sync_service_uid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.RegisteredServerUpdateParameters(ProxyResource):
        id: str
        name: str
        properties: Optional[RegisteredServerUpdateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegisteredServerUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.RegisteredServerUpdateProperties(_Model):
        application_id: Optional[str]
        identity: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storagesync.models.RestoreFileSpec(_Model):
        isdir: Optional[bool]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                isdir: Optional[bool] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.ServerAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE = "Certificate"
        MANAGED_IDENTITY = "ManagedIdentity"


    class azure.mgmt.storagesync.models.ServerEndpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[ServerEndpointProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.ServerEndpointBackgroundDataDownloadActivity(_Model):
        downloaded_bytes: Optional[int]
        percent_progress: Optional[int]
        started_timestamp: Optional[datetime]
        timestamp: Optional[datetime]


    class azure.mgmt.storagesync.models.ServerEndpointCloudTieringStatus(_Model):
        cache_performance: Optional[CloudTieringCachePerformance]
        date_policy_status: Optional[CloudTieringDatePolicyStatus]
        files_not_tiering: Optional[CloudTieringFilesNotTiering]
        health: Optional[Union[str, ServerEndpointHealthState]]
        health_last_updated_timestamp: Optional[datetime]
        last_cloud_tiering_result: Optional[int]
        last_success_timestamp: Optional[datetime]
        last_updated_timestamp: Optional[datetime]
        low_disk_mode: Optional[CloudTieringLowDiskMode]
        space_savings: Optional[CloudTieringSpaceSavings]
        volume_free_space_policy_status: Optional[CloudTieringVolumeFreeSpacePolicyStatus]


    class azure.mgmt.storagesync.models.ServerEndpointCreateParameters(ProxyResource):
        id: str
        name: str
        properties: Optional[ServerEndpointCreateParametersProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerEndpointCreateParametersProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.ServerEndpointCreateParametersProperties(_Model):
        cloud_tiering: Optional[Union[str, FeatureStatus]]
        friendly_name: Optional[str]
        initial_download_policy: Optional[Union[str, InitialDownloadPolicy]]
        initial_upload_policy: Optional[Union[str, InitialUploadPolicy]]
        local_cache_mode: Optional[Union[str, LocalCacheMode]]
        offline_data_transfer: Optional[Union[str, FeatureStatus]]
        offline_data_transfer_share_name: Optional[str]
        server_local_path: Optional[str]
        server_resource_id: Optional[str]
        tier_files_older_than_days: Optional[int]
        volume_free_space_percent: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cloud_tiering: Optional[Union[str, FeatureStatus]] = ..., 
                friendly_name: Optional[str] = ..., 
                initial_download_policy: Optional[Union[str, InitialDownloadPolicy]] = ..., 
                initial_upload_policy: Optional[Union[str, InitialUploadPolicy]] = ..., 
                local_cache_mode: Optional[Union[str, LocalCacheMode]] = ..., 
                offline_data_transfer: Optional[Union[str, FeatureStatus]] = ..., 
                offline_data_transfer_share_name: Optional[str] = ..., 
                server_local_path: Optional[str] = ..., 
                server_resource_id: Optional[str] = ..., 
                tier_files_older_than_days: Optional[int] = ..., 
                volume_free_space_percent: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.ServerEndpointFilesNotSyncingError(_Model):
        error_code: Optional[int]
        persistent_count: Optional[int]
        transient_count: Optional[int]


    class azure.mgmt.storagesync.models.ServerEndpointHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        HEALTHY = "Healthy"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.storagesync.models.ServerEndpointOfflineDataTransferState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        IN_PROGRESS = "InProgress"
        NOT_RUNNING = "NotRunning"
        STOPPING = "Stopping"


    class azure.mgmt.storagesync.models.ServerEndpointProperties(_Model):
        cloud_tiering: Optional[Union[str, FeatureStatus]]
        cloud_tiering_status: Optional[ServerEndpointCloudTieringStatus]
        friendly_name: Optional[str]
        initial_download_policy: Optional[Union[str, InitialDownloadPolicy]]
        initial_upload_policy: Optional[Union[str, InitialUploadPolicy]]
        last_operation_name: Optional[str]
        last_workflow_id: Optional[str]
        local_cache_mode: Optional[Union[str, LocalCacheMode]]
        offline_data_transfer: Optional[Union[str, FeatureStatus]]
        offline_data_transfer_share_name: Optional[str]
        offline_data_transfer_storage_account_resource_id: Optional[str]
        offline_data_transfer_storage_account_tenant_id: Optional[str]
        provisioning_state: Optional[str]
        recall_status: Optional[ServerEndpointRecallStatus]
        server_endpoint_provisioning_status: Optional[ServerEndpointProvisioningStatus]
        server_local_path: Optional[str]
        server_name: Optional[str]
        server_resource_id: Optional[str]
        sync_status: Optional[ServerEndpointSyncStatus]
        tier_files_older_than_days: Optional[int]
        volume_free_space_percent: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cloud_tiering: Optional[Union[str, FeatureStatus]] = ..., 
                friendly_name: Optional[str] = ..., 
                initial_download_policy: Optional[Union[str, InitialDownloadPolicy]] = ..., 
                initial_upload_policy: Optional[Union[str, InitialUploadPolicy]] = ..., 
                local_cache_mode: Optional[Union[str, LocalCacheMode]] = ..., 
                offline_data_transfer: Optional[Union[str, FeatureStatus]] = ..., 
                offline_data_transfer_share_name: Optional[str] = ..., 
                server_endpoint_provisioning_status: Optional[ServerEndpointProvisioningStatus] = ..., 
                server_local_path: Optional[str] = ..., 
                server_resource_id: Optional[str] = ..., 
                tier_files_older_than_days: Optional[int] = ..., 
                volume_free_space_percent: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.ServerEndpointProvisioningStatus(_Model):
        provisioning_status: Optional[Union[str, ServerProvisioningStatus]]
        provisioning_step_statuses: Optional[list[ServerEndpointProvisioningStepStatus]]
        provisioning_type: Optional[str]


    class azure.mgmt.storagesync.models.ServerEndpointProvisioningStepStatus(_Model):
        additional_information: Optional[dict[str, str]]
        end_time: Optional[datetime]
        error_code: Optional[int]
        minutes_left: Optional[int]
        name: Optional[str]
        progress_percentage: Optional[int]
        start_time: Optional[datetime]
        status: Optional[str]


    class azure.mgmt.storagesync.models.ServerEndpointRecallError(_Model):
        count: Optional[int]
        error_code: Optional[int]


    class azure.mgmt.storagesync.models.ServerEndpointRecallStatus(_Model):
        last_updated_timestamp: Optional[datetime]
        recall_errors: Optional[list[ServerEndpointRecallError]]
        total_recall_errors_count: Optional[int]


    class azure.mgmt.storagesync.models.ServerEndpointSyncActivityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD = "Download"
        UPLOAD = "Upload"
        UPLOAD_AND_DOWNLOAD = "UploadAndDownload"


    class azure.mgmt.storagesync.models.ServerEndpointSyncActivityStatus(_Model):
        applied_bytes: Optional[int]
        applied_item_count: Optional[int]
        per_item_error_count: Optional[int]
        session_minutes_remaining: Optional[int]
        sync_mode: Optional[Union[str, ServerEndpointSyncMode]]
        timestamp: Optional[datetime]
        total_bytes: Optional[int]
        total_item_count: Optional[int]


    class azure.mgmt.storagesync.models.ServerEndpointSyncMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIAL_FULL_DOWNLOAD = "InitialFullDownload"
        INITIAL_UPLOAD = "InitialUpload"
        NAMESPACE_DOWNLOAD = "NamespaceDownload"
        REGULAR = "Regular"
        SNAPSHOT_UPLOAD = "SnapshotUpload"


    class azure.mgmt.storagesync.models.ServerEndpointSyncSessionStatus(_Model):
        files_not_syncing_errors: Optional[list[ServerEndpointFilesNotSyncingError]]
        last_sync_mode: Optional[Union[str, ServerEndpointSyncMode]]
        last_sync_per_item_error_count: Optional[int]
        last_sync_result: Optional[int]
        last_sync_success_timestamp: Optional[datetime]
        last_sync_timestamp: Optional[datetime]
        persistent_files_not_syncing_count: Optional[int]
        transient_files_not_syncing_count: Optional[int]


    class azure.mgmt.storagesync.models.ServerEndpointSyncStatus(_Model):
        background_data_download_activity: Optional[ServerEndpointBackgroundDataDownloadActivity]
        combined_health: Optional[Union[str, ServerEndpointHealthState]]
        download_activity: Optional[ServerEndpointSyncActivityStatus]
        download_health: Optional[Union[str, ServerEndpointHealthState]]
        download_status: Optional[ServerEndpointSyncSessionStatus]
        last_updated_timestamp: Optional[datetime]
        offline_data_transfer_status: Optional[Union[str, ServerEndpointOfflineDataTransferState]]
        sync_activity: Optional[Union[str, ServerEndpointSyncActivityState]]
        total_persistent_files_not_syncing_count: Optional[int]
        upload_activity: Optional[ServerEndpointSyncActivityStatus]
        upload_health: Optional[Union[str, ServerEndpointHealthState]]
        upload_status: Optional[ServerEndpointSyncSessionStatus]


    class azure.mgmt.storagesync.models.ServerEndpointUpdateParameters(_Model):
        properties: Optional[ServerEndpointUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerEndpointUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.ServerEndpointUpdateProperties(_Model):
        cloud_tiering: Optional[Union[str, FeatureStatus]]
        local_cache_mode: Optional[Union[str, LocalCacheMode]]
        offline_data_transfer: Optional[Union[str, FeatureStatus]]
        offline_data_transfer_share_name: Optional[str]
        tier_files_older_than_days: Optional[int]
        volume_free_space_percent: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cloud_tiering: Optional[Union[str, FeatureStatus]] = ..., 
                local_cache_mode: Optional[Union[str, LocalCacheMode]] = ..., 
                offline_data_transfer: Optional[Union[str, FeatureStatus]] = ..., 
                offline_data_transfer_share_name: Optional[str] = ..., 
                tier_files_older_than_days: Optional[int] = ..., 
                volume_free_space_percent: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.ServerProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        READY_SYNC_FUNCTIONAL = "Ready_SyncFunctional"
        READY_SYNC_NOT_FUNCTIONAL = "Ready_SyncNotFunctional"


    class azure.mgmt.storagesync.models.StorageSyncApiError(_Model):
        code: Optional[str]
        details: Optional[StorageSyncErrorDetails]
        innererror: Optional[StorageSyncInnerErrorDetails]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[StorageSyncErrorDetails] = ..., 
                innererror: Optional[StorageSyncInnerErrorDetails] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncError(_Model):
        error: Optional[StorageSyncApiError]
        innererror: Optional[StorageSyncApiError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[StorageSyncApiError] = ..., 
                innererror: Optional[StorageSyncApiError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncErrorDetails(_Model):
        code: Optional[str]
        exception_type: Optional[str]
        hashed_message: Optional[str]
        http_error_code: Optional[str]
        http_method: Optional[str]
        message: Optional[str]
        request_uri: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                exception_type: Optional[str] = ..., 
                hashed_message: Optional[str] = ..., 
                http_error_code: Optional[str] = ..., 
                http_method: Optional[str] = ..., 
                message: Optional[str] = ..., 
                request_uri: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncInnerErrorDetails(_Model):
        call_stack: Optional[str]
        inner_exception: Optional[str]
        inner_exception_call_stack: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                call_stack: Optional[str] = ..., 
                inner_exception: Optional[str] = ..., 
                inner_exception_call_stack: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncService(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[StorageSyncServiceProperties]
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
                properties: Optional[StorageSyncServiceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceCreateParameters(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[StorageSyncServiceCreateParametersProperties]
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
                properties: Optional[StorageSyncServiceCreateParametersProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceCreateParametersProperties(_Model):
        incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]]
        use_identity: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]] = ..., 
                use_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceProperties(_Model):
        incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]]
        last_operation_name: Optional[str]
        last_workflow_id: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        storage_sync_service_status: Optional[int]
        storage_sync_service_uid: Optional[str]
        use_identity: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[StorageSyncServiceUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[StorageSyncServiceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceUpdateProperties(_Model):
        incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]]
        use_identity: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]] = ..., 
                use_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.SyncGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[SyncGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SyncGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.SyncGroupCreateParameters(ProxyResource):
        id: str
        name: str
        properties: Optional[Any]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.SyncGroupProperties(_Model):
        sync_group_status: Optional[str]
        unique_id: Optional[str]


    class azure.mgmt.storagesync.models.SystemData(_Model):
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


    class azure.mgmt.storagesync.models.TrackedResource(Resource):
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


    class azure.mgmt.storagesync.models.TriggerChangeDetectionParameters(_Model):
        change_detection_mode: Optional[Union[str, ChangeDetectionMode]]
        directory_path: Optional[str]
        paths: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                change_detection_mode: Optional[Union[str, ChangeDetectionMode]] = ..., 
                directory_path: Optional[str] = ..., 
                paths: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.TriggerRolloverRequest(_Model):
        server_certificate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                server_certificate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_STORAGE_SYNC_STORAGE_SYNC_SERVICES = "Microsoft.StorageSync/storageSyncServices"


    class azure.mgmt.storagesync.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.storagesync.models.Workflow(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkflowProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkflowProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagesync.models.WorkflowProperties(_Model):
        command_name: Optional[str]
        created_timestamp: Optional[datetime]
        last_operation_id: Optional[str]
        last_status_timestamp: Optional[datetime]
        last_step_name: Optional[str]
        operation: Optional[Union[str, OperationDirection]]
        status: Optional[Union[str, WorkflowStatus]]
        steps: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_operation_id: Optional[str] = ..., 
                last_step_name: Optional[str] = ..., 
                operation: Optional[Union[str, OperationDirection]] = ..., 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                steps: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagesync.models.WorkflowStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABORTED = "aborted"
        ACTIVE = "active"
        EXPIRED = "expired"
        FAILED = "failed"
        SUCCEEDED = "succeeded"


namespace azure.mgmt.storagesync.operations

    class azure.mgmt.storagesync.operations.CloudEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def afs_share_metadata_certificate_public_keys(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> CloudEndpointAfsShareMetadataCertificatePublicKeys: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: CloudEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: CloudEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_post_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostBackupResponse]: ...

        @overload
        def begin_post_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostBackupResponse]: ...

        @overload
        def begin_post_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostBackupResponse]: ...

        @overload
        def begin_post_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PostRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_post_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PostRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_post_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: BackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_backup(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PreRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: PreRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_restore(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_change_detection(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: TriggerChangeDetectionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_change_detection(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: TriggerChangeDetectionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_change_detection(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> CloudEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CloudEndpoint]: ...

        @distributed_trace
        def restore_heartbeat(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.storagesync.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                location_name: str, 
                workflow_id: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.storagesync.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationEntity]: ...


    class azure.mgmt.storagesync.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.storagesync.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.storagesync.operations.RegisteredServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegisteredServer]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegisteredServer]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegisteredServer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rollover(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: TriggerRolloverRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rollover(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: TriggerRolloverRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rollover(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegisteredServer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: RegisteredServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegisteredServer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegisteredServer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                **kwargs: Any
            ) -> RegisteredServer: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RegisteredServer]: ...


    class azure.mgmt.storagesync.operations.ServerEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: ServerEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: ServerEndpointCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_recall_action(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: RecallActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_recall_action(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: RecallActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_recall_action(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: Optional[ServerEndpointUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: Optional[ServerEndpointUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                server_endpoint_name: str, 
                **kwargs: Any
            ) -> ServerEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ServerEndpoint]: ...


    class azure.mgmt.storagesync.operations.StorageSyncServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: StorageSyncServiceCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: StorageSyncServiceCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: Optional[StorageSyncServiceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: Optional[StorageSyncServiceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @overload
        def check_name_availability(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> StorageSyncService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageSyncService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StorageSyncService]: ...


    class azure.mgmt.storagesync.operations.SyncGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                parameters: SyncGroupCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SyncGroup: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                parameters: SyncGroupCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SyncGroup: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SyncGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                **kwargs: Any
            ) -> SyncGroup: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SyncGroup]: ...


    class azure.mgmt.storagesync.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def abort(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workflow]: ...


namespace azure.mgmt.storagesync.types

    class azure.mgmt.storagesync.types.BackupRequest(TypedDict, total=False):
        key "azureFileShare": str
        azure_file_share: str


    class azure.mgmt.storagesync.types.CheckNameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, Type]]
        name: str
        type: Union[str, Type]


    class azure.mgmt.storagesync.types.CheckNameAvailabilityResult(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": Union[str, NameAvailabilityReason]
        message: str
        name_available: bool
        reason: Union[str, NameAvailabilityReason]


    class azure.mgmt.storagesync.types.CloudEndpoint(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CloudEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CloudEndpointProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.CloudEndpointAfsShareMetadataCertificatePublicKeys(TypedDict, total=False):
        key "firstKey": str
        key "secondKey": str
        first_key: str
        second_key: str


    class azure.mgmt.storagesync.types.CloudEndpointChangeEnumerationActivity(TypedDict, total=False):
        key "deletesProgressPercent": int
        key "lastUpdatedTimestamp": str
        key "minutesRemaining": int
        key "operationState": Union[str, CloudEndpointChangeEnumerationActivityState]
        key "processedDirectoriesCount": int
        key "processedFilesCount": int
        key "progressPercent": int
        key "startedTimestamp": str
        key "statusCode": int
        key "totalCountsState": Union[str, CloudEndpointChangeEnumerationTotalCountsState]
        key "totalDirectoriesCount": int
        key "totalFilesCount": int
        key "totalSizeBytes": int
        deletes_progress_percent: int
        last_updated_timestamp: str
        minutes_remaining: int
        operation_state: Union[str, CloudEndpointChangeEnumerationActivityState]
        processed_directories_count: int
        processed_files_count: int
        progress_percent: int
        started_timestamp: str
        status_code: int
        total_counts_state: Union[str, CloudEndpointChangeEnumerationTotalCountsState]
        total_directories_count: int
        total_files_count: int
        total_size_bytes: int


    class azure.mgmt.storagesync.types.CloudEndpointChangeEnumerationStatus(TypedDict, total=False):
        key "activity": ForwardRef('CloudEndpointChangeEnumerationActivity', module='types')
        key "lastEnumerationStatus": ForwardRef('CloudEndpointLastChangeEnumerationStatus', module='types')
        key "lastUpdatedTimestamp": str
        activity: CloudEndpointChangeEnumerationActivity
        last_enumeration_status: CloudEndpointLastChangeEnumerationStatus
        last_updated_timestamp: str


    class azure.mgmt.storagesync.types.CloudEndpointCreateParameters(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CloudEndpointCreateParametersProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CloudEndpointCreateParametersProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.CloudEndpointCreateParametersProperties(TypedDict, total=False):
        key "azureFileShareName": str
        key "friendlyName": str
        key "storageAccountResourceId": str
        key "storageAccountTenantId": str
        azure_file_share_name: str
        friendly_name: str
        storage_account_resource_id: str
        storage_account_tenant_id: str


    class azure.mgmt.storagesync.types.CloudEndpointLastChangeEnumerationStatus(TypedDict, total=False):
        key "completedTimestamp": str
        key "namespaceDirectoriesCount": int
        key "namespaceFilesCount": int
        key "namespaceSizeBytes": int
        key "nextRunTimestamp": str
        key "startedTimestamp": str
        completed_timestamp: str
        namespace_directories_count: int
        namespace_files_count: int
        namespace_size_bytes: int
        next_run_timestamp: str
        started_timestamp: str


    class azure.mgmt.storagesync.types.CloudEndpointProperties(TypedDict, total=False):
        key "azureFileShareName": str
        key "backupEnabled": str
        key "changeEnumerationStatus": ForwardRef('CloudEndpointChangeEnumerationStatus', module='types')
        key "friendlyName": str
        key "lastOperationName": str
        key "lastWorkflowId": str
        key "partnershipId": str
        key "provisioningState": str
        key "storageAccountResourceId": str
        key "storageAccountTenantId": str
        azure_file_share_name: str
        backup_enabled: str
        change_enumeration_status: CloudEndpointChangeEnumerationStatus
        friendly_name: str
        last_operation_name: str
        last_workflow_id: str
        partnership_id: str
        provisioning_state: str
        storage_account_resource_id: str
        storage_account_tenant_id: str


    class azure.mgmt.storagesync.types.CloudTieringCachePerformance(TypedDict, total=False):
        key "cacheHitBytes": int
        key "cacheHitBytesPercent": int
        key "cacheMissBytes": int
        key "lastUpdatedTimestamp": str
        cache_hit_bytes: int
        cache_hit_bytes_percent: int
        cache_miss_bytes: int
        last_updated_timestamp: str


    class azure.mgmt.storagesync.types.CloudTieringDatePolicyStatus(TypedDict, total=False):
        key "lastUpdatedTimestamp": str
        key "tieredFilesMostRecentAccessTimestamp": str
        last_updated_timestamp: str
        tiered_files_most_recent_access_timestamp: str


    class azure.mgmt.storagesync.types.CloudTieringFilesNotTiering(TypedDict, total=False):
        key "lastUpdatedTimestamp": str
        key "totalFileCount": int
        errors: list[FilesNotTieringError]
        last_updated_timestamp: str
        total_file_count: int


    class azure.mgmt.storagesync.types.CloudTieringLowDiskMode(TypedDict, total=False):
        key "lastUpdatedTimestamp": str
        key "state": Union[str, CloudTieringLowDiskModeState]
        last_updated_timestamp: str
        state: Union[str, CloudTieringLowDiskModeState]


    class azure.mgmt.storagesync.types.CloudTieringSpaceSavings(TypedDict, total=False):
        key "cachedSizeBytes": int
        key "lastUpdatedTimestamp": str
        key "spaceSavingsBytes": int
        key "spaceSavingsPercent": int
        key "totalSizeCloudBytes": int
        key "volumeSizeBytes": int
        cached_size_bytes: int
        last_updated_timestamp: str
        space_savings_bytes: int
        space_savings_percent: int
        total_size_cloud_bytes: int
        volume_size_bytes: int


    class azure.mgmt.storagesync.types.CloudTieringVolumeFreeSpacePolicyStatus(TypedDict, total=False):
        key "currentVolumeFreeSpacePercent": int
        key "effectiveVolumeFreeSpacePolicy": int
        key "lastUpdatedTimestamp": str
        current_volume_free_space_percent: int
        effective_volume_free_space_policy: int
        last_updated_timestamp: str


    class azure.mgmt.storagesync.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.storagesync.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.storagesync.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.storagesync.types.FilesNotTieringError(TypedDict, total=False):
        key "errorCode": int
        key "fileCount": int
        error_code: int
        file_count: int


    class azure.mgmt.storagesync.types.LocationOperationStatus(TypedDict, total=False):
        key "endTime": str
        key "error": ForwardRef('StorageSyncApiError', module='types')
        key "id": str
        key "name": str
        key "percentComplete": int
        key "startTime": str
        key "status": str
        end_time: str
        error: StorageSyncApiError
        id: str
        name: str
        percent_complete: int
        start_time: str
        status: str


    class azure.mgmt.storagesync.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.storagesync.types.OperationDisplayInfo(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.storagesync.types.OperationEntity(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplayInfo', module='types')
        key "name": str
        key "origin": str
        key "properties": ForwardRef('OperationProperties', module='types')
        display: OperationDisplayInfo
        name: str
        origin: str
        properties: OperationProperties


    class azure.mgmt.storagesync.types.OperationProperties(TypedDict, total=False):
        key "serviceSpecification": ForwardRef('OperationResourceServiceSpecification', module='types')
        service_specification: OperationResourceServiceSpecification


    class azure.mgmt.storagesync.types.OperationResourceMetricSpecification(TypedDict, total=False):
        key "aggregationType": str
        key "displayDescription": str
        key "displayName": str
        key "fillGapWithZero": bool
        key "lockAggregationType": str
        key "name": str
        key "unit": str
        aggregation_type: str
        dimensions: list[OperationResourceMetricSpecificationDimension]
        display_description: str
        display_name: str
        fill_gap_with_zero: bool
        lock_aggregation_type: str
        name: str
        supportedAggregationTypes: list[str]
        supported_aggregation_types: list[str]
        unit: str


    class azure.mgmt.storagesync.types.OperationResourceMetricSpecificationDimension(TypedDict, total=False):
        key "displayName": str
        key "name": str
        key "toBeExportedForShoebox": bool
        display_name: str
        name: str
        to_be_exported_for_shoebox: bool


    class azure.mgmt.storagesync.types.OperationResourceServiceSpecification(TypedDict, total=False):
        metricSpecifications: list[OperationResourceMetricSpecification]
        metric_specifications: list[OperationResourceMetricSpecification]


    class azure.mgmt.storagesync.types.OperationStatus(TypedDict, total=False):
        key "endTime": str
        key "error": ForwardRef('StorageSyncApiError', module='types')
        key "name": str
        key "startTime": str
        key "status": str
        end_time: str
        error: StorageSyncApiError
        name: str
        start_time: str
        status: str


    class azure.mgmt.storagesync.types.PostBackupResponse(TypedDict, total=False):
        key "backupMetadata": ForwardRef('PostBackupResponseProperties', module='types')
        backup_metadata: PostBackupResponseProperties


    class azure.mgmt.storagesync.types.PostBackupResponseProperties(TypedDict, total=False):
        key "cloudEndpointName": str
        cloud_endpoint_name: str


    class azure.mgmt.storagesync.types.PostRestoreRequest(TypedDict, total=False):
        key "azureFileShareUri": str
        key "failedFileList": str
        key "partition": str
        key "replicaGroup": str
        key "requestId": str
        key "sourceAzureFileShareUri": str
        key "status": str
        azure_file_share_uri: str
        failed_file_list: str
        partition: str
        replica_group: str
        request_id: str
        restoreFileSpec: list[RestoreFileSpec]
        restore_file_spec: list[RestoreFileSpec]
        source_azure_file_share_uri: str
        status: str


    class azure.mgmt.storagesync.types.PreRestoreRequest(TypedDict, total=False):
        key "azureFileShareUri": str
        key "backupMetadataPropertyBag": str
        key "partition": str
        key "pauseWaitForSyncDrainTimePeriodInSeconds": int
        key "replicaGroup": str
        key "requestId": str
        key "sourceAzureFileShareUri": str
        key "status": str
        azure_file_share_uri: str
        backup_metadata_property_bag: str
        partition: str
        pause_wait_for_sync_drain_time_period_in_seconds: int
        replica_group: str
        request_id: str
        restoreFileSpec: list[RestoreFileSpec]
        restore_file_spec: list[RestoreFileSpec]
        source_azure_file_share_uri: str
        status: str


    class azure.mgmt.storagesync.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.storagesync.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.storagesync.types.PrivateLinkResource(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.PrivateLinkResourceListResult(TypedDict, total=False):
        value: list[PrivateLinkResource]


    class azure.mgmt.storagesync.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.storagesync.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.storagesync.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.RecallActionParameters(TypedDict, total=False):
        key "pattern": str
        key "recallPath": str
        pattern: str
        recall_path: str


    class azure.mgmt.storagesync.types.RegisteredServer(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RegisteredServerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RegisteredServerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.RegisteredServerCreateParameters(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RegisteredServerCreateParametersProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RegisteredServerCreateParametersProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.RegisteredServerCreateParametersProperties(TypedDict, total=False):
        key "agentVersion": str
        key "applicationId": str
        key "clusterId": str
        key "clusterName": str
        key "friendlyName": str
        key "identity": bool
        key "lastHeartBeat": str
        key "serverCertificate": str
        key "serverId": str
        key "serverOSVersion": str
        key "serverRole": str
        agent_version: str
        application_id: str
        cluster_id: str
        cluster_name: str
        friendly_name: str
        identity: bool
        last_heart_beat: str
        server_certificate: str
        server_id: str
        server_os_version: str
        server_role: str


    class azure.mgmt.storagesync.types.RegisteredServerProperties(TypedDict, total=False):
        key "activeAuthType": Union[str, ServerAuthType]
        key "agentVersion": str
        key "agentVersionExpirationDate": str
        key "agentVersionStatus": Union[str, RegisteredServerAgentVersionStatus]
        key "applicationId": str
        key "clusterId": str
        key "clusterName": str
        key "discoveryEndpointUri": str
        key "friendlyName": str
        key "identity": bool
        key "lastHeartBeat": str
        key "lastOperationName": str
        key "lastWorkflowId": str
        key "latestApplicationId": str
        key "managementEndpointUri": str
        key "monitoringConfiguration": str
        key "monitoringEndpointUri": str
        key "provisioningState": str
        key "resourceLocation": str
        key "serverCertificate": str
        key "serverId": str
        key "serverManagementErrorCode": int
        key "serverName": str
        key "serverOSVersion": str
        key "serverRole": str
        key "serviceLocation": str
        key "storageSyncServiceUid": str
        active_auth_type: Union[str, ServerAuthType]
        agent_version: str
        agent_version_expiration_date: str
        agent_version_status: Union[str, RegisteredServerAgentVersionStatus]
        application_id: str
        cluster_id: str
        cluster_name: str
        discovery_endpoint_uri: str
        friendly_name: str
        identity: bool
        last_heart_beat: str
        last_operation_name: str
        last_workflow_id: str
        latest_application_id: str
        management_endpoint_uri: str
        monitoring_configuration: str
        monitoring_endpoint_uri: str
        provisioning_state: str
        resource_location: str
        server_certificate: str
        server_id: str
        server_management_error_code: int
        server_name: str
        server_os_version: str
        server_role: str
        service_location: str
        storage_sync_service_uid: str


    class azure.mgmt.storagesync.types.RegisteredServerUpdateParameters(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RegisteredServerUpdateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RegisteredServerUpdateProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.RegisteredServerUpdateProperties(TypedDict, total=False):
        key "applicationId": str
        key "identity": bool
        application_id: str
        identity: bool


    class azure.mgmt.storagesync.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.RestoreFileSpec(TypedDict, total=False):
        key "isdir": bool
        key "path": str
        isdir: bool
        path: str


    class azure.mgmt.storagesync.types.ServerEndpoint(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServerEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServerEndpointProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.ServerEndpointBackgroundDataDownloadActivity(TypedDict, total=False):
        key "downloadedBytes": int
        key "percentProgress": int
        key "startedTimestamp": str
        key "timestamp": str
        downloaded_bytes: int
        percent_progress: int
        started_timestamp: str
        timestamp: str


    class azure.mgmt.storagesync.types.ServerEndpointCloudTieringStatus(TypedDict, total=False):
        key "cachePerformance": ForwardRef('CloudTieringCachePerformance', module='types')
        key "datePolicyStatus": ForwardRef('CloudTieringDatePolicyStatus', module='types')
        key "filesNotTiering": ForwardRef('CloudTieringFilesNotTiering', module='types')
        key "health": Union[str, ServerEndpointHealthState]
        key "healthLastUpdatedTimestamp": str
        key "lastCloudTieringResult": int
        key "lastSuccessTimestamp": str
        key "lastUpdatedTimestamp": str
        key "lowDiskMode": ForwardRef('CloudTieringLowDiskMode', module='types')
        key "spaceSavings": ForwardRef('CloudTieringSpaceSavings', module='types')
        key "volumeFreeSpacePolicyStatus": ForwardRef('CloudTieringVolumeFreeSpacePolicyStatus', module='types')
        cache_performance: CloudTieringCachePerformance
        date_policy_status: CloudTieringDatePolicyStatus
        files_not_tiering: CloudTieringFilesNotTiering
        health: Union[str, ServerEndpointHealthState]
        health_last_updated_timestamp: str
        last_cloud_tiering_result: int
        last_success_timestamp: str
        last_updated_timestamp: str
        low_disk_mode: CloudTieringLowDiskMode
        space_savings: CloudTieringSpaceSavings
        volume_free_space_policy_status: CloudTieringVolumeFreeSpacePolicyStatus


    class azure.mgmt.storagesync.types.ServerEndpointCreateParameters(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServerEndpointCreateParametersProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServerEndpointCreateParametersProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.ServerEndpointCreateParametersProperties(TypedDict, total=False):
        key "cloudTiering": Union[str, FeatureStatus]
        key "friendlyName": str
        key "initialDownloadPolicy": Union[str, InitialDownloadPolicy]
        key "initialUploadPolicy": Union[str, InitialUploadPolicy]
        key "localCacheMode": Union[str, LocalCacheMode]
        key "offlineDataTransfer": Union[str, FeatureStatus]
        key "offlineDataTransferShareName": str
        key "serverLocalPath": str
        key "serverResourceId": str
        key "tierFilesOlderThanDays": int
        key "volumeFreeSpacePercent": int
        cloud_tiering: Union[str, FeatureStatus]
        friendly_name: str
        initial_download_policy: Union[str, InitialDownloadPolicy]
        initial_upload_policy: Union[str, InitialUploadPolicy]
        local_cache_mode: Union[str, LocalCacheMode]
        offline_data_transfer: Union[str, FeatureStatus]
        offline_data_transfer_share_name: str
        server_local_path: str
        server_resource_id: str
        tier_files_older_than_days: int
        volume_free_space_percent: int


    class azure.mgmt.storagesync.types.ServerEndpointFilesNotSyncingError(TypedDict, total=False):
        key "errorCode": int
        key "persistentCount": int
        key "transientCount": int
        error_code: int
        persistent_count: int
        transient_count: int


    class azure.mgmt.storagesync.types.ServerEndpointProperties(TypedDict, total=False):
        key "cloudTiering": Union[str, FeatureStatus]
        key "cloudTieringStatus": ForwardRef('ServerEndpointCloudTieringStatus', module='types')
        key "friendlyName": str
        key "initialDownloadPolicy": Union[str, InitialDownloadPolicy]
        key "initialUploadPolicy": Union[str, InitialUploadPolicy]
        key "lastOperationName": str
        key "lastWorkflowId": str
        key "localCacheMode": Union[str, LocalCacheMode]
        key "offlineDataTransfer": Union[str, FeatureStatus]
        key "offlineDataTransferShareName": str
        key "offlineDataTransferStorageAccountResourceId": str
        key "offlineDataTransferStorageAccountTenantId": str
        key "provisioningState": str
        key "recallStatus": ForwardRef('ServerEndpointRecallStatus', module='types')
        key "serverEndpointProvisioningStatus": ForwardRef('ServerEndpointProvisioningStatus', module='types')
        key "serverLocalPath": str
        key "serverName": str
        key "serverResourceId": str
        key "syncStatus": ForwardRef('ServerEndpointSyncStatus', module='types')
        key "tierFilesOlderThanDays": int
        key "volumeFreeSpacePercent": int
        cloud_tiering: Union[str, FeatureStatus]
        cloud_tiering_status: ServerEndpointCloudTieringStatus
        friendly_name: str
        initial_download_policy: Union[str, InitialDownloadPolicy]
        initial_upload_policy: Union[str, InitialUploadPolicy]
        last_operation_name: str
        last_workflow_id: str
        local_cache_mode: Union[str, LocalCacheMode]
        offline_data_transfer: Union[str, FeatureStatus]
        offline_data_transfer_share_name: str
        offline_data_transfer_storage_account_resource_id: str
        offline_data_transfer_storage_account_tenant_id: str
        provisioning_state: str
        recall_status: ServerEndpointRecallStatus
        server_endpoint_provisioning_status: ServerEndpointProvisioningStatus
        server_local_path: str
        server_name: str
        server_resource_id: str
        sync_status: ServerEndpointSyncStatus
        tier_files_older_than_days: int
        volume_free_space_percent: int


    class azure.mgmt.storagesync.types.ServerEndpointProvisioningStatus(TypedDict, total=False):
        key "provisioningStatus": Union[str, ServerProvisioningStatus]
        key "provisioningType": str
        provisioningStepStatuses: list[ServerEndpointProvisioningStepStatus]
        provisioning_status: Union[str, ServerProvisioningStatus]
        provisioning_step_statuses: list[ServerEndpointProvisioningStepStatus]
        provisioning_type: str


    class azure.mgmt.storagesync.types.ServerEndpointProvisioningStepStatus(TypedDict, total=False):
        key "endTime": str
        key "errorCode": int
        key "minutesLeft": int
        key "name": str
        key "progressPercentage": int
        key "startTime": str
        key "status": str
        additionalInformation: dict[str, str]
        additional_information: dict[str, str]
        end_time: str
        error_code: int
        minutes_left: int
        name: str
        progress_percentage: int
        start_time: str
        status: str


    class azure.mgmt.storagesync.types.ServerEndpointRecallError(TypedDict, total=False):
        key "count": int
        key "errorCode": int
        count: int
        error_code: int


    class azure.mgmt.storagesync.types.ServerEndpointRecallStatus(TypedDict, total=False):
        key "lastUpdatedTimestamp": str
        key "totalRecallErrorsCount": int
        last_updated_timestamp: str
        recallErrors: list[ServerEndpointRecallError]
        recall_errors: list[ServerEndpointRecallError]
        total_recall_errors_count: int


    class azure.mgmt.storagesync.types.ServerEndpointSyncActivityStatus(TypedDict, total=False):
        key "appliedBytes": int
        key "appliedItemCount": int
        key "perItemErrorCount": int
        key "sessionMinutesRemaining": int
        key "syncMode": Union[str, ServerEndpointSyncMode]
        key "timestamp": str
        key "totalBytes": int
        key "totalItemCount": int
        applied_bytes: int
        applied_item_count: int
        per_item_error_count: int
        session_minutes_remaining: int
        sync_mode: Union[str, ServerEndpointSyncMode]
        timestamp: str
        total_bytes: int
        total_item_count: int


    class azure.mgmt.storagesync.types.ServerEndpointSyncSessionStatus(TypedDict, total=False):
        key "lastSyncMode": Union[str, ServerEndpointSyncMode]
        key "lastSyncPerItemErrorCount": int
        key "lastSyncResult": int
        key "lastSyncSuccessTimestamp": str
        key "lastSyncTimestamp": str
        key "persistentFilesNotSyncingCount": int
        key "transientFilesNotSyncingCount": int
        filesNotSyncingErrors: list[ServerEndpointFilesNotSyncingError]
        files_not_syncing_errors: list[ServerEndpointFilesNotSyncingError]
        last_sync_mode: Union[str, ServerEndpointSyncMode]
        last_sync_per_item_error_count: int
        last_sync_result: int
        last_sync_success_timestamp: str
        last_sync_timestamp: str
        persistent_files_not_syncing_count: int
        transient_files_not_syncing_count: int


    class azure.mgmt.storagesync.types.ServerEndpointSyncStatus(TypedDict, total=False):
        key "backgroundDataDownloadActivity": ForwardRef('ServerEndpointBackgroundDataDownloadActivity', module='types')
        key "combinedHealth": Union[str, ServerEndpointHealthState]
        key "downloadActivity": ForwardRef('ServerEndpointSyncActivityStatus', module='types')
        key "downloadHealth": Union[str, ServerEndpointHealthState]
        key "downloadStatus": ForwardRef('ServerEndpointSyncSessionStatus', module='types')
        key "lastUpdatedTimestamp": str
        key "offlineDataTransferStatus": Union[str, ServerEndpointOfflineDataTransferState]
        key "syncActivity": Union[str, ServerEndpointSyncActivityState]
        key "totalPersistentFilesNotSyncingCount": int
        key "uploadActivity": ForwardRef('ServerEndpointSyncActivityStatus', module='types')
        key "uploadHealth": Union[str, ServerEndpointHealthState]
        key "uploadStatus": ForwardRef('ServerEndpointSyncSessionStatus', module='types')
        background_data_download_activity: ServerEndpointBackgroundDataDownloadActivity
        combined_health: Union[str, ServerEndpointHealthState]
        download_activity: ServerEndpointSyncActivityStatus
        download_health: Union[str, ServerEndpointHealthState]
        download_status: ServerEndpointSyncSessionStatus
        last_updated_timestamp: str
        offline_data_transfer_status: Union[str, ServerEndpointOfflineDataTransferState]
        sync_activity: Union[str, ServerEndpointSyncActivityState]
        total_persistent_files_not_syncing_count: int
        upload_activity: ServerEndpointSyncActivityStatus
        upload_health: Union[str, ServerEndpointHealthState]
        upload_status: ServerEndpointSyncSessionStatus


    class azure.mgmt.storagesync.types.ServerEndpointUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ServerEndpointUpdateProperties', module='types')
        properties: ServerEndpointUpdateProperties


    class azure.mgmt.storagesync.types.ServerEndpointUpdateProperties(TypedDict, total=False):
        key "cloudTiering": Union[str, FeatureStatus]
        key "localCacheMode": Union[str, LocalCacheMode]
        key "offlineDataTransfer": Union[str, FeatureStatus]
        key "offlineDataTransferShareName": str
        key "tierFilesOlderThanDays": int
        key "volumeFreeSpacePercent": int
        cloud_tiering: Union[str, FeatureStatus]
        local_cache_mode: Union[str, LocalCacheMode]
        offline_data_transfer: Union[str, FeatureStatus]
        offline_data_transfer_share_name: str
        tier_files_older_than_days: int
        volume_free_space_percent: int


    class azure.mgmt.storagesync.types.StorageSyncApiError(TypedDict, total=False):
        key "code": str
        key "details": ForwardRef('StorageSyncErrorDetails', module='types')
        key "innererror": ForwardRef('StorageSyncInnerErrorDetails', module='types')
        key "message": str
        key "target": str
        code: str
        details: StorageSyncErrorDetails
        innererror: StorageSyncInnerErrorDetails
        message: str
        target: str


    class azure.mgmt.storagesync.types.StorageSyncError(TypedDict, total=False):
        key "error": ForwardRef('StorageSyncApiError', module='types')
        key "innererror": ForwardRef('StorageSyncApiError', module='types')
        error: StorageSyncApiError
        innererror: StorageSyncApiError


    class azure.mgmt.storagesync.types.StorageSyncErrorDetails(TypedDict, total=False):
        key "code": str
        key "exceptionType": str
        key "hashedMessage": str
        key "httpErrorCode": str
        key "httpMethod": str
        key "message": str
        key "requestUri": str
        key "target": str
        code: str
        exception_type: str
        hashed_message: str
        http_error_code: str
        http_method: str
        message: str
        request_uri: str
        target: str


    class azure.mgmt.storagesync.types.StorageSyncInnerErrorDetails(TypedDict, total=False):
        key "callStack": str
        key "innerException": str
        key "innerExceptionCallStack": str
        key "message": str
        call_stack: str
        inner_exception: str
        inner_exception_call_stack: str
        message: str


    class azure.mgmt.storagesync.types.StorageSyncService(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageSyncServiceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: StorageSyncServiceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagesync.types.StorageSyncServiceCreateParameters(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageSyncServiceCreateParametersProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: StorageSyncServiceCreateParametersProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagesync.types.StorageSyncServiceCreateParametersProperties(TypedDict, total=False):
        key "incomingTrafficPolicy": Union[str, IncomingTrafficPolicy]
        key "useIdentity": bool
        incoming_traffic_policy: Union[str, IncomingTrafficPolicy]
        use_identity: bool


    class azure.mgmt.storagesync.types.StorageSyncServiceProperties(TypedDict, total=False):
        key "incomingTrafficPolicy": Union[str, IncomingTrafficPolicy]
        key "lastOperationName": str
        key "lastWorkflowId": str
        key "provisioningState": str
        key "storageSyncServiceStatus": int
        key "storageSyncServiceUid": str
        key "useIdentity": bool
        incoming_traffic_policy: Union[str, IncomingTrafficPolicy]
        last_operation_name: str
        last_workflow_id: str
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        storage_sync_service_status: int
        storage_sync_service_uid: str
        use_identity: bool


    class azure.mgmt.storagesync.types.StorageSyncServiceUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('StorageSyncServiceUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: StorageSyncServiceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.storagesync.types.StorageSyncServiceUpdateProperties(TypedDict, total=False):
        key "incomingTrafficPolicy": Union[str, IncomingTrafficPolicy]
        key "useIdentity": bool
        incoming_traffic_policy: Union[str, IncomingTrafficPolicy]
        use_identity: bool


    class azure.mgmt.storagesync.types.SyncGroup(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SyncGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SyncGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.SyncGroupCreateParameters(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Any
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: Any
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.SyncGroupProperties(TypedDict, total=False):
        key "syncGroupStatus": str
        key "uniqueId": str
        sync_group_status: str
        unique_id: str


    class azure.mgmt.storagesync.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.storagesync.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagesync.types.TriggerChangeDetectionParameters(TypedDict, total=False):
        key "changeDetectionMode": Union[str, ChangeDetectionMode]
        key "directoryPath": str
        change_detection_mode: Union[str, ChangeDetectionMode]
        directory_path: str
        paths: list[str]


    class azure.mgmt.storagesync.types.TriggerRolloverRequest(TypedDict, total=False):
        key "serverCertificate": str
        server_certificate: str


    class azure.mgmt.storagesync.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.storagesync.types.Workflow(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkflowProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: WorkflowProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagesync.types.WorkflowProperties(TypedDict, total=False):
        key "commandName": str
        key "createdTimestamp": str
        key "lastOperationId": str
        key "lastStatusTimestamp": str
        key "lastStepName": str
        key "operation": Union[str, OperationDirection]
        key "status": Union[str, WorkflowStatus]
        key "steps": str
        command_name: str
        created_timestamp: str
        last_operation_id: str
        last_status_timestamp: str
        last_step_name: str
        operation: Union[str, OperationDirection]
        status: Union[str, WorkflowStatus]
        steps: str


```