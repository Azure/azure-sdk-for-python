```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.containerorchestratorruntime

    class azure.mgmt.containerorchestratorruntime.ContainerOrchestratorRuntimeMgmtClient: implements ContextManager 
        bgp_peers: BgpPeersOperations
        load_balancers: LoadBalancersOperations
        operations: Operations
        services: ServicesOperations
        storage_class: StorageClassOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
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


namespace azure.mgmt.containerorchestratorruntime.aio

    class azure.mgmt.containerorchestratorruntime.aio.ContainerOrchestratorRuntimeMgmtClient: implements AsyncContextManager 
        bgp_peers: BgpPeersOperations
        load_balancers: LoadBalancersOperations
        operations: Operations
        services: ServicesOperations
        storage_class: StorageClassOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
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


namespace azure.mgmt.containerorchestratorruntime.aio.operations

    class azure.mgmt.containerorchestratorruntime.aio.operations.BgpPeersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                resource: BgpPeer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BgpPeer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BgpPeer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BgpPeer]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-03-01', params_added_on={'2024-03-01': ['api_version', 'resource_uri', 'bgp_peer_name', 'accept']})
        async def delete(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                **kwargs: Any
            ) -> BgpPeer: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[BgpPeer]: ...


    class azure.mgmt.containerorchestratorruntime.aio.operations.LoadBalancersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                resource: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-03-01', params_added_on={'2024-03-01': ['api_version', 'resource_uri', 'load_balancer_name', 'accept']})
        async def delete(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[LoadBalancer]: ...


    class azure.mgmt.containerorchestratorruntime.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.containerorchestratorruntime.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                service_name: str, 
                resource: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                service_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                service_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[ServiceResource]: ...


    class azure.mgmt.containerorchestratorruntime.aio.operations.StorageClassOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                resource: StorageClassResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                properties: StorageClassResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                **kwargs: Any
            ) -> StorageClassResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[StorageClassResource]: ...


namespace azure.mgmt.containerorchestratorruntime.models

    class azure.mgmt.containerorchestratorruntime.models.AccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_WRITE_MANY = "ReadWriteMany"
        READ_WRITE_ONCE = "ReadWriteOnce"


    class azure.mgmt.containerorchestratorruntime.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.containerorchestratorruntime.models.AdvertiseMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARP = "ARP"
        BGP = "BGP"
        BOTH = "Both"


    class azure.mgmt.containerorchestratorruntime.models.BgpPeer(ExtensionResource):
        id: str
        name: str
        properties: Optional[BgpPeerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BgpPeerProperties] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.BgpPeerProperties(Model):
        my_asn: int
        peer_address: str
        peer_asn: int
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                my_asn: int, 
                peer_address: str, 
                peer_asn: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.BlobStorageClassTypeProperties(StorageClassTypeProperties, discriminator='Blob'):
        azure_storage_account_key: str
        azure_storage_account_name: str
        type: Literal[SCType.BLOB]

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_account_key: str, 
                azure_storage_account_name: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerorchestratorruntime.models.DataResilienceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_RESILIENT = "DataResilient"
        NOT_DATA_RESILIENT = "NotDataResilient"


    class azure.mgmt.containerorchestratorruntime.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerorchestratorruntime.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerorchestratorruntime.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerorchestratorruntime.models.FailoverTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAST = "Fast"
        NOT_AVAILABLE = "NotAvailable"
        SLOW = "Slow"
        SUPER = "Super"


    class azure.mgmt.containerorchestratorruntime.models.LoadBalancer(ExtensionResource):
        id: str
        name: str
        properties: Optional[LoadBalancerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LoadBalancerProperties] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.LoadBalancerProperties(Model):
        addresses: List[str]
        advertise_mode: Union[str, AdvertiseMode]
        bgp_peers: Optional[List[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_selector: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                addresses: List[str], 
                advertise_mode: Union[str, AdvertiseMode], 
                bgp_peers: Optional[List[str]] = ..., 
                service_selector: Optional[Dict[str, str]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.NativeStorageClassTypeProperties(StorageClassTypeProperties, discriminator='Native'):
        type: Literal[SCType.NATIVE]

        @overload
        def __init__(self): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.NfsDirectoryActionOnVolumeDeletion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        RETAIN = "Retain"


    class azure.mgmt.containerorchestratorruntime.models.NfsStorageClassTypeProperties(StorageClassTypeProperties, discriminator='NFS'):
        mount_permissions: Optional[str]
        on_delete: Optional[Union[str, NfsDirectoryActionOnVolumeDeletion]]
        server: str
        share: str
        sub_dir: Optional[str]
        type: Literal[SCType.NFS]

        @overload
        def __init__(
                self, 
                *, 
                mount_permissions: Optional[str] = ..., 
                on_delete: Optional[Union[str, NfsDirectoryActionOnVolumeDeletion]] = ..., 
                server: str, 
                share: str, 
                sub_dir: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.Operation(Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ActionType]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.containerorchestratorruntime.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.containerorchestratorruntime.models.PerformanceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"
        ULTRA = "Ultra"
        UNDEFINED = "Undefined"


    class azure.mgmt.containerorchestratorruntime.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerorchestratorruntime.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerorchestratorruntime.models.RwxStorageClassTypeProperties(StorageClassTypeProperties, discriminator='RWX'):
        backing_storage_class_name: str
        type: Literal[SCType.RWX]

        @overload
        def __init__(
                self, 
                *, 
                backing_storage_class_name: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.SCType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "Blob"
        NATIVE = "Native"
        NFS = "NFS"
        RWX = "RWX"
        SMB = "SMB"


    class azure.mgmt.containerorchestratorruntime.models.ServiceProperties(Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rp_object_id: Optional[str]


    class azure.mgmt.containerorchestratorruntime.models.ServiceResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[ServiceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceProperties] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.SmbStorageClassTypeProperties(StorageClassTypeProperties, discriminator='SMB'):
        domain: Optional[str]
        password: Optional[str]
        source: str
        sub_dir: Optional[str]
        type: Literal[SCType.SMB]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domain: Optional[str] = ..., 
                password: Optional[str] = ..., 
                source: str, 
                sub_dir: Optional[str] = ..., 
                username: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.StorageClassProperties(Model):
        access_modes: Optional[List[Union[str, AccessMode]]]
        allow_volume_expansion: Optional[Union[str, VolumeExpansion]]
        data_resilience: Optional[Union[str, DataResilienceTier]]
        failover_speed: Optional[Union[str, FailoverTier]]
        limitations: Optional[List[str]]
        mount_options: Optional[List[str]]
        performance: Optional[Union[str, PerformanceTier]]
        priority: Optional[int]
        provisioner: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        type_properties: StorageClassTypeProperties
        volume_binding_mode: Optional[Union[str, VolumeBindingMode]]

        @overload
        def __init__(
                self, 
                *, 
                access_modes: Optional[List[Union[str, AccessMode]]] = ..., 
                allow_volume_expansion: Optional[Union[str, VolumeExpansion]] = ..., 
                data_resilience: Optional[Union[str, DataResilienceTier]] = ..., 
                failover_speed: Optional[Union[str, FailoverTier]] = ..., 
                limitations: Optional[List[str]] = ..., 
                mount_options: Optional[List[str]] = ..., 
                performance: Optional[Union[str, PerformanceTier]] = ..., 
                priority: Optional[int] = ..., 
                provisioner: Optional[str] = ..., 
                type_properties: StorageClassTypeProperties, 
                volume_binding_mode: Optional[Union[str, VolumeBindingMode]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.StorageClassPropertiesUpdate(Model):
        access_modes: Optional[List[Union[str, AccessMode]]]
        allow_volume_expansion: Optional[Union[str, VolumeExpansion]]
        data_resilience: Optional[Union[str, DataResilienceTier]]
        failover_speed: Optional[Union[str, FailoverTier]]
        limitations: Optional[List[str]]
        mount_options: Optional[List[str]]
        performance: Optional[Union[str, PerformanceTier]]
        priority: Optional[int]
        type_properties: Optional[StorageClassTypePropertiesUpdate]

        @overload
        def __init__(
                self, 
                *, 
                access_modes: Optional[List[Union[str, AccessMode]]] = ..., 
                allow_volume_expansion: Optional[Union[str, VolumeExpansion]] = ..., 
                data_resilience: Optional[Union[str, DataResilienceTier]] = ..., 
                failover_speed: Optional[Union[str, FailoverTier]] = ..., 
                limitations: Optional[List[str]] = ..., 
                mount_options: Optional[List[str]] = ..., 
                performance: Optional[Union[str, PerformanceTier]] = ..., 
                priority: Optional[int] = ..., 
                type_properties: Optional[StorageClassTypePropertiesUpdate] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.StorageClassResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[StorageClassProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageClassProperties] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.StorageClassResourceUpdate(Model):
        properties: Optional[StorageClassPropertiesUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageClassPropertiesUpdate] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.StorageClassTypeProperties(Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.StorageClassTypePropertiesUpdate(Model):
        azure_storage_account_key: Optional[str]
        azure_storage_account_name: Optional[str]
        backing_storage_class_name: Optional[str]
        domain: Optional[str]
        mount_permissions: Optional[str]
        on_delete: Optional[Union[str, NfsDirectoryActionOnVolumeDeletion]]
        password: Optional[str]
        server: Optional[str]
        share: Optional[str]
        source: Optional[str]
        sub_dir: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_account_key: Optional[str] = ..., 
                azure_storage_account_name: Optional[str] = ..., 
                backing_storage_class_name: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                mount_permissions: Optional[str] = ..., 
                on_delete: Optional[Union[str, NfsDirectoryActionOnVolumeDeletion]] = ..., 
                password: Optional[str] = ..., 
                server: Optional[str] = ..., 
                share: Optional[str] = ..., 
                source: Optional[str] = ..., 
                sub_dir: Optional[str] = ..., 
                username: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.SystemData(Model):
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
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.mgmt.containerorchestratorruntime.models.VolumeBindingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMMEDIATE = "Immediate"
        WAIT_FOR_FIRST_CONSUMER = "WaitForFirstConsumer"


    class azure.mgmt.containerorchestratorruntime.models.VolumeExpansion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DISALLOW = "Disallow"


namespace azure.mgmt.containerorchestratorruntime.operations

    class azure.mgmt.containerorchestratorruntime.operations.BgpPeersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                resource: BgpPeer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BgpPeer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BgpPeer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BgpPeer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01', params_added_on={'2024-03-01': ['api_version', 'resource_uri', 'bgp_peer_name', 'accept']})
        def delete(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                bgp_peer_name: str, 
                **kwargs: Any
            ) -> BgpPeer: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[BgpPeer]: ...


    class azure.mgmt.containerorchestratorruntime.operations.LoadBalancersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                resource: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01', params_added_on={'2024-03-01': ['api_version', 'resource_uri', 'load_balancer_name', 'accept']})
        def delete(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[LoadBalancer]: ...


    class azure.mgmt.containerorchestratorruntime.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.containerorchestratorruntime.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                service_name: str, 
                resource: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                service_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                service_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[ServiceResource]: ...


    class azure.mgmt.containerorchestratorruntime.operations.StorageClassOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                resource: StorageClassResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                properties: StorageClassResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassResource]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassResource]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                storage_class_name: str, 
                **kwargs: Any
            ) -> StorageClassResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[StorageClassResource]: ...


```