```py
namespace azure.mgmt.purestorageblock

    class azure.mgmt.purestorageblock.PureStorageBlockMgmtClient: implements ContextManager 
        avs_storage_container_volumes: AvsStorageContainerVolumesOperations
        avs_storage_containers: AvsStorageContainersOperations
        avs_vm_volumes: AvsVmVolumesOperations
        avs_vms: AvsVmsOperations
        operations: Operations
        recoverable_volume_groups: RecoverableVolumeGroupsOperations
        reservations: ReservationsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        storage_pools: StoragePoolsOperations
        volume_group_snapshots: VolumeGroupSnapshotsOperations
        volume_groups: VolumeGroupsOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.purestorageblock.aio

    class azure.mgmt.purestorageblock.aio.PureStorageBlockMgmtClient: implements AsyncContextManager 
        avs_storage_container_volumes: AvsStorageContainerVolumesOperations
        avs_storage_containers: AvsStorageContainersOperations
        avs_vm_volumes: AvsVmVolumesOperations
        avs_vms: AvsVmsOperations
        operations: Operations
        recoverable_volume_groups: RecoverableVolumeGroupsOperations
        reservations: ReservationsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        storage_pools: StoragePoolsOperations
        volume_group_snapshots: VolumeGroupSnapshotsOperations
        volume_groups: VolumeGroupsOperations
        volumes: VolumesOperations

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


    class azure.mgmt.purestorageblock.aio.operations.RecoverableVolumeGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'recoverable_volume_group_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                recoverable_volume_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'recoverable_volume_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                recoverable_volume_group_name: str, 
                **kwargs: Any
            ) -> RecoverableVolumeGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoverableVolumeGroup]: ...


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
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                body: LinkSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                body: LinkSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Reservation]: ...

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
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']}, api_versions_list=['2024-11-01-preview', '2024-11-01', '2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def get_billing_report(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> ReservationBillingUsageReport: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']}, api_versions_list=['2024-11-01-preview', '2024-11-01', '2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
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

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-05-01-preview'])
        async def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Reservation]: ...


    class azure.mgmt.purestorageblock.aio.operations.SaaSOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: ActivateSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: ActivateSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...


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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StoragePool]: ...

        @overload
        async def configure_platform_console_auth(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                config: PlatformConsoleAuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlatformConsoleAuthResult: ...

        @overload
        async def configure_platform_console_auth(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                config: PlatformConsoleAuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlatformConsoleAuthResult: ...

        @overload
        async def configure_platform_console_auth(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                config: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlatformConsoleAuthResult: ...

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

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def list_platform_console_activation_code(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> PlatformConsoleActivationCode: ...


    class azure.mgmt.purestorageblock.aio.operations.VolumeGroupSnapshotsOperations:

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
                volume_group_name: str, 
                snapshot_name: str, 
                resource: VolumeGroupSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroupSnapshot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                resource: VolumeGroupSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroupSnapshot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroupSnapshot]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'snapshot_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'snapshot_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> VolumeGroupSnapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'filter', 'orderby', 'top', 'skip', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VolumeGroupSnapshot]: ...

        @overload
        async def list_snapshots(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupSnapshotListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VolumeGroupSnapshotPostListResult: ...

        @overload
        async def list_snapshots(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupSnapshotListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VolumeGroupSnapshotPostListResult: ...

        @overload
        async def list_snapshots(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VolumeGroupSnapshotPostListResult: ...


    class azure.mgmt.purestorageblock.aio.operations.VolumeGroupsOperations:

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
                volume_group_name: str, 
                resource: VolumeGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                resource: VolumeGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                body: VolumeGroupOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                body: VolumeGroupOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroup: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def get_status(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroupStatus: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VolumeGroup]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def list_connection_parameters(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> ConnectionParametersResponse: ...


    class azure.mgmt.purestorageblock.aio.operations.VolumesOperations:

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
                volume_group_name: str, 
                volume_name: str, 
                resource: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                resource: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'volume_name']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                body: VolumeOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                body: VolumeOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                properties: VolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                properties: VolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'volume_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Volume]: ...


namespace azure.mgmt.purestorageblock.models

    class azure.mgmt.purestorageblock.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.purestorageblock.models.ActivateSaaSRequest(_Model):
        publisher_id: Optional[str]
        saas_guid: str

        @overload
        def __init__(
                self, 
                *, 
                publisher_id: Optional[str] = ..., 
                saas_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.purestorageblock.models.AzureVolumeProperties(_Model):
        created_at: Optional[datetime]
        provisioned_size: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serial_number: Optional[str]
        soft_deletion: Optional[DestroyedStateProperties]
        source_recoverable_volume_resource_id: Optional[str]
        source_serial_number: Optional[str]
        source_type: Optional[Union[str, VolumeSourceType]]
        source_volume_group_resource_id: Optional[str]
        source_volume_resource_id: Optional[str]
        source_volume_snapshot: Optional[VolumeSnapshotSource]
        space: Optional[Space]

        @overload
        def __init__(
                self, 
                *, 
                provisioned_size: Optional[int] = ..., 
                source_recoverable_volume_resource_id: Optional[str] = ..., 
                source_serial_number: Optional[str] = ..., 
                source_type: Optional[Union[str, VolumeSourceType]] = ..., 
                source_volume_group_resource_id: Optional[str] = ..., 
                source_volume_resource_id: Optional[str] = ..., 
                source_volume_snapshot: Optional[VolumeSnapshotSource] = ...
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
        sub_properties: Optional[list[BillingUsageProperty]]

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
                sub_properties: Optional[list[BillingUsageProperty]] = ...
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


    class azure.mgmt.purestorageblock.models.ConnectionParametersResponse(_Model):
        iscsi: IscsiConnectionParameters

        @overload
        def __init__(
                self, 
                *, 
                iscsi: IscsiConnectionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.purestorageblock.models.DestroyedStateProperties(_Model):
        destroyed: bool
        destroyed_at: Optional[datetime]
        eradication_timestamp: Optional[datetime]
        previous_name: Optional[str]


    class azure.mgmt.purestorageblock.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.purestorageblock.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
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


    class azure.mgmt.purestorageblock.models.IscsiConnectionParameters(_Model):
        endpoints: list[IscsiEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: list[IscsiEndpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.IscsiEndpoint(_Model):
        ip: str
        iqn: str
        port: int

        @overload
        def __init__(
                self, 
                *, 
                ip: str, 
                iqn: str, 
                port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.LatestLinkedSaaSResponse(_Model):
        is_hidden_saa_s: Optional[bool]
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_hidden_saa_s: Optional[bool] = ..., 
                saa_s_resource_id: Optional[str] = ...
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


    class azure.mgmt.purestorageblock.models.LinkSaaSRequest(_Model):
        saa_s_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.purestorageblock.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.purestorageblock.models.MarketplaceDetails(_Model):
        offer_details: Optional[OfferDetails]
        saa_s_resource_id: Optional[str]
        subscription_id: Optional[str]
        subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                offer_details: Optional[OfferDetails] = ..., 
                saa_s_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.purestorageblock.models.PerformanceParameters(_Model):
        bandwidth_limit_mb_per_sec: Optional[int]
        iops_limit: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_limit_mb_per_sec: Optional[int] = ..., 
                iops_limit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.purestorageblock.models.PlatformConsoleAccessSettings(_Model):
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.PlatformConsoleActivationCode(_Model):
        activation_code: str
        expires_at: datetime
        username: str

        @overload
        def __init__(
                self, 
                *, 
                activation_code: str, 
                expires_at: datetime, 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.PlatformConsoleAuthConfig(_Model):
        auth_type: str

        @overload
        def __init__(
                self, 
                *, 
                auth_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.PlatformConsoleAuthResult(_Model):
        auth_type: str

        @overload
        def __init__(
                self, 
                *, 
                auth_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.PlatformConsoleAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SSH = "ssh"


    class azure.mgmt.purestorageblock.models.PlatformConsoleRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY_ADMIN = "array_admin"
        READ_ONLY = "read_only"
        STORAGE_ADMIN = "storage_admin"


    class azure.mgmt.purestorageblock.models.PlatformConsoleSettings(_Model):
        api: Optional[PlatformConsoleAccessSettings]
        cli: Optional[PlatformConsoleAccessSettings]
        default_username: Optional[str]
        enabled: Optional[bool]
        gui: Optional[PlatformConsoleAccessSettings]
        subnets: Optional[list[PlatformConsoleSubnet]]

        @overload
        def __init__(
                self, 
                *, 
                api: Optional[PlatformConsoleAccessSettings] = ..., 
                cli: Optional[PlatformConsoleAccessSettings] = ..., 
                enabled: Optional[bool] = ..., 
                gui: Optional[PlatformConsoleAccessSettings] = ..., 
                subnets: Optional[list[PlatformConsoleSubnet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.PlatformConsoleSubnet(_Model):
        id: str
        management_ip_address: Optional[str]
        service_backend_ips: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ProtectionParameters(_Model):
        frequency: Optional[timedelta]
        retention: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                frequency: Optional[timedelta] = ..., 
                retention: Optional[timedelta] = ...
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


    class azure.mgmt.purestorageblock.models.RecoverableVolumeGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[RecoverableVolumeGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecoverableVolumeGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.RecoverableVolumeGroupProperties(_Model):
        created_at: Optional[datetime]
        performance_parameters: Optional[PerformanceParameters]
        protection_parameters: Optional[ProtectionParameters]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        soft_deletion: Optional[DestroyedStateProperties]
        space: Optional[Space]


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
                tags: Optional[dict[str, str]] = ...
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
        billing_usage_properties: list[BillingUsageProperty]
        overall_status_message: str
        timestamp: str

        @overload
        def __init__(
                self, 
                *, 
                billing_usage_properties: list[BillingUsageProperty], 
                overall_status_message: str, 
                timestamp: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationPropertiesBaseResourceProperties(_Model):
        marketplace: MarketplaceDetails
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reservation_internal_id: Optional[str]
        user: Optional[UserDetails]

        @overload
        def __init__(
                self, 
                *, 
                marketplace: MarketplaceDetails, 
                user: Optional[UserDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.ReservationUpdate(_Model):
        properties: Optional[ReservationUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReservationUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
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


    class azure.mgmt.purestorageblock.models.SaaSResourceDetailsResponse(ProxyResource):
        id: str
        name: str
        saas_id: Optional[str]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                saas_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.purestorageblock.models.SshPlatformConsoleAuthConfig(PlatformConsoleAuthConfig, discriminator='ssh'):
        auth_type: Literal[PlatformConsoleAuthType.SSH]
        public_key: str
        role: Union[str, PlatformConsoleRole]
        username: str

        @overload
        def __init__(
                self, 
                *, 
                public_key: str, 
                role: Union[str, PlatformConsoleRole], 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.SshPlatformConsoleAuthResult(PlatformConsoleAuthResult, discriminator='ssh'):
        auth_type: Literal[PlatformConsoleAuthType.SSH]
        role: Union[str, PlatformConsoleRole]
        username: str

        @overload
        def __init__(
                self, 
                *, 
                role: Union[str, PlatformConsoleRole], 
                username: str
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
                tags: Optional[dict[str, str]] = ...
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
        alerts: list[Alert]
        health: HealthDetails

        @overload
        def __init__(
                self, 
                *, 
                alerts: list[Alert], 
                health: HealthDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolLimits(_Model):
        physical_availability_zones: list[str]
        provisioned_bandwidth_mb_per_sec: RangeLimits
        provisioned_iops: RangeLimits

        @overload
        def __init__(
                self, 
                *, 
                physical_availability_zones: list[str], 
                provisioned_bandwidth_mb_per_sec: RangeLimits, 
                provisioned_iops: RangeLimits
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolProperties(_Model):
        availability_zone: str
        avs: Optional[AzureVmwareService]
        data_retention_period: Optional[int]
        platform_console_settings: Optional[PlatformConsoleSettings]
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
                platform_console_settings: Optional[PlatformConsoleSettings] = ..., 
                provisioned_bandwidth_mb_per_sec: int, 
                reservation_resource_id: str, 
                vnet_injection: VnetInjection
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[StoragePoolUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[StoragePoolUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.StoragePoolUpdateProperties(_Model):
        platform_console_settings: Optional[PlatformConsoleSettings]
        provisioned_bandwidth_mb_per_sec: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                platform_console_settings: Optional[PlatformConsoleSettings] = ..., 
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


    class azure.mgmt.purestorageblock.models.Volume(ProxyResource):
        id: str
        name: str
        properties: Optional[AzureVolumeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureVolumeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS = "avs"


    class azure.mgmt.purestorageblock.models.VolumeGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[VolumeGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[VolumeGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupOverwriteRequest(_Model):
        source_snapshot_resource_id: str
        source_volume_group_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                source_snapshot_resource_id: str, 
                source_volume_group_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupProperties(_Model):
        performance_parameters: Optional[PerformanceParameters]
        protection_parameters: Optional[ProtectionParameters]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_recoverable_volume_group_resource_id: Optional[str]
        source_snapshot_resource_id: Optional[str]
        source_type: Optional[Union[str, VolumeGroupSourceType]]
        source_volume_group_resource_id: Optional[str]
        storage_pool_internal_id: Optional[str]
        volume_group_internal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                performance_parameters: Optional[PerformanceParameters] = ..., 
                protection_parameters: Optional[ProtectionParameters] = ..., 
                source_recoverable_volume_group_resource_id: Optional[str] = ..., 
                source_snapshot_resource_id: Optional[str] = ..., 
                source_type: Optional[Union[str, VolumeGroupSourceType]] = ..., 
                source_volume_group_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupSnapshot(ProxyResource):
        id: str
        name: str
        properties: Optional[VolumeGroupSnapshotProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeGroupSnapshotProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupSnapshotListRequest(_Model):
        filter: Optional[str]
        orderby: Optional[str]
        skip: Optional[int]
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupSnapshotPostListResult(_Model):
        count: Optional[int]
        total_count: Optional[int]
        value: list[VolumeGroupSnapshot]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                total_count: Optional[int] = ..., 
                value: list[VolumeGroupSnapshot]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupSnapshotProperties(_Model):
        created_at: Optional[datetime]
        created_by_policy: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        soft_deletion: Optional[DestroyedStateProperties]
        source_snapshot_resource_id: Optional[str]
        space: Optional[Space]
        volume_snapshots: Optional[list[VolumeSnapshotInfo]]

        @overload
        def __init__(
                self, 
                *, 
                source_snapshot_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        RECOVERABLE_VOLUME_GROUP = "recoverableVolumeGroup"
        SNAPSHOT = "snapshot"
        VOLUME_GROUP = "volumeGroup"


    class azure.mgmt.purestorageblock.models.VolumeGroupStatus(_Model):
        connected_host_count: int
        space: Space

        @overload
        def __init__(
                self, 
                *, 
                connected_host_count: int, 
                space: Space
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupUpdate(_Model):
        properties: Optional[VolumeGroupUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeGroupUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeGroupUpdateProperties(_Model):
        performance_parameters: Optional[PerformanceParameters]
        protection_parameters: Optional[ProtectionParameters]

        @overload
        def __init__(
                self, 
                *, 
                performance_parameters: Optional[PerformanceParameters] = ..., 
                protection_parameters: Optional[ProtectionParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.purestorageblock.models.VolumeOverwriteRequest(_Model):
        source_serial_number: Optional[str]
        source_type: Union[str, VolumeSourceType]
        source_volume_group_resource_id: Optional[str]
        source_volume_resource_id: Optional[str]
        source_volume_snapshot: Optional[VolumeSnapshotSource]

        @overload
        def __init__(
                self, 
                *, 
                source_serial_number: Optional[str] = ..., 
                source_type: Union[str, VolumeSourceType], 
                source_volume_group_resource_id: Optional[str] = ..., 
                source_volume_resource_id: Optional[str] = ..., 
                source_volume_snapshot: Optional[VolumeSnapshotSource] = ...
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


    class azure.mgmt.purestorageblock.models.VolumeSnapshotInfo(_Model):
        name: str
        provisioned_size: Optional[int]
        serial_number: Optional[str]
        space: Optional[Space]


    class azure.mgmt.purestorageblock.models.VolumeSnapshotSource(_Model):
        volume_group_snapshot_resource_id: str
        volume_snapshot_name: str

        @overload
        def __init__(
                self, 
                *, 
                volume_group_snapshot_resource_id: str, 
                volume_snapshot_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        RECOVERABLE_VOLUME = "recoverableVolume"
        SERIAL_NUMBER = "serialNumber"
        SNAPSHOT = "snapshot"
        VOLUME = "volume"


    class azure.mgmt.purestorageblock.models.VolumeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS = "avs"


    class azure.mgmt.purestorageblock.models.VolumeUpdate(_Model):
        properties: Optional[VolumeUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purestorageblock.models.VolumeUpdateProperties(_Model):
        provisioned_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                provisioned_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.purestorageblock.operations.RecoverableVolumeGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'recoverable_volume_group_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                recoverable_volume_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'recoverable_volume_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                recoverable_volume_group_name: str, 
                **kwargs: Any
            ) -> RecoverableVolumeGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoverableVolumeGroup]: ...


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
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                body: LinkSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                body: LinkSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Reservation]: ...

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
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']}, api_versions_list=['2024-11-01-preview', '2024-11-01', '2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def get_billing_report(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> ReservationBillingUsageReport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-01-preview', params_added_on={'2024-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']}, api_versions_list=['2024-11-01-preview', '2024-11-01', '2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
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
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'reservation_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-05-01-preview'])
        def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                reservation_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Reservation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Reservation]: ...


    class azure.mgmt.purestorageblock.operations.SaaSOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_activate_resource(
                self, 
                body: ActivateSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_activate_resource(
                self, 
                body: ActivateSaaSRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...


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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StoragePool]: ...

        @overload
        def configure_platform_console_auth(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                config: PlatformConsoleAuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlatformConsoleAuthResult: ...

        @overload
        def configure_platform_console_auth(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                config: PlatformConsoleAuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlatformConsoleAuthResult: ...

        @overload
        def configure_platform_console_auth(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                config: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlatformConsoleAuthResult: ...

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

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_platform_console_activation_code(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> PlatformConsoleActivationCode: ...


    class azure.mgmt.purestorageblock.operations.VolumeGroupSnapshotsOperations:

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
                volume_group_name: str, 
                snapshot_name: str, 
                resource: VolumeGroupSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroupSnapshot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                resource: VolumeGroupSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroupSnapshot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroupSnapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'snapshot_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'snapshot_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> VolumeGroupSnapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'filter', 'orderby', 'top', 'skip', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VolumeGroupSnapshot]: ...

        @overload
        def list_snapshots(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupSnapshotListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VolumeGroupSnapshotPostListResult: ...

        @overload
        def list_snapshots(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupSnapshotListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VolumeGroupSnapshotPostListResult: ...

        @overload
        def list_snapshots(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VolumeGroupSnapshotPostListResult: ...


    class azure.mgmt.purestorageblock.operations.VolumeGroupsOperations:

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
                volume_group_name: str, 
                resource: VolumeGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                resource: VolumeGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                body: VolumeGroupOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                body: VolumeGroupOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: VolumeGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def get_status(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroupStatus: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def list_by_storage_pool(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VolumeGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def list_connection_parameters(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> ConnectionParametersResponse: ...


    class azure.mgmt.purestorageblock.operations.VolumesOperations:

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
                volume_group_name: str, 
                volume_name: str, 
                resource: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                resource: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'volume_name']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                body: VolumeOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                body: VolumeOverwriteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_overwrite(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                properties: VolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                properties: VolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'volume_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'storage_pool_name', 'volume_group_name', 'accept']}, api_versions_list=['2026-01-01-preview', '2026-03-01-preview', '2026-05-01-preview'])
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                storage_pool_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Volume]: ...


namespace azure.mgmt.purestorageblock.types

    class azure.mgmt.purestorageblock.types.ActivateSaaSRequest(TypedDict, total=False):
        key "publisherId": str
        key "saasGuid": Required[str]
        publisher_id: str
        saas_guid: str


    class azure.mgmt.purestorageblock.types.Address(TypedDict, total=False):
        key "addressLine1": Required[str]
        key "addressLine2": str
        key "city": Required[str]
        key "country": Required[str]
        key "postalCode": Required[str]
        key "state": Required[str]
        address_line1: str
        address_line2: str
        city: str
        country: str
        postal_code: str
        state: str


    class azure.mgmt.purestorageblock.types.AvsStorageContainerVolumeUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AvsStorageContainerVolumeUpdateProperties', module='types')
        properties: AvsStorageContainerVolumeUpdateProperties


    class azure.mgmt.purestorageblock.types.AvsStorageContainerVolumeUpdateProperties(TypedDict, total=False):
        key "softDeletion": ForwardRef('SoftDeletion', module='types')
        soft_deletion: SoftDeletion


    class azure.mgmt.purestorageblock.types.AvsVmUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AvsVmUpdateProperties', module='types')
        properties: AvsVmUpdateProperties


    class azure.mgmt.purestorageblock.types.AvsVmUpdateProperties(TypedDict, total=False):
        key "softDeletion": ForwardRef('SoftDeletion', module='types')
        soft_deletion: SoftDeletion


    class azure.mgmt.purestorageblock.types.AvsVmVolumeUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AvsVmVolumeUpdateProperties', module='types')
        properties: AvsVmVolumeUpdateProperties


    class azure.mgmt.purestorageblock.types.AvsVmVolumeUpdateProperties(TypedDict, total=False):
        key "softDeletion": ForwardRef('SoftDeletion', module='types')
        soft_deletion: SoftDeletion


    class azure.mgmt.purestorageblock.types.AzureVmwareService(TypedDict, total=False):
        key "avsEnabled": Required[bool]
        key "sddcResourceId": str
        avs_enabled: bool
        cluster_resource_id: str


    class azure.mgmt.purestorageblock.types.AzureVolumeProperties(TypedDict, total=False):
        key "createdAt": str
        key "provisionedSize": int
        key "provisioningState": Union[str, ProvisioningState]
        key "serialNumber": str
        key "softDeletion": ForwardRef('DestroyedStateProperties', module='types')
        key "sourceRecoverableVolumeResourceId": str
        key "sourceSerialNumber": str
        key "sourceType": Union[str, VolumeSourceType]
        key "sourceVolumeGroupResourceId": str
        key "sourceVolumeResourceId": str
        key "sourceVolumeSnapshot": ForwardRef('VolumeSnapshotSource', module='types')
        key "space": ForwardRef('Space', module='types')
        created_at: str
        provisioned_size: int
        provisioning_state: Union[str, ProvisioningState]
        serial_number: str
        soft_deletion: DestroyedStateProperties
        source_recoverable_volume_resource_id: str
        source_serial_number: str
        source_type: Union[str, VolumeSourceType]
        source_volume_group_resource_id: str
        source_volume_resource_id: str
        source_volume_snapshot: VolumeSnapshotSource
        space: Space


    class azure.mgmt.purestorageblock.types.CompanyDetails(TypedDict, total=False):
        key "address": ForwardRef('Address', module='types')
        key "companyName": Required[str]
        address: Address
        company_name: str


    class azure.mgmt.purestorageblock.types.DestroyedStateProperties(TypedDict, total=False):
        key "destroyed": Required[bool]
        key "destroyedAt": str
        key "eradicationTimestamp": str
        key "previousName": str
        destroyed: bool
        destroyed_at: str
        eradication_timestamp: str
        previous_name: str


    class azure.mgmt.purestorageblock.types.LinkSaaSRequest(TypedDict, total=False):
        key "saaSResourceId": Required[str]
        saa_s_resource_id: str


    class azure.mgmt.purestorageblock.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.purestorageblock.types.MarketplaceDetails(TypedDict, total=False):
        key "offerDetails": ForwardRef('OfferDetails', module='types')
        key "saaSResourceId": str
        key "subscriptionId": str
        key "subscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        offer_details: OfferDetails
        saa_s_resource_id: str
        subscription_id: str
        subscription_status: Union[str, MarketplaceSubscriptionStatus]


    class azure.mgmt.purestorageblock.types.OfferDetails(TypedDict, total=False):
        key "offerId": Required[str]
        key "planId": Required[str]
        key "planName": str
        key "publisherId": Required[str]
        key "termId": str
        key "termUnit": str
        offer_id: str
        plan_id: str
        plan_name: str
        publisher_id: str
        term_id: str
        term_unit: str


    class azure.mgmt.purestorageblock.types.PerformanceParameters(TypedDict, total=False):
        key "bandwidthLimitMbPerSec": int
        key "iopsLimit": int
        bandwidth_limit_mb_per_sec: int
        iops_limit: int


    class azure.mgmt.purestorageblock.types.PlatformConsoleAccessSettings(TypedDict, total=False):
        key "enabled": Required[bool]
        enabled: bool


    class azure.mgmt.purestorageblock.types.PlatformConsoleAuthConfig(TypedDict, total=False):
        key "authType": Required[Literal[PlatformConsoleAuthType.SSH]]
        key "publicKey": Required[str]
        key "role": Required[Union[str, PlatformConsoleRole]]
        key "username": Required[str]
        auth_type: Literal[PlatformConsoleAuthType.SSH]
        public_key: str
        role: Union[str, PlatformConsoleRole]
        username: str


    class azure.mgmt.purestorageblock.types.PlatformConsoleAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SSH = "ssh"


    class azure.mgmt.purestorageblock.types.PlatformConsoleSettings(TypedDict, total=False):
        key "api": ForwardRef('PlatformConsoleAccessSettings', module='types')
        key "cli": ForwardRef('PlatformConsoleAccessSettings', module='types')
        key "defaultUsername": str
        key "enabled": bool
        key "gui": ForwardRef('PlatformConsoleAccessSettings', module='types')
        api: PlatformConsoleAccessSettings
        cli: PlatformConsoleAccessSettings
        default_username: str
        enabled: bool
        gui: PlatformConsoleAccessSettings
        subnets: list[PlatformConsoleSubnet]


    class azure.mgmt.purestorageblock.types.PlatformConsoleSubnet(TypedDict, total=False):
        key "id": Required[str]
        key "managementIpAddress": str
        id: str
        management_ip_address: str
        serviceBackendIps: list[str]
        service_backend_ips: list[str]


    class azure.mgmt.purestorageblock.types.ProtectionParameters(TypedDict, total=False):
        key "frequency": str
        key "retention": str
        frequency: str
        retention: str


    class azure.mgmt.purestorageblock.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.purestorageblock.types.Reservation(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ReservationPropertiesBaseResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ReservationPropertiesBaseResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.purestorageblock.types.ReservationPropertiesBaseResourceProperties(TypedDict, total=False):
        key "marketplace": Required[MarketplaceDetails]
        key "provisioningState": Union[str, ProvisioningState]
        key "reservationInternalId": str
        key "user": ForwardRef('UserDetails', module='types')
        marketplace: MarketplaceDetails
        provisioning_state: Union[str, ProvisioningState]
        reservation_internal_id: str
        user: UserDetails


    class azure.mgmt.purestorageblock.types.ReservationUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ReservationUpdateProperties', module='types')
        properties: ReservationUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.purestorageblock.types.ReservationUpdateProperties(TypedDict, total=False):
        key "user": ForwardRef('UserDetails', module='types')
        user: UserDetails


    class azure.mgmt.purestorageblock.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.purestorageblock.types.ServiceInitializationInfo(TypedDict, total=False):
        key "serviceAccountPassword": str
        key "serviceAccountUsername": str
        key "vSphereCertificate": str
        key "vSphereIp": str
        service_account_password: str
        service_account_username: str
        v_sphere_certificate: str
        v_sphere_ip: str


    class azure.mgmt.purestorageblock.types.SoftDeletion(TypedDict, total=False):
        key "destroyed": Required[bool]
        key "eradicationTimestamp": str
        destroyed: bool
        eradication_timestamp: str


    class azure.mgmt.purestorageblock.types.Space(TypedDict, total=False):
        key "shared": Required[int]
        key "snapshots": Required[int]
        key "totalUsed": Required[int]
        key "unique": Required[int]
        shared: int
        snapshots: int
        total_used: int
        unique: int


    class azure.mgmt.purestorageblock.types.SshPlatformConsoleAuthConfig(TypedDict, total=False):
        key "authType": Required[Literal[PlatformConsoleAuthType.SSH]]
        key "publicKey": Required[str]
        key "role": Required[Union[str, PlatformConsoleRole]]
        key "username": Required[str]
        auth_type: Literal[PlatformConsoleAuthType.SSH]
        public_key: str
        role: Union[str, PlatformConsoleRole]
        username: str


    class azure.mgmt.purestorageblock.types.StoragePool(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StoragePoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: StoragePoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.purestorageblock.types.StoragePoolEnableAvsConnectionPost(TypedDict, total=False):
        key "sddcResourceId": Required[str]
        cluster_resource_id: str


    class azure.mgmt.purestorageblock.types.StoragePoolFinalizeAvsConnectionPost(TypedDict, total=False):
        key "serviceInitializationData": ForwardRef('ServiceInitializationInfo', module='types')
        key "serviceInitializationDataEnc": str
        service_initialization_data: ServiceInitializationInfo
        service_initialization_data_enc: str


    class azure.mgmt.purestorageblock.types.StoragePoolProperties(TypedDict, total=False):
        key "availabilityZone": Required[str]
        key "avs": ForwardRef('AzureVmwareService', module='types')
        key "dataRetentionPeriod": int
        key "platformConsoleSettings": ForwardRef('PlatformConsoleSettings', module='types')
        key "provisionedBandwidthMbPerSec": Required[int]
        key "provisionedIops": int
        key "provisioningState": Union[str, ProvisioningState]
        key "reservationResourceId": Required[str]
        key "storagePoolInternalId": str
        key "vnetInjection": Required[VnetInjection]
        availability_zone: str
        avs: AzureVmwareService
        data_retention_period: int
        platform_console_settings: PlatformConsoleSettings
        provisioned_bandwidth_mb_per_sec: int
        provisioned_iops: int
        provisioning_state: Union[str, ProvisioningState]
        reservation_resource_id: str
        storage_pool_internal_id: str
        vnet_injection: VnetInjection


    class azure.mgmt.purestorageblock.types.StoragePoolUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('StoragePoolUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: StoragePoolUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.purestorageblock.types.StoragePoolUpdateProperties(TypedDict, total=False):
        key "platformConsoleSettings": ForwardRef('PlatformConsoleSettings', module='types')
        key "provisionedBandwidthMbPerSec": int
        platform_console_settings: PlatformConsoleSettings
        provisioned_bandwidth_mb_per_sec: int


    class azure.mgmt.purestorageblock.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.purestorageblock.types.TrackedResource(Resource):
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


    class azure.mgmt.purestorageblock.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.purestorageblock.types.UserDetails(TypedDict, total=False):
        key "companyDetails": ForwardRef('CompanyDetails', module='types')
        key "emailAddress": Required[str]
        key "firstName": Required[str]
        key "lastName": Required[str]
        key "phoneNumber": str
        key "upn": str
        company_details: CompanyDetails
        email_address: str
        first_name: str
        last_name: str
        phone_number: str
        upn: str


    class azure.mgmt.purestorageblock.types.VnetInjection(TypedDict, total=False):
        key "subnetId": Required[str]
        key "vnetId": Required[str]
        subnet_id: str
        vnet_id: str


    class azure.mgmt.purestorageblock.types.Volume(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AzureVolumeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AzureVolumeProperties
        system_data: SystemData
        type: str


    class azure.mgmt.purestorageblock.types.VolumeGroup(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VolumeGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: VolumeGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.purestorageblock.types.VolumeGroupOverwriteRequest(TypedDict, total=False):
        key "sourceSnapshotResourceId": Required[str]
        key "sourceVolumeGroupResourceId": Required[str]
        source_snapshot_resource_id: str
        source_volume_group_resource_id: str


    class azure.mgmt.purestorageblock.types.VolumeGroupProperties(TypedDict, total=False):
        key "performanceParameters": ForwardRef('PerformanceParameters', module='types')
        key "protectionParameters": ForwardRef('ProtectionParameters', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceRecoverableVolumeGroupResourceId": str
        key "sourceSnapshotResourceId": str
        key "sourceType": Union[str, VolumeGroupSourceType]
        key "sourceVolumeGroupResourceId": str
        key "storagePoolInternalId": str
        key "volumeGroupInternalId": str
        performance_parameters: PerformanceParameters
        protection_parameters: ProtectionParameters
        provisioning_state: Union[str, ProvisioningState]
        source_recoverable_volume_group_resource_id: str
        source_snapshot_resource_id: str
        source_type: Union[str, VolumeGroupSourceType]
        source_volume_group_resource_id: str
        storage_pool_internal_id: str
        volume_group_internal_id: str


    class azure.mgmt.purestorageblock.types.VolumeGroupSnapshot(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('VolumeGroupSnapshotProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: VolumeGroupSnapshotProperties
        system_data: SystemData
        type: str


    class azure.mgmt.purestorageblock.types.VolumeGroupSnapshotListRequest(TypedDict, total=False):
        key "filter": str
        key "orderby": str
        key "skip": int
        key "top": int
        filter: str
        orderby: str
        skip: int
        top: int


    class azure.mgmt.purestorageblock.types.VolumeGroupSnapshotProperties(TypedDict, total=False):
        key "createdAt": str
        key "createdByPolicy": bool
        key "provisioningState": Union[str, ProvisioningState]
        key "softDeletion": ForwardRef('DestroyedStateProperties', module='types')
        key "sourceSnapshotResourceId": str
        key "space": ForwardRef('Space', module='types')
        created_at: str
        created_by_policy: bool
        provisioning_state: Union[str, ProvisioningState]
        soft_deletion: DestroyedStateProperties
        source_snapshot_resource_id: str
        space: Space
        volumeSnapshots: list[VolumeSnapshotInfo]
        volume_snapshots: list[VolumeSnapshotInfo]


    class azure.mgmt.purestorageblock.types.VolumeGroupUpdate(TypedDict, total=False):
        key "properties": ForwardRef('VolumeGroupUpdateProperties', module='types')
        properties: VolumeGroupUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.purestorageblock.types.VolumeGroupUpdateProperties(TypedDict, total=False):
        key "performanceParameters": ForwardRef('PerformanceParameters', module='types')
        key "protectionParameters": ForwardRef('ProtectionParameters', module='types')
        performance_parameters: PerformanceParameters
        protection_parameters: ProtectionParameters


    class azure.mgmt.purestorageblock.types.VolumeOverwriteRequest(TypedDict, total=False):
        key "sourceSerialNumber": str
        key "sourceType": Required[Union[str, VolumeSourceType]]
        key "sourceVolumeGroupResourceId": str
        key "sourceVolumeResourceId": str
        key "sourceVolumeSnapshot": ForwardRef('VolumeSnapshotSource', module='types')
        source_serial_number: str
        source_type: Union[str, VolumeSourceType]
        source_volume_group_resource_id: str
        source_volume_resource_id: str
        source_volume_snapshot: VolumeSnapshotSource


    class azure.mgmt.purestorageblock.types.VolumeSnapshotInfo(TypedDict, total=False):
        key "name": Required[str]
        key "provisionedSize": int
        key "serialNumber": str
        key "space": ForwardRef('Space', module='types')
        name: str
        provisioned_size: int
        serial_number: str
        space: Space


    class azure.mgmt.purestorageblock.types.VolumeSnapshotSource(TypedDict, total=False):
        key "volumeGroupSnapshotResourceId": Required[str]
        key "volumeSnapshotName": Required[str]
        volume_group_snapshot_resource_id: str
        volume_snapshot_name: str


    class azure.mgmt.purestorageblock.types.VolumeUpdate(TypedDict, total=False):
        key "properties": ForwardRef('VolumeUpdateProperties', module='types')
        properties: VolumeUpdateProperties


    class azure.mgmt.purestorageblock.types.VolumeUpdateProperties(TypedDict, total=False):
        key "provisionedSize": int
        provisioned_size: int


```