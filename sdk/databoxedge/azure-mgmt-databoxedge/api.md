```py
namespace azure.mgmt.databoxedge

    class azure.mgmt.databoxedge.DataBoxEdgeManagementClient: implements ContextManager 
        addons: AddonsOperations
        alerts: AlertsOperations
        available_skus: AvailableSkusOperations
        bandwidth_schedules: BandwidthSchedulesOperations
        containers: ContainersOperations
        device_capacity_check: DeviceCapacityCheckOperations
        device_capacity_info: DeviceCapacityInfoOperations
        devices: DevicesOperations
        diagnostic_settings: DiagnosticSettingsOperations
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
        support_packages: SupportPackagesOperations
        triggers: TriggersOperations
        users: UsersOperations

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


namespace azure.mgmt.databoxedge.aio

    class azure.mgmt.databoxedge.aio.DataBoxEdgeManagementClient: implements AsyncContextManager 
        addons: AddonsOperations
        alerts: AlertsOperations
        available_skus: AvailableSkusOperations
        bandwidth_schedules: BandwidthSchedulesOperations
        containers: ContainersOperations
        device_capacity_check: DeviceCapacityCheckOperations
        device_capacity_info: DeviceCapacityInfoOperations
        devices: DevicesOperations
        diagnostic_settings: DiagnosticSettingsOperations
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
        support_packages: SupportPackagesOperations
        triggers: TriggersOperations
        users: UsersOperations

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


    class azure.mgmt.databoxedge.aio.operations.DeviceCapacityCheckOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_check_resource_creation_feasibility(
                self, 
                resource_group_name: str, 
                device_name: str, 
                device_capacity_request_info: DeviceCapacityRequestInfo, 
                *, 
                capacity_name: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_check_resource_creation_feasibility(
                self, 
                resource_group_name: str, 
                device_name: str, 
                device_capacity_request_info: DeviceCapacityRequestInfo, 
                *, 
                capacity_name: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_check_resource_creation_feasibility(
                self, 
                resource_group_name: str, 
                device_name: str, 
                device_capacity_request_info: IO[bytes], 
                *, 
                capacity_name: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.databoxedge.aio.operations.DeviceCapacityInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_device_capacity_info(
                self, 
                resource_group_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> DeviceCapacityInfo: ...


    class azure.mgmt.databoxedge.aio.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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

        @overload
        async def create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        async def create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        async def create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

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
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DataBoxEdgeDevice]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[str] = ..., 
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


    class azure.mgmt.databoxedge.aio.operations.DiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                proactive_log_collection_settings: DiagnosticProactiveLogCollectionSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticProactiveLogCollectionSettings]: ...

        @overload
        async def begin_update_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                proactive_log_collection_settings: DiagnosticProactiveLogCollectionSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticProactiveLogCollectionSettings]: ...

        @overload
        async def begin_update_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                proactive_log_collection_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticProactiveLogCollectionSettings]: ...

        @overload
        async def begin_update_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                diagnostic_remote_support_settings: DiagnosticRemoteSupportSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticRemoteSupportSettings]: ...

        @overload
        async def begin_update_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                diagnostic_remote_support_settings: DiagnosticRemoteSupportSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticRemoteSupportSettings]: ...

        @overload
        async def begin_update_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                diagnostic_remote_support_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticRemoteSupportSettings]: ...

        @distributed_trace_async
        async def get_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DiagnosticProactiveLogCollectionSettings: ...

        @distributed_trace_async
        async def get_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DiagnosticRemoteSupportSettings: ...


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


    class azure.mgmt.databoxedge.aio.operations.SupportPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_trigger_support_package(
                self, 
                device_name: str, 
                resource_group_name: str, 
                trigger_support_package_request: TriggerSupportPackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_support_package(
                self, 
                device_name: str, 
                resource_group_name: str, 
                trigger_support_package_request: TriggerSupportPackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_support_package(
                self, 
                device_name: str, 
                resource_group_name: str, 
                trigger_support_package_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[User]: ...


namespace azure.mgmt.databoxedge.models

    class azure.mgmt.databoxedge.models.ARMBaseModel(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.databoxedge.models.AccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_ACCESS = "FullAccess"
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.databoxedge.models.AccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_STORAGE = "BlobStorage"
        GENERAL_PURPOSE_STORAGE = "GeneralPurposeStorage"


    class azure.mgmt.databoxedge.models.Addon(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.Address(_Model):
        address_line1: Optional[str]
        address_line2: Optional[str]
        address_line3: Optional[str]
        city: Optional[str]
        country: str
        postal_code: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_line1: Optional[str] = ..., 
                address_line2: Optional[str] = ..., 
                address_line3: Optional[str] = ..., 
                city: Optional[str] = ..., 
                country: str, 
                postal_code: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Alert(ProxyResource):
        id: str
        name: str
        properties: Optional[AlertProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.models.AlertErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        occurrences: Optional[int]


    class azure.mgmt.databoxedge.models.AlertProperties(_Model):
        alert_type: Optional[str]
        appeared_at_date_time: Optional[datetime]
        detailed_information: Optional[dict[str, str]]
        error_details: Optional[AlertErrorDetails]
        recommendation: Optional[str]
        severity: Optional[Union[str, AlertSeverity]]
        title: Optional[str]


    class azure.mgmt.databoxedge.models.AlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        INFORMATIONAL = "Informational"
        WARNING = "Warning"


    class azure.mgmt.databoxedge.models.ArcAddon(Addon, discriminator='ArcForKubernetes'):
        id: str
        kind: Literal[AddonType.ARC_FOR_KUBERNETES]
        name: str
        properties: ArcAddonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ArcAddonProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.ArcAddonProperties(_Model):
        host_platform: Optional[Union[str, PlatformType]]
        host_platform_type: Optional[Union[str, HostPlatformType]]
        provisioning_state: Optional[Union[str, AddonState]]
        resource_group_name: str
        resource_location: str
        resource_name: str
        subscription_id: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_group_name: str, 
                resource_location: str, 
                resource_name: str, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.AsymmetricEncryptedSecret(_Model):
        encryption_algorithm: Union[str, EncryptionAlgorithm]
        encryption_cert_thumbprint: Optional[str]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                encryption_algorithm: Union[str, EncryptionAlgorithm], 
                encryption_cert_thumbprint: Optional[str] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Authentication(_Model):
        symmetric_key: Optional[SymmetricKey]

        @overload
        def __init__(
                self, 
                *, 
                symmetric_key: Optional[SymmetricKey] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        INVALID = "Invalid"


    class azure.mgmt.databoxedge.models.AzureContainerDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE = "AzureFile"
        BLOCK_BLOB = "BlockBlob"
        PAGE_BLOB = "PageBlob"


    class azure.mgmt.databoxedge.models.AzureContainerInfo(_Model):
        container_name: str
        data_format: Union[str, AzureContainerDataFormat]
        storage_account_credential_id: str

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                data_format: Union[str, AzureContainerDataFormat], 
                storage_account_credential_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.BandwidthSchedule(ProxyResource):
        id: str
        name: str
        properties: BandwidthScheduleProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: BandwidthScheduleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.BandwidthScheduleProperties(_Model):
        days: list[Union[str, DayOfWeek]]
        rate_in_mbps: int
        start: str
        stop: str

        @overload
        def __init__(
                self, 
                *, 
                days: list[Union[str, DayOfWeek]], 
                rate_in_mbps: int, 
                start: str, 
                stop: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClientAccessRight(_Model):
        access_permission: Union[str, ClientPermissionType]
        client: str

        @overload
        def __init__(
                self, 
                *, 
                access_permission: Union[str, ClientPermissionType], 
                client: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClientPermissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACCESS = "NoAccess"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.databoxedge.models.CloudEdgeManagementRole(Role, discriminator='CloudEdgeManagement'):
        id: str
        kind: Literal[RoleTypes.CLOUD_EDGE_MANAGEMENT]
        name: str
        properties: Optional[CloudEdgeManagementRoleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudEdgeManagementRoleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.CloudEdgeManagementRoleProperties(_Model):
        edge_profile: Optional[EdgeProfile]
        local_management_status: Optional[Union[str, RoleStatus]]
        role_status: Union[str, RoleStatus]

        @overload
        def __init__(
                self, 
                *, 
                role_status: Union[str, RoleStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClusterCapacityViewData(_Model):
        fqdn: Optional[str]
        gpu_capacity: Optional[ClusterGpuCapacity]
        last_refreshed_time: Optional[datetime]
        memory_capacity: Optional[ClusterMemoryCapacity]
        total_provisioned_non_hpn_cores: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                fqdn: Optional[str] = ..., 
                gpu_capacity: Optional[ClusterGpuCapacity] = ..., 
                last_refreshed_time: Optional[datetime] = ..., 
                memory_capacity: Optional[ClusterMemoryCapacity] = ..., 
                total_provisioned_non_hpn_cores: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClusterGpuCapacity(_Model):
        gpu_free_units_count: Optional[int]
        gpu_reserved_for_failover_units_count: Optional[int]
        gpu_total_units_count: Optional[int]
        gpu_type: Optional[str]
        gpu_used_units_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                gpu_free_units_count: Optional[int] = ..., 
                gpu_reserved_for_failover_units_count: Optional[int] = ..., 
                gpu_total_units_count: Optional[int] = ..., 
                gpu_type: Optional[str] = ..., 
                gpu_used_units_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClusterMemoryCapacity(_Model):
        cluster_failover_memory_mb: Optional[float]
        cluster_fragmentation_memory_mb: Optional[float]
        cluster_free_memory_mb: Optional[float]
        cluster_hyperv_reserve_memory_mb: Optional[float]
        cluster_infra_vm_memory_mb: Optional[float]
        cluster_memory_used_by_vms_mb: Optional[float]
        cluster_non_failover_vm_mb: Optional[float]
        cluster_total_memory_mb: Optional[float]
        cluster_used_memory_mb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                cluster_failover_memory_mb: Optional[float] = ..., 
                cluster_fragmentation_memory_mb: Optional[float] = ..., 
                cluster_free_memory_mb: Optional[float] = ..., 
                cluster_hyperv_reserve_memory_mb: Optional[float] = ..., 
                cluster_infra_vm_memory_mb: Optional[float] = ..., 
                cluster_memory_used_by_vms_mb: Optional[float] = ..., 
                cluster_non_failover_vm_mb: Optional[float] = ..., 
                cluster_total_memory_mb: Optional[float] = ..., 
                cluster_used_memory_mb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClusterStorageViewData(_Model):
        cluster_free_storage_mb: Optional[float]
        cluster_total_storage_mb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                cluster_free_storage_mb: Optional[float] = ..., 
                cluster_total_storage_mb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ClusterWitnessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        FILE_SHARE = "FileShare"
        NONE = "None"


    class azure.mgmt.databoxedge.models.CniConfig(_Model):
        pod_subnet: Optional[str]
        service_subnet: Optional[str]
        type: Optional[str]
        version: Optional[str]


    class azure.mgmt.databoxedge.models.ComputeResource(_Model):
        memory_in_gb: int
        processor_count: int

        @overload
        def __init__(
                self, 
                *, 
                memory_in_gb: int, 
                processor_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ContactDetails(_Model):
        company_name: str
        contact_person: str
        email_list: list[str]
        phone: str

        @overload
        def __init__(
                self, 
                *, 
                company_name: str, 
                contact_person: str, 
                email_list: list[str], 
                phone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Container(ProxyResource):
        id: str
        name: str
        properties: ContainerProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ContainerProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.ContainerProperties(_Model):
        container_status: Optional[Union[str, ContainerStatus]]
        created_date_time: Optional[datetime]
        data_format: Union[str, AzureContainerDataFormat]
        refresh_details: Optional[RefreshDetails]

        @overload
        def __init__(
                self, 
                *, 
                data_format: Union[str, AzureContainerDataFormat]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.DCAccessCode(_Model):
        properties: Optional[DCAccessCodeProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DCAccessCodeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DCAccessCodeProperties(_Model):
        auth_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDevice(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ResourceIdentity]
        kind: Optional[Union[str, DataBoxEdgeDeviceKind]]
        location: str
        name: str
        properties: Optional[DataBoxEdgeDeviceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                properties: Optional[DataBoxEdgeDeviceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceExtendedInfo(ARMBaseModel):
        id: str
        name: str
        properties: Optional[DataBoxEdgeDeviceExtendedInfoProperties]
        system_data: Optional[SystemData]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataBoxEdgeDeviceExtendedInfoProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceExtendedInfoPatch(_Model):
        channel_integrity_key_name: Optional[str]
        channel_integrity_key_version: Optional[str]
        client_secret_store_id: Optional[str]
        client_secret_store_url: Optional[str]
        sync_status: Optional[Union[str, KeyVaultSyncStatus]]

        @overload
        def __init__(
                self, 
                *, 
                channel_integrity_key_name: Optional[str] = ..., 
                channel_integrity_key_version: Optional[str] = ..., 
                client_secret_store_id: Optional[str] = ..., 
                client_secret_store_url: Optional[str] = ..., 
                sync_status: Optional[Union[str, KeyVaultSyncStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceExtendedInfoProperties(_Model):
        channel_integrity_key_name: Optional[str]
        channel_integrity_key_version: Optional[str]
        client_secret_store_id: Optional[str]
        client_secret_store_url: Optional[str]
        cloud_witness_container_name: Optional[str]
        cloud_witness_storage_account_name: Optional[str]
        cloud_witness_storage_endpoint: Optional[str]
        cluster_witness_type: Optional[Union[str, ClusterWitnessType]]
        device_secrets: Optional[dict[str, Secret]]
        encryption_key: Optional[str]
        encryption_key_thumbprint: Optional[str]
        file_share_witness_location: Optional[str]
        file_share_witness_username: Optional[str]
        key_vault_sync_status: Optional[Union[str, KeyVaultSyncStatus]]
        resource_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_integrity_key_name: Optional[str] = ..., 
                channel_integrity_key_version: Optional[str] = ..., 
                client_secret_store_id: Optional[str] = ..., 
                client_secret_store_url: Optional[str] = ..., 
                encryption_key: Optional[str] = ..., 
                encryption_key_thumbprint: Optional[str] = ..., 
                key_vault_sync_status: Optional[Union[str, KeyVaultSyncStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DATA_BOX_GATEWAY = "AzureDataBoxGateway"
        AZURE_MODULAR_DATA_CENTRE = "AzureModularDataCentre"
        AZURE_STACK_EDGE = "AzureStackEdge"
        AZURE_STACK_HUB = "AzureStackHub"


    class azure.mgmt.databoxedge.models.DataBoxEdgeDevicePatch(_Model):
        identity: Optional[ResourceIdentity]
        properties: Optional[DataBoxEdgeDevicePropertiesPatch]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                properties: Optional[DataBoxEdgeDevicePropertiesPatch] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceProperties(_Model):
        configured_role_types: Optional[list[Union[str, RoleTypes]]]
        culture: Optional[str]
        data_box_edge_device_status: Optional[Union[str, DataBoxEdgeDeviceStatus]]
        data_residency: Optional[DataResidency]
        description: Optional[str]
        device_hcs_version: Optional[str]
        device_local_capacity: Optional[int]
        device_model: Optional[str]
        device_software_version: Optional[str]
        device_type: Optional[Union[str, DeviceType]]
        edge_profile: Optional[EdgeProfile]
        friendly_name: Optional[str]
        kubernetes_workload_profile: Optional[str]
        model_description: Optional[str]
        node_count: Optional[int]
        resource_move_details: Optional[ResourceMoveDetails]
        serial_number: Optional[str]
        system_data: Optional[SystemData]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_residency: Optional[DataResidency] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDevicePropertiesPatch(_Model):
        edge_profile: Optional[EdgeProfilePatch]

        @overload
        def __init__(
                self, 
                *, 
                edge_profile: Optional[EdgeProfilePatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DataBoxEdgeDeviceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISCONNECTED = "Disconnected"
        MAINTENANCE = "Maintenance"
        NEEDS_ATTENTION = "NeedsAttention"
        OFFLINE = "Offline"
        ONLINE = "Online"
        PARTIALLY_DISCONNECTED = "PartiallyDisconnected"
        READY_TO_SETUP = "ReadyToSetup"


    class azure.mgmt.databoxedge.models.DataBoxEdgeSku(_Model):
        api_versions: Optional[list[str]]
        availability: Optional[Union[str, SkuAvailability]]
        capabilities: Optional[list[SkuCapability]]
        costs: Optional[list[SkuCost]]
        family: Optional[str]
        kind: Optional[str]
        location_info: Optional[list[SkuLocationInfo]]
        locations: Optional[list[str]]
        name: Optional[Union[str, SkuName]]
        resource_type: Optional[str]
        shipment_types: Optional[list[Union[str, ShipmentType]]]
        signup_option: Optional[Union[str, SkuSignupOption]]
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]
        version: Optional[Union[str, SkuVersion]]


    class azure.mgmt.databoxedge.models.DataPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        LOCAL = "Local"


    class azure.mgmt.databoxedge.models.DataResidency(_Model):
        type: Optional[Union[str, DataResidencyType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, DataResidencyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DataResidencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_ZONE_REPLICATION = "GeoZoneReplication"
        ZONE_REPLICATION = "ZoneReplication"


    class azure.mgmt.databoxedge.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.databoxedge.models.DeviceCapacityInfo(ProxyResource):
        id: str
        name: str
        properties: Optional[DeviceCapacityInfoProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeviceCapacityInfoProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DeviceCapacityInfoProperties(_Model):
        cluster_compute_capacity_info: Optional[ClusterCapacityViewData]
        cluster_storage_capacity_info: Optional[ClusterStorageViewData]
        node_capacity_infos: Optional[dict[str, HostCapacity]]
        time_stamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                cluster_compute_capacity_info: Optional[ClusterCapacityViewData] = ..., 
                cluster_storage_capacity_info: Optional[ClusterStorageViewData] = ..., 
                node_capacity_infos: Optional[dict[str, HostCapacity]] = ..., 
                time_stamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DeviceCapacityRequestInfo(_Model):
        properties: DeviceCapacityRequestInfoProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: DeviceCapacityRequestInfoProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DeviceCapacityRequestInfoProperties(_Model):
        vm_placement_query: list[list[str]]
        vm_placement_results: Optional[list[VmPlacementRequestResult]]

        @overload
        def __init__(
                self, 
                *, 
                vm_placement_query: list[list[str]], 
                vm_placement_results: Optional[list[VmPlacementRequestResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DeviceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX_EDGE_DEVICE = "DataBoxEdgeDevice"


    class azure.mgmt.databoxedge.models.DiagnosticProactiveLogCollectionSettings(ProxyResource):
        id: str
        name: str
        properties: ProactiveLogCollectionSettingsProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ProactiveLogCollectionSettingsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DiagnosticRemoteSupportSettings(ProxyResource):
        id: str
        name: str
        properties: DiagnosticRemoteSupportSettingsProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: DiagnosticRemoteSupportSettingsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.DiagnosticRemoteSupportSettingsProperties(_Model):
        remote_support_settings_list: Optional[list[RemoteSupportSettings]]

        @overload
        def __init__(
                self, 
                *, 
                remote_support_settings_list: Optional[list[RemoteSupportSettings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.DownloadPhase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWNLOADING = "Downloading"
        INITIALIZING = "Initializing"
        UNKNOWN = "Unknown"
        VERIFYING = "Verifying"


    class azure.mgmt.databoxedge.models.EdgeProfile(_Model):
        subscription: Optional[EdgeProfileSubscription]

        @overload
        def __init__(
                self, 
                *, 
                subscription: Optional[EdgeProfileSubscription] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.EdgeProfilePatch(_Model):
        subscription: Optional[EdgeProfileSubscriptionPatch]

        @overload
        def __init__(
                self, 
                *, 
                subscription: Optional[EdgeProfileSubscriptionPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.EdgeProfileSubscription(_Model):
        id: Optional[str]
        properties: Optional[SubscriptionProperties]
        registration_date: Optional[str]
        registration_id: Optional[str]
        state: Optional[Union[str, SubscriptionState]]
        subscription_id: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[SubscriptionProperties] = ..., 
                registration_date: Optional[str] = ..., 
                registration_id: Optional[str] = ..., 
                state: Optional[Union[str, SubscriptionState]] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.EdgeProfileSubscriptionPatch(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.EncryptionAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AES256 = "AES256"
        NONE = "None"
        RSAES_PKCS1_V1_5 = "RSAES_PKCS1_v_1_5"


    class azure.mgmt.databoxedge.models.EtcdInfo(_Model):
        type: Optional[str]
        version: Optional[str]


    class azure.mgmt.databoxedge.models.FileEventTrigger(Trigger, discriminator='FileEvent'):
        id: str
        kind: Literal[TriggerEventType.FILE_EVENT]
        name: str
        properties: FileTriggerProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: FileTriggerProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.FileSourceInfo(_Model):
        share_id: str

        @overload
        def __init__(
                self, 
                *, 
                share_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.FileTriggerProperties(_Model):
        custom_context_tag: Optional[str]
        sink_info: RoleSinkInfo
        source_info: FileSourceInfo

        @overload
        def __init__(
                self, 
                *, 
                custom_context_tag: Optional[str] = ..., 
                sink_info: RoleSinkInfo, 
                source_info: FileSourceInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.GenerateCertResponse(_Model):
        expiry_time_in_utc: Optional[str]
        private_key: Optional[str]
        public_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time_in_utc: Optional[str] = ..., 
                private_key: Optional[str] = ..., 
                public_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.HostCapacity(_Model):
        available_gpu_count: Optional[int]
        effective_available_memory_mb_on_host: Optional[int]
        gpu_type: Optional[str]
        host_name: Optional[str]
        numa_nodes_data: Optional[list[NumaNodeData]]
        vm_used_memory: Optional[dict[str, VmMemory]]

        @overload
        def __init__(
                self, 
                *, 
                available_gpu_count: Optional[int] = ..., 
                effective_available_memory_mb_on_host: Optional[int] = ..., 
                gpu_type: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                numa_nodes_data: Optional[list[NumaNodeData]] = ..., 
                vm_used_memory: Optional[dict[str, VmMemory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.HostPlatformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KUBERNETES_CLUSTER = "KubernetesCluster"
        LINUX_VM = "LinuxVM"


    class azure.mgmt.databoxedge.models.ImageRepositoryCredential(_Model):
        image_repository_url: str
        password: Optional[AsymmetricEncryptedSecret]
        user_name: str

        @overload
        def __init__(
                self, 
                *, 
                image_repository_url: str, 
                password: Optional[AsymmetricEncryptedSecret] = ..., 
                user_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.InstallRebootBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEVER_REBOOTS = "NeverReboots"
        REQUEST_REBOOT = "RequestReboot"
        REQUIRES_REBOOT = "RequiresReboot"


    class azure.mgmt.databoxedge.models.InstallationImpact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVICE_REBOOTED = "DeviceRebooted"
        KUBERNETES_WORKLOADS_DOWN = "KubernetesWorkloadsDown"
        NONE = "None"


    class azure.mgmt.databoxedge.models.IoTAddon(Addon, discriminator='IotEdge'):
        id: str
        kind: Literal[AddonType.IOT_EDGE]
        name: str
        properties: IoTAddonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: IoTAddonProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.IoTAddonProperties(_Model):
        host_platform: Optional[Union[str, PlatformType]]
        host_platform_type: Optional[Union[str, HostPlatformType]]
        io_t_device_details: IoTDeviceInfo
        io_t_edge_device_details: IoTDeviceInfo
        provisioning_state: Optional[Union[str, AddonState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                io_t_device_details: IoTDeviceInfo, 
                io_t_edge_device_details: IoTDeviceInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.IoTDeviceInfo(_Model):
        authentication: Optional[Authentication]
        device_id: str
        io_t_host_hub: str
        io_t_host_hub_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[Authentication] = ..., 
                device_id: str, 
                io_t_host_hub: str, 
                io_t_host_hub_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.IoTEdgeAgentInfo(_Model):
        image_name: str
        image_repository: Optional[ImageRepositoryCredential]
        tag: str

        @overload
        def __init__(
                self, 
                *, 
                image_name: str, 
                image_repository: Optional[ImageRepositoryCredential] = ..., 
                tag: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.IoTRole(Role, discriminator='IOT'):
        id: str
        kind: Literal[RoleTypes.IOT]
        name: str
        properties: Optional[IoTRoleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IoTRoleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.IoTRoleProperties(_Model):
        compute_resource: Optional[ComputeResource]
        host_platform: Union[str, PlatformType]
        host_platform_type: Optional[Union[str, HostPlatformType]]
        io_t_device_details: IoTDeviceInfo
        io_t_edge_agent_info: Optional[IoTEdgeAgentInfo]
        io_t_edge_device_details: IoTDeviceInfo
        role_status: Union[str, RoleStatus]
        share_mappings: Optional[list[MountPointMap]]

        @overload
        def __init__(
                self, 
                *, 
                compute_resource: Optional[ComputeResource] = ..., 
                host_platform: Union[str, PlatformType], 
                io_t_device_details: IoTDeviceInfo, 
                io_t_edge_agent_info: Optional[IoTEdgeAgentInfo] = ..., 
                io_t_edge_device_details: IoTDeviceInfo, 
                role_status: Union[str, RoleStatus], 
                share_mappings: Optional[list[MountPointMap]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Ipv4Config(_Model):
        gateway: Optional[str]
        ip_address: Optional[str]
        subnet: Optional[str]


    class azure.mgmt.databoxedge.models.Ipv6Config(_Model):
        gateway: Optional[str]
        ip_address: Optional[str]
        prefix_length: Optional[int]


    class azure.mgmt.databoxedge.models.Job(ProxyResource):
        end_time: Optional[datetime]
        error: Optional[JobErrorDetails]
        id: str
        name: str
        percent_complete: Optional[int]
        properties: Optional[JobProperties]
        start_time: Optional[datetime]
        status: Optional[Union[str, JobStatus]]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.JobErrorDetails(_Model):
        code: Optional[str]
        error_details: Optional[list[JobErrorItem]]
        message: Optional[str]


    class azure.mgmt.databoxedge.models.JobErrorItem(_Model):
        code: Optional[str]
        message: Optional[str]
        recommendations: Optional[list[str]]


    class azure.mgmt.databoxedge.models.JobProperties(_Model):
        current_stage: Optional[Union[str, UpdateOperationStage]]
        download_progress: Optional[UpdateDownloadProgress]
        error_manifest_file: Optional[str]
        folder: Optional[str]
        install_progress: Optional[UpdateInstallProgress]
        job_type: Optional[Union[str, JobType]]
        refreshed_entity_id: Optional[str]
        total_refresh_errors: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                folder: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.KubernetesClusterInfo(_Model):
        etcd_info: Optional[EtcdInfo]
        nodes: Optional[list[NodeInfo]]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesIPConfiguration(_Model):
        ip_address: Optional[str]
        port: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesNodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        MASTER = "Master"
        WORKER = "Worker"


    class azure.mgmt.databoxedge.models.KubernetesRole(Role, discriminator='Kubernetes'):
        id: str
        kind: Literal[RoleTypes.KUBERNETES]
        name: str
        properties: Optional[KubernetesRoleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[KubernetesRoleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleCompute(_Model):
        memory_in_bytes: Optional[int]
        processor_count: Optional[int]
        vm_profile: str

        @overload
        def __init__(
                self, 
                *, 
                vm_profile: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleNetwork(_Model):
        cni_config: Optional[CniConfig]
        load_balancer_config: Optional[LoadBalancerConfig]


    class azure.mgmt.databoxedge.models.KubernetesRoleProperties(_Model):
        host_platform: Union[str, PlatformType]
        host_platform_type: Optional[Union[str, HostPlatformType]]
        kubernetes_cluster_info: KubernetesClusterInfo
        kubernetes_role_resources: KubernetesRoleResources
        provisioning_state: Optional[Union[str, KubernetesState]]
        role_status: Union[str, RoleStatus]

        @overload
        def __init__(
                self, 
                *, 
                host_platform: Union[str, PlatformType], 
                kubernetes_cluster_info: KubernetesClusterInfo, 
                kubernetes_role_resources: KubernetesRoleResources, 
                role_status: Union[str, RoleStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleResources(_Model):
        compute: KubernetesRoleCompute
        network: Optional[KubernetesRoleNetwork]
        storage: Optional[KubernetesRoleStorage]

        @overload
        def __init__(
                self, 
                *, 
                compute: KubernetesRoleCompute, 
                storage: Optional[KubernetesRoleStorage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleStorage(_Model):
        endpoints: Optional[list[MountPointMap]]
        storage_classes: Optional[list[KubernetesRoleStorageClassInfo]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[list[MountPointMap]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.KubernetesRoleStorageClassInfo(_Model):
        name: Optional[str]
        posix_compliant: Optional[Union[str, PosixComplianceStatus]]
        type: Optional[str]


    class azure.mgmt.databoxedge.models.KubernetesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INVALID = "Invalid"
        RECONFIGURING = "Reconfiguring"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.LoadBalancerConfig(_Model):
        ip_range: Optional[list[str]]
        type: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_range: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MECRole(Role, discriminator='MEC'):
        id: str
        kind: Literal[RoleTypes.MEC]
        name: str
        properties: Optional[MECRoleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MECRoleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.MECRoleProperties(_Model):
        connection_string: Optional[AsymmetricEncryptedSecret]
        controller_endpoint: Optional[str]
        resource_unique_id: Optional[str]
        role_status: Union[str, RoleStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[AsymmetricEncryptedSecret] = ..., 
                controller_endpoint: Optional[str] = ..., 
                resource_unique_id: Optional[str] = ..., 
                role_status: Union[str, RoleStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.MetricConfiguration(_Model):
        counter_sets: list[MetricCounterSet]
        mdm_account: Optional[str]
        metric_name_space: Optional[str]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                counter_sets: list[MetricCounterSet], 
                mdm_account: Optional[str] = ..., 
                metric_name_space: Optional[str] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MetricCounter(_Model):
        additional_dimensions: Optional[list[MetricDimension]]
        dimension_filter: Optional[list[MetricDimension]]
        instance: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                additional_dimensions: Optional[list[MetricDimension]] = ..., 
                dimension_filter: Optional[list[MetricDimension]] = ..., 
                instance: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MetricCounterSet(_Model):
        counters: list[MetricCounter]

        @overload
        def __init__(
                self, 
                *, 
                counters: list[MetricCounter]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MetricDimension(_Model):
        source_name: str
        source_type: str

        @overload
        def __init__(
                self, 
                *, 
                source_name: str, 
                source_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MetricDimensionV1(_Model):
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


    class azure.mgmt.databoxedge.models.MetricSpecificationV1(_Model):
        aggregation_type: Optional[Union[str, MetricAggregationType]]
        category: Optional[Union[str, MetricCategory]]
        dimensions: Optional[list[MetricDimensionV1]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[bool]
        name: Optional[str]
        resource_id_dimension_name_override: Optional[str]
        supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]]
        supported_time_grain_types: Optional[list[Union[str, TimeGrain]]]
        unit: Optional[Union[str, MetricUnit]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[Union[str, MetricAggregationType]] = ..., 
                category: Optional[Union[str, MetricCategory]] = ..., 
                dimensions: Optional[list[MetricDimensionV1]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]] = ..., 
                supported_time_grain_types: Optional[list[Union[str, TimeGrain]]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLISECONDS = "Milliseconds"
        NOT_SPECIFIED = "NotSpecified"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.databoxedge.models.MonitoringMetricConfiguration(ProxyResource):
        id: str
        name: str
        properties: MonitoringMetricConfigurationProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: MonitoringMetricConfigurationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.MonitoringMetricConfigurationProperties(_Model):
        metric_configurations: list[MetricConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                metric_configurations: list[MetricConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MonitoringStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.MountPointMap(_Model):
        mount_point: Optional[str]
        mount_type: Optional[Union[str, MountType]]
        role_id: Optional[str]
        role_type: Optional[Union[str, RoleTypes]]
        share_id: str

        @overload
        def __init__(
                self, 
                *, 
                share_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.MountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOST_PATH = "HostPath"
        VOLUME = "Volume"


    class azure.mgmt.databoxedge.models.MsiIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.databoxedge.models.NetworkAdapter(_Model):
        adapter_id: Optional[str]
        adapter_position: Optional[NetworkAdapterPosition]
        dhcp_status: Optional[Union[str, NetworkAdapterDHCPStatus]]
        dns_servers: Optional[list[str]]
        index: Optional[int]
        ipv4_configuration: Optional[Ipv4Config]
        ipv6_configuration: Optional[Ipv6Config]
        ipv6_link_local_address: Optional[str]
        label: Optional[str]
        link_speed: Optional[int]
        mac_address: Optional[str]
        network_adapter_name: Optional[str]
        node_id: Optional[str]
        rdma_status: Optional[Union[str, NetworkAdapterRDMAStatus]]
        status: Optional[Union[str, NetworkAdapterStatus]]

        @overload
        def __init__(
                self, 
                *, 
                dhcp_status: Optional[Union[str, NetworkAdapterDHCPStatus]] = ..., 
                rdma_status: Optional[Union[str, NetworkAdapterRDMAStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.NetworkAdapterDHCPStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.NetworkAdapterPosition(_Model):
        network_group: Optional[Union[str, NetworkGroup]]
        port: Optional[int]


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


    class azure.mgmt.databoxedge.models.NetworkSettings(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSettingsProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.models.NetworkSettingsProperties(_Model):
        network_adapters: Optional[list[NetworkAdapter]]


    class azure.mgmt.databoxedge.models.Node(ARMBaseModel):
        id: str
        name: str
        properties: Optional[NodeProperties]
        type: str


    class azure.mgmt.databoxedge.models.NodeInfo(_Model):
        ip_configuration: Optional[list[KubernetesIPConfiguration]]
        name: Optional[str]
        type: Optional[Union[str, KubernetesNodeType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_configuration: Optional[list[KubernetesIPConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.NodeProperties(_Model):
        node_chassis_serial_number: Optional[str]
        node_display_name: Optional[str]
        node_friendly_software_version: Optional[str]
        node_hcs_version: Optional[str]
        node_instance_id: Optional[str]
        node_serial_number: Optional[str]
        node_status: Optional[Union[str, NodeStatus]]


    class azure.mgmt.databoxedge.models.NodeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "Down"
        REBOOTING = "Rebooting"
        SHUTTING_DOWN = "ShuttingDown"
        UNKNOWN = "Unknown"
        UP = "Up"


    class azure.mgmt.databoxedge.models.NumaNodeData(_Model):
        effective_available_memory_in_mb: Optional[int]
        free_v_cpu_indexes_for_hpn: Optional[list[int]]
        logical_core_count_per_core: Optional[int]
        numa_node_index: Optional[int]
        total_memory_in_mb: Optional[int]
        v_cpu_indexes_for_hpn: Optional[list[int]]
        v_cpu_indexes_for_root: Optional[list[int]]

        @overload
        def __init__(
                self, 
                *, 
                effective_available_memory_in_mb: Optional[int] = ..., 
                free_v_cpu_indexes_for_hpn: Optional[list[int]] = ..., 
                logical_core_count_per_core: Optional[int] = ..., 
                numa_node_index: Optional[int] = ..., 
                total_memory_in_mb: Optional[int] = ..., 
                v_cpu_indexes_for_hpn: Optional[list[int]] = ..., 
                v_cpu_indexes_for_root: Optional[list[int]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.OperationDisplay(_Model):
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


    class azure.mgmt.databoxedge.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Order(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[OrderProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OrderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.OrderProperties(_Model):
        contact_information: ContactDetails
        current_status: Optional[OrderStatus]
        delivery_tracking_info: Optional[list[TrackingInfo]]
        order_history: Optional[list[OrderStatus]]
        order_id: Optional[str]
        return_tracking_info: Optional[list[TrackingInfo]]
        serial_number: Optional[str]
        shipment_type: Optional[Union[str, ShipmentType]]
        shipping_address: Optional[Address]

        @overload
        def __init__(
                self, 
                *, 
                contact_information: ContactDetails, 
                shipment_type: Optional[Union[str, ShipmentType]] = ..., 
                shipping_address: Optional[Address] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.OrderStatus(_Model):
        additional_order_details: Optional[dict[str, str]]
        comments: Optional[str]
        status: Union[str, OrderState]
        tracking_information: Optional[TrackingInfo]
        update_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ..., 
                status: Union[str, OrderState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.PeriodicTimerEventTrigger(Trigger, discriminator='PeriodicTimerEvent'):
        id: str
        kind: Literal[TriggerEventType.PERIODIC_TIMER_EVENT]
        name: str
        properties: PeriodicTimerProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: PeriodicTimerProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.PeriodicTimerProperties(_Model):
        custom_context_tag: Optional[str]
        sink_info: RoleSinkInfo
        source_info: PeriodicTimerSourceInfo

        @overload
        def __init__(
                self, 
                *, 
                custom_context_tag: Optional[str] = ..., 
                sink_info: RoleSinkInfo, 
                source_info: PeriodicTimerSourceInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.PeriodicTimerSourceInfo(_Model):
        schedule: str
        start_time: datetime
        topic: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                schedule: str, 
                start_time: datetime, 
                topic: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.PlatformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.databoxedge.models.PosixComplianceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.databoxedge.models.ProactiveDiagnosticsConsent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databoxedge.models.ProactiveLogCollectionSettingsProperties(_Model):
        user_consent: Union[str, ProactiveDiagnosticsConsent]

        @overload
        def __init__(
                self, 
                *, 
                user_consent: Union[str, ProactiveDiagnosticsConsent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.models.RawCertificateData(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        certificate: str

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                certificate: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.RefreshDetails(_Model):
        error_manifest_file: Optional[str]
        in_progress_refresh_job_id: Optional[str]
        last_completed_refresh_job_time_in_utc: Optional[datetime]
        last_job: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_manifest_file: Optional[str] = ..., 
                in_progress_refresh_job_id: Optional[str] = ..., 
                last_completed_refresh_job_time_in_utc: Optional[datetime] = ..., 
                last_job: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.RemoteApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_APPLICATIONS = "AllApplications"
        LOCAL_UI = "LocalUI"
        POWERSHELL = "Powershell"
        WAC = "WAC"


    class azure.mgmt.databoxedge.models.RemoteSupportSettings(_Model):
        access_level: Optional[Union[str, AccessLevel]]
        expiration_time_stamp_in_utc: Optional[datetime]
        remote_application_type: Optional[Union[str, RemoteApplicationType]]

        @overload
        def __init__(
                self, 
                *, 
                access_level: Optional[Union[str, AccessLevel]] = ..., 
                expiration_time_stamp_in_utc: Optional[datetime] = ..., 
                remote_application_type: Optional[Union[str, RemoteApplicationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.databoxedge.models.ResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, MsiIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, MsiIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ResourceMoveDetails(_Model):
        operation_in_progress: Optional[Union[str, ResourceMoveStatus]]
        operation_in_progress_lock_timeout_in_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                operation_in_progress: Optional[Union[str, ResourceMoveStatus]] = ..., 
                operation_in_progress_lock_timeout_in_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ResourceMoveStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        RESOURCE_MOVE_FAILED = "ResourceMoveFailed"
        RESOURCE_MOVE_IN_PROGRESS = "ResourceMoveInProgress"


    class azure.mgmt.databoxedge.models.Role(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.RoleSinkInfo(_Model):
        role_id: str

        @overload
        def __init__(
                self, 
                *, 
                role_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.Secret(_Model):
        encrypted_secret: Optional[AsymmetricEncryptedSecret]
        key_vault_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encrypted_secret: Optional[AsymmetricEncryptedSecret] = ..., 
                key_vault_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.SecuritySettings(ARMBaseModel):
        id: str
        name: str
        properties: SecuritySettingsProperties
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SecuritySettingsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.SecuritySettingsProperties(_Model):
        device_admin_password: AsymmetricEncryptedSecret

        @overload
        def __init__(
                self, 
                *, 
                device_admin_password: AsymmetricEncryptedSecret
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ServiceSpecification(_Model):
        metric_specifications: Optional[list[MetricSpecificationV1]]

        @overload
        def __init__(
                self, 
                *, 
                metric_specifications: Optional[list[MetricSpecificationV1]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Share(ProxyResource):
        id: str
        name: str
        properties: ShareProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ShareProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.ShareAccessProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.mgmt.databoxedge.models.ShareAccessRight(_Model):
        access_type: Union[str, ShareAccessType]
        share_id: str

        @overload
        def __init__(
                self, 
                *, 
                access_type: Union[str, ShareAccessType], 
                share_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.ShareAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGE = "Change"
        CUSTOM = "Custom"
        READ = "Read"


    class azure.mgmt.databoxedge.models.ShareProperties(_Model):
        access_protocol: Union[str, ShareAccessProtocol]
        azure_container_info: Optional[AzureContainerInfo]
        client_access_rights: Optional[list[ClientAccessRight]]
        data_policy: Optional[Union[str, DataPolicy]]
        description: Optional[str]
        monitoring_status: Union[str, MonitoringStatus]
        refresh_details: Optional[RefreshDetails]
        share_mappings: Optional[list[MountPointMap]]
        share_status: Union[str, ShareStatus]
        user_access_rights: Optional[list[UserAccessRight]]

        @overload
        def __init__(
                self, 
                *, 
                access_protocol: Union[str, ShareAccessProtocol], 
                azure_container_info: Optional[AzureContainerInfo] = ..., 
                client_access_rights: Optional[list[ClientAccessRight]] = ..., 
                data_policy: Optional[Union[str, DataPolicy]] = ..., 
                description: Optional[str] = ..., 
                monitoring_status: Union[str, MonitoringStatus], 
                refresh_details: Optional[RefreshDetails] = ..., 
                share_status: Union[str, ShareStatus], 
                user_access_rights: Optional[list[UserAccessRight]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.models.Sku(_Model):
        name: Optional[Union[str, SkuName]]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.SkuAvailability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.databoxedge.models.SkuCapability(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.databoxedge.models.SkuCost(_Model):
        extended_unit: Optional[str]
        meter_id: Optional[str]
        quantity: Optional[int]


    class azure.mgmt.databoxedge.models.SkuLocationInfo(_Model):
        location: Optional[str]
        sites: Optional[list[str]]
        zones: Optional[list[str]]


    class azure.mgmt.databoxedge.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE = "Edge"
        EDGE_MR_MINI = "EdgeMR_Mini"
        EDGE_MR_TCP = "EdgeMR_TCP"
        EDGE_PR_BASE = "EdgePR_Base"
        EDGE_PR_BASE_UPS = "EdgePR_Base_UPS"
        EDGE_P_BASE = "EdgeP_Base"
        EDGE_P_HIGH = "EdgeP_High"
        EP2_128_1_T4_MX1_W = "EP2_128_1T4_Mx1_W"
        EP2_128_GPU1_MX1_W = "EP2_128_GPU1_Mx1_W"
        EP2_256_2_T4_W = "EP2_256_2T4_W"
        EP2_256_GPU2_MX1 = "EP2_256_GPU2_Mx1"
        EP2_64_1_VPU_W = "EP2_64_1VPU_W"
        EP2_64_MX1_W = "EP2_64_Mx1_W"
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


    class azure.mgmt.databoxedge.models.StorageAccount(ProxyResource):
        id: str
        name: str
        properties: StorageAccountProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: StorageAccountProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.StorageAccountCredential(ProxyResource):
        id: str
        name: str
        properties: StorageAccountCredentialProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: StorageAccountCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.StorageAccountCredentialProperties(_Model):
        account_key: Optional[AsymmetricEncryptedSecret]
        account_type: Union[str, AccountType]
        alias: str
        blob_domain_name: Optional[str]
        connection_string: Optional[str]
        ssl_status: Union[str, SSLStatus]
        storage_account_id: Optional[str]
        user_name: Optional[str]

        @overload
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
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.StorageAccountProperties(_Model):
        blob_endpoint: Optional[str]
        container_count: Optional[int]
        data_policy: Union[str, DataPolicy]
        description: Optional[str]
        storage_account_credential_id: Optional[str]
        storage_account_status: Optional[Union[str, StorageAccountStatus]]

        @overload
        def __init__(
                self, 
                *, 
                data_policy: Union[str, DataPolicy], 
                description: Optional[str] = ..., 
                storage_account_credential_id: Optional[str] = ..., 
                storage_account_status: Optional[Union[str, StorageAccountStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.StorageAccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEEDS_ATTENTION = "NeedsAttention"
        OFFLINE = "Offline"
        OK = "OK"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.databoxedge.models.SubscriptionProperties(_Model):
        location_placement_id: Optional[str]
        quota_id: Optional[str]
        registered_features: Optional[list[SubscriptionRegisteredFeatures]]
        serialized_details: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location_placement_id: Optional[str] = ..., 
                quota_id: Optional[str] = ..., 
                registered_features: Optional[list[SubscriptionRegisteredFeatures]] = ..., 
                serialized_details: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.SubscriptionRegisteredFeatures(_Model):
        name: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        REGISTERED = "Registered"
        SUSPENDED = "Suspended"
        UNREGISTERED = "Unregistered"
        WARNED = "Warned"


    class azure.mgmt.databoxedge.models.SupportPackageRequestProperties(_Model):
        include: Optional[str]
        maximum_time_stamp: Optional[datetime]
        minimum_time_stamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                include: Optional[str] = ..., 
                maximum_time_stamp: Optional[datetime] = ..., 
                minimum_time_stamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.SymmetricKey(_Model):
        connection_string: Optional[AsymmetricEncryptedSecret]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[AsymmetricEncryptedSecret] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.SystemData(_Model):
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


    class azure.mgmt.databoxedge.models.TimeGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PT12_H = "PT12H"
        PT15_M = "PT15M"
        PT1_D = "PT1D"
        PT1_H = "PT1H"
        PT1_M = "PT1M"
        PT30_M = "PT30M"
        PT5_M = "PT5M"
        PT6_H = "PT6H"


    class azure.mgmt.databoxedge.models.TrackedResource(Resource):
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


    class azure.mgmt.databoxedge.models.TrackingInfo(_Model):
        carrier_name: Optional[str]
        serial_number: Optional[str]
        tracking_id: Optional[str]
        tracking_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                carrier_name: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                tracking_id: Optional[str] = ..., 
                tracking_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.Trigger(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.TriggerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_EVENT = "FileEvent"
        PERIODIC_TIMER_EVENT = "PeriodicTimerEvent"


    class azure.mgmt.databoxedge.models.TriggerSupportPackageRequest(ARMBaseModel):
        id: str
        name: str
        properties: SupportPackageRequestProperties
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SupportPackageRequestProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.UpdateDetails(_Model):
        estimated_install_time_in_mins: Optional[int]
        friendly_version_number: Optional[str]
        installation_impact: Optional[Union[str, InstallationImpact]]
        reboot_behavior: Optional[Union[str, InstallRebootBehavior]]
        status: Optional[Union[str, UpdateStatus]]
        target_version: Optional[str]
        update_size: Optional[float]
        update_title: Optional[str]
        update_type: Optional[Union[str, UpdateType]]

        @overload
        def __init__(
                self, 
                *, 
                estimated_install_time_in_mins: Optional[int] = ..., 
                friendly_version_number: Optional[str] = ..., 
                installation_impact: Optional[Union[str, InstallationImpact]] = ..., 
                reboot_behavior: Optional[Union[str, InstallRebootBehavior]] = ..., 
                status: Optional[Union[str, UpdateStatus]] = ..., 
                target_version: Optional[str] = ..., 
                update_size: Optional[float] = ..., 
                update_title: Optional[str] = ..., 
                update_type: Optional[Union[str, UpdateType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.UpdateDownloadProgress(_Model):
        download_phase: Optional[Union[str, DownloadPhase]]
        number_of_updates_downloaded: Optional[int]
        number_of_updates_to_download: Optional[int]
        percent_complete: Optional[int]
        total_bytes_downloaded: Optional[float]
        total_bytes_to_download: Optional[float]


    class azure.mgmt.databoxedge.models.UpdateInstallProgress(_Model):
        number_of_updates_installed: Optional[int]
        number_of_updates_to_install: Optional[int]
        percent_complete: Optional[int]


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


    class azure.mgmt.databoxedge.models.UpdateSummary(ProxyResource):
        id: str
        name: str
        properties: Optional[UpdateSummaryProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateSummaryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.UpdateSummaryProperties(_Model):
        device_last_scanned_date_time: Optional[datetime]
        device_version_number: Optional[str]
        friendly_device_version_name: Optional[str]
        in_progress_download_job_id: Optional[str]
        in_progress_download_job_started_date_time: Optional[datetime]
        in_progress_install_job_id: Optional[str]
        in_progress_install_job_started_date_time: Optional[datetime]
        last_completed_download_job_date_time: Optional[datetime]
        last_completed_download_job_id: Optional[str]
        last_completed_install_job_date_time: Optional[datetime]
        last_completed_install_job_id: Optional[str]
        last_completed_scan_job_date_time: Optional[datetime]
        last_download_job_status: Optional[Union[str, JobStatus]]
        last_install_job_status: Optional[Union[str, JobStatus]]
        last_successful_install_job_date_time: Optional[datetime]
        last_successful_scan_job_time: Optional[datetime]
        ongoing_update_operation: Optional[Union[str, UpdateOperation]]
        reboot_behavior: Optional[Union[str, InstallRebootBehavior]]
        total_number_of_updates_available: Optional[int]
        total_number_of_updates_pending_download: Optional[int]
        total_number_of_updates_pending_install: Optional[int]
        total_time_in_minutes: Optional[int]
        total_update_size_in_bytes: Optional[float]
        update_titles: Optional[list[str]]
        updates: Optional[list[UpdateDetails]]

        @overload
        def __init__(
                self, 
                *, 
                device_last_scanned_date_time: Optional[datetime] = ..., 
                device_version_number: Optional[str] = ..., 
                friendly_device_version_name: Optional[str] = ..., 
                last_completed_scan_job_date_time: Optional[datetime] = ..., 
                last_successful_install_job_date_time: Optional[datetime] = ..., 
                last_successful_scan_job_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.UpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRMWARE = "Firmware"
        KUBERNETES = "Kubernetes"
        SOFTWARE = "Software"


    class azure.mgmt.databoxedge.models.UploadCertificateRequest(_Model):
        properties: RawCertificateData

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: RawCertificateData
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.UploadCertificateResponse(_Model):
        aad_audience: Optional[str]
        aad_authority: Optional[str]
        aad_tenant_id: Optional[str]
        auth_type: Optional[Union[str, AuthenticationType]]
        azure_management_endpoint_audience: Optional[str]
        resource_id: Optional[str]
        service_principal_client_id: Optional[str]
        service_principal_object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth_type: Optional[Union[str, AuthenticationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.User(ProxyResource):
        id: str
        name: str
        properties: UserProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: UserProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databoxedge.models.UserAccessRight(_Model):
        access_type: Union[str, ShareAccessType]
        user_id: str

        @overload
        def __init__(
                self, 
                *, 
                access_type: Union[str, ShareAccessType], 
                user_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.UserProperties(_Model):
        encrypted_password: Optional[AsymmetricEncryptedSecret]
        share_access_rights: Optional[list[ShareAccessRight]]
        user_type: Union[str, UserType]

        @overload
        def __init__(
                self, 
                *, 
                encrypted_password: Optional[AsymmetricEncryptedSecret] = ..., 
                user_type: Union[str, UserType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.UserType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM = "ARM"
        LOCAL_MANAGEMENT = "LocalManagement"
        SHARE = "Share"


    class azure.mgmt.databoxedge.models.VmMemory(_Model):
        current_memory_usage_mb: Optional[int]
        startup_memory_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                current_memory_usage_mb: Optional[int] = ..., 
                startup_memory_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databoxedge.models.VmPlacementRequestResult(_Model):
        is_feasible: Optional[bool]
        message: Optional[str]
        message_code: Optional[str]
        vm_size: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                is_feasible: Optional[bool] = ..., 
                message: Optional[str] = ..., 
                message_code: Optional[str] = ..., 
                vm_size: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.databoxedge.operations.DeviceCapacityCheckOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_check_resource_creation_feasibility(
                self, 
                resource_group_name: str, 
                device_name: str, 
                device_capacity_request_info: DeviceCapacityRequestInfo, 
                *, 
                capacity_name: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_check_resource_creation_feasibility(
                self, 
                resource_group_name: str, 
                device_name: str, 
                device_capacity_request_info: DeviceCapacityRequestInfo, 
                *, 
                capacity_name: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_check_resource_creation_feasibility(
                self, 
                resource_group_name: str, 
                device_name: str, 
                device_capacity_request_info: IO[bytes], 
                *, 
                capacity_name: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.databoxedge.operations.DeviceCapacityInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_device_capacity_info(
                self, 
                resource_group_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> DeviceCapacityInfo: ...


    class azure.mgmt.databoxedge.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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

        @overload
        def create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        def create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: DataBoxEdgeDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

        @overload
        def create_or_update(
                self, 
                device_name: str, 
                resource_group_name: str, 
                data_box_edge_device: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoxEdgeDevice: ...

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
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DataBoxEdgeDevice]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[str] = ..., 
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


    class azure.mgmt.databoxedge.operations.DiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                proactive_log_collection_settings: DiagnosticProactiveLogCollectionSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticProactiveLogCollectionSettings]: ...

        @overload
        def begin_update_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                proactive_log_collection_settings: DiagnosticProactiveLogCollectionSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticProactiveLogCollectionSettings]: ...

        @overload
        def begin_update_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                proactive_log_collection_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticProactiveLogCollectionSettings]: ...

        @overload
        def begin_update_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                diagnostic_remote_support_settings: DiagnosticRemoteSupportSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticRemoteSupportSettings]: ...

        @overload
        def begin_update_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                diagnostic_remote_support_settings: DiagnosticRemoteSupportSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticRemoteSupportSettings]: ...

        @overload
        def begin_update_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                diagnostic_remote_support_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticRemoteSupportSettings]: ...

        @distributed_trace
        def get_diagnostic_proactive_log_collection_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DiagnosticProactiveLogCollectionSettings: ...

        @distributed_trace
        def get_diagnostic_remote_support_settings(
                self, 
                device_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> DiagnosticRemoteSupportSettings: ...


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


    class azure.mgmt.databoxedge.operations.SupportPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_trigger_support_package(
                self, 
                device_name: str, 
                resource_group_name: str, 
                trigger_support_package_request: TriggerSupportPackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_support_package(
                self, 
                device_name: str, 
                resource_group_name: str, 
                trigger_support_package_request: TriggerSupportPackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_support_package(
                self, 
                device_name: str, 
                resource_group_name: str, 
                trigger_support_package_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[User]: ...


namespace azure.mgmt.databoxedge.types

    class azure.mgmt.databoxedge.types.ARMBaseModel(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.databoxedge.types.AddonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC_FOR_KUBERNETES = "ArcForKubernetes"
        IOT_EDGE = "IotEdge"


    class azure.mgmt.databoxedge.types.Address(TypedDict, total=False):
        key "addressLine1": str
        key "addressLine2": str
        key "addressLine3": str
        key "city": str
        key "country": Required[str]
        key "postalCode": str
        key "state": str
        address_line1: str
        address_line2: str
        address_line3: str
        city: str
        country: str
        postal_code: str
        state: str


    class azure.mgmt.databoxedge.types.ArcAddon(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[AddonType.ARC_FOR_KUBERNETES]]
        key "name": str
        key "properties": Required[ArcAddonProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[AddonType.ARC_FOR_KUBERNETES]
        name: str
        properties: ArcAddonProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.ArcAddonProperties(TypedDict, total=False):
        key "hostPlatform": Union[str, PlatformType]
        key "hostPlatformType": Union[str, HostPlatformType]
        key "provisioningState": Union[str, AddonState]
        key "resourceGroupName": Required[str]
        key "resourceLocation": Required[str]
        key "resourceName": Required[str]
        key "subscriptionId": Required[str]
        key "version": str
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        provisioning_state: Union[str, AddonState]
        resource_group_name: str
        resource_location: str
        resource_name: str
        subscription_id: str
        version: str


    class azure.mgmt.databoxedge.types.AsymmetricEncryptedSecret(TypedDict, total=False):
        key "encryptionAlgorithm": Required[Union[str, EncryptionAlgorithm]]
        key "encryptionCertThumbprint": str
        key "value": Required[str]
        encryption_algorithm: Union[str, EncryptionAlgorithm]
        encryption_cert_thumbprint: str
        value: str


    class azure.mgmt.databoxedge.types.Authentication(TypedDict, total=False):
        key "symmetricKey": ForwardRef('SymmetricKey', module='types')
        symmetric_key: SymmetricKey


    class azure.mgmt.databoxedge.types.AzureContainerInfo(TypedDict, total=False):
        key "containerName": Required[str]
        key "dataFormat": Required[Union[str, AzureContainerDataFormat]]
        key "storageAccountCredentialId": Required[str]
        container_name: str
        data_format: Union[str, AzureContainerDataFormat]
        storage_account_credential_id: str


    class azure.mgmt.databoxedge.types.BandwidthSchedule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[BandwidthScheduleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: BandwidthScheduleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.BandwidthScheduleProperties(TypedDict, total=False):
        key "days": Required[list[Union[str, DayOfWeek]]]
        key "rateInMbps": Required[int]
        key "start": Required[str]
        key "stop": Required[str]
        days: list[Union[str, DayOfWeek]]
        rate_in_mbps: int
        start: str
        stop: str


    class azure.mgmt.databoxedge.types.ClientAccessRight(TypedDict, total=False):
        key "accessPermission": Required[Union[str, ClientPermissionType]]
        key "client": Required[str]
        access_permission: Union[str, ClientPermissionType]
        client: str


    class azure.mgmt.databoxedge.types.CloudEdgeManagementRole(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[RoleTypes.CLOUD_EDGE_MANAGEMENT]]
        key "name": str
        key "properties": ForwardRef('CloudEdgeManagementRoleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[RoleTypes.CLOUD_EDGE_MANAGEMENT]
        name: str
        properties: CloudEdgeManagementRoleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.CloudEdgeManagementRoleProperties(TypedDict, total=False):
        key "edgeProfile": ForwardRef('EdgeProfile', module='types')
        key "localManagementStatus": Union[str, RoleStatus]
        key "roleStatus": Required[Union[str, RoleStatus]]
        edge_profile: EdgeProfile
        local_management_status: Union[str, RoleStatus]
        role_status: Union[str, RoleStatus]


    class azure.mgmt.databoxedge.types.CniConfig(TypedDict, total=False):
        key "podSubnet": str
        key "serviceSubnet": str
        key "type": str
        key "version": str
        pod_subnet: str
        service_subnet: str
        type: str
        version: str


    class azure.mgmt.databoxedge.types.ComputeResource(TypedDict, total=False):
        key "memoryInGB": Required[int]
        key "processorCount": Required[int]
        memory_in_gb: int
        processor_count: int


    class azure.mgmt.databoxedge.types.ContactDetails(TypedDict, total=False):
        key "companyName": Required[str]
        key "contactPerson": Required[str]
        key "emailList": Required[list[str]]
        key "phone": Required[str]
        company_name: str
        contact_person: str
        email_list: list[str]
        phone: str


    class azure.mgmt.databoxedge.types.Container(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ContainerProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ContainerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.ContainerProperties(TypedDict, total=False):
        key "containerStatus": Union[str, ContainerStatus]
        key "createdDateTime": str
        key "dataFormat": Required[Union[str, AzureContainerDataFormat]]
        key "refreshDetails": ForwardRef('RefreshDetails', module='types')
        container_status: Union[str, ContainerStatus]
        created_date_time: str
        data_format: Union[str, AzureContainerDataFormat]
        refresh_details: RefreshDetails


    class azure.mgmt.databoxedge.types.DataBoxEdgeDevice(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "kind": Union[str, DataBoxEdgeDeviceKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DataBoxEdgeDeviceProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: ResourceIdentity
        kind: Union[str, DataBoxEdgeDeviceKind]
        location: str
        name: str
        properties: DataBoxEdgeDeviceProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.databoxedge.types.DataBoxEdgeDeviceExtendedInfoPatch(TypedDict, total=False):
        key "channelIntegrityKeyName": str
        key "channelIntegrityKeyVersion": str
        key "clientSecretStoreId": str
        key "clientSecretStoreUrl": str
        key "syncStatus": Union[str, KeyVaultSyncStatus]
        channel_integrity_key_name: str
        channel_integrity_key_version: str
        client_secret_store_id: str
        client_secret_store_url: str
        sync_status: Union[str, KeyVaultSyncStatus]


    class azure.mgmt.databoxedge.types.DataBoxEdgeDevicePatch(TypedDict, total=False):
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "properties": ForwardRef('DataBoxEdgeDevicePropertiesPatch', module='types')
        identity: ResourceIdentity
        properties: DataBoxEdgeDevicePropertiesPatch
        tags: dict[str, str]


    class azure.mgmt.databoxedge.types.DataBoxEdgeDeviceProperties(TypedDict, total=False):
        key "culture": str
        key "dataBoxEdgeDeviceStatus": Union[str, DataBoxEdgeDeviceStatus]
        key "dataResidency": ForwardRef('DataResidency', module='types')
        key "description": str
        key "deviceHcsVersion": str
        key "deviceLocalCapacity": int
        key "deviceModel": str
        key "deviceSoftwareVersion": str
        key "deviceType": Union[str, DeviceType]
        key "edgeProfile": ForwardRef('EdgeProfile', module='types')
        key "friendlyName": str
        key "kubernetesWorkloadProfile": str
        key "modelDescription": str
        key "nodeCount": int
        key "resourceMoveDetails": ForwardRef('ResourceMoveDetails', module='types')
        key "serialNumber": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "timeZone": str
        configuredRoleTypes: list[Union[str, RoleTypes]]
        configured_role_types: list[Union[str, RoleTypes]]
        culture: str
        data_box_edge_device_status: Union[str, DataBoxEdgeDeviceStatus]
        data_residency: DataResidency
        description: str
        device_hcs_version: str
        device_local_capacity: int
        device_model: str
        device_software_version: str
        device_type: Union[str, DeviceType]
        edge_profile: EdgeProfile
        friendly_name: str
        kubernetes_workload_profile: str
        model_description: str
        node_count: int
        resource_move_details: ResourceMoveDetails
        serial_number: str
        system_data: SystemData
        time_zone: str


    class azure.mgmt.databoxedge.types.DataBoxEdgeDevicePropertiesPatch(TypedDict, total=False):
        key "edgeProfile": ForwardRef('EdgeProfilePatch', module='types')
        edge_profile: EdgeProfilePatch


    class azure.mgmt.databoxedge.types.DataResidency(TypedDict, total=False):
        key "type": Union[str, DataResidencyType]
        type: Union[str, DataResidencyType]


    class azure.mgmt.databoxedge.types.DeviceCapacityRequestInfo(TypedDict, total=False):
        key "properties": Required[DeviceCapacityRequestInfoProperties]
        properties: DeviceCapacityRequestInfoProperties


    class azure.mgmt.databoxedge.types.DeviceCapacityRequestInfoProperties(TypedDict, total=False):
        key "vmPlacementQuery": Required[list[list[str]]]
        vmPlacementResults: list[VmPlacementRequestResult]
        vm_placement_query: list[list[str]]
        vm_placement_results: list[VmPlacementRequestResult]


    class azure.mgmt.databoxedge.types.DiagnosticProactiveLogCollectionSettings(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ProactiveLogCollectionSettingsProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProactiveLogCollectionSettingsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.DiagnosticRemoteSupportSettings(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[DiagnosticRemoteSupportSettingsProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DiagnosticRemoteSupportSettingsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.DiagnosticRemoteSupportSettingsProperties(TypedDict, total=False):
        remoteSupportSettingsList: list[RemoteSupportSettings]
        remote_support_settings_list: list[RemoteSupportSettings]


    class azure.mgmt.databoxedge.types.EdgeProfile(TypedDict, total=False):
        key "subscription": ForwardRef('EdgeProfileSubscription', module='types')
        subscription: EdgeProfileSubscription


    class azure.mgmt.databoxedge.types.EdgeProfilePatch(TypedDict, total=False):
        key "subscription": ForwardRef('EdgeProfileSubscriptionPatch', module='types')
        subscription: EdgeProfileSubscriptionPatch


    class azure.mgmt.databoxedge.types.EdgeProfileSubscription(TypedDict, total=False):
        key "id": str
        key "properties": ForwardRef('SubscriptionProperties', module='types')
        key "registrationDate": str
        key "registrationId": str
        key "state": Union[str, SubscriptionState]
        key "subscriptionId": str
        id: str
        properties: SubscriptionProperties
        registration_date: str
        registration_id: str
        state: Union[str, SubscriptionState]
        subscription_id: str


    class azure.mgmt.databoxedge.types.EdgeProfileSubscriptionPatch(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.databoxedge.types.EtcdInfo(TypedDict, total=False):
        key "type": str
        key "version": str
        type: str
        version: str


    class azure.mgmt.databoxedge.types.FileEventTrigger(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[TriggerEventType.FILE_EVENT]]
        key "name": str
        key "properties": Required[FileTriggerProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[TriggerEventType.FILE_EVENT]
        name: str
        properties: FileTriggerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.FileSourceInfo(TypedDict, total=False):
        key "shareId": Required[str]
        share_id: str


    class azure.mgmt.databoxedge.types.FileTriggerProperties(TypedDict, total=False):
        key "customContextTag": str
        key "sinkInfo": Required[RoleSinkInfo]
        key "sourceInfo": Required[FileSourceInfo]
        custom_context_tag: str
        sink_info: RoleSinkInfo
        source_info: FileSourceInfo


    class azure.mgmt.databoxedge.types.ImageRepositoryCredential(TypedDict, total=False):
        key "imageRepositoryUrl": Required[str]
        key "password": ForwardRef('AsymmetricEncryptedSecret', module='types')
        key "userName": Required[str]
        image_repository_url: str
        password: AsymmetricEncryptedSecret
        user_name: str


    class azure.mgmt.databoxedge.types.IoTAddon(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[AddonType.IOT_EDGE]]
        key "name": str
        key "properties": Required[IoTAddonProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[AddonType.IOT_EDGE]
        name: str
        properties: IoTAddonProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.IoTAddonProperties(TypedDict, total=False):
        key "hostPlatform": Union[str, PlatformType]
        key "hostPlatformType": Union[str, HostPlatformType]
        key "ioTDeviceDetails": Required[IoTDeviceInfo]
        key "ioTEdgeDeviceDetails": Required[IoTDeviceInfo]
        key "provisioningState": Union[str, AddonState]
        key "version": str
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        io_t_device_details: IoTDeviceInfo
        io_t_edge_device_details: IoTDeviceInfo
        provisioning_state: Union[str, AddonState]
        version: str


    class azure.mgmt.databoxedge.types.IoTDeviceInfo(TypedDict, total=False):
        key "authentication": ForwardRef('Authentication', module='types')
        key "deviceId": Required[str]
        key "ioTHostHub": Required[str]
        key "ioTHostHubId": str
        authentication: Authentication
        device_id: str
        io_t_host_hub: str
        io_t_host_hub_id: str


    class azure.mgmt.databoxedge.types.IoTEdgeAgentInfo(TypedDict, total=False):
        key "imageName": Required[str]
        key "imageRepository": ForwardRef('ImageRepositoryCredential', module='types')
        key "tag": Required[str]
        image_name: str
        image_repository: ImageRepositoryCredential
        tag: str


    class azure.mgmt.databoxedge.types.IoTRole(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[RoleTypes.IOT]]
        key "name": str
        key "properties": ForwardRef('IoTRoleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[RoleTypes.IOT]
        name: str
        properties: IoTRoleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.IoTRoleProperties(TypedDict, total=False):
        key "computeResource": ForwardRef('ComputeResource', module='types')
        key "hostPlatform": Required[Union[str, PlatformType]]
        key "hostPlatformType": Union[str, HostPlatformType]
        key "ioTDeviceDetails": Required[IoTDeviceInfo]
        key "ioTEdgeAgentInfo": ForwardRef('IoTEdgeAgentInfo', module='types')
        key "ioTEdgeDeviceDetails": Required[IoTDeviceInfo]
        key "roleStatus": Required[Union[str, RoleStatus]]
        compute_resource: ComputeResource
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        io_t_device_details: IoTDeviceInfo
        io_t_edge_agent_info: IoTEdgeAgentInfo
        io_t_edge_device_details: IoTDeviceInfo
        role_status: Union[str, RoleStatus]
        shareMappings: list[MountPointMap]
        share_mappings: list[MountPointMap]


    class azure.mgmt.databoxedge.types.KubernetesClusterInfo(TypedDict, total=False):
        key "etcdInfo": ForwardRef('EtcdInfo', module='types')
        key "version": Required[str]
        etcd_info: EtcdInfo
        nodes: list[NodeInfo]
        version: str


    class azure.mgmt.databoxedge.types.KubernetesIPConfiguration(TypedDict, total=False):
        key "ipAddress": str
        key "port": str
        ip_address: str
        port: str


    class azure.mgmt.databoxedge.types.KubernetesRole(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[RoleTypes.KUBERNETES]]
        key "name": str
        key "properties": ForwardRef('KubernetesRoleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[RoleTypes.KUBERNETES]
        name: str
        properties: KubernetesRoleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.KubernetesRoleCompute(TypedDict, total=False):
        key "memoryInBytes": int
        key "processorCount": int
        key "vmProfile": Required[str]
        memory_in_bytes: int
        processor_count: int
        vm_profile: str


    class azure.mgmt.databoxedge.types.KubernetesRoleNetwork(TypedDict, total=False):
        key "cniConfig": ForwardRef('CniConfig', module='types')
        key "loadBalancerConfig": ForwardRef('LoadBalancerConfig', module='types')
        cni_config: CniConfig
        load_balancer_config: LoadBalancerConfig


    class azure.mgmt.databoxedge.types.KubernetesRoleProperties(TypedDict, total=False):
        key "hostPlatform": Required[Union[str, PlatformType]]
        key "hostPlatformType": Union[str, HostPlatformType]
        key "kubernetesClusterInfo": Required[KubernetesClusterInfo]
        key "kubernetesRoleResources": Required[KubernetesRoleResources]
        key "provisioningState": Union[str, KubernetesState]
        key "roleStatus": Required[Union[str, RoleStatus]]
        host_platform: Union[str, PlatformType]
        host_platform_type: Union[str, HostPlatformType]
        kubernetes_cluster_info: KubernetesClusterInfo
        kubernetes_role_resources: KubernetesRoleResources
        provisioning_state: Union[str, KubernetesState]
        role_status: Union[str, RoleStatus]


    class azure.mgmt.databoxedge.types.KubernetesRoleResources(TypedDict, total=False):
        key "compute": Required[KubernetesRoleCompute]
        key "network": ForwardRef('KubernetesRoleNetwork', module='types')
        key "storage": ForwardRef('KubernetesRoleStorage', module='types')
        compute: KubernetesRoleCompute
        network: KubernetesRoleNetwork
        storage: KubernetesRoleStorage


    class azure.mgmt.databoxedge.types.KubernetesRoleStorage(TypedDict, total=False):
        endpoints: list[MountPointMap]
        storageClasses: list[KubernetesRoleStorageClassInfo]
        storage_classes: list[KubernetesRoleStorageClassInfo]


    class azure.mgmt.databoxedge.types.KubernetesRoleStorageClassInfo(TypedDict, total=False):
        key "name": str
        key "posixCompliant": Union[str, PosixComplianceStatus]
        key "type": str
        name: str
        posix_compliant: Union[str, PosixComplianceStatus]
        type: str


    class azure.mgmt.databoxedge.types.LoadBalancerConfig(TypedDict, total=False):
        key "type": str
        key "version": str
        ipRange: list[str]
        ip_range: list[str]
        type: str
        version: str


    class azure.mgmt.databoxedge.types.MECRole(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[RoleTypes.MEC]]
        key "name": str
        key "properties": ForwardRef('MECRoleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[RoleTypes.MEC]
        name: str
        properties: MECRoleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.MECRoleProperties(TypedDict, total=False):
        key "connectionString": ForwardRef('AsymmetricEncryptedSecret', module='types')
        key "controllerEndpoint": str
        key "resourceUniqueId": str
        key "roleStatus": Required[Union[str, RoleStatus]]
        connection_string: AsymmetricEncryptedSecret
        controller_endpoint: str
        resource_unique_id: str
        role_status: Union[str, RoleStatus]


    class azure.mgmt.databoxedge.types.MetricConfiguration(TypedDict, total=False):
        key "counterSets": Required[list[MetricCounterSet]]
        key "mdmAccount": str
        key "metricNameSpace": str
        key "resourceId": Required[str]
        counter_sets: list[MetricCounterSet]
        mdm_account: str
        metric_name_space: str
        resource_id: str


    class azure.mgmt.databoxedge.types.MetricCounter(TypedDict, total=False):
        key "instance": str
        key "name": Required[str]
        additionalDimensions: list[MetricDimension]
        additional_dimensions: list[MetricDimension]
        dimensionFilter: list[MetricDimension]
        dimension_filter: list[MetricDimension]
        instance: str
        name: str


    class azure.mgmt.databoxedge.types.MetricCounterSet(TypedDict, total=False):
        key "counters": Required[list[MetricCounter]]
        counters: list[MetricCounter]


    class azure.mgmt.databoxedge.types.MetricDimension(TypedDict, total=False):
        key "sourceName": Required[str]
        key "sourceType": Required[str]
        source_name: str
        source_type: str


    class azure.mgmt.databoxedge.types.MonitoringMetricConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[MonitoringMetricConfigurationProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MonitoringMetricConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.MonitoringMetricConfigurationProperties(TypedDict, total=False):
        key "metricConfigurations": Required[list[MetricConfiguration]]
        metric_configurations: list[MetricConfiguration]


    class azure.mgmt.databoxedge.types.MountPointMap(TypedDict, total=False):
        key "mountPoint": str
        key "mountType": Union[str, MountType]
        key "roleId": str
        key "roleType": Union[str, RoleTypes]
        key "shareId": Required[str]
        mount_point: str
        mount_type: Union[str, MountType]
        role_id: str
        role_type: Union[str, RoleTypes]
        share_id: str


    class azure.mgmt.databoxedge.types.NodeInfo(TypedDict, total=False):
        key "name": str
        key "type": Union[str, KubernetesNodeType]
        ipConfiguration: list[KubernetesIPConfiguration]
        ip_configuration: list[KubernetesIPConfiguration]
        name: str
        type: Union[str, KubernetesNodeType]


    class azure.mgmt.databoxedge.types.Order(ProxyResource):
        key "id": str
        key "kind": str
        key "name": str
        key "properties": ForwardRef('OrderProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: str
        name: str
        properties: OrderProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.OrderProperties(TypedDict, total=False):
        key "contactInformation": Required[ContactDetails]
        key "currentStatus": ForwardRef('OrderStatus', module='types')
        key "orderId": str
        key "serialNumber": str
        key "shipmentType": Union[str, ShipmentType]
        key "shippingAddress": ForwardRef('Address', module='types')
        contact_information: ContactDetails
        current_status: OrderStatus
        deliveryTrackingInfo: list[TrackingInfo]
        delivery_tracking_info: list[TrackingInfo]
        orderHistory: list[OrderStatus]
        order_history: list[OrderStatus]
        order_id: str
        returnTrackingInfo: list[TrackingInfo]
        return_tracking_info: list[TrackingInfo]
        serial_number: str
        shipment_type: Union[str, ShipmentType]
        shipping_address: Address


    class azure.mgmt.databoxedge.types.OrderStatus(TypedDict, total=False):
        key "comments": str
        key "status": Required[Union[str, OrderState]]
        key "trackingInformation": ForwardRef('TrackingInfo', module='types')
        key "updateDateTime": str
        additionalOrderDetails: dict[str, str]
        additional_order_details: dict[str, str]
        comments: str
        status: Union[str, OrderState]
        tracking_information: TrackingInfo
        update_date_time: str


    class azure.mgmt.databoxedge.types.PeriodicTimerEventTrigger(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[TriggerEventType.PERIODIC_TIMER_EVENT]]
        key "name": str
        key "properties": Required[PeriodicTimerProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[TriggerEventType.PERIODIC_TIMER_EVENT]
        name: str
        properties: PeriodicTimerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.PeriodicTimerProperties(TypedDict, total=False):
        key "customContextTag": str
        key "sinkInfo": Required[RoleSinkInfo]
        key "sourceInfo": Required[PeriodicTimerSourceInfo]
        custom_context_tag: str
        sink_info: RoleSinkInfo
        source_info: PeriodicTimerSourceInfo


    class azure.mgmt.databoxedge.types.PeriodicTimerSourceInfo(TypedDict, total=False):
        key "schedule": Required[str]
        key "startTime": Required[str]
        key "topic": str
        schedule: str
        start_time: str
        topic: str


    class azure.mgmt.databoxedge.types.ProactiveLogCollectionSettingsProperties(TypedDict, total=False):
        key "userConsent": Required[Union[str, ProactiveDiagnosticsConsent]]
        user_consent: Union[str, ProactiveDiagnosticsConsent]


    class azure.mgmt.databoxedge.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.RawCertificateData(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "certificate": Required[str]
        authentication_type: Union[str, AuthenticationType]
        certificate: str


    class azure.mgmt.databoxedge.types.RefreshDetails(TypedDict, total=False):
        key "errorManifestFile": str
        key "inProgressRefreshJobId": str
        key "lastCompletedRefreshJobTimeInUTC": str
        key "lastJob": str
        error_manifest_file: str
        in_progress_refresh_job_id: str
        last_completed_refresh_job_time_in_utc: str
        last_job: str


    class azure.mgmt.databoxedge.types.RemoteSupportSettings(TypedDict, total=False):
        key "accessLevel": Union[str, AccessLevel]
        key "expirationTimeStampInUTC": str
        key "remoteApplicationType": Union[str, RemoteApplicationType]
        access_level: Union[str, AccessLevel]
        expiration_time_stamp_in_utc: str
        remote_application_type: Union[str, RemoteApplicationType]


    class azure.mgmt.databoxedge.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.ResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, MsiIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, MsiIdentityType]


    class azure.mgmt.databoxedge.types.ResourceMoveDetails(TypedDict, total=False):
        key "operationInProgress": Union[str, ResourceMoveStatus]
        key "operationInProgressLockTimeoutInUTC": str
        operation_in_progress: Union[str, ResourceMoveStatus]
        operation_in_progress_lock_timeout_in_utc: str


    class azure.mgmt.databoxedge.types.RoleSinkInfo(TypedDict, total=False):
        key "roleId": Required[str]
        role_id: str


    class azure.mgmt.databoxedge.types.RoleTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASA = "ASA"
        CLOUD_EDGE_MANAGEMENT = "CloudEdgeManagement"
        COGNITIVE = "Cognitive"
        FUNCTIONS = "Functions"
        IOT = "IOT"
        KUBERNETES = "Kubernetes"
        MEC = "MEC"


    class azure.mgmt.databoxedge.types.SecuritySettings(ARMBaseModel):
        key "id": str
        key "name": str
        key "properties": Required[SecuritySettingsProperties]
        key "type": str
        id: str
        name: str
        properties: SecuritySettingsProperties
        type: str


    class azure.mgmt.databoxedge.types.SecuritySettingsProperties(TypedDict, total=False):
        key "deviceAdminPassword": Required[AsymmetricEncryptedSecret]
        device_admin_password: AsymmetricEncryptedSecret


    class azure.mgmt.databoxedge.types.Share(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ShareProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ShareProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.ShareAccessRight(TypedDict, total=False):
        key "accessType": Required[Union[str, ShareAccessType]]
        key "shareId": Required[str]
        access_type: Union[str, ShareAccessType]
        share_id: str


    class azure.mgmt.databoxedge.types.ShareProperties(TypedDict, total=False):
        key "accessProtocol": Required[Union[str, ShareAccessProtocol]]
        key "azureContainerInfo": ForwardRef('AzureContainerInfo', module='types')
        key "dataPolicy": Union[str, DataPolicy]
        key "description": str
        key "monitoringStatus": Required[Union[str, MonitoringStatus]]
        key "refreshDetails": ForwardRef('RefreshDetails', module='types')
        key "shareStatus": Required[Union[str, ShareStatus]]
        access_protocol: Union[str, ShareAccessProtocol]
        azure_container_info: AzureContainerInfo
        clientAccessRights: list[ClientAccessRight]
        client_access_rights: list[ClientAccessRight]
        data_policy: Union[str, DataPolicy]
        description: str
        monitoring_status: Union[str, MonitoringStatus]
        refresh_details: RefreshDetails
        shareMappings: list[MountPointMap]
        share_mappings: list[MountPointMap]
        share_status: Union[str, ShareStatus]
        userAccessRights: list[UserAccessRight]
        user_access_rights: list[UserAccessRight]


    class azure.mgmt.databoxedge.types.Sku(TypedDict, total=False):
        key "name": Union[str, SkuName]
        key "tier": Union[str, SkuTier]
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.databoxedge.types.StorageAccount(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[StorageAccountProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StorageAccountProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.StorageAccountCredential(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[StorageAccountCredentialProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StorageAccountCredentialProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.StorageAccountCredentialProperties(TypedDict, total=False):
        key "accountKey": ForwardRef('AsymmetricEncryptedSecret', module='types')
        key "accountType": Required[Union[str, AccountType]]
        key "alias": Required[str]
        key "blobDomainName": str
        key "connectionString": str
        key "sslStatus": Required[Union[str, SSLStatus]]
        key "storageAccountId": str
        key "userName": str
        account_key: AsymmetricEncryptedSecret
        account_type: Union[str, AccountType]
        alias: str
        blob_domain_name: str
        connection_string: str
        ssl_status: Union[str, SSLStatus]
        storage_account_id: str
        user_name: str


    class azure.mgmt.databoxedge.types.StorageAccountProperties(TypedDict, total=False):
        key "blobEndpoint": str
        key "containerCount": int
        key "dataPolicy": Required[Union[str, DataPolicy]]
        key "description": str
        key "storageAccountCredentialId": str
        key "storageAccountStatus": Union[str, StorageAccountStatus]
        blob_endpoint: str
        container_count: int
        data_policy: Union[str, DataPolicy]
        description: str
        storage_account_credential_id: str
        storage_account_status: Union[str, StorageAccountStatus]


    class azure.mgmt.databoxedge.types.SubscriptionProperties(TypedDict, total=False):
        key "locationPlacementId": str
        key "quotaId": str
        key "serializedDetails": str
        key "tenantId": str
        location_placement_id: str
        quota_id: str
        registeredFeatures: list[SubscriptionRegisteredFeatures]
        registered_features: list[SubscriptionRegisteredFeatures]
        serialized_details: str
        tenant_id: str


    class azure.mgmt.databoxedge.types.SubscriptionRegisteredFeatures(TypedDict, total=False):
        key "name": str
        key "state": str
        name: str
        state: str


    class azure.mgmt.databoxedge.types.SupportPackageRequestProperties(TypedDict, total=False):
        key "include": str
        key "maximumTimeStamp": str
        key "minimumTimeStamp": str
        include: str
        maximum_time_stamp: str
        minimum_time_stamp: str


    class azure.mgmt.databoxedge.types.SymmetricKey(TypedDict, total=False):
        key "connectionString": ForwardRef('AsymmetricEncryptedSecret', module='types')
        connection_string: AsymmetricEncryptedSecret


    class azure.mgmt.databoxedge.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.databoxedge.types.TrackedResource(Resource):
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


    class azure.mgmt.databoxedge.types.TrackingInfo(TypedDict, total=False):
        key "carrierName": str
        key "serialNumber": str
        key "trackingId": str
        key "trackingUrl": str
        carrier_name: str
        serial_number: str
        tracking_id: str
        tracking_url: str


    class azure.mgmt.databoxedge.types.TriggerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_EVENT = "FileEvent"
        PERIODIC_TIMER_EVENT = "PeriodicTimerEvent"


    class azure.mgmt.databoxedge.types.TriggerSupportPackageRequest(ARMBaseModel):
        key "id": str
        key "name": str
        key "properties": Required[SupportPackageRequestProperties]
        key "type": str
        id: str
        name: str
        properties: SupportPackageRequestProperties
        type: str


    class azure.mgmt.databoxedge.types.UploadCertificateRequest(TypedDict, total=False):
        key "properties": Required[RawCertificateData]
        properties: RawCertificateData


    class azure.mgmt.databoxedge.types.User(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[UserProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: UserProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databoxedge.types.UserAccessRight(TypedDict, total=False):
        key "accessType": Required[Union[str, ShareAccessType]]
        key "userId": Required[str]
        access_type: Union[str, ShareAccessType]
        user_id: str


    class azure.mgmt.databoxedge.types.UserProperties(TypedDict, total=False):
        key "encryptedPassword": ForwardRef('AsymmetricEncryptedSecret', module='types')
        key "userType": Required[Union[str, UserType]]
        encrypted_password: AsymmetricEncryptedSecret
        shareAccessRights: list[ShareAccessRight]
        share_access_rights: list[ShareAccessRight]
        user_type: Union[str, UserType]


    class azure.mgmt.databoxedge.types.VmPlacementRequestResult(TypedDict, total=False):
        key "isFeasible": bool
        key "message": str
        key "messageCode": str
        is_feasible: bool
        message: str
        message_code: str
        vmSize: list[str]
        vm_size: list[str]


```