```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.recoveryservicesbackup.passivestamp

    class azure.mgmt.recoveryservicesbackup.passivestamp.RecoveryServicesBackupPassiveClient: implements ContextManager 
        aad_properties: AadPropertiesOperations
        backup_crr_job_details: BackupCrrJobDetailsOperations
        backup_crr_jobs: BackupCrrJobsOperations
        backup_protected_items_crr: BackupProtectedItemsCrrOperations
        backup_resource_storage_configs: BackupResourceStorageConfigsOperations
        backup_usage_summaries_crr: BackupUsageSummariesCRROperations
        cross_region_restore: CrossRegionRestoreOperations
        crr_operation_results: CrrOperationResultsOperations
        crr_operation_status: CrrOperationStatusOperations
        recovery_points: RecoveryPointsOperations
        recovery_points_crr: RecoveryPointsCrrOperations

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


namespace azure.mgmt.recoveryservicesbackup.passivestamp.aio

    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.RecoveryServicesBackupPassiveClient: implements AsyncContextManager 
        aad_properties: AadPropertiesOperations
        backup_crr_job_details: BackupCrrJobDetailsOperations
        backup_crr_jobs: BackupCrrJobsOperations
        backup_protected_items_crr: BackupProtectedItemsCrrOperations
        backup_resource_storage_configs: BackupResourceStorageConfigsOperations
        backup_usage_summaries_crr: BackupUsageSummariesCRROperations
        cross_region_restore: CrossRegionRestoreOperations
        crr_operation_results: CrrOperationResultsOperations
        crr_operation_status: CrrOperationStatusOperations
        recovery_points: RecoveryPointsOperations
        recovery_points_crr: RecoveryPointsCrrOperations

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


namespace azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations

    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.AadPropertiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                azure_region: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AADPropertiesResource: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.BackupCrrJobDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get(
                self, 
                azure_region: str, 
                parameters: CrrJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResource: ...

        @overload
        async def get(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResource: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.BackupCrrJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                azure_region: str, 
                parameters: CrrJobRequest, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[JobResource]: ...

        @overload
        def list(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[JobResource]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.BackupProtectedItemsCrrOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectedItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.BackupResourceStorageConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> BackupResourceConfigResource: ...

        @overload
        async def patch(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceConfigResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def patch(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceConfigResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupResourceConfigResource: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupResourceConfigResource: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.BackupUsageSummariesCRROperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupManagementUsage]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.CrossRegionRestoreOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_trigger(
                self, 
                azure_region: str, 
                parameters: CrossRegionRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.CrrOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                azure_region: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.CrrOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                azure_region: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.RecoveryPointsCrrOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                **kwargs: Any
            ) -> RecoveryPointResource: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPointResource]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.aio.operations.RecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get_access_token(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: AADPropertiesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CrrAccessTokenResource: ...

        @overload
        async def get_access_token(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CrrAccessTokenResource: ...


namespace azure.mgmt.recoveryservicesbackup.passivestamp.models

    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AADProperties(Model):
        audience: str
        authority: str
        service_principal_client_id: str
        service_principal_object_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audience: Optional[str] = ..., 
                authority: Optional[str] = ..., 
                service_principal_client_id: Optional[str] = ..., 
                service_principal_object_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AADPropertiesResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: AADProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AADProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureFileShareRecoveryPoint(RecoveryPoint):
        file_share_snapshot_uri: str
        object_type: str
        recovery_point_size_in_gb: int
        recovery_point_time: datetime
        recovery_point_type: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureFileShareRestoreRequest(RestoreRequest):
        copy_options: Union[str, CopyOptions]
        object_type: str
        recovery_type: Union[str, RecoveryType]
        restore_file_specs: list[RestoreFileSpecs]
        restore_request_type: Union[str, RestoreRequestType]
        source_resource_id: str
        target_details: TargetAFSRestoreInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                copy_options: Optional[Union[str, CopyOptions]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                restore_file_specs: Optional[list[RestoreFileSpecs]] = ..., 
                restore_request_type: Optional[Union[str, RestoreRequestType]] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_details: Optional[TargetAFSRestoreInfo] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureFileshareProtectedItem(ProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureFileshareProtectedItemExtendedInfo
        friendly_name: str
        health_status: Union[str, HealthStatus]
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureFileshareProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[Union[str, HealthStatus]] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureFileshareProtectedItemExtendedInfo(Model):
        oldest_recovery_point: datetime
        policy_state: str
        recovery_point_count: int
        resource_state: str
        resource_state_sync_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                oldest_recovery_point: Optional[datetime] = ..., 
                policy_state: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSClassicComputeVMProtectedItem(AzureIaaSVMProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureIaaSVMProtectedItemExtendedInfo
        extended_properties: ExtendedProperties
        friendly_name: str
        health_details: list[AzureIaaSVMHealthDetails]
        health_status: Union[str, HealthStatus]
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        protected_item_data_id: str
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        virtual_machine_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo] = ..., 
                extended_properties: Optional[ExtendedProperties] = ..., 
                friendly_name: Optional[str] = ..., 
                health_details: Optional[list[AzureIaaSVMHealthDetails]] = ..., 
                health_status: Optional[Union[str, HealthStatus]] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSComputeVMProtectedItem(AzureIaaSVMProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureIaaSVMProtectedItemExtendedInfo
        extended_properties: ExtendedProperties
        friendly_name: str
        health_details: list[AzureIaaSVMHealthDetails]
        health_status: Union[str, HealthStatus]
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        protected_item_data_id: str
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        virtual_machine_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo] = ..., 
                extended_properties: Optional[ExtendedProperties] = ..., 
                friendly_name: Optional[str] = ..., 
                health_details: Optional[list[AzureIaaSVMHealthDetails]] = ..., 
                health_status: Optional[Union[str, HealthStatus]] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMErrorInfo(Model):
        error_code: int
        error_string: str
        error_title: str
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMHealthDetails(ResourceHealthDetails):
        code: int
        message: str
        recommendations: list[str]
        title: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMJob(Job):
        actions_info: Union[list[str, JobSupportedAction]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: timedelta
        end_time: datetime
        entity_friendly_name: str
        error_details: list[AzureIaaSVMErrorInfo]
        extended_info: AzureIaaSVMJobExtendedInfo
        job_type: str
        operation: str
        start_time: datetime
        status: str
        virtual_machine_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[AzureIaaSVMErrorInfo]] = ..., 
                extended_info: Optional[AzureIaaSVMJobExtendedInfo] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMJobExtendedInfo(Model):
        dynamic_error_message: str
        estimated_remaining_duration: str
        internal_property_bag: dict[str, str]
        progress_percentage: float
        property_bag: dict[str, str]
        tasks_list: list[AzureIaaSVMJobTaskDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                estimated_remaining_duration: Optional[str] = ..., 
                internal_property_bag: Optional[dict[str, str]] = ..., 
                progress_percentage: Optional[float] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[AzureIaaSVMJobTaskDetails]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMJobTaskDetails(Model):
        duration: timedelta
        end_time: datetime
        instance_id: str
        progress_percentage: float
        start_time: datetime
        status: str
        task_execution_details: str
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                instance_id: Optional[str] = ..., 
                progress_percentage: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                task_execution_details: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMProtectedItem(ProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureIaaSVMProtectedItemExtendedInfo
        extended_properties: ExtendedProperties
        friendly_name: str
        health_details: list[AzureIaaSVMHealthDetails]
        health_status: Union[str, HealthStatus]
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        protected_item_data_id: str
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        virtual_machine_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo] = ..., 
                extended_properties: Optional[ExtendedProperties] = ..., 
                friendly_name: Optional[str] = ..., 
                health_details: Optional[list[AzureIaaSVMHealthDetails]] = ..., 
                health_status: Optional[Union[str, HealthStatus]] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureIaaSVMProtectedItemExtendedInfo(Model):
        oldest_recovery_point: datetime
        policy_inconsistent: bool
        recovery_point_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                oldest_recovery_point: Optional[datetime] = ..., 
                policy_inconsistent: Optional[bool] = ..., 
                recovery_point_count: Optional[int] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureSqlProtectedItem(ProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureSqlProtectedItemExtendedInfo
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        protected_item_data_id: str
        protected_item_type: str
        protection_state: Union[str, ProtectedItemState]
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureSqlProtectedItemExtendedInfo] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectedItemState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureSqlProtectedItemExtendedInfo(Model):
        oldest_recovery_point: datetime
        policy_state: str
        recovery_point_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                oldest_recovery_point: Optional[datetime] = ..., 
                policy_state: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureStorageErrorInfo(Model):
        error_code: int
        error_string: str
        recommendations: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_code: Optional[int] = ..., 
                error_string: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureStorageJob(Job):
        actions_info: Union[list[str, JobSupportedAction]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: timedelta
        end_time: datetime
        entity_friendly_name: str
        error_details: list[AzureStorageErrorInfo]
        extended_info: AzureStorageJobExtendedInfo
        job_type: str
        operation: str
        start_time: datetime
        status: str
        storage_account_name: str
        storage_account_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[AzureStorageErrorInfo]] = ..., 
                extended_info: Optional[AzureStorageJobExtendedInfo] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_account_version: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureStorageJobExtendedInfo(Model):
        dynamic_error_message: str
        property_bag: dict[str, str]
        tasks_list: list[AzureStorageJobTaskDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[AzureStorageJobTaskDetails]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureStorageJobTaskDetails(Model):
        status: str
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureVmWorkloadProtectedItem(ProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        parent_name: str
        parent_type: str
        policy_id: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureVmWorkloadProtectedItemExtendedInfo(Model):
        oldest_recovery_point: datetime
        policy_state: str
        recovery_point_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                oldest_recovery_point: Optional[datetime] = ..., 
                policy_state: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureVmWorkloadSAPAseDatabaseProtectedItem(AzureVmWorkloadProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        parent_name: str
        parent_type: str
        policy_id: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureVmWorkloadSAPHanaDatabaseProtectedItem(AzureVmWorkloadProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        parent_name: str
        parent_type: str
        policy_id: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureVmWorkloadSQLDatabaseProtectedItem(AzureVmWorkloadProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        parent_name: str
        parent_type: str
        policy_id: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadErrorInfo(Model):
        additional_details: str
        error_code: int
        error_string: str
        error_title: str
        recommendations: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_details: Optional[str] = ..., 
                error_code: Optional[int] = ..., 
                error_string: Optional[str] = ..., 
                error_title: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadJob(Job):
        actions_info: Union[list[str, JobSupportedAction]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: timedelta
        end_time: datetime
        entity_friendly_name: str
        error_details: list[AzureWorkloadErrorInfo]
        extended_info: AzureWorkloadJobExtendedInfo
        job_type: str
        operation: str
        start_time: datetime
        status: str
        workload_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[AzureWorkloadErrorInfo]] = ..., 
                extended_info: Optional[AzureWorkloadJobExtendedInfo] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                workload_type: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadJobExtendedInfo(Model):
        dynamic_error_message: str
        property_bag: dict[str, str]
        tasks_list: list[AzureWorkloadJobTaskDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[AzureWorkloadJobTaskDetails]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadJobTaskDetails(Model):
        status: str
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadPointInTimeRecoveryPoint(AzureWorkloadRecoveryPoint):
        object_type: str
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time_in_utc: datetime
        time_ranges: list[PointInTimeRange]
        type: Union[str, RestorePointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
                time_ranges: Optional[list[PointInTimeRange]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadPointInTimeRestoreRequest(AzureWorkloadRestoreRequest):
        object_type: str
        point_in_time: datetime
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadRecoveryPoint(RecoveryPoint):
        object_type: str
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time_in_utc: datetime
        type: Union[str, RestorePointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadRestoreRequest(RestoreRequest):
        object_type: str
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSAPHanaPointInTimeRecoveryPoint(AzureWorkloadPointInTimeRecoveryPoint):
        object_type: str
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time_in_utc: datetime
        time_ranges: list[PointInTimeRange]
        type: Union[str, RestorePointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
                time_ranges: Optional[list[PointInTimeRange]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSAPHanaPointInTimeRestoreRequest(AzureWorkloadSAPHanaRestoreRequest):
        object_type: str
        point_in_time: datetime
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSAPHanaRecoveryPoint(AzureWorkloadRecoveryPoint):
        object_type: str
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time_in_utc: datetime
        type: Union[str, RestorePointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSAPHanaRestoreRequest(AzureWorkloadRestoreRequest):
        object_type: str
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSQLPointInTimeRecoveryPoint(AzureWorkloadSQLRecoveryPoint):
        extended_info: AzureWorkloadSQLRecoveryPointExtendedInfo
        object_type: str
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time_in_utc: datetime
        time_ranges: list[PointInTimeRange]
        type: Union[str, RestorePointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_info: Optional[AzureWorkloadSQLRecoveryPointExtendedInfo] = ..., 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
                time_ranges: Optional[list[PointInTimeRange]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSQLPointInTimeRestoreRequest(AzureWorkloadSQLRestoreRequest):
        alternate_directory_paths: list[SQLDataDirectoryMapping]
        is_non_recoverable: bool
        object_type: str
        point_in_time: datetime
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        should_use_alternate_target_location: bool
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alternate_directory_paths: Optional[list[SQLDataDirectoryMapping]] = ..., 
                is_non_recoverable: Optional[bool] = ..., 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                should_use_alternate_target_location: Optional[bool] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSQLRecoveryPoint(AzureWorkloadRecoveryPoint):
        extended_info: AzureWorkloadSQLRecoveryPointExtendedInfo
        object_type: str
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time_in_utc: datetime
        type: Union[str, RestorePointType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_info: Optional[AzureWorkloadSQLRecoveryPointExtendedInfo] = ..., 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSQLRecoveryPointExtendedInfo(Model):
        data_directory_paths: list[SQLDataDirectory]
        data_directory_time_in_utc: datetime

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.AzureWorkloadSQLRestoreRequest(AzureWorkloadRestoreRequest):
        alternate_directory_paths: list[SQLDataDirectoryMapping]
        is_non_recoverable: bool
        object_type: str
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        should_use_alternate_target_location: bool
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alternate_directory_paths: Optional[list[SQLDataDirectoryMapping]] = ..., 
                is_non_recoverable: Optional[bool] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                should_use_alternate_target_location: Optional[bool] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BEKDetails(Model):
        secret_data: str
        secret_url: str
        secret_vault_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secret_data: Optional[str] = ..., 
                secret_url: Optional[str] = ..., 
                secret_vault_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BMSAADPropertiesQueryObject(Model):
        backup_management_type: Union[str, BackupManagementType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BMSBackupSummariesQueryObject(Model):
        type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, Type]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BMSRPQueryObject(Model):
        end_date: datetime
        extended_info: bool
        move_ready_rp_only: bool
        restore_point_query_type: Union[str, RestorePointQueryType]
        start_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                extended_info: Optional[bool] = ..., 
                move_ready_rp_only: Optional[bool] = ..., 
                restore_point_query_type: Optional[Union[str, RestorePointQueryType]] = ..., 
                start_date: Optional[datetime] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BackupManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP_SERVER = "AzureBackupServer"
        AZURE_IAAS_VM = "AzureIaasVM"
        AZURE_SQL = "AzureSql"
        AZURE_STORAGE = "AzureStorage"
        AZURE_WORKLOAD = "AzureWorkload"
        DEFAULT_BACKUP = "DefaultBackup"
        DPM = "DPM"
        INVALID = "Invalid"
        MAB = "MAB"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BackupManagementUsage(Model):
        current_value: int
        limit: int
        name: NameInfo
        next_reset_time: datetime
        quota_period: str
        unit: Union[str, UsagesUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[NameInfo] = ..., 
                next_reset_time: Optional[datetime] = ..., 
                quota_period: Optional[str] = ..., 
                unit: Optional[Union[str, UsagesUnit]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BackupManagementUsageList(Model):
        value: list[BackupManagementUsage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[BackupManagementUsage]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BackupResourceConfig(Model):
        cross_region_restore_flag: bool
        storage_model_type: Union[str, StorageType]
        storage_type: Union[str, StorageType]
        storage_type_state: Union[str, StorageTypeState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cross_region_restore_flag: Optional[bool] = ..., 
                storage_model_type: Optional[Union[str, StorageType]] = ..., 
                storage_type: Optional[Union[str, StorageType]] = ..., 
                storage_type_state: Optional[Union[str, StorageTypeState]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.BackupResourceConfigResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: BackupResourceConfig
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupResourceConfig] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ClientScriptForConnect(Model):
        os_type: str
        script_content: str
        script_extension: str
        script_name_suffix: str
        url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                os_type: Optional[str] = ..., 
                script_content: Optional[str] = ..., 
                script_extension: Optional[str] = ..., 
                script_name_suffix: Optional[str] = ..., 
                url: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CopyOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_COPY = "CreateCopy"
        FAIL_ON_CONFLICT = "FailOnConflict"
        INVALID = "Invalid"
        OVERWRITE = "Overwrite"
        SKIP = "Skip"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        INVALID = "Invalid"
        RECOVER = "Recover"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CrossRegionRestoreRequest(Model):
        cross_region_restore_access_details: CrrAccessToken
        restore_request: RestoreRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cross_region_restore_access_details: Optional[CrrAccessToken] = ..., 
                restore_request: Optional[RestoreRequest] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CrossRegionRestoreRequestResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: CrossRegionRestoreRequest
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CrossRegionRestoreRequest] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CrrAccessToken(Model):
        access_token_string: str
        b_ms_active_region: str
        backup_management_type: str
        container_name: str
        container_type: str
        coordinator_service_stamp_id: str
        coordinator_service_stamp_uri: str
        datasource_container_name: str
        datasource_id: str
        datasource_name: str
        datasource_type: str
        object_type: str
        protection_container_id: int
        protection_service_stamp_id: str
        protection_service_stamp_uri: str
        recovery_point_id: str
        recovery_point_time: str
        resource_group_name: str
        resource_id: str
        resource_name: str
        rp_is_managed_virtual_machine: bool
        rp_original_sa_option: bool
        rp_tier_information: dict[str, str]
        rp_vm_size_description: str
        subscription_id: str
        token_extended_information: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_token_string: Optional[str] = ..., 
                b_ms_active_region: Optional[str] = ..., 
                backup_management_type: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                container_type: Optional[str] = ..., 
                coordinator_service_stamp_id: Optional[str] = ..., 
                coordinator_service_stamp_uri: Optional[str] = ..., 
                datasource_container_name: Optional[str] = ..., 
                datasource_id: Optional[str] = ..., 
                datasource_name: Optional[str] = ..., 
                datasource_type: Optional[str] = ..., 
                protection_container_id: Optional[int] = ..., 
                protection_service_stamp_id: Optional[str] = ..., 
                protection_service_stamp_uri: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_time: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                rp_is_managed_virtual_machine: Optional[bool] = ..., 
                rp_original_sa_option: Optional[bool] = ..., 
                rp_tier_information: Optional[dict[str, str]] = ..., 
                rp_vm_size_description: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                token_extended_information: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CrrAccessTokenResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: CrrAccessToken
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CrrAccessToken] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CrrJobRequest(Model):
        job_name: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                job_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.CrrJobRequestResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: CrrJobRequest
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CrrJobRequest] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DPMProtectedItem(ProtectedItem):
        backup_engine_name: str
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: DPMProtectedItemExtendedInfo
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        protected_item_type: str
        protection_state: Union[str, ProtectedItemState]
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_engine_name: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[DPMProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectedItemState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DPMProtectedItemExtendedInfo(Model):
        disk_storage_used_in_bytes: str
        is_collocated: bool
        is_present_on_cloud: bool
        last_backup_status: str
        last_refreshed_at: datetime
        oldest_recovery_point: datetime
        on_premise_latest_recovery_point: datetime
        on_premise_oldest_recovery_point: datetime
        on_premise_recovery_point_count: int
        protectable_object_load_path: dict[str, str]
        protected: bool
        protection_group_name: str
        recovery_point_count: int
        total_disk_storage_size_in_bytes: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_storage_used_in_bytes: Optional[str] = ..., 
                is_collocated: Optional[bool] = ..., 
                is_present_on_cloud: Optional[bool] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_refreshed_at: Optional[datetime] = ..., 
                oldest_recovery_point: Optional[datetime] = ..., 
                on_premise_latest_recovery_point: Optional[datetime] = ..., 
                on_premise_oldest_recovery_point: Optional[datetime] = ..., 
                on_premise_recovery_point_count: Optional[int] = ..., 
                protectable_object_load_path: Optional[dict[str, str]] = ..., 
                protected: Optional[bool] = ..., 
                protection_group_name: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ..., 
                total_disk_storage_size_in_bytes: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DataSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE_SHARE = "AzureFileShare"
        AZURE_SQL_DB = "AzureSqlDb"
        CLIENT = "Client"
        EXCHANGE = "Exchange"
        FILE_FOLDER = "FileFolder"
        GENERIC_DATA_SOURCE = "GenericDataSource"
        INVALID = "Invalid"
        SAP_ASE_DATABASE = "SAPAseDatabase"
        SAP_HANA_DATABASE = "SAPHanaDatabase"
        SHAREPOINT = "Sharepoint"
        SQLDB = "SQLDB"
        SQL_DATA_BASE = "SQLDataBase"
        SYSTEM_STATE = "SystemState"
        VM = "VM"
        V_MWARE_VM = "VMwareVM"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DiskExclusionProperties(Model):
        disk_lun_list: list[int]
        is_inclusion_list: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_lun_list: Optional[list[int]] = ..., 
                is_inclusion_list: Optional[bool] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DiskInformation(Model):
        lun: int
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lun: Optional[int] = ..., 
                name: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DpmErrorInfo(Model):
        error_string: str
        recommendations: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_string: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DpmJob(Job):
        actions_info: Union[list[str, JobSupportedAction]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        container_name: str
        container_type: str
        dpm_server_name: str
        duration: timedelta
        end_time: datetime
        entity_friendly_name: str
        error_details: list[DpmErrorInfo]
        extended_info: DpmJobExtendedInfo
        job_type: str
        operation: str
        start_time: datetime
        status: str
        workload_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_name: Optional[str] = ..., 
                container_type: Optional[str] = ..., 
                dpm_server_name: Optional[str] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[DpmErrorInfo]] = ..., 
                extended_info: Optional[DpmJobExtendedInfo] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                workload_type: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DpmJobExtendedInfo(Model):
        dynamic_error_message: str
        property_bag: dict[str, str]
        tasks_list: list[DpmJobTaskDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[DpmJobTaskDetails]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.DpmJobTaskDetails(Model):
        duration: timedelta
        end_time: datetime
        start_time: datetime
        status: str
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.EncryptionDetails(Model):
        encryption_enabled: bool
        kek_url: str
        kek_vault_id: str
        secret_key_url: str
        secret_key_vault_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_enabled: Optional[bool] = ..., 
                kek_url: Optional[str] = ..., 
                kek_vault_id: Optional[str] = ..., 
                secret_key_url: Optional[str] = ..., 
                secret_key_vault_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ErrorAdditionalInfo(Model):
        info: JSON
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ErrorDetail(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ExtendedProperties(Model):
        disk_exclusion_properties: DiskExclusionProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_exclusion_properties: Optional[DiskExclusionProperties] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.GenericProtectedItem(ProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        fabric_name: str
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        policy_state: str
        protected_item_id: int
        protected_item_type: str
        protection_state: Union[str, ProtectionState]
        resource_guard_operation_requests: list[str]
        source_associations: dict[str, str]
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_state: Optional[str] = ..., 
                protected_item_id: Optional[int] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_associations: Optional[dict[str, str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.GenericRecoveryPoint(RecoveryPoint):
        friendly_name: str
        object_type: str
        recovery_point_additional_info: str
        recovery_point_time: datetime
        recovery_point_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                recovery_point_additional_info: Optional[str] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                recovery_point_type: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.HealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "ActionRequired"
        ACTION_SUGGESTED = "ActionSuggested"
        INVALID = "Invalid"
        PASSED = "Passed"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "ActionRequired"
        ACTION_SUGGESTED = "ActionSuggested"
        INVALID = "Invalid"
        PASSED = "Passed"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.IaasVMRecoveryPoint(RecoveryPoint):
        is_instant_ilr_session_active: bool
        is_managed_virtual_machine: bool
        is_source_vm_encrypted: bool
        key_and_secret: KeyAndSecretDetails
        object_type: str
        original_storage_account_option: bool
        os_type: str
        recovery_point_additional_info: str
        recovery_point_disk_configuration: RecoveryPointDiskConfiguration
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_tier_details: list[RecoveryPointTierInformation]
        recovery_point_time: datetime
        recovery_point_type: str
        source_vm_storage_type: str
        virtual_machine_size: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_instant_ilr_session_active: Optional[bool] = ..., 
                is_managed_virtual_machine: Optional[bool] = ..., 
                key_and_secret: Optional[KeyAndSecretDetails] = ..., 
                original_storage_account_option: Optional[bool] = ..., 
                os_type: Optional[str] = ..., 
                recovery_point_disk_configuration: Optional[RecoveryPointDiskConfiguration] = ..., 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
                virtual_machine_size: Optional[str] = ..., 
                zones: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.IaasVMRestoreRequest(RestoreRequest):
        affinity_group: str
        create_new_cloud_service: bool
        disk_encryption_set_id: str
        encryption_details: EncryptionDetails
        identity_based_restore_details: IdentityBasedRestoreDetails
        identity_info: IdentityInfo
        object_type: str
        original_storage_account_option: bool
        recovery_point_id: str
        recovery_type: Union[str, RecoveryType]
        region: str
        restore_disk_lun_list: list[int]
        restore_with_managed_disks: bool
        source_resource_id: str
        storage_account_id: str
        subnet_id: str
        target_domain_name_id: str
        target_resource_group_id: str
        target_virtual_machine_id: str
        virtual_network_id: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                affinity_group: Optional[str] = ..., 
                create_new_cloud_service: Optional[bool] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                encryption_details: Optional[EncryptionDetails] = ..., 
                identity_based_restore_details: Optional[IdentityBasedRestoreDetails] = ..., 
                identity_info: Optional[IdentityInfo] = ..., 
                original_storage_account_option: Optional[bool] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                region: Optional[str] = ..., 
                restore_disk_lun_list: Optional[list[int]] = ..., 
                restore_with_managed_disks: Optional[bool] = ..., 
                source_resource_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                target_domain_name_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ..., 
                zones: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.IdentityBasedRestoreDetails(Model):
        object_type: str
        target_storage_account_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_type: Optional[str] = ..., 
                target_storage_account_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.IdentityInfo(Model):
        is_system_assigned_identity: bool
        managed_identity_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_system_assigned_identity: Optional[bool] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.InstantItemRecoveryTarget(Model):
        client_scripts: list[ClientScriptForConnect]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_scripts: Optional[list[ClientScriptForConnect]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.Job(Model):
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        end_time: datetime
        entity_friendly_name: str
        job_type: str
        operation: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.JobOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP = "Backup"
        CONFIGURE_BACKUP = "ConfigureBackup"
        CROSS_REGION_RESTORE = "CrossRegionRestore"
        DELETE_BACKUP_DATA = "DeleteBackupData"
        DISABLE_BACKUP = "DisableBackup"
        INVALID = "Invalid"
        REGISTER = "Register"
        RESTORE = "Restore"
        UNDELETE = "Undelete"
        UN_REGISTER = "UnRegister"
        UPDATE_CUSTOMER_MANAGED_KEY = "UpdateCustomerManagedKey"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.JobQueryObject(Model):
        backup_management_type: Union[str, BackupManagementType]
        end_time: datetime
        job_id: str
        operation: Union[str, JobOperationType]
        start_time: datetime
        status: Union[str, JobStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                end_time: Optional[datetime] = ..., 
                job_id: Optional[str] = ..., 
                operation: Optional[Union[str, JobOperationType]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.JobResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: Job
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Job] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.JobResourceList(ResourceList):
        next_link: str
        value: list[JobResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[JobResource]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        COMPLETED = "Completed"
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.JobSupportedAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLABLE = "Cancellable"
        INVALID = "Invalid"
        RETRIABLE = "Retriable"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.KEKDetails(Model):
        key_backup_data: str
        key_url: str
        key_vault_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_backup_data: Optional[str] = ..., 
                key_url: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.KPIResourceHealthDetails(Model):
        resource_health_details: list[ResourceHealthDetails]
        resource_health_status: Union[str, ResourceHealthStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_health_details: Optional[list[ResourceHealthDetails]] = ..., 
                resource_health_status: Optional[Union[str, ResourceHealthStatus]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.KeyAndSecretDetails(Model):
        bek_details: BEKDetails
        encryption_mechanism: str
        kek_details: KEKDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bek_details: Optional[BEKDetails] = ..., 
                encryption_mechanism: Optional[str] = ..., 
                kek_details: Optional[KEKDetails] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.LastBackupStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabErrorInfo(Model):
        error_string: str
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabFileFolderProtectedItem(ProtectedItem):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        computer_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_sync_time_in_utc: int
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: MabFileFolderProtectedItemExtendedInfo
        friendly_name: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        protected_item_type: str
        protection_state: str
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                computer_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_sync_time_in_utc: Optional[int] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[MabFileFolderProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabFileFolderProtectedItemExtendedInfo(Model):
        last_refreshed_at: datetime
        oldest_recovery_point: datetime
        recovery_point_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                last_refreshed_at: Optional[datetime] = ..., 
                oldest_recovery_point: Optional[datetime] = ..., 
                recovery_point_count: Optional[int] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabJob(Job):
        actions_info: Union[list[str, JobSupportedAction]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: timedelta
        end_time: datetime
        entity_friendly_name: str
        error_details: list[MabErrorInfo]
        extended_info: MabJobExtendedInfo
        job_type: str
        mab_server_name: str
        mab_server_type: Union[str, MabServerType]
        operation: str
        start_time: datetime
        status: str
        workload_type: Union[str, WorkloadType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[MabErrorInfo]] = ..., 
                extended_info: Optional[MabJobExtendedInfo] = ..., 
                mab_server_name: Optional[str] = ..., 
                mab_server_type: Optional[Union[str, MabServerType]] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                workload_type: Optional[Union[str, WorkloadType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabJobExtendedInfo(Model):
        dynamic_error_message: str
        property_bag: dict[str, str]
        tasks_list: list[MabJobTaskDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[MabJobTaskDetails]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabJobTaskDetails(Model):
        duration: timedelta
        end_time: datetime
        start_time: datetime
        status: str
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.MabServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP_SERVER_CONTAINER = "AzureBackupServerContainer"
        AZURE_SQL_CONTAINER = "AzureSqlContainer"
        CLUSTER = "Cluster"
        DPM_CONTAINER = "DPMContainer"
        GENERIC_CONTAINER = "GenericContainer"
        IAAS_VM_CONTAINER = "IaasVMContainer"
        IAAS_VM_SERVICE_CONTAINER = "IaasVMServiceContainer"
        INVALID = "Invalid"
        MAB_CONTAINER = "MABContainer"
        SQLAG_WORK_LOAD_CONTAINER = "SQLAGWorkLoadContainer"
        STORAGE_CONTAINER = "StorageContainer"
        UNKNOWN = "Unknown"
        VM_APP_CONTAINER = "VMAppContainer"
        V_CENTER = "VCenter"
        WINDOWS = "Windows"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.NameInfo(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.NewErrorResponse(Model):
        error: NewErrorResponseError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[NewErrorResponseError] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.NewErrorResponseError(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[NewErrorResponse]
        message: str
        target: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatus(Model):
        end_time: datetime
        error: OperationStatusError
        id: str
        name: str
        properties: OperationStatusExtendedInfo
        start_time: datetime
        status: Union[str, OperationStatusValues]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[OperationStatusError] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[OperationStatusExtendedInfo] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, OperationStatusValues]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusError(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusExtendedInfo(Model):
        object_type: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusJobExtendedInfo(OperationStatusExtendedInfo):
        job_id: str
        object_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusJobsExtendedInfo(OperationStatusExtendedInfo):
        failed_jobs_error: dict[str, str]
        job_ids: list[str]
        object_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failed_jobs_error: Optional[dict[str, str]] = ..., 
                job_ids: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusProvisionILRExtendedInfo(OperationStatusExtendedInfo):
        object_type: str
        recovery_target: InstantItemRecoveryTarget

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recovery_target: Optional[InstantItemRecoveryTarget] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusRecoveryPointExtendedInfo(OperationStatusExtendedInfo):
        deleted_backup_item_version: str
        object_type: str
        updated_recovery_point: RecoveryPoint

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deleted_backup_item_version: Optional[str] = ..., 
                updated_recovery_point: Optional[RecoveryPoint] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OperationStatusValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.OverwriteOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL_ON_CONFLICT = "FailOnConflict"
        INVALID = "Invalid"
        OVERWRITE = "Overwrite"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.PointInTimeRange(Model):
        end_time: datetime
        start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectedItem(Model):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        protected_item_type: str
        resource_guard_operation_requests: list[str]
        source_resource_id: str
        workload_type: Union[str, DataSourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, DataSourceType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectedItemHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        NOT_REACHABLE = "NotReachable"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectedItemQueryObject(Model):
        backup_engine_name: str
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        fabric_name: str
        friendly_name: str
        health_state: Union[str, HealthState]
        item_type: Union[str, DataSourceType]
        policy_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_engine_name: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_state: Optional[Union[str, HealthState]] = ..., 
                item_type: Optional[Union[str, DataSourceType]] = ..., 
                policy_name: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectedItemResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: ProtectedItem
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProtectedItem] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectedItemResourceList(ResourceList):
        next_link: str
        value: list[ProtectedItemResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[ProtectedItemResource]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectedItemState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        PROTECTED = "Protected"
        PROTECTION_ERROR = "ProtectionError"
        PROTECTION_PAUSED = "ProtectionPaused"
        PROTECTION_STOPPED = "ProtectionStopped"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        PROTECTED = "Protected"
        PROTECTION_ERROR = "ProtectionError"
        PROTECTION_PAUSED = "ProtectionPaused"
        PROTECTION_STOPPED = "ProtectionStopped"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_RECOVERY = "FileRecovery"
        INVALID = "Invalid"
        WORKLOAD_RECOVERY = "WorkloadRecovery"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPoint(Model):
        object_type: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointDiskConfiguration(Model):
        excluded_disk_list: list[DiskInformation]
        included_disk_list: list[DiskInformation]
        number_of_disks_attached_to_vm: int
        number_of_disks_included_in_backup: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                excluded_disk_list: Optional[list[DiskInformation]] = ..., 
                included_disk_list: Optional[list[DiskInformation]] = ..., 
                number_of_disks_attached_to_vm: Optional[int] = ..., 
                number_of_disks_included_in_backup: Optional[int] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointMoveReadinessInfo(Model):
        additional_info: str
        is_ready_for_move: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_info: Optional[str] = ..., 
                is_ready_for_move: Optional[bool] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointResource(Resource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: RecoveryPoint
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[RecoveryPoint] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointResourceList(ResourceList):
        next_link: str
        value: list[RecoveryPointResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[RecoveryPointResource]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointTierInformation(Model):
        extended_info: dict[str, str]
        status: Union[str, RecoveryPointTierStatus]
        type: Union[str, RecoveryPointTierType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_info: Optional[dict[str, str]] = ..., 
                status: Optional[Union[str, RecoveryPointTierStatus]] = ..., 
                type: Optional[Union[str, RecoveryPointTierType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointTierStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DISABLED = "Disabled"
        INVALID = "Invalid"
        REHYDRATED = "Rehydrated"
        VALID = "Valid"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryPointTierType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVED_RP = "ArchivedRP"
        HARDENED_RP = "HardenedRP"
        INSTANT_RP = "InstantRP"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RecoveryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALTERNATE_LOCATION = "AlternateLocation"
        INVALID = "Invalid"
        OFFLINE = "Offline"
        ORIGINAL_LOCATION = "OriginalLocation"
        RESTORE_DISKS = "RestoreDisks"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.Resource(Model):
        e_tag: str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ResourceHealthDetails(Model):
        code: int
        message: str
        recommendations: list[str]
        title: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ResourceHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        PERSISTENT_DEGRADED = "PersistentDegraded"
        PERSISTENT_UNHEALTHY = "PersistentUnhealthy"
        TRANSIENT_DEGRADED = "TransientDegraded"
        TRANSIENT_UNHEALTHY = "TransientUnhealthy"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.ResourceList(Model):
        next_link: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RestoreFileSpecs(Model):
        file_spec_type: str
        path: str
        target_folder_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_spec_type: Optional[str] = ..., 
                path: Optional[str] = ..., 
                target_folder_path: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RestorePointQueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        DIFFERENTIAL = "Differential"
        FULL = "Full"
        FULL_AND_DIFFERENTIAL = "FullAndDifferential"
        INCREMENTAL = "Incremental"
        INVALID = "Invalid"
        LOG = "Log"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RestorePointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIFFERENTIAL = "Differential"
        FULL = "Full"
        INCREMENTAL = "Incremental"
        INVALID = "Invalid"
        LOG = "Log"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RestoreRequest(Model):
        object_type: str

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.RestoreRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_SHARE_RESTORE = "FullShareRestore"
        INVALID = "Invalid"
        ITEM_LEVEL_RESTORE = "ItemLevelRestore"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.SQLDataDirectory(Model):
        logical_name: str
        path: str
        type: Union[str, SQLDataDirectoryType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                logical_name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                type: Optional[Union[str, SQLDataDirectoryType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.SQLDataDirectoryMapping(Model):
        mapping_type: Union[str, SQLDataDirectoryType]
        source_logical_name: str
        source_path: str
        target_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mapping_type: Optional[Union[str, SQLDataDirectoryType]] = ..., 
                source_logical_name: Optional[str] = ..., 
                source_path: Optional[str] = ..., 
                target_path: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.SQLDataDirectoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        INVALID = "Invalid"
        LOG = "Log"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_REDUNDANT = "GeoRedundant"
        INVALID = "Invalid"
        LOCALLY_REDUNDANT = "LocallyRedundant"
        READ_ACCESS_GEO_ZONE_REDUNDANT = "ReadAccessGeoZoneRedundant"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.StorageTypeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.TargetAFSRestoreInfo(Model):
        name: str
        target_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                target_resource_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.TargetRestoreInfo(Model):
        container_id: str
        database_name: str
        overwrite_option: Union[str, OverwriteOptions]
        target_directory_for_file_restore: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_id: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                overwrite_option: Optional[Union[str, OverwriteOptions]] = ..., 
                target_directory_for_file_restore: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_PROTECTED_ITEM_COUNT_SUMMARY = "BackupProtectedItemCountSummary"
        BACKUP_PROTECTION_CONTAINER_COUNT_SUMMARY = "BackupProtectionContainerCountSummary"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.UsagesUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.WorkloadCrrAccessToken(CrrAccessToken):
        access_token_string: str
        b_ms_active_region: str
        backup_management_type: str
        container_id: str
        container_name: str
        container_type: str
        coordinator_service_stamp_id: str
        coordinator_service_stamp_uri: str
        datasource_container_name: str
        datasource_id: str
        datasource_name: str
        datasource_type: str
        object_type: str
        policy_id: str
        policy_name: str
        protectable_object_container_host_os_name: str
        protectable_object_friendly_name: str
        protectable_object_parent_logical_container_name: str
        protectable_object_protection_state: str
        protectable_object_unique_name: str
        protectable_object_workload_type: str
        protection_container_id: int
        protection_service_stamp_id: str
        protection_service_stamp_uri: str
        recovery_point_id: str
        recovery_point_time: str
        resource_group_name: str
        resource_id: str
        resource_name: str
        rp_is_managed_virtual_machine: bool
        rp_original_sa_option: bool
        rp_tier_information: dict[str, str]
        rp_vm_size_description: str
        subscription_id: str
        token_extended_information: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_token_string: Optional[str] = ..., 
                b_ms_active_region: Optional[str] = ..., 
                backup_management_type: Optional[str] = ..., 
                container_id: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                container_type: Optional[str] = ..., 
                coordinator_service_stamp_id: Optional[str] = ..., 
                coordinator_service_stamp_uri: Optional[str] = ..., 
                datasource_container_name: Optional[str] = ..., 
                datasource_id: Optional[str] = ..., 
                datasource_name: Optional[str] = ..., 
                datasource_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protectable_object_container_host_os_name: Optional[str] = ..., 
                protectable_object_friendly_name: Optional[str] = ..., 
                protectable_object_parent_logical_container_name: Optional[str] = ..., 
                protectable_object_protection_state: Optional[str] = ..., 
                protectable_object_unique_name: Optional[str] = ..., 
                protectable_object_workload_type: Optional[str] = ..., 
                protection_container_id: Optional[int] = ..., 
                protection_service_stamp_id: Optional[str] = ..., 
                protection_service_stamp_uri: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_time: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                rp_is_managed_virtual_machine: Optional[bool] = ..., 
                rp_original_sa_option: Optional[bool] = ..., 
                rp_tier_information: Optional[dict[str, str]] = ..., 
                rp_vm_size_description: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                token_extended_information: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.models.WorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE_SHARE = "AzureFileShare"
        AZURE_SQL_DB = "AzureSqlDb"
        CLIENT = "Client"
        EXCHANGE = "Exchange"
        FILE_FOLDER = "FileFolder"
        GENERIC_DATA_SOURCE = "GenericDataSource"
        INVALID = "Invalid"
        SAP_ASE_DATABASE = "SAPAseDatabase"
        SAP_HANA_DATABASE = "SAPHanaDatabase"
        SHAREPOINT = "Sharepoint"
        SQLDB = "SQLDB"
        SQL_DATA_BASE = "SQLDataBase"
        SYSTEM_STATE = "SystemState"
        VM = "VM"
        V_MWARE_VM = "VMwareVM"


namespace azure.mgmt.recoveryservicesbackup.passivestamp.operations

    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.AadPropertiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                azure_region: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AADPropertiesResource: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.BackupCrrJobDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get(
                self, 
                azure_region: str, 
                parameters: CrrJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResource: ...

        @overload
        def get(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResource: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.BackupCrrJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                azure_region: str, 
                parameters: CrrJobRequest, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[JobResource]: ...

        @overload
        def list(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[JobResource]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.BackupProtectedItemsCrrOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ProtectedItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.BackupResourceStorageConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> BackupResourceConfigResource: ...

        @overload
        def patch(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceConfigResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def patch(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceConfigResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupResourceConfigResource: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupResourceConfigResource: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.BackupUsageSummariesCRROperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[BackupManagementUsage]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.CrossRegionRestoreOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_trigger(
                self, 
                azure_region: str, 
                parameters: CrossRegionRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.CrrOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                azure_region: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.CrrOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                azure_region: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.RecoveryPointsCrrOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                **kwargs: Any
            ) -> RecoveryPointResource: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPointResource]: ...


    class azure.mgmt.recoveryservicesbackup.passivestamp.operations.RecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get_access_token(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: AADPropertiesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CrrAccessTokenResource: ...

        @overload
        def get_access_token(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CrrAccessTokenResource: ...


```