```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.databoxedge

    class azure.mgmt.databoxedge.DataBoxEdgeManagementClient: implements ContextManager 
        addons: AddonsOperations
        alerts: AlertsOperations
        available_skus: AvailableSkusOperations
        bandwidth_schedules: BandwidthSchedulesOperations
        containers: ContainersOperations
        devices: DevicesOperations
        jobs: JobsOperations
        monitoring_config: MonitoringConfigOperations
        nodes: NodesOperations
        operations: Operations
        operations_status: OperationsStatusOperations
        orders: OrdersOperations
        roles: RolesOperations
        shares: SharesOperations
        storage_account_credentials: StorageAccountCredentialsOperations
        storage_accounts: StorageAccountsOperations
        triggers: TriggersOperations
        users: UsersOperations

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


namespace azure.mgmt.databoxedge.aio

    class azure.mgmt.databoxedge.aio.DataBoxEdgeManagementClient: implements AsyncContextManager 
        addons: AddonsOperations
        alerts: AlertsOperations
        available_skus: AvailableSkusOperations
        bandwidth_schedules: BandwidthSchedulesOperations
        containers: ContainersOperations
        devices: DevicesOperations
        jobs: JobsOperations
        monitoring_config: MonitoringConfigOperations
        nodes: NodesOperations
        operations: Operations
        operations_status: OperationsStatusOperations
        orders: OrdersOperations
        roles: RolesOperations
        shares: SharesOperations
        storage_account_credentials: StorageAccountCredentialsOperations
        storage_accounts: StorageAccountsOperations
        triggers: TriggersOperations
        users: UsersOperations

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


namespace azure.mgmt.databoxedge.aio.operations

    class azure.mgmt.databoxedge.aio.operations.AddonsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                addon: Addon, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Addon]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                addon: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Addon]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Addon: ...

        @distributed_trace
        def list_by_role(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Addon]: ...


    class azure.mgmt.databoxedge.aio.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Alert]: ...


    class azure.mgmt.databoxedge.aio.operations.AvailableSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DataBoxEdgeSku]: ...


    class azure.mgmt.databoxedge.aio.operations.BandwidthSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                parameters: BandwidthSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BandwidthSchedule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BandwidthSchedule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> BandwidthSchedule: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BandwidthSchedule]: ...


    class azure.mgmt.databoxedge.aio.operations.ContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                container: Container, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Container]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                container: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Container]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Container: ...

        @distributed_trace
        def list_by_storage_account(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Container]: ...


    class azure.mgmt.databoxedge.aio.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataBoxEdgeDevice]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataBoxEdgeDevice]: ...

        @overload
        async def begin_create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                security_settings: SecuritySettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                security_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_download_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_install_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_scan_for_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def generate_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> GenerateCertResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @distributed_trace_async
        async def get_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        @distributed_trace_async
        async def get_network_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> NetworkSettings: ...

        @distributed_trace_async
        async def get_update_summary(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> UpdateSummary: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataBoxEdgeDevice]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataBoxEdgeDevice]: ...

        @overload
        async def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: DataBoxEdgeDevicePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        async def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        async def update_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: DataBoxEdgeDeviceExtendedInfoPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        @overload
        async def update_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        @overload
        async def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: UploadCertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UploadCertificateResponse: ...

        @overload
        async def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UploadCertificateResponse: ...


    class azure.mgmt.databoxedge.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.databoxedge.aio.operations.MonitoringConfigOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                monitoring_metric_configuration: MonitoringMetricConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoringMetricConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                monitoring_metric_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoringMetricConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> MonitoringMetricConfiguration: ...

        @distributed_trace
        def list(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoringMetricConfiguration]: ...


    class azure.mgmt.databoxedge.aio.operations.NodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Node]: ...


    class azure.mgmt.databoxedge.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.databoxedge.aio.operations.OperationsStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.databoxedge.aio.operations.OrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                order: Order, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Order]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                order: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Order]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Order: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Order]: ...

        @distributed_trace_async
        async def list_dc_access_code(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DCAccessCode: ...


    class azure.mgmt.databoxedge.aio.operations.RolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                role: Role, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Role]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                role: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Role]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Role: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Role]: ...


    class azure.mgmt.databoxedge.aio.operations.SharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                share: Share, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Share]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Share]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Share: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Share]: ...


    class azure.mgmt.databoxedge.aio.operations.StorageAccountCredentialsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                storage_account_credential: StorageAccountCredential, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccountCredential]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                storage_account_credential: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccountCredential]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> StorageAccountCredential: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageAccountCredential]: ...


    class azure.mgmt.databoxedge.aio.operations.StorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                storage_account: StorageAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccount]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                storage_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccount]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> StorageAccount: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageAccount]: ...


    class azure.mgmt.databoxedge.aio.operations.TriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                trigger: Trigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Trigger]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                trigger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Trigger]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Trigger]: ...


    class azure.mgmt.databoxedge.aio.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                user: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @overload
        async def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                user: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[User]: ...


namespace azure.mgmt.databoxedge.models

    class azure.mgmt.databoxedge.models.ARMBaseModel(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_STORAGE = "BlobStorage"
        GENERAL_PURPOSE_STORAGE = "GeneralPurposeStorage"


    class azure.mgmt.databoxedge.models.Addon(ARMBaseModel):
        id: str
        kind: Union[str, AddonType]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AddonList(Model):
        next_link: str
        value: list[Addon]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AddonState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INVALID = "Invalid"
        RECONFIGURING = "Reconfiguring"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.AddonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC_FOR_KUBERNETES = "ArcForKubernetes"
        IOT_EDGE = "IotEdge"


    class azure.mgmt.databoxedge.models.Address(Model):
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        country: str
        postal_code: str
        state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_line1: Optional[str] = ..., 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                country: str, 
                postal_code: Optional[str] = ..., 
                state: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Alert(ARMBaseModel):
        alert_type: str
        appeared_at_date_time: datetime
        detailed_information: dict[str, str]
        error_details: AlertErrorDetails
        id: str
        name: str
        recommendation: str
        severity: Union[str, AlertSeverity]
        system_data: SystemData
        title: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AlertErrorDetails(Model):
        error_code: str
        error_message: str
        occurrences: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AlertList(Model):
        next_link: str
        value: list[Alert]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        INFORMATIONAL = "Informational"
        WARNING = "Warning"


    class azure.mgmt.databoxedge.models.ArcAddon(Addon):
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        id: str
        kind: Union[str, AddonType]
        name: str
        provisioning_state: Union[str, AddonState]
        resource_group_name: str
        resource_location: str
        resource_name: str
        subscription_id: str
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_group_name: str, 
                resource_location: str, 
                resource_name: str, 
                subscription_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AsymmetricEncryptedSecret(Model):
        encryption_algorithm: Union[str, EncryptionAlgorithm]
        encryption_cert_thumbprint: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_algorithm: Union[str, EncryptionAlgorithm], 
                encryption_cert_thumbprint: Optional[str] = ..., 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Authentication(Model):
        symmetric_key: SymmetricKey

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                symmetric_key: Optional[SymmetricKey] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        INVALID = "Invalid"


    class azure.mgmt.databoxedge.models.AzureContainerDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE = "AzureFile"
        BLOCK_BLOB = "BlockBlob"
        PAGE_BLOB = "PageBlob"


    class azure.mgmt.databoxedge.models.AzureContainerInfo(Model):
        container_name: str
        data_format: Union[str, AzureContainerDataFormat]
        storage_account_credential_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_name: str, 
                data_format: Union[str, AzureContainerDataFormat], 
                storage_account_credential_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.BandwidthSchedule(ARMBaseModel):
        days: Union[list[str, DayOfWeek]]
        id: str
        name: str
        rate_in_mbps: int
        start: str
        stop: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days: List[Union[str, DayOfWeek]], 
                rate_in_mbps: int, 
                start: str, 
                stop: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.BandwidthSchedulesList(Model):
        next_link: str
        value: list[BandwidthSchedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ClientAccessRight(Model):
        access_permission: Union[str, ClientPermissionType]
        client: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_permission: Union[str, ClientPermissionType], 
                client: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ClientPermissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACCESS = "NoAccess"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.databoxedge.models.CloudEdgeManagementRole(Role):
        edge_profile: EdgeProfile
        id: str
        kind: Union[str, RoleTypes]
        local_management_status: Union[str, RoleStatus]
        name: str
        role_status: Union[str, RoleStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                role_status: Optional[Union[str, RoleStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.CniConfig(Model):
        pod_subnet: str
        service_subnet: str
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ComputeResource(Model):
        memory_in_gb: int
        processor_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                memory_in_gb: int, 
                processor_count: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ContactDetails(Model):
        company_name: str
        contact_person: str
        email_list: list[str]
        phone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                company_name: str, 
                contact_person: str, 
                email_list: List[str], 
                phone: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Container(ARMBaseModel):
        container_status: Union[str, ContainerStatus]
        created_date_time: datetime
        data_format: Union[str, AzureContainerDataFormat]
        id: str
        name: str
        refresh_details: RefreshDetails
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_format: Union[str, AzureContainerDataFormat], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ContainerList(Model):
        next_link: str
        value: list[Container]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ContainerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEEDS_ATTENTION = "NeedsAttention"
        OFFLINE = "Offline"
        OK = "OK"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.databoxedge.models.DCAccessCode(Model):
        auth_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDevice(ARMBaseModel):
        configured_role_types: Union[list[str, RoleTypes]]
        culture: str
        data_box_edge_device_status: Union[str, DataBoxEdgeDeviceStatus]
        description: str
        device_hcs_version: str
        device_local_capacity: int
        device_model: str
        device_software_version: str
        device_type: Union[str, DeviceType]
        edge_profile: EdgeProfile
        etag: str
        friendly_name: str
        id: str
        identity: ResourceIdentity
        kind: Union[str, DataBoxEdgeDeviceKind]
        location: str
        model_description: str
        name: str
        node_count: int
        resource_move_details: ResourceMoveDetails
        serial_number: str
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        time_zone: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_box_edge_device_status: Optional[Union[str, DataBoxEdgeDeviceStatus]] = ..., 
                etag: Optional[str] = ..., 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceExtendedInfo(ARMBaseModel):
        channel_integrity_key_name: str
        channel_integrity_key_version: str
        client_secret_store_id: str
        client_secret_store_url: str
        device_secrets: dict[str, Secret]
        encryption_key: str
        encryption_key_thumbprint: str
        id: str
        key_vault_sync_status: Union[str, KeyVaultSyncStatus]
        name: str
        resource_key: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                channel_integrity_key_name: Optional[str] = ..., 
                channel_integrity_key_version: Optional[str] = ..., 
                client_secret_store_id: Optional[str] = ..., 
                client_secret_store_url: Optional[str] = ..., 
                encryption_key: Optional[str] = ..., 
                encryption_key_thumbprint: Optional[str] = ..., 
                key_vault_sync_status: Optional[Union[str, KeyVaultSyncStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceExtendedInfoPatch(Model):
        channel_integrity_key_name: str
        channel_integrity_key_version: str
        client_secret_store_id: str
        client_secret_store_url: str
        sync_status: Union[str, KeyVaultSyncStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                channel_integrity_key_name: Optional[str] = ..., 
                channel_integrity_key_version: Optional[str] = ..., 
                client_secret_store_id: Optional[str] = ..., 
                client_secret_store_url: Optional[str] = ..., 
                sync_status: Optional[Union[str, KeyVaultSyncStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DATA_BOX_GATEWAY = "AzureDataBoxGateway"
        AZURE_MODULAR_DATA_CENTRE = "AzureModularDataCentre"
        AZURE_STACK_EDGE = "AzureStackEdge"
        AZURE_STACK_HUB = "AzureStackHub"


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceList(Model):
        next_link: str
        value: list[DataBoxEdgeDevice]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDevicePatch(Model):
        edge_profile: EdgeProfilePatch
        identity: ResourceIdentity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                edge_profile: Optional[EdgeProfilePatch] = ..., 
                identity: Optional[ResourceIdentity] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISCONNECTED = "Disconnected"
        MAINTENANCE = "Maintenance"
        NEEDS_ATTENTION = "NeedsAttention"
        OFFLINE = "Offline"
        ONLINE = "Online"
        PARTIALLY_DISCONNECTED = "PartiallyDisconnected"
        READY_TO_SETUP = "ReadyToSetup"


    class azure.mgmt.databoxedge.models.DataBoxEdgeMoveRequest(Model):
        resources: list[str]
        target_resource_group: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resources: List[str], 
                target_resource_group: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeSku(Model):
        api_versions: list[str]
        availability: Union[str, SkuAvailability]
        capabilities: list[SkuCapability]
        costs: list[SkuCost]
        family: str
        kind: str
        location_info: list[SkuLocationInfo]
        locations: list[str]
        name: Union[str, SkuName]
        resource_type: str
        shipment_types: Union[list[str, ShipmentType]]
        signup_option: Union[str, SkuSignupOption]
        size: str
        tier: Union[str, SkuTier]
        version: Union[str, SkuVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeSkuList(Model):
        next_link: str
        value: list[DataBoxEdgeSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.DataPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        LOCAL = "Local"


    class azure.mgmt.databoxedge.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.databoxedge.models.DeviceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX_EDGE_DEVICE = "DataBoxEdgeDevice"


    class azure.mgmt.databoxedge.models.DownloadPhase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOADING = "Downloading"
        INITIALIZING = "Initializing"
        UNKNOWN = "Unknown"
        VERIFYING = "Verifying"


    class azure.mgmt.databoxedge.models.EdgeProfile(Model):
        subscription: EdgeProfileSubscription

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                subscription: Optional[EdgeProfileSubscription] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.EdgeProfilePatch(Model):
        subscription: EdgeProfileSubscriptionPatch

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                subscription: Optional[EdgeProfileSubscriptionPatch] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.EdgeProfileSubscription(Model):
        id: str
        location_placement_id: str
        quota_id: str
        registered_features: list[SubscriptionRegisteredFeatures]
        registration_date: str
        registration_id: str
        serialized_details: str
        state: Union[str, SubscriptionState]
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location_placement_id: Optional[str] = ..., 
                quota_id: Optional[str] = ..., 
                registered_features: Optional[List[SubscriptionRegisteredFeatures]] = ..., 
                registration_date: Optional[str] = ..., 
                registration_id: Optional[str] = ..., 
                serialized_details: Optional[str] = ..., 
                state: Optional[Union[str, SubscriptionState]] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.EdgeProfileSubscriptionPatch(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.EncryptionAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AES256 = "AES256"
        NONE = "None"
        RSAES_PKCS1_V1_5 = "RSAES_PKCS1_v_1_5"


    class azure.mgmt.databoxedge.models.EtcdInfo(Model):
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.FileEventTrigger(Trigger):
        custom_context_tag: str
        id: str
        kind: Union[str, TriggerEventType]
        name: str
        sink_info: RoleSinkInfo
        source_info: FileSourceInfo
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_context_tag: Optional[str] = ..., 
                sink_info: RoleSinkInfo, 
                source_info: FileSourceInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.FileSourceInfo(Model):
        share_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                share_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.GenerateCertResponse(Model):
        expiry_time_in_utc: str
        private_key: str
        public_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiry_time_in_utc: Optional[str] = ..., 
                private_key: Optional[str] = ..., 
                public_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.HostPlatformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KUBERNETES_CLUSTER = "KubernetesCluster"
        LINUX_VM = "LinuxVM"


    class azure.mgmt.databoxedge.models.ImageRepositoryCredential(Model):
        image_repository_url: str
        password: AsymmetricEncryptedSecret
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image_repository_url: str, 
                password: Optional[AsymmetricEncryptedSecret] = ..., 
                user_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.InstallRebootBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEVER_REBOOTS = "NeverReboots"
        REQUEST_REBOOT = "RequestReboot"
        REQUIRES_REBOOT = "RequiresReboot"


    class azure.mgmt.databoxedge.models.IoTAddon(Addon):
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        id: str
        io_t_device_details: IoTDeviceInfo
        io_t_edge_device_details: IoTDeviceInfo
        kind: Union[str, AddonType]
        name: str
        provisioning_state: Union[str, AddonState]
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                io_t_device_details: IoTDeviceInfo, 
                io_t_edge_device_details: IoTDeviceInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.IoTDeviceInfo(Model):
        authentication: Authentication
        device_id: str
        io_t_host_hub: str
        io_t_host_hub_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication: Optional[Authentication] = ..., 
                device_id: str, 
                io_t_host_hub: str, 
                io_t_host_hub_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.IoTEdgeAgentInfo(Model):
        image_name: str
        image_repository: ImageRepositoryCredential
        tag: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image_name: str, 
                image_repository: Optional[ImageRepositoryCredential] = ..., 
                tag: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.IoTRole(Role):
        compute_resource: ComputeResource
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        id: str
        io_t_device_details: IoTDeviceInfo
        io_t_edge_agent_info: IoTEdgeAgentInfo
        io_t_edge_device_details: IoTDeviceInfo
        kind: Union[str, RoleTypes]
        name: str
        role_status: Union[str, RoleStatus]
        share_mappings: list[MountPointMap]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_resource: Optional[ComputeResource] = ..., 
                host_platform: Optional[Union[str, PlatformType]] = ..., 
                io_t_device_details: Optional[IoTDeviceInfo] = ..., 
                io_t_edge_agent_info: Optional[IoTEdgeAgentInfo] = ..., 
                io_t_edge_device_details: Optional[IoTDeviceInfo] = ..., 
                role_status: Optional[Union[str, RoleStatus]] = ..., 
                share_mappings: Optional[List[MountPointMap]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Ipv4Config(Model):
        gateway: str
        ip_address: str
        subnet: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Ipv6Config(Model):
        gateway: str
        ip_address: str
        prefix_length: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Job(Model):
        current_stage: Union[str, UpdateOperationStage]
        download_progress: UpdateDownloadProgress
        end_time: datetime
        error: JobErrorDetails
        error_manifest_file: str
        folder: str
        id: str
        install_progress: UpdateInstallProgress
        job_type: Union[str, JobType]
        name: str
        percent_complete: int
        refreshed_entity_id: str
        start_time: datetime
        status: Union[str, JobStatus]
        total_refresh_errors: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                folder: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.JobErrorDetails(Model):
        code: str
        error_details: list[JobErrorItem]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.JobErrorItem(Model):
        code: str
        message: str
        recommendations: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        INVALID = "Invalid"
        PAUSED = "Paused"
        RUNNING = "Running"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.databoxedge.models.JobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP = "Backup"
        DOWNLOAD_UPDATES = "DownloadUpdates"
        INSTALL_UPDATES = "InstallUpdates"
        INVALID = "Invalid"
        REFRESH_CONTAINER = "RefreshContainer"
        REFRESH_SHARE = "RefreshShare"
        RESTORE = "Restore"
        SCAN_FOR_UPDATES = "ScanForUpdates"
        TRIGGER_SUPPORT_PACKAGE = "TriggerSupportPackage"


    class azure.mgmt.databoxedge.models.KeyVaultSyncStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_NOT_CONFIGURED = "KeyVaultNotConfigured"
        KEY_VAULT_NOT_SYNCED = "KeyVaultNotSynced"
        KEY_VAULT_SYNCED = "KeyVaultSynced"
        KEY_VAULT_SYNCING = "KeyVaultSyncing"
        KEY_VAULT_SYNC_FAILED = "KeyVaultSyncFailed"
        KEY_VAULT_SYNC_PENDING = "KeyVaultSyncPending"


    class azure.mgmt.databoxedge.models.KubernetesClusterInfo(Model):
        etcd_info: EtcdInfo
        nodes: list[NodeInfo]
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesIPConfiguration(Model):
        ip_address: str
        port: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesNodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        MASTER = "Master"
        WORKER = "Worker"


    class azure.mgmt.databoxedge.models.KubernetesRole(Role):
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        id: str
        kind: Union[str, RoleTypes]
        kubernetes_cluster_info: KubernetesClusterInfo
        kubernetes_role_resources: KubernetesRoleResources
        name: str
        provisioning_state: Union[str, KubernetesState]
        role_status: Union[str, RoleStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_platform: Optional[Union[str, PlatformType]] = ..., 
                kubernetes_cluster_info: Optional[KubernetesClusterInfo] = ..., 
                kubernetes_role_resources: Optional[KubernetesRoleResources] = ..., 
                role_status: Optional[Union[str, RoleStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleCompute(Model):
        memory_in_bytes: int
        processor_count: int
        vm_profile: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                vm_profile: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleNetwork(Model):
        cni_config: CniConfig
        load_balancer_config: LoadBalancerConfig

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleResources(Model):
        compute: KubernetesRoleCompute
        network: KubernetesRoleNetwork
        storage: KubernetesRoleStorage

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute: KubernetesRoleCompute, 
                storage: Optional[KubernetesRoleStorage] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleStorage(Model):
        endpoints: list[MountPointMap]
        storage_classes: list[KubernetesRoleStorageClassInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoints: Optional[List[MountPointMap]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleStorageClassInfo(Model):
        name: str
        posix_compliant: Union[str, PosixComplianceStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.KubernetesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INVALID = "Invalid"
        RECONFIGURING = "Reconfiguring"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.LoadBalancerConfig(Model):
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MECRole(Role):
        connection_string: AsymmetricEncryptedSecret
        controller_endpoint: str
        id: str
        kind: Union[str, RoleTypes]
        name: str
        resource_unique_id: str
        role_status: Union[str, RoleStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_string: Optional[AsymmetricEncryptedSecret] = ..., 
                controller_endpoint: Optional[str] = ..., 
                resource_unique_id: Optional[str] = ..., 
                role_status: Optional[Union[str, RoleStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"
        TOTAL = "Total"


    class azure.mgmt.databoxedge.models.MetricCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY = "Capacity"
        TRANSACTION = "Transaction"


    class azure.mgmt.databoxedge.models.MetricConfiguration(Model):
        counter_sets: list[MetricCounterSet]
        mdm_account: str
        metric_name_space: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                counter_sets: List[MetricCounterSet], 
                mdm_account: Optional[str] = ..., 
                metric_name_space: Optional[str] = ..., 
                resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricCounter(Model):
        additional_dimensions: list[MetricDimension]
        dimension_filter: list[MetricDimension]
        instance: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_dimensions: Optional[List[MetricDimension]] = ..., 
                dimension_filter: Optional[List[MetricDimension]] = ..., 
                instance: Optional[str] = ..., 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricCounterSet(Model):
        counters: list[MetricCounter]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                counters: List[MetricCounter], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricDimension(Model):
        source_name: str
        source_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_name: str, 
                source_type: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricDimensionV1(Model):
        display_name: str
        name: str
        to_be_exported_for_shoebox: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricSpecificationV1(Model):
        aggregation_type: Union[str, MetricAggregationType]
        category: Union[str, MetricCategory]
        dimensions: list[MetricDimensionV1]
        display_description: str
        display_name: str
        fill_gap_with_zero: bool
        name: str
        resource_id_dimension_name_override: str
        supported_aggregation_types: Union[list[str, MetricAggregationType]]
        supported_time_grain_types: Union[list[str, TimeGrain]]
        unit: Union[str, MetricUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[Union[str, MetricAggregationType]] = ..., 
                category: Optional[Union[str, MetricCategory]] = ..., 
                dimensions: Optional[List[MetricDimensionV1]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                supported_aggregation_types: Optional[List[Union[str, MetricAggregationType]]] = ..., 
                supported_time_grain_types: Optional[List[Union[str, TimeGrain]]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLISECONDS = "Milliseconds"
        NOT_SPECIFIED = "NotSpecified"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.databoxedge.models.MonitoringMetricConfiguration(ARMBaseModel):
        id: str
        metric_configurations: list[MetricConfiguration]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric_configurations: List[MetricConfiguration], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MonitoringMetricConfigurationList(Model):
        next_link: str
        value: list[MonitoringMetricConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MonitoringStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.MountPointMap(Model):
        mount_point: str
        mount_type: Union[str, MountType]
        role_id: str
        role_type: Union[str, RoleTypes]
        share_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                share_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.MountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOST_PATH = "HostPath"
        VOLUME = "Volume"


    class azure.mgmt.databoxedge.models.MsiIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.databoxedge.models.NetworkAdapter(Model):
        adapter_id: str
        adapter_position: NetworkAdapterPosition
        dhcp_status: Union[str, NetworkAdapterDHCPStatus]
        dns_servers: list[str]
        index: int
        ipv4_configuration: Ipv4Config
        ipv6_configuration: Ipv6Config
        ipv6_link_local_address: str
        label: str
        link_speed: int
        mac_address: str
        network_adapter_name: str
        node_id: str
        rdma_status: Union[str, NetworkAdapterRDMAStatus]
        status: Union[str, NetworkAdapterStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dhcp_status: Optional[Union[str, NetworkAdapterDHCPStatus]] = ..., 
                rdma_status: Optional[Union[str, NetworkAdapterRDMAStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.NetworkAdapterDHCPStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.NetworkAdapterPosition(Model):
        network_group: Union[str, NetworkGroup]
        port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.NetworkAdapterRDMAStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPABLE = "Capable"
        INCAPABLE = "Incapable"


    class azure.mgmt.databoxedge.models.NetworkAdapterStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.databoxedge.models.NetworkGroup(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        NON_RDMA = "NonRDMA"
        RDMA = "RDMA"


    class azure.mgmt.databoxedge.models.NetworkSettings(ARMBaseModel):
        id: str
        name: str
        network_adapters: list[NetworkAdapter]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Node(ARMBaseModel):
        id: str
        name: str
        node_chassis_serial_number: str
        node_display_name: str
        node_friendly_software_version: str
        node_hcs_version: str
        node_instance_id: str
        node_serial_number: str
        node_status: Union[str, NodeStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.NodeInfo(Model):
        ip_configuration: list[KubernetesIPConfiguration]
        name: str
        type: Union[str, KubernetesNodeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_configuration: Optional[List[KubernetesIPConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.NodeList(Model):
        next_link: str
        value: list[Node]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.NodeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "Down"
        REBOOTING = "Rebooting"
        SHUTTING_DOWN = "ShuttingDown"
        UNKNOWN = "Unknown"
        UP = "Up"


    class azure.mgmt.databoxedge.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        service_specification: ServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                service_specification: Optional[ServiceSpecification] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.OperationsList(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Operation], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Order(ARMBaseModel):
        contact_information: ContactDetails
        current_status: OrderStatus
        delivery_tracking_info: list[TrackingInfo]
        id: str
        name: str
        order_history: list[OrderStatus]
        return_tracking_info: list[TrackingInfo]
        serial_number: str
        shipment_type: Union[str, ShipmentType]
        shipping_address: Address
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_information: Optional[ContactDetails] = ..., 
                shipment_type: Optional[Union[str, ShipmentType]] = ..., 
                shipping_address: Optional[Address] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.OrderList(Model):
        next_link: str
        value: list[Order]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.OrderState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRIVING = "Arriving"
        AWAITING_DROP = "AwaitingDrop"
        AWAITING_FULFILLMENT = "AwaitingFulfillment"
        AWAITING_PICKUP = "AwaitingPickup"
        AWAITING_PREPARATION = "AwaitingPreparation"
        AWAITING_RETURN_SHIPMENT = "AwaitingReturnShipment"
        AWAITING_SHIPMENT = "AwaitingShipment"
        COLLECTED_AT_MICROSOFT = "CollectedAtMicrosoft"
        DECLINED = "Declined"
        DELIVERED = "Delivered"
        LOST_DEVICE = "LostDevice"
        PICKUP_COMPLETED = "PickupCompleted"
        REPLACEMENT_REQUESTED = "ReplacementRequested"
        RETURN_INITIATED = "ReturnInitiated"
        SHIPPED = "Shipped"
        SHIPPED_BACK = "ShippedBack"
        UNTRACKED = "Untracked"


    class azure.mgmt.databoxedge.models.OrderStatus(Model):
        additional_order_details: dict[str, str]
        comments: str
        status: Union[str, OrderState]
        tracking_information: TrackingInfo
        update_date_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                comments: Optional[str] = ..., 
                status: Union[str, OrderState], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.PeriodicTimerEventTrigger(Trigger):
        custom_context_tag: str
        id: str
        kind: Union[str, TriggerEventType]
        name: str
        sink_info: RoleSinkInfo
        source_info: PeriodicTimerSourceInfo
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_context_tag: Optional[str] = ..., 
                sink_info: RoleSinkInfo, 
                source_info: PeriodicTimerSourceInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.PeriodicTimerSourceInfo(Model):
        schedule: str
        start_time: datetime
        topic: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                schedule: str, 
                start_time: datetime, 
                topic: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.PlatformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.databoxedge.models.PosixComplianceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.databoxedge.models.RefreshDetails(Model):
        error_manifest_file: str
        in_progress_refresh_job_id: str
        last_completed_refresh_job_time_in_utc: datetime
        last_job: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_manifest_file: Optional[str] = ..., 
                in_progress_refresh_job_id: Optional[str] = ..., 
                last_completed_refresh_job_time_in_utc: Optional[datetime] = ..., 
                last_job: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ResourceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, MsiIdentityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, MsiIdentityType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ResourceMoveDetails(Model):
        operation_in_progress: Union[str, ResourceMoveStatus]
        operation_in_progress_lock_timeout_in_utc: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operation_in_progress: Optional[Union[str, ResourceMoveStatus]] = ..., 
                operation_in_progress_lock_timeout_in_utc: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ResourceMoveStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        RESOURCE_MOVE_FAILED = "ResourceMoveFailed"
        RESOURCE_MOVE_IN_PROGRESS = "ResourceMoveInProgress"


    class azure.mgmt.databoxedge.models.ResourceTypeSku(Model):
        resource_type: str
        skus: list[SkuInformation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Role(ARMBaseModel):
        id: str
        kind: Union[str, RoleTypes]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.RoleList(Model):
        next_link: str
        value: list[Role]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.RoleSinkInfo(Model):
        role_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                role_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.RoleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.RoleTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASA = "ASA"
        CLOUD_EDGE_MANAGEMENT = "CloudEdgeManagement"
        COGNITIVE = "Cognitive"
        FUNCTIONS = "Functions"
        IOT = "IOT"
        KUBERNETES = "Kubernetes"
        MEC = "MEC"


    class azure.mgmt.databoxedge.models.SSLStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.Secret(Model):
        encrypted_secret: AsymmetricEncryptedSecret
        key_vault_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encrypted_secret: Optional[AsymmetricEncryptedSecret] = ..., 
                key_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SecuritySettings(ARMBaseModel):
        device_admin_password: AsymmetricEncryptedSecret
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_admin_password: AsymmetricEncryptedSecret, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ServiceSpecification(Model):
        metric_specifications: list[MetricSpecificationV1]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric_specifications: Optional[List[MetricSpecificationV1]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Share(ARMBaseModel):
        access_protocol: Union[str, ShareAccessProtocol]
        azure_container_info: AzureContainerInfo
        client_access_rights: list[ClientAccessRight]
        data_policy: Union[str, DataPolicy]
        description: str
        id: str
        monitoring_status: Union[str, MonitoringStatus]
        name: str
        refresh_details: RefreshDetails
        share_mappings: list[MountPointMap]
        share_status: Union[str, ShareStatus]
        system_data: SystemData
        type: str
        user_access_rights: list[UserAccessRight]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_protocol: Union[str, ShareAccessProtocol], 
                azure_container_info: Optional[AzureContainerInfo] = ..., 
                client_access_rights: Optional[List[ClientAccessRight]] = ..., 
                data_policy: Optional[Union[str, DataPolicy]] = ..., 
                description: Optional[str] = ..., 
                monitoring_status: Union[str, MonitoringStatus], 
                refresh_details: Optional[RefreshDetails] = ..., 
                share_status: Union[str, ShareStatus], 
                user_access_rights: Optional[List[UserAccessRight]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ShareAccessProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.mgmt.databoxedge.models.ShareAccessRight(Model):
        access_type: Union[str, ShareAccessType]
        share_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_type: Union[str, ShareAccessType], 
                share_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ShareAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGE = "Change"
        CUSTOM = "Custom"
        READ = "Read"


    class azure.mgmt.databoxedge.models.ShareList(Model):
        next_link: str
        value: list[Share]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.ShareStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEEDS_ATTENTION = "NeedsAttention"
        OFFLINE = "Offline"
        OK = "OK"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.ShipmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        SELF_PICKUP = "SelfPickup"
        SHIPPED_TO_CUSTOMER = "ShippedToCustomer"


    class azure.mgmt.databoxedge.models.Sku(Model):
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SkuAvailability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.databoxedge.models.SkuCapability(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SkuCost(Model):
        extended_unit: str
        meter_id: str
        quantity: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SkuInformation(Model):
        costs: list[SkuCost]
        family: str
        kind: str
        location_info: list[SkuLocationInfo]
        locations: list[str]
        name: str
        required_features: list[str]
        required_quota_ids: list[str]
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SkuInformationList(Model):
        next_link: str
        value: list[ResourceTypeSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SkuLocationInfo(Model):
        location: str
        sites: list[str]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE = "Edge"
        EDGE_MR_MINI = "EdgeMR_Mini"
        EDGE_PR_BASE = "EdgePR_Base"
        EDGE_PR_BASE_UPS = "EdgePR_Base_UPS"
        EDGE_P_BASE = "EdgeP_Base"
        EDGE_P_HIGH = "EdgeP_High"
        EP2_128_1_T4_MX1_W = "EP2_128_1T4_Mx1_W"
        EP2_256_2_T4_W = "EP2_256_2T4_W"
        EP2_64_1_VPU_W = "EP2_64_1VPU_W"
        GATEWAY = "Gateway"
        GPU = "GPU"
        MANAGEMENT = "Management"
        RCA_LARGE = "RCA_Large"
        RCA_SMALL = "RCA_Small"
        RDC = "RDC"
        TCA_LARGE = "TCA_Large"
        TCA_SMALL = "TCA_Small"
        TDC = "TDC"
        TEA1_NODE = "TEA_1Node"
        TEA1_NODE_HEATER = "TEA_1Node_Heater"
        TEA1_NODE_UPS = "TEA_1Node_UPS"
        TEA1_NODE_UPS_HEATER = "TEA_1Node_UPS_Heater"
        TEA4_NODE_HEATER = "TEA_4Node_Heater"
        TEA4_NODE_UPS_HEATER = "TEA_4Node_UPS_Heater"
        TMA = "TMA"


    class azure.mgmt.databoxedge.models.SkuSignupOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        NONE = "None"


    class azure.mgmt.databoxedge.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD = "Standard"


    class azure.mgmt.databoxedge.models.SkuVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREVIEW = "Preview"
        STABLE = "Stable"


    class azure.mgmt.databoxedge.models.StorageAccount(ARMBaseModel):
        blob_endpoint: str
        container_count: int
        data_policy: Union[str, DataPolicy]
        description: str
        id: str
        name: str
        storage_account_credential_id: str
        storage_account_status: Union[str, StorageAccountStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_policy: Union[str, DataPolicy], 
                description: Optional[str] = ..., 
                storage_account_credential_id: Optional[str] = ..., 
                storage_account_status: Optional[Union[str, StorageAccountStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.StorageAccountCredential(ARMBaseModel):
        account_key: AsymmetricEncryptedSecret
        account_type: Union[str, AccountType]
        alias: str
        blob_domain_name: str
        connection_string: str
        id: str
        name: str
        ssl_status: Union[str, SSLStatus]
        storage_account_id: str
        system_data: SystemData
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_key: Optional[AsymmetricEncryptedSecret] = ..., 
                account_type: Union[str, AccountType], 
                alias: str, 
                blob_domain_name: Optional[str] = ..., 
                connection_string: Optional[str] = ..., 
                ssl_status: Union[str, SSLStatus], 
                storage_account_id: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.StorageAccountCredentialList(Model):
        next_link: str
        value: list[StorageAccountCredential]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.StorageAccountList(Model):
        next_link: str
        value: list[StorageAccount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.StorageAccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEEDS_ATTENTION = "NeedsAttention"
        OFFLINE = "Offline"
        OK = "OK"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.SubscriptionRegisteredFeatures(Model):
        name: str
        state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                state: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        REGISTERED = "Registered"
        SUSPENDED = "Suspended"
        UNREGISTERED = "Unregistered"
        WARNED = "Warned"


    class azure.mgmt.databoxedge.models.SymmetricKey(Model):
        connection_string: AsymmetricEncryptedSecret

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_string: Optional[AsymmetricEncryptedSecret] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.TimeGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PT12_H = "PT12H"
        PT15_M = "PT15M"
        PT1_D = "PT1D"
        PT1_H = "PT1H"
        PT1_M = "PT1M"
        PT30_M = "PT30M"
        PT5_M = "PT5M"
        PT6_H = "PT6H"


    class azure.mgmt.databoxedge.models.TrackingInfo(Model):
        carrier_name: str
        serial_number: str
        tracking_id: str
        tracking_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                carrier_name: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                tracking_id: Optional[str] = ..., 
                tracking_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.Trigger(ARMBaseModel):
        id: str
        kind: Union[str, TriggerEventType]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.TriggerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_EVENT = "FileEvent"
        PERIODIC_TIMER_EVENT = "PeriodicTimerEvent"


    class azure.mgmt.databoxedge.models.TriggerList(Model):
        next_link: str
        value: list[Trigger]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UpdateDetails(Model):
        estimated_install_time_in_mins: int
        reboot_behavior: Union[str, InstallRebootBehavior]
        status: Union[str, UpdateStatus]
        target_version: str
        update_size: float
        update_title: str
        update_type: Union[str, UpdateType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                estimated_install_time_in_mins: Optional[int] = ..., 
                reboot_behavior: Optional[Union[str, InstallRebootBehavior]] = ..., 
                status: Optional[Union[str, UpdateStatus]] = ..., 
                target_version: Optional[str] = ..., 
                update_size: Optional[float] = ..., 
                update_title: Optional[str] = ..., 
                update_type: Optional[Union[str, UpdateType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UpdateDownloadProgress(Model):
        download_phase: Union[str, DownloadPhase]
        number_of_updates_downloaded: int
        number_of_updates_to_download: int
        percent_complete: int
        total_bytes_downloaded: float
        total_bytes_to_download: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UpdateInstallProgress(Model):
        number_of_updates_installed: int
        number_of_updates_to_install: int
        percent_complete: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UpdateOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD = "Download"
        INSTALL = "Install"
        NONE = "None"
        SCAN = "Scan"


    class azure.mgmt.databoxedge.models.UpdateOperationStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD_COMPLETE = "DownloadComplete"
        DOWNLOAD_FAILED = "DownloadFailed"
        DOWNLOAD_STARTED = "DownloadStarted"
        FAILURE = "Failure"
        INITIAL = "Initial"
        INSTALL_COMPLETE = "InstallComplete"
        INSTALL_FAILED = "InstallFailed"
        INSTALL_STARTED = "InstallStarted"
        REBOOT_INITIATED = "RebootInitiated"
        RESCAN_COMPLETE = "RescanComplete"
        RESCAN_FAILED = "RescanFailed"
        RESCAN_STARTED = "RescanStarted"
        SCAN_COMPLETE = "ScanComplete"
        SCAN_FAILED = "ScanFailed"
        SCAN_STARTED = "ScanStarted"
        SUCCESS = "Success"
        UNKNOWN = "Unknown"


    class azure.mgmt.databoxedge.models.UpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOAD_COMPLETED = "DownloadCompleted"
        DOWNLOAD_PENDING = "DownloadPending"
        DOWNLOAD_STARTED = "DownloadStarted"
        INSTALL_COMPLETED = "InstallCompleted"
        INSTALL_STARTED = "InstallStarted"


    class azure.mgmt.databoxedge.models.UpdateSummary(ARMBaseModel):
        device_last_scanned_date_time: datetime
        device_version_number: str
        friendly_device_version_name: str
        id: str
        in_progress_download_job_id: str
        in_progress_download_job_started_date_time: datetime
        in_progress_install_job_id: str
        in_progress_install_job_started_date_time: datetime
        last_completed_download_job_date_time: datetime
        last_completed_download_job_id: str
        last_completed_install_job_date_time: datetime
        last_completed_install_job_id: str
        last_completed_scan_job_date_time: datetime
        last_download_job_status: Union[str, JobStatus]
        last_install_job_status: Union[str, JobStatus]
        name: str
        ongoing_update_operation: Union[str, UpdateOperation]
        reboot_behavior: Union[str, InstallRebootBehavior]
        system_data: SystemData
        total_number_of_updates_available: int
        total_number_of_updates_pending_download: int
        total_number_of_updates_pending_install: int
        total_time_in_minutes: int
        total_update_size_in_bytes: float
        type: str
        update_titles: list[str]
        updates: list[UpdateDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_last_scanned_date_time: Optional[datetime] = ..., 
                device_version_number: Optional[str] = ..., 
                friendly_device_version_name: Optional[str] = ..., 
                last_completed_scan_job_date_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRMWARE = "Firmware"
        KUBERNETES = "Kubernetes"
        SOFTWARE = "Software"


    class azure.mgmt.databoxedge.models.UploadCertificateRequest(Model):
        authentication_type: Union[str, AuthenticationType]
        certificate: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                certificate: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UploadCertificateResponse(Model):
        aad_audience: str
        aad_authority: str
        aad_tenant_id: str
        auth_type: Union[str, AuthenticationType]
        azure_management_endpoint_audience: str
        resource_id: str
        service_principal_client_id: str
        service_principal_object_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_type: Optional[Union[str, AuthenticationType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.User(ARMBaseModel):
        encrypted_password: AsymmetricEncryptedSecret
        id: str
        name: str
        share_access_rights: list[ShareAccessRight]
        system_data: SystemData
        type: str
        user_type: Union[str, UserType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encrypted_password: Optional[AsymmetricEncryptedSecret] = ..., 
                user_type: Optional[Union[str, UserType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UserAccessRight(Model):
        access_type: Union[str, ShareAccessType]
        user_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_type: Union[str, ShareAccessType], 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UserList(Model):
        next_link: str
        value: list[User]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.databoxedge.models.UserType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM = "ARM"
        LOCAL_MANAGEMENT = "LocalManagement"
        SHARE = "Share"


namespace azure.mgmt.databoxedge.operations

    class azure.mgmt.databoxedge.operations.AddonsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                addon: Addon, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Addon]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                addon: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Addon]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                role_name: str, 
                addon_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Addon: ...

        @distributed_trace
        def list_by_role(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Addon]: ...


    class azure.mgmt.databoxedge.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Alert]: ...


    class azure.mgmt.databoxedge.operations.AvailableSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DataBoxEdgeSku]: ...


    class azure.mgmt.databoxedge.operations.BandwidthSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                parameters: BandwidthSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BandwidthSchedule]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BandwidthSchedule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> BandwidthSchedule: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BandwidthSchedule]: ...


    class azure.mgmt.databoxedge.operations.ContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                container: Container, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Container]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                container: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Container]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                storage_account_name: str, 
                container_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Container: ...

        @distributed_trace
        def list_by_storage_account(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Container]: ...


    class azure.mgmt.databoxedge.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataBoxEdgeDevice]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataBoxEdgeDevice]: ...

        @overload
        def begin_create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                security_settings: SecuritySettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update_security_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                security_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_download_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_install_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_scan_for_updates(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def generate_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> GenerateCertResponse: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @distributed_trace
        def get_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        @distributed_trace
        def get_network_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> NetworkSettings: ...

        @distributed_trace
        def get_update_summary(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> UpdateSummary: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[DataBoxEdgeDevice]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[DataBoxEdgeDevice]: ...

        @overload
        def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: DataBoxEdgeDevicePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        def update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        def update_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: DataBoxEdgeDeviceExtendedInfoPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        @overload
        def update_extended_information(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDeviceExtendedInfo: ...

        @overload
        def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: UploadCertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UploadCertificateResponse: ...

        @overload
        def upload_certificate(
                self, 
                device_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UploadCertificateResponse: ...


    class azure.mgmt.databoxedge.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.databoxedge.operations.MonitoringConfigOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                monitoring_metric_configuration: MonitoringMetricConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoringMetricConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                monitoring_metric_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoringMetricConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> MonitoringMetricConfiguration: ...

        @distributed_trace
        def list(
                self, 
                device_name: str, 
                role_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoringMetricConfiguration]: ...


    class azure.mgmt.databoxedge.operations.NodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Node]: ...


    class azure.mgmt.databoxedge.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.databoxedge.operations.OperationsStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.databoxedge.operations.OrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                order: Order, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Order]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                order: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Order]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Order: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Order]: ...

        @distributed_trace
        def list_dc_access_code(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DCAccessCode: ...


    class azure.mgmt.databoxedge.operations.RolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                role: Role, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Role]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                role: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Role]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Role: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Role]: ...


    class azure.mgmt.databoxedge.operations.SharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                share: Share, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Share]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Share]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Share: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Share]: ...


    class azure.mgmt.databoxedge.operations.StorageAccountCredentialsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                storage_account_credential: StorageAccountCredential, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccountCredential]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                storage_account_credential: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccountCredential]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> StorageAccountCredential: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageAccountCredential]: ...


    class azure.mgmt.databoxedge.operations.StorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                storage_account: StorageAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccount]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                storage_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccount]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                storage_account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> StorageAccount: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageAccount]: ...


    class azure.mgmt.databoxedge.operations.TriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                trigger: Trigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Trigger]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                trigger: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Trigger]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[Trigger]: ...


    class azure.mgmt.databoxedge.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                user: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @overload
        def begin_create_or_update(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                user: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @distributed_trace
        def begin_delete(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                device_name: str, 
                name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        def list_by_data_box_edge_device(
                self, 
                device_name: str, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[User]: ...


```