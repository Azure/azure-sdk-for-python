```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.storagesync

    class azure.mgmt.storagesync.MicrosoftStorageSync(MicrosoftStorageSyncOperationsMixin): implements ContextManager 
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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def location_operation_status(
                self, 
                location_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LocationOperationStatus: ...


namespace azure.mgmt.storagesync.aio

    class azure.mgmt.storagesync.aio.MicrosoftStorageSync(MicrosoftStorageSyncOperationsMixin): implements AsyncContextManager 
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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def location_operation_status(
                self, 
                location_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LocationOperationStatus: ...


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
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CloudEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CloudEndpoint]: ...

        @distributed_trace_async
        async def restoreheartbeat(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.storagesync.aio.operations.MicrosoftStorageSyncOperationsMixin(MicrosoftStorageSyncMixinABC):

        @distributed_trace_async
        async def location_operation_status(
                self, 
                location_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LocationOperationStatus: ...


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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.storagesync.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OperationEntity]: ...


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
                properties: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnection]: ...


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
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RegisteredServer: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RegisteredServer]: ...


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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
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
                parameters: Optional[IO] = None, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServerEndpoint]: ...


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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageSyncService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: Optional[IO] = None, 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StorageSyncService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[StorageSyncService]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[StorageSyncService]: ...


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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SyncGroup: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SyncGroup]: ...


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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workflow]: ...


namespace azure.mgmt.storagesync.models

    class azure.mgmt.storagesync.models.BackupRequest(Model):
        azure_file_share: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_file_share: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ChangeDetectionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        RECURSIVE = "Recursive"


    class azure.mgmt.storagesync.models.CheckNameAvailabilityParameters(Model):
        name: str
        type: str = "Microsoft.StorageSync/storageSyncServices"

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CheckNameAvailabilityResult(Model):
        message: str
        name_available: bool
        reason: Union[str, NameAvailabilityReason]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpoint(ProxyResource):
        azure_file_share_name: str
        backup_enabled: str
        change_enumeration_status: CloudEndpointChangeEnumerationStatus
        friendly_name: str
        id: str
        last_operation_name: str
        last_workflow_id: str
        name: str
        partnership_id: str
        provisioning_state: str
        storage_account_resource_id: str
        storage_account_tenant_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

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
                storage_account_tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpointAfsShareMetadataCertificatePublicKeys(Model):
        first_key: str
        second_key: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpointArray(Model):
        value: list[CloudEndpoint]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[CloudEndpoint]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationActivity(Model):
        deletes_progress_percent: int
        last_updated_timestamp: datetime
        minutes_remaining: int
        operation_state: Union[str, CloudEndpointChangeEnumerationActivityState]
        processed_directories_count: int
        processed_files_count: int
        progress_percent: int
        started_timestamp: datetime
        status_code: int
        total_counts_state: Union[str, CloudEndpointChangeEnumerationTotalCountsState]
        total_directories_count: int
        total_files_count: int
        total_size_bytes: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationActivityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUMERATION_IN_PROGRESS = "EnumerationInProgress"
        INITIAL_ENUMERATION_IN_PROGRESS = "InitialEnumerationInProgress"


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationStatus(Model):
        activity: CloudEndpointChangeEnumerationActivity
        last_enumeration_status: CloudEndpointLastChangeEnumerationStatus
        last_updated_timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpointChangeEnumerationTotalCountsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALCULATING = "Calculating"
        FINAL = "Final"


    class azure.mgmt.storagesync.models.CloudEndpointCreateParameters(ProxyResource):
        azure_file_share_name: str
        friendly_name: str
        id: str
        name: str
        storage_account_resource_id: str
        storage_account_tenant_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_file_share_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                storage_account_tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudEndpointLastChangeEnumerationStatus(Model):
        completed_timestamp: datetime
        namespace_directories_count: int
        namespace_files_count: int
        namespace_size_bytes: int
        next_run_timestamp: datetime
        started_timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudTieringCachePerformance(Model):
        cache_hit_bytes: int
        cache_hit_bytes_percent: int
        cache_miss_bytes: int
        last_updated_timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudTieringDatePolicyStatus(Model):
        last_updated_timestamp: datetime
        tiered_files_most_recent_access_timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudTieringFilesNotTiering(Model):
        errors: list[FilesNotTieringError]
        last_updated_timestamp: datetime
        total_file_count: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudTieringLowDiskMode(Model):
        last_updated_timestamp: datetime
        state: Union[str, CloudTieringLowDiskModeState]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudTieringLowDiskModeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storagesync.models.CloudTieringSpaceSavings(Model):
        cached_size_bytes: int
        last_updated_timestamp: datetime
        space_savings_bytes: int
        space_savings_percent: int
        total_size_cloud_bytes: int
        volume_size_bytes: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CloudTieringVolumeFreeSpacePolicyStatus(Model):
        current_volume_free_space_percent: int
        effective_volume_free_space_policy: int
        last_updated_timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storagesync.models.FeatureStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "off"
        ON = "on"


    class azure.mgmt.storagesync.models.FilesNotTieringError(Model):
        error_code: int
        file_count: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


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


    class azure.mgmt.storagesync.models.LocationOperationStatus(Model):
        end_time: datetime
        error: StorageSyncApiError
        id: str
        name: str
        percent_complete: int
        start_time: datetime
        status: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.NameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.storagesync.models.OperationDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "cancel"
        DO = "do"
        UNDO = "undo"


    class azure.mgmt.storagesync.models.OperationDisplayInfo(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationDisplayResource(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationEntity(Model):
        display: OperationDisplayInfo
        name: str
        origin: str
        properties: OperationProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationEntityListResult(Model):
        next_link: str
        value: list[OperationEntity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationEntity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationProperties(Model):
        service_specification: OperationResourceServiceSpecification

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                service_specification: Optional[OperationResourceServiceSpecification] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationResourceMetricSpecification(Model):
        aggregation_type: str
        dimensions: list[OperationResourceMetricSpecificationDimension]
        display_description: str
        display_name: str
        fill_gap_with_zero: bool
        name: str
        supported_aggregation_types: list[str]
        unit: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[List[OperationResourceMetricSpecificationDimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                supported_aggregation_types: Optional[List[str]] = ..., 
                unit: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationResourceMetricSpecificationDimension(Model):
        display_name: str
        name: str
        to_be_exported_for_shoebox: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationResourceServiceSpecification(Model):
        metric_specifications: list[OperationResourceMetricSpecification]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                metric_specifications: Optional[List[OperationResourceMetricSpecification]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.OperationStatus(Model):
        end_time: datetime
        error: StorageSyncApiError
        name: str
        start_time: datetime
        status: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PostBackupResponse(Model):
        cloud_endpoint_name: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PostRestoreRequest(Model):
        azure_file_share_uri: str
        failed_file_list: str
        partition: str
        replica_group: str
        request_id: str
        restore_file_spec: list[RestoreFileSpec]
        source_azure_file_share_uri: str
        status: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_file_share_uri: Optional[str] = ..., 
                failed_file_list: Optional[str] = ..., 
                partition: Optional[str] = ..., 
                replica_group: Optional[str] = ..., 
                request_id: Optional[str] = ..., 
                restore_file_spec: Optional[List[RestoreFileSpec]] = ..., 
                source_azure_file_share_uri: Optional[str] = ..., 
                status: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PreRestoreRequest(Model):
        azure_file_share_uri: str
        backup_metadata_property_bag: str
        partition: str
        pause_wait_for_sync_drain_time_period_in_seconds: int
        replica_group: str
        request_id: str
        restore_file_spec: list[RestoreFileSpec]
        source_azure_file_share_uri: str
        status: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_file_share_uri: Optional[str] = ..., 
                backup_metadata_property_bag: Optional[str] = ..., 
                partition: Optional[str] = ..., 
                pause_wait_for_sync_drain_time_period_in_seconds: Optional[int] = ..., 
                replica_group: Optional[str] = ..., 
                request_id: Optional[str] = ..., 
                restore_file_spec: Optional[List[RestoreFileSpec]] = ..., 
                source_azure_file_share_uri: Optional[str] = ..., 
                status: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


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
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResource]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ProgressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD = "download"
        INITIALIZE = "initialize"
        NONE = "none"
        RECALL = "recall"
        UPLOAD = "upload"


    class azure.mgmt.storagesync.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        REGISTERED = "Registered"
        SUSPENDED = "Suspended"
        UNREGISTERED = "Unregistered"
        WARNED = "Warned"


    class azure.mgmt.storagesync.models.RecallActionParameters(Model):
        pattern: str
        recall_path: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                pattern: Optional[str] = ..., 
                recall_path: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.RegisteredServer(ProxyResource):
        agent_version: str
        agent_version_expiration_date: datetime
        agent_version_status: Union[str, RegisteredServerAgentVersionStatus]
        cluster_id: str
        cluster_name: str
        discovery_endpoint_uri: str
        friendly_name: str
        id: str
        last_heart_beat: str
        last_operation_name: str
        last_workflow_id: str
        management_endpoint_uri: str
        monitoring_configuration: str
        monitoring_endpoint_uri: str
        name: str
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
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                cluster_id: Optional[str] = ..., 
                cluster_name: Optional[str] = ..., 
                discovery_endpoint_uri: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                last_heart_beat: Optional[str] = ..., 
                last_operation_name: Optional[str] = ..., 
                last_workflow_id: Optional[str] = ..., 
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
                storage_sync_service_uid: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.RegisteredServerAgentVersionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        EXPIRED = "Expired"
        NEAR_EXPIRY = "NearExpiry"
        OK = "Ok"


    class azure.mgmt.storagesync.models.RegisteredServerArray(Model):
        value: list[RegisteredServer]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[RegisteredServer]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.RegisteredServerCreateParameters(ProxyResource):
        agent_version: str
        cluster_id: str
        cluster_name: str
        friendly_name: str
        id: str
        last_heart_beat: str
        name: str
        server_certificate: str
        server_id: str
        server_os_version: str
        server_role: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                cluster_id: Optional[str] = ..., 
                cluster_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                last_heart_beat: Optional[str] = ..., 
                server_certificate: Optional[str] = ..., 
                server_id: Optional[str] = ..., 
                server_os_version: Optional[str] = ..., 
                server_role: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ResourcesMoveInfo(Model):
        resources: list[str]
        target_resource_group: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resources: Optional[List[str]] = ..., 
                target_resource_group: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.RestoreFileSpec(Model):
        isdir: bool
        path: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                isdir: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpoint(ProxyResource):
        cloud_tiering: Union[str, FeatureStatus]
        cloud_tiering_status: ServerEndpointCloudTieringStatus
        friendly_name: str
        id: str
        initial_download_policy: Union[str, InitialDownloadPolicy]
        initial_upload_policy: Union[str, InitialUploadPolicy]
        last_operation_name: str
        last_workflow_id: str
        local_cache_mode: Union[str, LocalCacheMode]
        name: str
        offline_data_transfer: Union[str, FeatureStatus]
        offline_data_transfer_share_name: str
        offline_data_transfer_storage_account_resource_id: str
        offline_data_transfer_storage_account_tenant_id: str
        provisioning_state: str
        recall_status: ServerEndpointRecallStatus
        server_local_path: str
        server_name: str
        server_resource_id: str
        sync_status: ServerEndpointSyncStatus
        system_data: SystemData
        tier_files_older_than_days: int
        type: str
        volume_free_space_percent: int

        def __eq__(self, other): ...

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
                volume_free_space_percent: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointArray(Model):
        value: list[ServerEndpoint]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ServerEndpoint]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointBackgroundDataDownloadActivity(Model):
        downloaded_bytes: int
        percent_progress: int
        started_timestamp: datetime
        timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointCloudTieringStatus(Model):
        cache_performance: CloudTieringCachePerformance
        date_policy_status: CloudTieringDatePolicyStatus
        files_not_tiering: CloudTieringFilesNotTiering
        health: Union[str, ServerEndpointHealthState]
        health_last_updated_timestamp: datetime
        last_cloud_tiering_result: int
        last_success_timestamp: datetime
        last_updated_timestamp: datetime
        low_disk_mode: CloudTieringLowDiskMode
        space_savings: CloudTieringSpaceSavings
        volume_free_space_policy_status: CloudTieringVolumeFreeSpacePolicyStatus

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointCreateParameters(ProxyResource):
        cloud_tiering: Union[str, FeatureStatus]
        friendly_name: str
        id: str
        initial_download_policy: Union[str, InitialDownloadPolicy]
        initial_upload_policy: Union[str, InitialUploadPolicy]
        local_cache_mode: Union[str, LocalCacheMode]
        name: str
        offline_data_transfer: Union[str, FeatureStatus]
        offline_data_transfer_share_name: str
        server_local_path: str
        server_resource_id: str
        system_data: SystemData
        tier_files_older_than_days: int
        type: str
        volume_free_space_percent: int

        def __eq__(self, other): ...

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
                tier_files_older_than_days: int = 0, 
                volume_free_space_percent: int = 20, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointFilesNotSyncingError(Model):
        error_code: int
        persistent_count: int
        transient_count: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        HEALTHY = "Healthy"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.storagesync.models.ServerEndpointOfflineDataTransferState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        IN_PROGRESS = "InProgress"
        NOT_RUNNING = "NotRunning"
        STOPPING = "Stopping"


    class azure.mgmt.storagesync.models.ServerEndpointRecallError(Model):
        count: int
        error_code: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointRecallStatus(Model):
        last_updated_timestamp: datetime
        recall_errors: list[ServerEndpointRecallError]
        total_recall_errors_count: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointSyncActivityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD = "Download"
        UPLOAD = "Upload"
        UPLOAD_AND_DOWNLOAD = "UploadAndDownload"


    class azure.mgmt.storagesync.models.ServerEndpointSyncActivityStatus(Model):
        applied_bytes: int
        applied_item_count: int
        per_item_error_count: int
        session_minutes_remaining: int
        sync_mode: Union[str, ServerEndpointSyncMode]
        timestamp: datetime
        total_bytes: int
        total_item_count: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointSyncMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIAL_FULL_DOWNLOAD = "InitialFullDownload"
        INITIAL_UPLOAD = "InitialUpload"
        NAMESPACE_DOWNLOAD = "NamespaceDownload"
        REGULAR = "Regular"
        SNAPSHOT_UPLOAD = "SnapshotUpload"


    class azure.mgmt.storagesync.models.ServerEndpointSyncSessionStatus(Model):
        files_not_syncing_errors: list[ServerEndpointFilesNotSyncingError]
        last_sync_mode: Union[str, ServerEndpointSyncMode]
        last_sync_per_item_error_count: int
        last_sync_result: int
        last_sync_success_timestamp: datetime
        last_sync_timestamp: datetime
        persistent_files_not_syncing_count: int
        transient_files_not_syncing_count: int

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointSyncStatus(Model):
        background_data_download_activity: ServerEndpointBackgroundDataDownloadActivity
        combined_health: Union[str, ServerEndpointHealthState]
        download_activity: ServerEndpointSyncActivityStatus
        download_health: Union[str, ServerEndpointHealthState]
        download_status: ServerEndpointSyncSessionStatus
        last_updated_timestamp: datetime
        offline_data_transfer_status: Union[str, ServerEndpointOfflineDataTransferState]
        sync_activity: Union[str, ServerEndpointSyncActivityState]
        total_persistent_files_not_syncing_count: int
        upload_activity: ServerEndpointSyncActivityStatus
        upload_health: Union[str, ServerEndpointHealthState]
        upload_status: ServerEndpointSyncSessionStatus

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.ServerEndpointUpdateParameters(Model):
        cloud_tiering: Union[str, FeatureStatus]
        local_cache_mode: Union[str, LocalCacheMode]
        offline_data_transfer: Union[str, FeatureStatus]
        offline_data_transfer_share_name: str
        tier_files_older_than_days: int
        volume_free_space_percent: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                cloud_tiering: Optional[Union[str, FeatureStatus]] = ..., 
                local_cache_mode: Optional[Union[str, LocalCacheMode]] = ..., 
                offline_data_transfer: Optional[Union[str, FeatureStatus]] = ..., 
                offline_data_transfer_share_name: Optional[str] = ..., 
                tier_files_older_than_days: Optional[int] = ..., 
                volume_free_space_percent: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncApiError(Model):
        code: str
        details: StorageSyncErrorDetails
        innererror: StorageSyncInnerErrorDetails
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[StorageSyncErrorDetails] = ..., 
                innererror: Optional[StorageSyncInnerErrorDetails] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncError(Model):
        error: StorageSyncApiError
        innererror: StorageSyncApiError

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[StorageSyncApiError] = ..., 
                innererror: Optional[StorageSyncApiError] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncErrorDetails(Model):
        code: str
        exception_type: str
        hashed_message: str
        http_error_code: str
        http_method: str
        message: str
        request_uri: str
        target: str

        def __eq__(self, other): ...

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
                target: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncInnerErrorDetails(Model):
        call_stack: str
        inner_exception: str
        inner_exception_call_stack: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                call_stack: Optional[str] = ..., 
                inner_exception: Optional[str] = ..., 
                inner_exception_call_stack: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncService(TrackedResource):
        id: str
        incoming_traffic_policy: Union[str, IncomingTrafficPolicy]
        last_operation_name: str
        last_workflow_id: str
        location: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        storage_sync_service_status: int
        storage_sync_service_uid: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceArray(Model):
        value: list[StorageSyncService]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[StorageSyncService]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceCreateParameters(Model):
        incoming_traffic_policy: Union[str, IncomingTrafficPolicy]
        location: str
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.StorageSyncServiceUpdateParameters(Model):
        incoming_traffic_policy: Union[str, IncomingTrafficPolicy]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                incoming_traffic_policy: Optional[Union[str, IncomingTrafficPolicy]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.SubscriptionState(Model):
        istransitioning: bool
        properties: JSON
        state: Union[str, Reason]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[JSON] = ..., 
                state: Optional[Union[str, Reason]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.SyncGroup(ProxyResource):
        id: str
        name: str
        sync_group_status: str
        system_data: SystemData
        type: str
        unique_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.SyncGroupArray(Model):
        value: list[SyncGroup]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SyncGroup]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.SyncGroupCreateParameters(ProxyResource):
        id: str
        name: str
        properties: JSON
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.TriggerChangeDetectionParameters(Model):
        change_detection_mode: Union[str, ChangeDetectionMode]
        directory_path: str
        paths: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                change_detection_mode: Optional[Union[str, ChangeDetectionMode]] = ..., 
                directory_path: Optional[str] = ..., 
                paths: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.TriggerRolloverRequest(Model):
        server_certificate: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                server_certificate: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.Workflow(ProxyResource):
        command_name: str
        created_timestamp: datetime
        id: str
        last_operation_id: str
        last_status_timestamp: datetime
        last_step_name: str
        name: str
        operation: Union[str, OperationDirection]
        status: Union[str, WorkflowStatus]
        steps: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                last_operation_id: Optional[str] = ..., 
                last_step_name: Optional[str] = ..., 
                operation: Optional[Union[str, OperationDirection]] = ..., 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                steps: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.storagesync.models.WorkflowArray(Model):
        value: list[Workflow]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Workflow]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


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
            ): ...

        @distributed_trace
        def afs_share_metadata_certificate_public_keys(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CloudEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CloudEndpoint]: ...

        @distributed_trace
        def restoreheartbeat(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                cloud_endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.storagesync.operations.MicrosoftStorageSyncOperationsMixin(MicrosoftStorageSyncMixinABC):

        @distributed_trace
        def location_operation_status(
                self, 
                location_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LocationOperationStatus: ...


    class azure.mgmt.storagesync.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                location_name: str, 
                workflow_id: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.storagesync.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OperationEntity]: ...


    class azure.mgmt.storagesync.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                properties: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnection]: ...


    class azure.mgmt.storagesync.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.storagesync.operations.RegisteredServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                server_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RegisteredServer: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RegisteredServer]: ...


    class azure.mgmt.storagesync.operations.ServerEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
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
                parameters: Optional[IO] = None, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerEndpoint: ...

        @distributed_trace
        def list_by_sync_group(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServerEndpoint]: ...


    class azure.mgmt.storagesync.operations.StorageSyncServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageSyncService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: Optional[IO] = None, 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StorageSyncService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[StorageSyncService]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[StorageSyncService]: ...


    class azure.mgmt.storagesync.operations.SyncGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                sync_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SyncGroup: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SyncGroup]: ...


    class azure.mgmt.storagesync.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def abort(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                workflow_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_storage_sync_service(
                self, 
                resource_group_name: str, 
                storage_sync_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workflow]: ...


```