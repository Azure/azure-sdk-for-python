```py
namespace azure.iot.deviceupdate

    class azure.iot.deviceupdate.DeviceUpdateClient(DeviceUpdateClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                instance_id: str, 
                credential: TokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
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


namespace azure.iot.deviceupdate.aio

    class azure.iot.deviceupdate.aio.DeviceUpdateClient(DeviceUpdateClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                instance_id: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
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


namespace azure.iot.deviceupdate.aio.operations

    class azure.iot.deviceupdate.aio.operations.DeviceManagementOperations(DeviceManagementOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_import_devices(
                self, 
                import_type: Union[str, ImportType], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        async def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        async def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace_async
        async def delete_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_best_updates_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClassSubgroupUpdatableDevices: ...

        @distributed_trace_async
        async def get_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace_async
        async def get_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace_async
        async def get_deployment_status(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> DeploymentStatus: ...

        @distributed_trace_async
        async def get_device(
                self, 
                device_id: str, 
                **kwargs: Any
            ) -> Device: ...

        @distributed_trace_async
        async def get_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClass: ...

        @distributed_trace_async
        async def get_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClassSubgroup: ...

        @distributed_trace_async
        async def get_device_class_subgroup_deployment_status(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> DeviceClassSubgroupDeploymentStatus: ...

        @distributed_trace_async
        async def get_device_class_subgroup_update_compliance(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> UpdateCompliance: ...

        @distributed_trace_async
        async def get_device_module(
                self, 
                device_id: str, 
                module_id: str, 
                **kwargs: Any
            ) -> Device: ...

        @distributed_trace_async
        async def get_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> Group: ...

        @distributed_trace_async
        async def get_log_collection(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> LogCollection: ...

        @distributed_trace_async
        async def get_log_collection_detailed_status(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> LogCollectionOperationDetailedStatus: ...

        async def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        @distributed_trace_async
        async def get_update_compliance(self, **kwargs: Any) -> UpdateCompliance: ...

        @distributed_trace_async
        async def get_update_compliance_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> UpdateCompliance: ...

        @distributed_trace
        def list_best_updates_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceClassSubgroupUpdatableDevices]: ...

        @distributed_trace
        def list_deployments_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...

        @distributed_trace
        def list_deployments_for_group(
                self, 
                group_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...

        @distributed_trace
        def list_device_class_subgroups_for_group(
                self, 
                group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceClassSubgroup]: ...

        @distributed_trace
        def list_device_classes(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceClass]: ...

        @distributed_trace
        def list_device_states_for_device_class_subgroup_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentDeviceState]: ...

        @distributed_trace
        def list_devices(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Device]: ...

        @distributed_trace
        def list_groups(
                self, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Group]: ...

        @distributed_trace
        def list_health_of_devices(
                self, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceHealth]: ...

        @distributed_trace
        def list_installable_updates_for_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateInfo]: ...

        @distributed_trace
        def list_log_collections(self, **kwargs: Any) -> AsyncItemPaged[LogCollection]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceOperation]: ...

        @distributed_trace_async
        async def retry_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        async def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: LogCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogCollection: ...

        @overload
        async def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogCollection: ...

        @overload
        async def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogCollection: ...

        @distributed_trace_async
        async def stop_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        async def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: PatchBody, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DeviceClass: ...

        @overload
        async def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DeviceClass: ...

        @overload
        async def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DeviceClass: ...


    class azure.iot.deviceupdate.aio.operations.DeviceUpdateOperations(DeviceUpdateOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                update_to_import: list[ImportUpdateInputItem], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                update_to_import: list[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_update(
                self, 
                update_to_import: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def get_file(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                file_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        async def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        async def get_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        @distributed_trace
        def list_files(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_names(
                self, 
                provider: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateOperation]: ...

        @distributed_trace
        def list_providers(self, **kwargs: Any) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_updates(
                self, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Update]: ...

        @distributed_trace
        def list_versions(
                self, 
                provider: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...


namespace azure.iot.deviceupdate.models

    class azure.iot.deviceupdate.models.CloudInitiatedRollbackPolicy(_Model):
        failure: CloudInitiatedRollbackPolicyFailure
        update_property: UpdateInfo

        @overload
        def __init__(
                self, 
                *, 
                failure: CloudInitiatedRollbackPolicyFailure, 
                update_property: UpdateInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.CloudInitiatedRollbackPolicyFailure(_Model):
        devices_failed_count: int
        devices_failed_percentage: int

        @overload
        def __init__(
                self, 
                *, 
                devices_failed_count: int, 
                devices_failed_percentage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.Compatibility(_Model):


    class azure.iot.deviceupdate.models.ContractModel(_Model):
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.Deployment(_Model):
        deployment_id: str
        device_class_subgroups: Optional[list[str]]
        download_security: Optional[Union[str, DownloadSecurity]]
        group_id: str
        is_canceled: Optional[bool]
        is_cloud_initiated_rollback: Optional[bool]
        is_retried: Optional[bool]
        rollback_policy: Optional[CloudInitiatedRollbackPolicy]
        start_date_time: datetime
        update_property: UpdateInfo

        @overload
        def __init__(
                self, 
                *, 
                deployment_id: str, 
                device_class_subgroups: Optional[list[str]] = ..., 
                download_security: Optional[Union[str, DownloadSecurity]] = ..., 
                group_id: str, 
                is_canceled: Optional[bool] = ..., 
                is_cloud_initiated_rollback: Optional[bool] = ..., 
                is_retried: Optional[bool] = ..., 
                rollback_policy: Optional[CloudInitiatedRollbackPolicy] = ..., 
                start_date_time: datetime, 
                update_property: UpdateInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeploymentDeviceState(_Model):
        device_id: str
        device_state: Union[str, DeviceDeploymentState]
        module_id: Optional[str]
        moved_on_to_new_deployment: bool
        retry_count: int

        @overload
        def __init__(
                self, 
                *, 
                device_id: str, 
                device_state: Union[str, DeviceDeploymentState], 
                module_id: Optional[str] = ..., 
                moved_on_to_new_deployment: bool, 
                retry_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeploymentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ACTIVE_WITH_SUBGROUP_FAILURES = "ActiveWithSubgroupFailures"
        CANCELED = "Canceled"
        FAILED = "Failed"
        INACTIVE = "Inactive"


    class azure.iot.deviceupdate.models.DeploymentStatus(_Model):
        deployment_state: Union[str, DeploymentState]
        error: Optional[Error]
        group_id: str
        subgroup_status: list[DeviceClassSubgroupDeploymentStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_state: Union[str, DeploymentState], 
                error: Optional[Error] = ..., 
                group_id: str, 
                subgroup_status: list[DeviceClassSubgroupDeploymentStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.Device(_Model):
        deployment_status: Optional[Union[str, DeviceDeploymentState]]
        device_class_id: str
        device_id: str
        group_id: Optional[str]
        installed_update: Optional[UpdateInfo]
        last_attempted_update: Optional[UpdateInfo]
        last_deployment_id: Optional[str]
        last_install_result: Optional[InstallResult]
        module_id: Optional[str]
        on_latest_update: bool

        @overload
        def __init__(
                self, 
                *, 
                deployment_status: Optional[Union[str, DeviceDeploymentState]] = ..., 
                device_class_id: str, 
                device_id: str, 
                group_id: Optional[str] = ..., 
                installed_update: Optional[UpdateInfo] = ..., 
                last_attempted_update: Optional[UpdateInfo] = ..., 
                last_deployment_id: Optional[str] = ..., 
                last_install_result: Optional[InstallResult] = ..., 
                module_id: Optional[str] = ..., 
                on_latest_update: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceClass(_Model):
        best_compatible_update: Optional[UpdateInfo]
        device_class_id: str
        device_class_properties: DeviceClassProperties
        friendly_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                best_compatible_update: Optional[UpdateInfo] = ..., 
                device_class_id: str, 
                device_class_properties: DeviceClassProperties, 
                friendly_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceClassProperties(_Model):
        compat_properties: dict[str, str]
        contract_model: Optional[ContractModel]

        @overload
        def __init__(
                self, 
                *, 
                compat_properties: dict[str, str], 
                contract_model: Optional[ContractModel] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceClassSubgroup(_Model):
        created_date_time: str
        deployment_id: Optional[str]
        device_class_id: str
        device_count: Optional[int]
        group_id: str

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: str, 
                deployment_id: Optional[str] = ..., 
                device_class_id: str, 
                device_count: Optional[int] = ..., 
                group_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceClassSubgroupDeploymentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        FAILED = "Failed"
        INACTIVE = "Inactive"


    class azure.iot.deviceupdate.models.DeviceClassSubgroupDeploymentStatus(_Model):
        deployment_state: Union[str, DeviceClassSubgroupDeploymentState]
        device_class_id: str
        devices_canceled_count: Optional[int]
        devices_completed_failed_count: Optional[int]
        devices_completed_succeeded_count: Optional[int]
        devices_in_progress_count: Optional[int]
        error: Optional[Error]
        group_id: str
        total_devices: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                deployment_state: Union[str, DeviceClassSubgroupDeploymentState], 
                device_class_id: str, 
                devices_canceled_count: Optional[int] = ..., 
                devices_completed_failed_count: Optional[int] = ..., 
                devices_completed_succeeded_count: Optional[int] = ..., 
                devices_in_progress_count: Optional[int] = ..., 
                error: Optional[Error] = ..., 
                group_id: str, 
                total_devices: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceClassSubgroupUpdatableDevices(_Model):
        device_class_id: str
        device_count: int
        group_id: str
        update_property: UpdateInfo

        @overload
        def __init__(
                self, 
                *, 
                device_class_id: str, 
                device_count: int, 
                group_id: str, 
                update_property: UpdateInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceDeploymentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.iot.deviceupdate.models.DeviceHealth(_Model):
        device_id: str
        digital_twin_model_id: Optional[str]
        health_checks: list[HealthCheck]
        module_id: Optional[str]
        state: Union[str, DeviceHealthState]

        @overload
        def __init__(
                self, 
                *, 
                device_id: str, 
                digital_twin_model_id: Optional[str] = ..., 
                health_checks: list[HealthCheck], 
                module_id: Optional[str] = ..., 
                state: Union[str, DeviceHealthState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"


    class azure.iot.deviceupdate.models.DeviceOperation(_Model):
        created_date_time: datetime
        error: Optional[Error]
        etag: Optional[str]
        last_action_date_time: datetime
        operation_id: str
        status: Union[str, OperationStatus]
        trace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                error: Optional[Error] = ..., 
                etag: Optional[str] = ..., 
                last_action_date_time: datetime, 
                operation_id: str, 
                status: Union[str, OperationStatus], 
                trace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DeviceUpdateAgentId(_Model):
        device_id: str
        module_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                device_id: str, 
                module_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.DownloadSecurity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        HTTPS = "https"


    class azure.iot.deviceupdate.models.Error(_Model):
        code: str
        details: Optional[list[Error]]
        innererror: Optional[InnerError]
        message: str
        occurred_date_time: Optional[datetime]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[list[Error]] = ..., 
                innererror: Optional[InnerError] = ..., 
                message: str, 
                occurred_date_time: Optional[datetime] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.ErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.FileImportMetadata(_Model):
        filename: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                filename: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.Group(_Model):
        created_date_time: str
        deployments: Optional[list[str]]
        device_count: Optional[int]
        group_id: str
        group_type: Union[str, GroupType]
        subgroups_with_new_updates_available_count: Optional[int]
        subgroups_with_on_latest_update_count: Optional[int]
        subgroups_with_updates_in_progress_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: str, 
                deployments: Optional[list[str]] = ..., 
                device_count: Optional[int] = ..., 
                group_id: str, 
                group_type: Union[str, GroupType], 
                subgroups_with_new_updates_available_count: Optional[int] = ..., 
                subgroups_with_on_latest_update_count: Optional[int] = ..., 
                subgroups_with_updates_in_progress_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.GroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT_NO_TAG = "DefaultNoTag"
        IO_T_HUB_TAG = "IoTHubTag"


    class azure.iot.deviceupdate.models.HealthCheck(_Model):
        name: Optional[str]
        result: Optional[Union[str, HealthCheckResult]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                result: Optional[Union[str, HealthCheckResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.HealthCheckResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUCCESS = "success"
        USER_ERROR = "userError"


    class azure.iot.deviceupdate.models.ImportManifestMetadata(_Model):
        hashes: dict[str, str]
        size_in_bytes: int
        url: str

        @overload
        def __init__(
                self, 
                *, 
                hashes: dict[str, str], 
                size_in_bytes: int, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.ImportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        DEVICES = "Devices"
        MODULES = "Modules"


    class azure.iot.deviceupdate.models.ImportUpdateInputItem(_Model):
        files: Optional[list[FileImportMetadata]]
        friendly_name: Optional[str]
        import_manifest: ImportManifestMetadata

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[list[FileImportMetadata]] = ..., 
                friendly_name: Optional[str] = ..., 
                import_manifest: ImportManifestMetadata
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.InnerError(_Model):
        code: str
        error_detail: Optional[str]
        inner_error: Optional[InnerError]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                error_detail: Optional[str] = ..., 
                inner_error: Optional[InnerError] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.InstallResult(_Model):
        extended_result_code: int
        result_code: int
        result_details: Optional[str]
        step_results: Optional[list[StepResult]]

        @overload
        def __init__(
                self, 
                *, 
                extended_result_code: int, 
                result_code: int, 
                result_details: Optional[str] = ..., 
                step_results: Optional[list[StepResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.Instructions(_Model):
        steps: list[Step]

        @overload
        def __init__(
                self, 
                *, 
                steps: list[Step]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.LogCollection(_Model):
        created_date_time: Optional[str]
        description: Optional[str]
        device_list: list[DeviceUpdateAgentId]
        last_action_date_time: Optional[str]
        log_collection_id: Optional[str]
        status: Optional[Union[str, OperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                device_list: list[DeviceUpdateAgentId], 
                log_collection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.LogCollectionOperationDetailedStatus(_Model):
        created_date_time: Optional[str]
        description: Optional[str]
        device_status: Optional[list[LogCollectionOperationDeviceStatus]]
        last_action_date_time: Optional[str]
        log_collection_id: Optional[str]
        status: Optional[Union[str, OperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: Optional[str] = ..., 
                description: Optional[str] = ..., 
                device_status: Optional[list[LogCollectionOperationDeviceStatus]] = ..., 
                last_action_date_time: Optional[str] = ..., 
                log_collection_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.LogCollectionOperationDeviceStatus(_Model):
        device_id: str
        extended_result_code: Optional[str]
        log_location: Optional[str]
        module_id: Optional[str]
        result_code: Optional[str]
        status: Union[str, OperationStatus]

        @overload
        def __init__(
                self, 
                *, 
                device_id: str, 
                extended_result_code: Optional[str] = ..., 
                log_location: Optional[str] = ..., 
                module_id: Optional[str] = ..., 
                result_code: Optional[str] = ..., 
                status: Union[str, OperationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.iot.deviceupdate.models.PatchBody(_Model):
        friendly_name: str

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.Step(_Model):
        description: Optional[str]
        files: Optional[list[str]]
        handler: Optional[str]
        handler_properties: Optional[dict[str, Any]]
        type: Optional[Union[str, StepType]]
        update_id: Optional[UpdateId]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                files: Optional[list[str]] = ..., 
                handler: Optional[str] = ..., 
                handler_properties: Optional[dict[str, Any]] = ..., 
                type: Optional[Union[str, StepType]] = ..., 
                update_id: Optional[UpdateId] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.StepResult(_Model):
        description: Optional[str]
        extended_result_code: int
        result_code: int
        result_details: Optional[str]
        update_property: Optional[UpdateInfo]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                extended_result_code: int, 
                result_code: int, 
                result_details: Optional[str] = ..., 
                update_property: Optional[UpdateInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.StepType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.iot.deviceupdate.models.Update(_Model):
        compatibility: list[Compatibility]
        created_date_time: datetime
        description: Optional[str]
        etag: Optional[str]
        friendly_name: Optional[str]
        imported_date_time: datetime
        installed_criteria: Optional[str]
        instructions: Optional[Instructions]
        is_deployable: Optional[bool]
        manifest_version: str
        referenced_by: Optional[list[UpdateId]]
        scan_result: Optional[str]
        update_id: UpdateId
        update_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compatibility: list[Compatibility], 
                created_date_time: datetime, 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                imported_date_time: datetime, 
                installed_criteria: Optional[str] = ..., 
                instructions: Optional[Instructions] = ..., 
                is_deployable: Optional[bool] = ..., 
                manifest_version: str, 
                referenced_by: Optional[list[UpdateId]] = ..., 
                scan_result: Optional[str] = ..., 
                update_id: UpdateId, 
                update_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateCompliance(_Model):
        new_updates_available_device_count: int
        on_latest_update_device_count: int
        total_device_count: int
        updates_in_progress_device_count: int

        @overload
        def __init__(
                self, 
                *, 
                new_updates_available_device_count: int, 
                on_latest_update_device_count: int, 
                total_device_count: int, 
                updates_in_progress_device_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateFile(UpdateFileBase):
        download_handler: Optional[UpdateFileDownloadHandler]
        etag: Optional[str]
        file_id: str
        file_name: str
        hashes: dict[str, str]
        mime_type: str
        properties: dict[str, str]
        related_files: Optional[list[UpdateFileBase]]
        scan_details: str
        scan_result: str
        size_in_bytes: int

        @overload
        def __init__(
                self, 
                *, 
                download_handler: Optional[UpdateFileDownloadHandler] = ..., 
                etag: Optional[str] = ..., 
                file_id: str, 
                file_name: str, 
                hashes: dict[str, str], 
                mime_type: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                related_files: Optional[list[UpdateFileBase]] = ..., 
                scan_details: Optional[str] = ..., 
                scan_result: Optional[str] = ..., 
                size_in_bytes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateFileBase(_Model):
        file_name: str
        hashes: dict[str, str]
        mime_type: Optional[str]
        properties: Optional[dict[str, str]]
        scan_details: Optional[str]
        scan_result: Optional[str]
        size_in_bytes: int

        @overload
        def __init__(
                self, 
                *, 
                file_name: str, 
                hashes: dict[str, str], 
                mime_type: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                scan_details: Optional[str] = ..., 
                scan_result: Optional[str] = ..., 
                size_in_bytes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateFileDownloadHandler(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateId(_Model):
        name: str
        provider: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                provider: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateInfo(_Model):
        description: Optional[str]
        friendly_name: Optional[str]
        update_id: UpdateId

        @overload
        def __init__(
                self, 
                *, 
                update_id: UpdateId
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.iot.deviceupdate.models.UpdateOperation(_Model):
        created_date_time: datetime
        error: Optional[Error]
        etag: Optional[str]
        last_action_date_time: datetime
        operation_id: str
        resource_location: Optional[str]
        status: Union[str, OperationStatus]
        trace_id: Optional[str]
        update_property: Optional[UpdateInfo]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                error: Optional[Error] = ..., 
                etag: Optional[str] = ..., 
                last_action_date_time: datetime, 
                operation_id: str, 
                resource_location: Optional[str] = ..., 
                status: Union[str, OperationStatus], 
                trace_id: Optional[str] = ..., 
                update_property: Optional[UpdateInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.iot.deviceupdate.operations

    class azure.iot.deviceupdate.operations.DeviceManagementOperations(DeviceManagementOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_import_devices(
                self, 
                import_type: Union[str, ImportType], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        def create_or_update_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def delete_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_best_updates_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClassSubgroupUpdatableDevices: ...

        @distributed_trace
        def get_deployment(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def get_deployment_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def get_deployment_status(
                self, 
                group_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> DeploymentStatus: ...

        @distributed_trace
        def get_device(
                self, 
                device_id: str, 
                **kwargs: Any
            ) -> Device: ...

        @distributed_trace
        def get_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClass: ...

        @distributed_trace
        def get_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> DeviceClassSubgroup: ...

        @distributed_trace
        def get_device_class_subgroup_deployment_status(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> DeviceClassSubgroupDeploymentStatus: ...

        @distributed_trace
        def get_device_class_subgroup_update_compliance(
                self, 
                group_id: str, 
                device_class_id: str, 
                **kwargs: Any
            ) -> UpdateCompliance: ...

        @distributed_trace
        def get_device_module(
                self, 
                device_id: str, 
                module_id: str, 
                **kwargs: Any
            ) -> Device: ...

        @distributed_trace
        def get_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> Group: ...

        @distributed_trace
        def get_log_collection(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> LogCollection: ...

        @distributed_trace
        def get_log_collection_detailed_status(
                self, 
                log_collection_id: str, 
                **kwargs: Any
            ) -> LogCollectionOperationDetailedStatus: ...

        def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        @distributed_trace
        def get_update_compliance(self, **kwargs: Any) -> UpdateCompliance: ...

        @distributed_trace
        def get_update_compliance_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> UpdateCompliance: ...

        @distributed_trace
        def list_best_updates_for_group(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> ItemPaged[DeviceClassSubgroupUpdatableDevices]: ...

        @distributed_trace
        def list_deployments_for_device_class_subgroup(
                self, 
                group_id: str, 
                device_class_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...

        @distributed_trace
        def list_deployments_for_group(
                self, 
                group_id: str, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...

        @distributed_trace
        def list_device_class_subgroups_for_group(
                self, 
                group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceClassSubgroup]: ...

        @distributed_trace
        def list_device_classes(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceClass]: ...

        @distributed_trace
        def list_device_states_for_device_class_subgroup_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentDeviceState]: ...

        @distributed_trace
        def list_devices(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Device]: ...

        @distributed_trace
        def list_groups(
                self, 
                *, 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Group]: ...

        @distributed_trace
        def list_health_of_devices(
                self, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[DeviceHealth]: ...

        @distributed_trace
        def list_installable_updates_for_device_class(
                self, 
                device_class_id: str, 
                **kwargs: Any
            ) -> ItemPaged[UpdateInfo]: ...

        @distributed_trace
        def list_log_collections(self, **kwargs: Any) -> ItemPaged[LogCollection]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceOperation]: ...

        @distributed_trace
        def retry_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: LogCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogCollection: ...

        @overload
        def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogCollection: ...

        @overload
        def start_log_collection(
                self, 
                log_collection_id: str, 
                log_collection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogCollection: ...

        @distributed_trace
        def stop_deployment(
                self, 
                group_id: str, 
                device_class_id: str, 
                deployment_id: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @overload
        def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: PatchBody, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DeviceClass: ...

        @overload
        def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DeviceClass: ...

        @overload
        def update_device_class(
                self, 
                device_class_id: str, 
                device_class_patch: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DeviceClass: ...


    class azure.iot.deviceupdate.operations.DeviceUpdateOperations(DeviceUpdateOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                update_to_import: list[ImportUpdateInputItem], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                update_to_import: list[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_update(
                self, 
                update_to_import: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def get_file(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                file_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        def get_operation_status(
                self, 
                operation_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        def get_update(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                if_none_match: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ): ...

        @distributed_trace
        def list_files(
                self, 
                provider: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_names(
                self, 
                provider: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_operation_statuses(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UpdateOperation]: ...

        @distributed_trace
        def list_providers(self, **kwargs: Any) -> ItemPaged[str]: ...

        @distributed_trace
        def list_updates(
                self, 
                *, 
                filter: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Update]: ...

        @distributed_trace
        def list_versions(
                self, 
                provider: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...


```