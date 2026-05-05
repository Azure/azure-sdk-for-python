```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.hardwaresecuritymodules

    class azure.mgmt.hardwaresecuritymodules.HardwareSecurityModulesMgmtClient: implements ContextManager 
        cloud_hsm_cluster_backup_status: CloudHsmClusterBackupStatusOperations
        cloud_hsm_cluster_private_endpoint_connections: CloudHsmClusterPrivateEndpointConnectionsOperations
        cloud_hsm_cluster_private_link_resources: CloudHsmClusterPrivateLinkResourcesOperations
        cloud_hsm_cluster_restore_status: CloudHsmClusterRestoreStatusOperations
        cloud_hsm_clusters: CloudHsmClustersOperations
        dedicated_hsm: DedicatedHsmOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.hardwaresecuritymodules.aio

    class azure.mgmt.hardwaresecuritymodules.aio.HardwareSecurityModulesMgmtClient: implements AsyncContextManager 
        cloud_hsm_cluster_backup_status: CloudHsmClusterBackupStatusOperations
        cloud_hsm_cluster_private_endpoint_connections: CloudHsmClusterPrivateEndpointConnectionsOperations
        cloud_hsm_cluster_private_link_resources: CloudHsmClusterPrivateLinkResourcesOperations
        cloud_hsm_cluster_restore_status: CloudHsmClusterRestoreStatusOperations
        cloud_hsm_clusters: CloudHsmClustersOperations
        dedicated_hsm: DedicatedHsmOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.hardwaresecuritymodules.aio.operations

    class azure.mgmt.hardwaresecuritymodules.aio.operations.CloudHsmClusterBackupStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.CloudHsmClusterPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.CloudHsmClusterPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_cloud_hsm_cluster(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.CloudHsmClusterRestoreStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.CloudHsmClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_backup(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[BackupRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupResult]: ...

        @overload
        async def begin_backup(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupResult]: ...

        @overload
        async def begin_backup(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: CloudHsmCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudHsmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudHsmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudHsmCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: RestoreRequestProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestoreResult]: ...

        @overload
        async def begin_restore(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestoreResult]: ...

        @overload
        async def begin_restore(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestoreResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: CloudHsmClusterPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudHsmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudHsmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudHsmCluster]: ...

        @overload
        async def begin_validate_backup_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[BackupRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupResult]: ...

        @overload
        async def begin_validate_backup_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupResult]: ...

        @overload
        async def begin_validate_backup_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupResult]: ...

        @overload
        async def begin_validate_restore_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: Optional[RestoreRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestoreResult]: ...

        @overload
        async def begin_validate_restore_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestoreResult]: ...

        @overload
        async def begin_validate_restore_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestoreResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> CloudHsmCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudHsmCluster]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudHsmCluster]: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.DedicatedHsmOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: DedicatedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHsm]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHsm]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHsm]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: DedicatedHsmPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHsm]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHsm]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHsm]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DedicatedHsm: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedHsm]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedHsm]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.hardwaresecuritymodules.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_cloud_hsm_cluster(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


namespace azure.mgmt.hardwaresecuritymodules.models

    class azure.mgmt.hardwaresecuritymodules.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.hardwaresecuritymodules.models.ActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        FAILED = "Failed"
        NOT_ACTIVATED = "NotActivated"
        NOT_DEFINED = "NotDefined"
        UNKNOWN = "Unknown"


    class azure.mgmt.hardwaresecuritymodules.models.ApiEntityReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.AutoGeneratedDomainNameLabelScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.hardwaresecuritymodules.models.BackupRequestProperties(BackupRestoreRequestBaseProperties):
        azure_storage_blob_container_uri: str
        token: str

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_blob_container_uri: str, 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.BackupRestoreBaseResultProperties(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        job_id: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, BackupRestoreOperationStatus]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                job_id: Optional[str] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.BackupRestoreOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.hardwaresecuritymodules.models.BackupRestoreRequestBaseProperties(_Model):
        azure_storage_blob_container_uri: str
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_blob_container_uri: str, 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.BackupResult(_Model):
        properties: Optional[BackupResultProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BackupResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.BackupResultProperties(BackupRestoreBaseResultProperties):
        azure_storage_blob_container_uri: Optional[str]
        backup_id: Optional[str]
        end_time: datetime
        error: ErrorDetail
        job_id: str
        start_time: datetime
        status: Union[str, BackupRestoreOperationStatus]
        status_details: str

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_blob_container_uri: Optional[str] = ..., 
                backup_id: Optional[str] = ..., 
                error: Optional[ErrorDetail] = ..., 
                job_id: Optional[str] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmCluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[CloudHsmClusterProperties]
        sku: Optional[CloudHsmClusterSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[CloudHsmClusterProperties] = ..., 
                sku: Optional[CloudHsmClusterSku] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmClusterPatchParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmClusterProperties(_Model):
        activation_state: Optional[Union[str, ActivationState]]
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        hsms: Optional[List[CloudHsmProperties]]
        private_endpoint_connections: Optional[List[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        status_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmClusterSku(_Model):
        capacity: Optional[int]
        family: Union[str, CloudHsmClusterSkuFamily]
        name: Union[str, CloudHsmClusterSkuName]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Union[str, CloudHsmClusterSkuFamily], 
                name: Union[str, CloudHsmClusterSkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmClusterSkuFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B = "B"


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmClusterSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_B1 = "Standard_B1"
        STANDARD_B10 = "Standard B10"


    class azure.mgmt.hardwaresecuritymodules.models.CloudHsmProperties(_Model):
        fqdn: Optional[str]
        state: Optional[str]
        state_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fqdn: Optional[str] = ..., 
                state: Optional[str] = ..., 
                state_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.hardwaresecuritymodules.models.DedicatedHsm(TrackedResource):
        id: str
        location: str
        name: str
        properties: DedicatedHsmProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DedicatedHsmProperties, 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                zones: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.DedicatedHsmError(_Model):
        error: Optional[Error]


    class azure.mgmt.hardwaresecuritymodules.models.DedicatedHsmPatchParameters(_Model):
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.DedicatedHsmProperties(_Model):
        management_network_profile: Optional[NetworkProfile]
        network_profile: Optional[NetworkProfile]
        provisioning_state: Optional[Union[str, JsonWebKeyType]]
        stamp_id: Optional[str]
        status_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                management_network_profile: Optional[NetworkProfile] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                stamp_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.EndpointDependency(_Model):
        domain_name: Optional[str]
        endpoint_details: Optional[List[EndpointDetail]]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                endpoint_details: Optional[List[EndpointDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.EndpointDetail(_Model):
        description: Optional[str]
        ip_address: Optional[str]
        port: Optional[int]
        protocol: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                port: Optional[int] = ..., 
                protocol: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.Error(_Model):
        code: Optional[str]
        inner_error: Optional[Error]
        message: Optional[str]


    class azure.mgmt.hardwaresecuritymodules.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.hardwaresecuritymodules.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.hardwaresecuritymodules.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.JsonWebKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOCATING = "Allocating"
        CHECKING_QUOTA = "CheckingQuota"
        CONNECTING = "Connecting"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.hardwaresecuritymodules.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.hardwaresecuritymodules.models.NetworkInterface(_Model):
        private_ip_address: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.NetworkProfile(_Model):
        network_interfaces: Optional[List[NetworkInterface]]
        subnet: Optional[ApiEntityReference]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[List[NetworkInterface]] = ..., 
                subnet: Optional[ApiEntityReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.hardwaresecuritymodules.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.hardwaresecuritymodules.models.OutboundEnvironmentEndpoint(_Model):
        category: Optional[str]
        endpoints: Optional[List[EndpointDependency]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[List[EndpointDependency]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.hardwaresecuritymodules.models.PrivateEndpointConnection(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[List[str]]
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


    class azure.mgmt.hardwaresecuritymodules.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INTERNAL_ERROR = "InternalError"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.hardwaresecuritymodules.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.hardwaresecuritymodules.models.PrivateLinkResource(Resource):
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


    class azure.mgmt.hardwaresecuritymodules.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[List[str]]
        required_zone_names: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.hardwaresecuritymodules.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.hardwaresecuritymodules.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.hardwaresecuritymodules.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"


    class azure.mgmt.hardwaresecuritymodules.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.hardwaresecuritymodules.models.RestoreRequestProperties(BackupRestoreRequestBaseProperties):
        azure_storage_blob_container_uri: str
        backup_id: str
        token: str

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_blob_container_uri: str, 
                backup_id: str, 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.RestoreResult(_Model):
        properties: Optional[BackupRestoreBaseResultProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BackupRestoreBaseResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.Sku(_Model):
        name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAY_SHIELD10_K_LMK1_CPS250 = "payShield10K_LMK1_CPS250"
        PAY_SHIELD10_K_LMK1_CPS2500 = "payShield10K_LMK1_CPS2500"
        PAY_SHIELD10_K_LMK1_CPS60 = "payShield10K_LMK1_CPS60"
        PAY_SHIELD10_K_LMK2_CPS250 = "payShield10K_LMK2_CPS250"
        PAY_SHIELD10_K_LMK2_CPS2500 = "payShield10K_LMK2_CPS2500"
        PAY_SHIELD10_K_LMK2_CPS60 = "payShield10K_LMK2_CPS60"
        SAFE_NET_LUNA_NETWORK_HSM_A790 = "SafeNet Luna Network HSM A790"


    class azure.mgmt.hardwaresecuritymodules.models.SystemData(_Model):
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


    class azure.mgmt.hardwaresecuritymodules.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hardwaresecuritymodules.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.hardwaresecuritymodules.operations

    class azure.mgmt.hardwaresecuritymodules.operations.CloudHsmClusterBackupStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.hardwaresecuritymodules.operations.CloudHsmClusterPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                pe_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.hardwaresecuritymodules.operations.CloudHsmClusterPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_cloud_hsm_cluster(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.hardwaresecuritymodules.operations.CloudHsmClusterRestoreStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.hardwaresecuritymodules.operations.CloudHsmClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_backup(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[BackupRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupResult]: ...

        @overload
        def begin_backup(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupResult]: ...

        @overload
        def begin_backup(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: CloudHsmCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudHsmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudHsmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudHsmCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: RestoreRequestProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestoreResult]: ...

        @overload
        def begin_restore(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestoreResult]: ...

        @overload
        def begin_restore(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestoreResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: CloudHsmClusterPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudHsmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudHsmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudHsmCluster]: ...

        @overload
        def begin_validate_backup_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[BackupRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupResult]: ...

        @overload
        def begin_validate_backup_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupResult]: ...

        @overload
        def begin_validate_backup_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                backup_request_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupResult]: ...

        @overload
        def begin_validate_restore_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: Optional[RestoreRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestoreResult]: ...

        @overload
        def begin_validate_restore_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestoreResult]: ...

        @overload
        def begin_validate_restore_properties(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                restore_request_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestoreResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> CloudHsmCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CloudHsmCluster]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CloudHsmCluster]: ...


    class azure.mgmt.hardwaresecuritymodules.operations.DedicatedHsmOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: DedicatedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHsm]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHsm]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHsm]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: DedicatedHsmPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHsm]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHsm]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHsm]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DedicatedHsm: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DedicatedHsm]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DedicatedHsm]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.hardwaresecuritymodules.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.hardwaresecuritymodules.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_cloud_hsm_cluster(
                self, 
                resource_group_name: str, 
                cloud_hsm_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


```