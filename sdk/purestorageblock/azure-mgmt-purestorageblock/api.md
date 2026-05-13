```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.purestorageblock

    class azure.mgmt.purestorageblock.PureStorageBlockMgmtClient: implements ContextManager 
        avs_storage_container_volumes: AvsStorageContainerVolumesOperations
        avs_storage_containers: AvsStorageContainersOperations
        avs_vm_volumes: AvsVmVolumesOperations
        avs_vms: AvsVmsOperations
        operations: Operations
        reservations: ReservationsOperations
        storage_pools: StoragePoolsOperations

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


namespace azure.mgmt.purestorageblock.aio

    class azure.mgmt.purestorageblock.aio.PureStorageBlockMgmtClient: implements AsyncContextManager 
        avs_storage_container_volumes: AvsStorageContainerVolumesOperations
        avs_storage_containers: AvsStorageContainersOperations
        avs_vm_volumes: AvsVmVolumesOperations
        avs_vms: AvsVmsOperations
        operations: Operations
        reservations: ReservationsOperations
        storage_pools: StoragePoolsOperations

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


namespace azure.mgmt.purestorageblock.aio.operations

    class azure.mgmt.purestorageblock.aio.operations.AvsStorageContainerVolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                properties: AvsStorageContainerVolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsStorageContainerVolume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsStorageContainerVolume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsStorageContainerVolume]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> AvsStorageContainerVolume: ...

        @distributed_trace
        def list_by_avs_storage_container(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvsStorageContainerVolume]: ...


    class azure.mgmt.purestorageblock.aio.operations.AvsStorageContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AvsStorageContainer: ...

        @distributed_trace
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvsStorageContainer]: ...


    class azure.mgmt.purestorageblock.aio.operations.AvsVmVolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                properties: AvsVmVolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsVmVolume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsVmVolume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsVmVolume]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> AvsVmVolume: ...

        @distributed_trace
        def list_by_avs_vm(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvsVmVolume]: ...


    class azure.mgmt.purestorageblock.aio.operations.AvsVmsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                properties: AvsVmUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsVm]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsVm]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsVm]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                **kwargs: Any
            ) -> AvsVm: ...

        @distributed_trace
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvsVm]: ...


    class azure.mgmt.purestorageblock.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.purestorageblock.aio.operations.ReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                resource: Reservation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                properties: ReservationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> Reservation: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']})
        async def get_billing_report(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> ReservationBillingUsageReport: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']})
        async def get_billing_status(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> ReservationBillingStatus: ...

        @distributed_trace_async
        async def get_resource_limits(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> LimitDetails: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Reservation]: ...


    class azure.mgmt.purestorageblock.aio.operations.StoragePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                resource: StoragePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_disable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_enable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: StoragePoolEnableAvsConnectionPost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_enable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_enable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_finalize_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: StoragePoolFinalizeAvsConnectionPost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_finalize_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_finalize_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_repair_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: StoragePoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> StoragePool: ...

        @distributed_trace_async
        async def get_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AvsConnection: ...

        @distributed_trace_async
        async def get_avs_status(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AvsStatus: ...

        @distributed_trace_async
        async def get_health_status(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> StoragePoolHealthInfo: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StoragePool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StoragePool]: ...


namespace azure.mgmt.purestorageblock.models

    class azure.mgmt.purestorageblock.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.purestorageblock.models.Address(_Model):
        address_line1: str
        address_line2: Optional[str]
        city: str
        country: str
        postal_code: str
        state: str

        @overload
        def __init__(
                self, 
                *, 
                address_line1: str, 
                address_line2: Optional[str] = ..., 
                city: str, 
                country: str, 
                postal_code: str, 
                state: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.Alert(_Model):
        level: Union[str, AlertLevel]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                level: Union[str, AlertLevel], 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AlertLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        INFO = "info"
        WARNING = "warning"


    class azure.mgmt.purestorageblock.models.AvsConnection(_Model):
        service_initialization_completed: bool
        service_initialization_handle: Optional[ServiceInitializationHandle]
        service_initialization_handle_enc: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_initialization_completed: bool, 
                service_initialization_handle: Optional[ServiceInitializationHandle] = ..., 
                service_initialization_handle_enc: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsDiskDetails(_Model):
        avs_storage_container_resource_id: str
        avs_vm_internal_id: str
        avs_vm_name: str
        avs_vm_resource_id: str
        disk_id: str
        disk_name: str
        folder: str

        @overload
        def __init__(
                self, 
                *, 
                avs_storage_container_resource_id: str, 
                avs_vm_internal_id: str, 
                avs_vm_name: str, 
                avs_vm_resource_id: str, 
                disk_id: str, 
                disk_name: str, 
                folder: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsStatus(_Model):
        avs_enabled: bool
        cluster_resource_id: Optional[str]
        current_connection_status: str

        @overload
        def __init__(
                self, 
                *, 
                avs_enabled: bool, 
                cluster_resource_id: Optional[str] = ..., 
                current_connection_status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsStorageContainer(ProxyResource):
        id: str
        name: str
        properties: Optional[AvsStorageContainerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvsStorageContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsStorageContainerProperties(_Model):
        datastore: Optional[str]
        mounted: Optional[bool]
        provisioned_limit: Optional[int]
        resource_name: str
        space: Optional[Space]

        @overload
        def __init__(
                self, 
                *, 
                provisioned_limit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsStorageContainerVolume(ProxyResource):
        id: str
        name: str
        properties: Optional[VolumeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsStorageContainerVolumeUpdate(_Model):
        properties: Optional[AvsStorageContainerVolumeUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvsStorageContainerVolumeUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsStorageContainerVolumeUpdateProperties(_Model):
        soft_deletion: Optional[SoftDeletion]

        @overload
        def __init__(
                self, 
                *, 
                soft_deletion: Optional[SoftDeletion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVm(ProxyResource):
        id: str
        name: str
        properties: Optional[AvsVmProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvsVmProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmDetails(_Model):
        avs_vm_internal_id: str
        vm_id: str
        vm_name: str
        vm_type: Union[str, VmType]

        @overload
        def __init__(
                self, 
                *, 
                avs_vm_internal_id: str, 
                vm_id: str, 
                vm_name: str, 
                vm_type: Union[str, VmType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmProperties(_Model):
        avs: Optional[AvsVmDetails]
        created_timestamp: Optional[str]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        soft_deletion: Optional[SoftDeletion]
        space: Optional[Space]
        storage_pool_internal_id: Optional[str]
        storage_pool_resource_id: Optional[str]
        volume_container_type: Optional[Union[str, VolumeContainerType]]

        @overload
        def __init__(
                self, 
                *, 
                soft_deletion: Optional[SoftDeletion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmUpdate(_Model):
        properties: Optional[AvsVmUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvsVmUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmUpdateProperties(_Model):
        soft_deletion: Optional[SoftDeletion]

        @overload
        def __init__(
                self, 
                *, 
                soft_deletion: Optional[SoftDeletion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmVolume(ProxyResource):
        id: str
        name: str
        properties: Optional[VolumeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmVolumeUpdate(_Model):
        properties: Optional[AvsVmVolumeUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvsVmVolumeUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AvsVmVolumeUpdateProperties(_Model):
        soft_deletion: Optional[SoftDeletion]

        @overload
        def __init__(
                self, 
                *, 
                soft_deletion: Optional[SoftDeletion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.AzureVmwareService(_Model):
        avs_enabled: bool
        cluster_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                avs_enabled: bool, 
                cluster_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.BandwidthUsage(_Model):
        current: int
        max: int
        provisioned: int

        @overload
        def __init__(
                self, 
                *, 
                current: int, 
                max: int, 
                provisioned: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.BillingUsageProperty(_Model):
        current_value: str
        previous_value: Optional[str]
        property_id: str
        property_name: str
        severity: Union[str, UsageSeverity]
        status_message: Optional[str]
        sub_properties: Optional[List[BillingUsageProperty]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: str, 
                previous_value: Optional[str] = ..., 
                property_id: str, 
                property_name: str, 
                severity: Union[str, UsageSeverity], 
                status_message: Optional[str] = ..., 
                sub_properties: Optional[List[BillingUsageProperty]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.CompanyDetails(_Model):
        address: Optional[Address]
        company_name: str

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[Address] = ..., 
                company_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.purestorageblock.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.purestorageblock.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.purestorageblock.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.HealthDetails(_Model):
        bandwidth_usage: BandwidthUsage
        data_reduction_ratio: float
        estimated_max_capacity: int
        iops_usage: IopsUsage
        space: Space
        used_capacity_percentage: float

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_usage: BandwidthUsage, 
                data_reduction_ratio: float, 
                estimated_max_capacity: int, 
                iops_usage: IopsUsage, 
                space: Space, 
                used_capacity_percentage: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.IopsUsage(_Model):
        current: int
        max: int
        provisioned: int

        @overload
        def __init__(
                self, 
                *, 
                current: int, 
                max: int, 
                provisioned: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.LimitDetails(_Model):
        performance_policy: PerformancePolicyLimits
        protection_policy: ProtectionPolicyLimits
        storage_pool: StoragePoolLimits
        volume: VolumeLimits

        @overload
        def __init__(
                self, 
                *, 
                performance_policy: PerformancePolicyLimits, 
                protection_policy: ProtectionPolicyLimits, 
                storage_pool: StoragePoolLimits, 
                volume: VolumeLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.purestorageblock.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.purestorageblock.models.MarketplaceDetails(_Model):
        offer_details: OfferDetails
        subscription_id: Optional[str]
        subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                offer_details: OfferDetails, 
                subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.purestorageblock.models.OfferDetails(_Model):
        offer_id: str
        plan_id: str
        plan_name: Optional[str]
        publisher_id: str
        term_id: Optional[str]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: str, 
                plan_id: str, 
                plan_name: Optional[str] = ..., 
                publisher_id: str, 
                term_id: Optional[str] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.Operation(_Model):
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


    class azure.mgmt.purestorageblock.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.purestorageblock.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.purestorageblock.models.PerformancePolicyLimits(_Model):
        bandwidth_limit: RangeLimits
        iops_limit: RangeLimits

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_limit: RangeLimits, 
                iops_limit: RangeLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ProtectionPolicyLimits(_Model):
        frequency: RangeLimits
        retention: RangeLimits

        @overload
        def __init__(
                self, 
                *, 
                frequency: RangeLimits, 
                retention: RangeLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.purestorageblock.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.purestorageblock.models.RangeLimits(_Model):
        max: int
        min: int

        @overload
        def __init__(
                self, 
                *, 
                max: int, 
                min: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.Reservation(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ReservationPropertiesBaseResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ReservationPropertiesBaseResourceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationBillingStatus(_Model):
        drr_weighted_average: float
        extra_used_capacity_low_usage_rounding: int
        extra_used_capacity_non_reducible: int
        extra_used_capacity_non_reducible_plan_discount: int
        low_drr_pool_count: int
        timestamp: str
        total_non_reducible_reported: int
        total_performance_included_plan: int
        total_performance_overage: int
        total_performance_reported: int
        total_used_capacity_billed: int
        total_used_capacity_included_plan: int
        total_used_capacity_overage: int
        total_used_capacity_reported: int

        @overload
        def __init__(
                self, 
                *, 
                drr_weighted_average: float, 
                extra_used_capacity_low_usage_rounding: int, 
                extra_used_capacity_non_reducible: int, 
                extra_used_capacity_non_reducible_plan_discount: int, 
                low_drr_pool_count: int, 
                timestamp: str, 
                total_non_reducible_reported: int, 
                total_performance_included_plan: int, 
                total_performance_overage: int, 
                total_performance_reported: int, 
                total_used_capacity_billed: int, 
                total_used_capacity_included_plan: int, 
                total_used_capacity_overage: int, 
                total_used_capacity_reported: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationBillingUsageReport(_Model):
        billing_usage_properties: List[BillingUsageProperty]
        overall_status_message: str
        timestamp: str

        @overload
        def __init__(
                self, 
                *, 
                billing_usage_properties: List[BillingUsageProperty], 
                overall_status_message: str, 
                timestamp: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationPropertiesBaseResourceProperties(_Model):
        marketplace: MarketplaceDetails
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reservation_internal_id: Optional[str]
        user: UserDetails

        @overload
        def __init__(
                self, 
                *, 
                marketplace: MarketplaceDetails, 
                user: UserDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationUpdate(_Model):
        properties: Optional[ReservationUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReservationUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationUpdateProperties(_Model):
        user: Optional[UserDetails]

        @overload
        def __init__(
                self, 
                *, 
                user: Optional[UserDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.purestorageblock.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.purestorageblock.models.ServiceInitializationHandle(_Model):
        cluster_resource_id: Optional[str]
        service_account_username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: Optional[str] = ..., 
                service_account_username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ServiceInitializationInfo(_Model):
        service_account_password: Optional[str]
        service_account_username: Optional[str]
        v_sphere_certificate: Optional[str]
        v_sphere_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_password: Optional[str] = ..., 
                service_account_username: Optional[str] = ..., 
                v_sphere_certificate: Optional[str] = ..., 
                v_sphere_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.SoftDeletion(_Model):
        destroyed: bool
        eradication_timestamp: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destroyed: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.Space(_Model):
        shared: int
        snapshots: int
        total_used: int
        unique: int

        @overload
        def __init__(
                self, 
                *, 
                shared: int, 
                snapshots: int, 
                total_used: int, 
                unique: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePool(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[StoragePoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[StoragePoolProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolEnableAvsConnectionPost(_Model):
        cluster_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolFinalizeAvsConnectionPost(_Model):
        service_initialization_data: Optional[ServiceInitializationInfo]
        service_initialization_data_enc: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_initialization_data: Optional[ServiceInitializationInfo] = ..., 
                service_initialization_data_enc: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolHealthInfo(_Model):
        alerts: List[Alert]
        health: HealthDetails

        @overload
        def __init__(
                self, 
                *, 
                alerts: List[Alert], 
                health: HealthDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolLimits(_Model):
        physical_availability_zones: List[str]
        provisioned_bandwidth_mb_per_sec: RangeLimits
        provisioned_iops: RangeLimits

        @overload
        def __init__(
                self, 
                *, 
                physical_availability_zones: List[str], 
                provisioned_bandwidth_mb_per_sec: RangeLimits, 
                provisioned_iops: RangeLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolProperties(_Model):
        availability_zone: str
        avs: Optional[AzureVmwareService]
        data_retention_period: Optional[int]
        provisioned_bandwidth_mb_per_sec: int
        provisioned_iops: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reservation_resource_id: str
        storage_pool_internal_id: Optional[str]
        vnet_injection: VnetInjection

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: str, 
                provisioned_bandwidth_mb_per_sec: int, 
                reservation_resource_id: str, 
                vnet_injection: VnetInjection
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[StoragePoolUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[StoragePoolUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolUpdateProperties(_Model):
        provisioned_bandwidth_mb_per_sec: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                provisioned_bandwidth_mb_per_sec: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.SystemData(_Model):
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


    class azure.mgmt.purestorageblock.models.TrackedResource(Resource):
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


    class azure.mgmt.purestorageblock.models.UsageSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "alert"
        INFORMATION = "information"
        NONE = "none"
        WARNING = "warning"


    class azure.mgmt.purestorageblock.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.purestorageblock.models.UserDetails(_Model):
        company_details: Optional[CompanyDetails]
        email_address: str
        first_name: str
        last_name: str
        phone_number: Optional[str]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                company_details: Optional[CompanyDetails] = ..., 
                email_address: str, 
                first_name: str, 
                last_name: str, 
                phone_number: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VmType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V_VOL = "vvol"


    class azure.mgmt.purestorageblock.models.VnetInjection(_Model):
        subnet_id: str
        vnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: str, 
                vnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS = "avs"


    class azure.mgmt.purestorageblock.models.VolumeLimits(_Model):
        provisioned_size: RangeLimits

        @overload
        def __init__(
                self, 
                *, 
                provisioned_size: RangeLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeProperties(_Model):
        avs: Optional[AvsDiskDetails]
        created_timestamp: Optional[str]
        display_name: Optional[str]
        provisioned_size: Optional[int]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        soft_deletion: SoftDeletion
        space: Optional[Space]
        storage_pool_internal_id: Optional[str]
        storage_pool_resource_id: Optional[str]
        volume_internal_id: Optional[str]
        volume_type: Optional[Union[str, VolumeType]]

        @overload
        def __init__(
                self, 
                *, 
                soft_deletion: SoftDeletion
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS = "avs"


namespace azure.mgmt.purestorageblock.operations

    class azure.mgmt.purestorageblock.operations.AvsStorageContainerVolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                properties: AvsStorageContainerVolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsStorageContainerVolume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsStorageContainerVolume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsStorageContainerVolume]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> AvsStorageContainerVolume: ...

        @distributed_trace
        def list_by_avs_storage_container(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvsStorageContainerVolume]: ...


    class azure.mgmt.purestorageblock.operations.AvsStorageContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AvsStorageContainer: ...

        @distributed_trace
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvsStorageContainer]: ...


    class azure.mgmt.purestorageblock.operations.AvsVmVolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                properties: AvsVmVolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsVmVolume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsVmVolume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsVmVolume]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                volume_id: str, 
                **kwargs: Any
            ) -> AvsVmVolume: ...

        @distributed_trace
        def list_by_avs_vm(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                **kwargs: Any
            ) -> ItemPaged[AvsVmVolume]: ...


    class azure.mgmt.purestorageblock.operations.AvsVmsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                properties: AvsVmUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsVm]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsVm]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsVm]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                avs_vm_id: str, 
                **kwargs: Any
            ) -> AvsVm: ...

        @distributed_trace
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvsVm]: ...


    class azure.mgmt.purestorageblock.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.purestorageblock.operations.ReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                resource: Reservation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                properties: ReservationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> Reservation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']})
        def get_billing_report(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> ReservationBillingUsageReport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']})
        def get_billing_status(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> ReservationBillingStatus: ...

        @distributed_trace
        def get_resource_limits(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> LimitDetails: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Reservation]: ...


    class azure.mgmt.purestorageblock.operations.StoragePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                resource: StoragePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_disable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_enable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: StoragePoolEnableAvsConnectionPost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_enable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_enable_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_finalize_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: StoragePoolFinalizeAvsConnectionPost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_finalize_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_finalize_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_repair_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: StoragePoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> StoragePool: ...

        @distributed_trace
        def get_avs_connection(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AvsConnection: ...

        @distributed_trace
        def get_avs_status(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AvsStatus: ...

        @distributed_trace
        def get_health_status(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> StoragePoolHealthInfo: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StoragePool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StoragePool]: ...


```