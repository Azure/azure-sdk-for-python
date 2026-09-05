```py
namespace azure.mgmt.dataprotection

    class azure.mgmt.dataprotection.DataProtectionMgmtClient: implements ContextManager 
        backup_instances: BackupInstancesOperations
        backup_instances_extension_routing: BackupInstancesExtensionRoutingOperations
        backup_policies: BackupPoliciesOperations
        backup_vault_operation_results: BackupVaultOperationResultsOperations
        backup_vaults: BackupVaultsOperations
        data_protection: DataProtectionOperations
        data_protection_operations: DataProtectionOperationsOperations
        deleted_backup_instances: DeletedBackupInstancesOperations
        deleted_backup_vaults: DeletedBackupVaultsOperations
        dpp_resource_guard_proxy: DppResourceGuardProxyOperations
        export_jobs: ExportJobsOperations
        export_jobs_operation_result: ExportJobsOperationResultOperations
        fetch_cross_region_restore_job: FetchCrossRegionRestoreJobOperations
        fetch_cross_region_restore_jobs: FetchCrossRegionRestoreJobsOperations
        fetch_secondary_recovery_points: FetchSecondaryRecoveryPointsOperations
        jobs: JobsOperations
        operation_result: OperationResultOperations
        operation_status: OperationStatusOperations
        operation_status_backup_vault_context: OperationStatusBackupVaultContextOperations
        operation_status_resource_group_context: OperationStatusResourceGroupContextOperations
        recovery_points: RecoveryPointsOperations
        resource_guards: ResourceGuardsOperations
        restorable_time_ranges: RestorableTimeRangesOperations

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


namespace azure.mgmt.dataprotection.aio

    class azure.mgmt.dataprotection.aio.DataProtectionMgmtClient: implements AsyncContextManager 
        backup_instances: BackupInstancesOperations
        backup_instances_extension_routing: BackupInstancesExtensionRoutingOperations
        backup_policies: BackupPoliciesOperations
        backup_vault_operation_results: BackupVaultOperationResultsOperations
        backup_vaults: BackupVaultsOperations
        data_protection: DataProtectionOperations
        data_protection_operations: DataProtectionOperationsOperations
        deleted_backup_instances: DeletedBackupInstancesOperations
        deleted_backup_vaults: DeletedBackupVaultsOperations
        dpp_resource_guard_proxy: DppResourceGuardProxyOperations
        export_jobs: ExportJobsOperations
        export_jobs_operation_result: ExportJobsOperationResultOperations
        fetch_cross_region_restore_job: FetchCrossRegionRestoreJobOperations
        fetch_cross_region_restore_jobs: FetchCrossRegionRestoreJobsOperations
        fetch_secondary_recovery_points: FetchSecondaryRecoveryPointsOperations
        jobs: JobsOperations
        operation_result: OperationResultOperations
        operation_status: OperationStatusOperations
        operation_status_backup_vault_context: OperationStatusBackupVaultContextOperations
        operation_status_resource_group_context: OperationStatusResourceGroupContextOperations
        recovery_points: RecoveryPointsOperations
        resource_guards: ResourceGuardsOperations
        restorable_time_ranges: RestorableTimeRangesOperations

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


namespace azure.mgmt.dataprotection.aio.operations

    class azure.mgmt.dataprotection.aio.operations.BackupInstancesExtensionRoutingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupInstanceResource]: ...


    class azure.mgmt.dataprotection.aio.operations.BackupInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_adhoc_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: TriggerBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_adhoc_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: TriggerBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_adhoc_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: BackupInstanceResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInstanceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: BackupInstanceResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInstanceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInstanceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                *, 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resume_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[ResumeProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[ResumeProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[StopProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[StopProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_suspend_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[SuspendBackupRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_suspend_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[SuspendBackupRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_suspend_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_sync_backup_instance(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: SyncBackupInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_sync_backup_instance(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: SyncBackupInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_sync_backup_instance(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_trigger_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_trigger_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_trigger_rehydrate(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRehydrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rehydrate(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRehydrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rehydrate(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_trigger_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_trigger_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: ValidateCrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: ValidateCrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_for_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: ValidateForBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_for_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: ValidateForBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_for_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_for_modify_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateForModifyBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_for_modify_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateForModifyBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_for_modify_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_for_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_for_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @overload
        async def begin_validate_for_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationJobExtendedInfo]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> BackupInstanceResource: ...

        @distributed_trace_async
        async def get_backup_instance_operation_result(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[BackupInstanceResource]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupInstanceResource]: ...


    class azure.mgmt.dataprotection.aio.operations.BackupPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                parameters: BaseBackupPolicyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                parameters: BaseBackupPolicyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BaseBackupPolicyResource]: ...


    class azure.mgmt.dataprotection.aio.operations.BackupVaultOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[BackupVaultResource]: ...


    class azure.mgmt.dataprotection.aio.operations.BackupVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: BackupVaultResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                x_ms_deleted_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVaultResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: BackupVaultResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                x_ms_deleted_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVaultResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                x_ms_deleted_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVaultResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: PatchResourceRequestInput, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVaultResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: PatchResourceRequestInput, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVaultResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVaultResource]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> BackupVaultResource: ...

        @distributed_trace
        def get_in_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupVaultResource]: ...

        @distributed_trace
        def get_in_subscription(self, **kwargs: Any) -> AsyncItemPaged[BackupVaultResource]: ...


    class azure.mgmt.dataprotection.aio.operations.DataProtectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_feature_support(
                self, 
                location: str, 
                parameters: FeatureValidationRequestBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FeatureValidationResponseBase: ...

        @overload
        async def check_feature_support(
                self, 
                location: str, 
                parameters: FeatureValidationRequestBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FeatureValidationResponseBase: ...

        @overload
        async def check_feature_support(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FeatureValidationResponseBase: ...


    class azure.mgmt.dataprotection.aio.operations.DataProtectionOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.dataprotection.aio.operations.DeletedBackupInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_undelete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> DeletedBackupInstanceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedBackupInstanceResource]: ...


    class azure.mgmt.dataprotection.aio.operations.DeletedBackupVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01', '2026-04-01-preview'])
        async def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedBackupVaultResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01', '2026-04-01-preview'])
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedBackupVaultResource]: ...


    class azure.mgmt.dataprotection.aio.operations.DppResourceGuardProxyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: ResourceGuardProxyBaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: ResourceGuardProxyBaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceGuardProxyBaseResource]: ...

        @overload
        async def unlock_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: UnlockDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        async def unlock_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: UnlockDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        async def unlock_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...


    class azure.mgmt.dataprotection.aio.operations.ExportJobsOperationResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ExportJobsResult]: ...


    class azure.mgmt.dataprotection.aio.operations.ExportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_trigger(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.dataprotection.aio.operations.FetchCrossRegionRestoreJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...

        @overload
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...

        @overload
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...


    class azure.mgmt.dataprotection.aio.operations.FetchCrossRegionRestoreJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupJobResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupJobResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupJobResource]: ...


    class azure.mgmt.dataprotection.aio.operations.FetchSecondaryRecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: FetchSecondaryRPsRequestParameters, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupRecoveryPointResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: FetchSecondaryRPsRequestParameters, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupRecoveryPointResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupRecoveryPointResource]: ...


    class azure.mgmt.dataprotection.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupJobResource]: ...


    class azure.mgmt.dataprotection.aio.operations.OperationResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                operation_id: str, 
                location: str, 
                **kwargs: Any
            ) -> Optional[OperationJobExtendedInfo]: ...


    class azure.mgmt.dataprotection.aio.operations.OperationStatusBackupVaultContextOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...


    class azure.mgmt.dataprotection.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...


    class azure.mgmt.dataprotection.aio.operations.OperationStatusResourceGroupContextOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...


    class azure.mgmt.dataprotection.aio.operations.RecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                recovery_point_id: str, 
                **kwargs: Any
            ) -> AzureBackupRecoveryPointResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureBackupRecoveryPointResource]: ...


    class azure.mgmt.dataprotection.aio.operations.ResourceGuardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @distributed_trace
        def get_backup_security_pin_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DppBaseResource]: ...

        @distributed_trace_async
        async def get_default_backup_security_pin_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace_async
        async def get_default_delete_protected_item_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace_async
        async def get_default_delete_resource_guard_proxy_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace_async
        async def get_default_disable_soft_delete_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace_async
        async def get_default_update_protected_item_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace_async
        async def get_default_update_protection_policy_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_delete_protected_item_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_delete_resource_guard_proxy_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_disable_soft_delete_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_resources_in_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceGuardResource]: ...

        @distributed_trace
        def get_resources_in_subscription(self, **kwargs: Any) -> AsyncItemPaged[ResourceGuardResource]: ...

        @distributed_trace
        def get_update_protected_item_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_update_protection_policy_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DppBaseResource]: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: PatchResourceGuardInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: PatchResourceGuardInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: ResourceGuardResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: ResourceGuardResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...


    class azure.mgmt.dataprotection.aio.operations.RestorableTimeRangesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def find(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupFindRestorableTimeRangesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupFindRestorableTimeRangesResponseResource: ...

        @overload
        async def find(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupFindRestorableTimeRangesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupFindRestorableTimeRangesResponseResource: ...

        @overload
        async def find(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupFindRestorableTimeRangesResponseResource: ...


namespace azure.mgmt.dataprotection.models

    class azure.mgmt.dataprotection.models.AKSVolumeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DISK = "AzureDisk"
        AZURE_FILE_SHARE_SMB = "AzureFileShareSMB"


    class azure.mgmt.dataprotection.models.AbsoluteDeleteOption(DeleteOption, discriminator='AbsoluteDeleteOption'):
        duration: str
        object_type: Literal["AbsoluteDeleteOption"]

        @overload
        def __init__(
                self, 
                *, 
                duration: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AbsoluteMarker(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_BACKUP = "AllBackup"
        FIRST_OF_DAY = "FirstOfDay"
        FIRST_OF_MONTH = "FirstOfMonth"
        FIRST_OF_WEEK = "FirstOfWeek"
        FIRST_OF_YEAR = "FirstOfYear"


    class azure.mgmt.dataprotection.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.dataprotection.models.AdHocBackupRuleOptions(_Model):
        rule_name: str
        trigger_option: AdhocBackupTriggerOption

        @overload
        def __init__(
                self, 
                *, 
                rule_name: str, 
                trigger_option: AdhocBackupTriggerOption
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AdhocBackupTriggerOption(_Model):
        retention_tag_override: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                retention_tag_override: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AdhocBasedTaggingCriteria(_Model):
        tag_info: Optional[RetentionTag]

        @overload
        def __init__(
                self, 
                *, 
                tag_info: Optional[RetentionTag] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AdhocBasedTriggerContext(TriggerContext, discriminator='AdhocBasedTriggerContext'):
        object_type: Literal["AdhocBasedTriggerContext"]
        tagging_criteria: AdhocBasedTaggingCriteria

        @overload
        def __init__(
                self, 
                *, 
                tagging_criteria: AdhocBasedTaggingCriteria
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AdlsBlobBackupDatasourceParameters(BlobBackupDatasourceParameters, discriminator='AdlsBlobBackupDatasourceParameters'):
        containers_list: list[str]
        object_type: Literal["AdlsBlobBackupDatasourceParameters"]

        @overload
        def __init__(
                self, 
                *, 
                containers_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AdlsBlobBackupDatasourceParametersForAutoProtection(BackupDatasourceParameters, discriminator='AdlsBlobBackupDatasourceParametersForAutoProtection'):
        auto_protection_settings: BlobBackupRuleBasedAutoProtectionSettings
        object_type: Literal["AdlsBlobBackupDatasourceParametersForAutoProtection"]

        @overload
        def __init__(
                self, 
                *, 
                auto_protection_settings: BlobBackupRuleBasedAutoProtectionSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AlertsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dataprotection.models.AuthCredentials(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupDiscreteRecoveryPoint(AzureBackupRecoveryPoint, discriminator='AzureBackupDiscreteRecoveryPoint'):
        expiry_time: Optional[datetime]
        friendly_name: Optional[str]
        object_type: Literal["AzureBackupDiscreteRecoveryPoint"]
        policy_name: Optional[str]
        policy_version: Optional[str]
        recovery_point_data_stores_details: Optional[list[RecoveryPointDataStoreDetails]]
        recovery_point_id: Optional[str]
        recovery_point_state: Optional[Union[str, RecoveryPointCompletionState]]
        recovery_point_time: datetime
        recovery_point_type: Optional[str]
        retention_tag_name: Optional[str]
        retention_tag_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                policy_version: Optional[str] = ..., 
                recovery_point_data_stores_details: Optional[list[RecoveryPointDataStoreDetails]] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_state: Optional[Union[str, RecoveryPointCompletionState]] = ..., 
                recovery_point_time: datetime, 
                recovery_point_type: Optional[str] = ..., 
                retention_tag_name: Optional[str] = ..., 
                retention_tag_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupFindRestorableTimeRangesRequest(_Model):
        end_time: Optional[str]
        source_data_store_type: Union[str, RestoreSourceDataStoreType]
        start_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                source_data_store_type: Union[str, RestoreSourceDataStoreType], 
                start_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupFindRestorableTimeRangesResponse(_Model):
        object_type: Optional[str]
        restorable_time_ranges: Optional[list[RestorableTimeRange]]

        @overload
        def __init__(
                self, 
                *, 
                object_type: Optional[str] = ..., 
                restorable_time_ranges: Optional[list[RestorableTimeRange]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupFindRestorableTimeRangesResponseResource(DppResource):
        id: str
        name: str
        properties: Optional[AzureBackupFindRestorableTimeRangesResponse]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureBackupFindRestorableTimeRangesResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupJob(_Model):
        activity_id: str
        backup_instance_friendly_name: str
        backup_instance_id: Optional[str]
        data_source_id: str
        data_source_location: str
        data_source_name: str
        data_source_set_name: Optional[str]
        data_source_type: str
        destination_data_store_name: Optional[str]
        duration: Optional[str]
        end_time: Optional[datetime]
        error_details: Optional[list[UserFacingError]]
        etag: Optional[str]
        extended_info: Optional[JobExtendedInfo]
        is_user_triggered: bool
        operation: str
        operation_category: str
        policy_id: Optional[str]
        policy_name: Optional[str]
        progress_enabled: bool
        progress_url: Optional[str]
        rehydration_priority: Optional[str]
        restore_type: Optional[str]
        source_data_store_name: Optional[str]
        source_resource_group: str
        source_subscription_id: str
        start_time: datetime
        status: str
        subscription_id: str
        supported_actions: list[str]
        vault_name: str

        @overload
        def __init__(
                self, 
                *, 
                activity_id: str, 
                backup_instance_friendly_name: str, 
                data_source_id: str, 
                data_source_location: str, 
                data_source_name: str, 
                data_source_set_name: Optional[str] = ..., 
                data_source_type: str, 
                destination_data_store_name: Optional[str] = ..., 
                duration: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                is_user_triggered: bool, 
                operation: str, 
                operation_category: str, 
                progress_enabled: bool, 
                source_data_store_name: Optional[str] = ..., 
                source_resource_group: str, 
                source_subscription_id: str, 
                start_time: datetime, 
                status: str, 
                subscription_id: str, 
                supported_actions: list[str], 
                vault_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupJobResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AzureBackupJob]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureBackupJob] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupParams(BackupParameters, discriminator='AzureBackupParams'):
        backup_type: str
        object_type: Literal["AzureBackupParams"]

        @overload
        def __init__(
                self, 
                *, 
                backup_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRecoveryPoint(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRecoveryPointBasedRestoreRequest(AzureBackupRestoreRequest, discriminator='AzureBackupRecoveryPointBasedRestoreRequest'):
        identity_details: IdentityDetails
        object_type: Literal["AzureBackupRecoveryPointBasedRestoreRequest"]
        recovery_point_id: str
        resource_guard_operation_requests: list[str]
        restore_target_info: RestoreTargetInfoBase
        source_data_store_type: Union[str, SourceDataStoreType]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                identity_details: Optional[IdentityDetails] = ..., 
                recovery_point_id: str, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_target_info: RestoreTargetInfoBase, 
                source_data_store_type: Union[str, SourceDataStoreType], 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRecoveryPointResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AzureBackupRecoveryPoint]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureBackupRecoveryPoint] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRecoveryTimeBasedRestoreRequest(AzureBackupRestoreRequest, discriminator='AzureBackupRecoveryTimeBasedRestoreRequest'):
        identity_details: IdentityDetails
        object_type: Literal["AzureBackupRecoveryTimeBasedRestoreRequest"]
        recovery_point_time: str
        resource_guard_operation_requests: list[str]
        restore_target_info: RestoreTargetInfoBase
        source_data_store_type: Union[str, SourceDataStoreType]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                identity_details: Optional[IdentityDetails] = ..., 
                recovery_point_time: str, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_target_info: RestoreTargetInfoBase, 
                source_data_store_type: Union[str, SourceDataStoreType], 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRehydrationRequest(_Model):
        recovery_point_id: str
        rehydration_priority: Optional[Union[str, RehydrationPriority]]
        rehydration_retention_duration: str

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_id: str, 
                rehydration_priority: Optional[Union[str, RehydrationPriority]] = ..., 
                rehydration_retention_duration: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRestoreRequest(_Model):
        identity_details: Optional[IdentityDetails]
        object_type: str
        resource_guard_operation_requests: Optional[list[str]]
        restore_target_info: RestoreTargetInfoBase
        source_data_store_type: Union[str, SourceDataStoreType]
        source_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_details: Optional[IdentityDetails] = ..., 
                object_type: str, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_target_info: RestoreTargetInfoBase, 
                source_data_store_type: Union[str, SourceDataStoreType], 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRestoreWithRehydrationRequest(AzureBackupRecoveryPointBasedRestoreRequest, discriminator='AzureBackupRestoreWithRehydrationRequest'):
        identity_details: IdentityDetails
        object_type: Literal["AzureBackupRestoreWithRehydrationRequest"]
        recovery_point_id: str
        rehydration_priority: Union[str, RehydrationPriority]
        rehydration_retention_duration: str
        resource_guard_operation_requests: list[str]
        restore_target_info: RestoreTargetInfoBase
        source_data_store_type: Union[str, SourceDataStoreType]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                identity_details: Optional[IdentityDetails] = ..., 
                recovery_point_id: str, 
                rehydration_priority: Union[str, RehydrationPriority], 
                rehydration_retention_duration: str, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_target_info: RestoreTargetInfoBase, 
                source_data_store_type: Union[str, SourceDataStoreType], 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureBackupRule(BasePolicyRule, discriminator='AzureBackupRule'):
        backup_parameters: Optional[BackupParameters]
        data_store: DataStoreInfoBase
        name: str
        object_type: Literal["AzureBackupRule"]
        trigger: TriggerContext

        @overload
        def __init__(
                self, 
                *, 
                backup_parameters: Optional[BackupParameters] = ..., 
                data_store: DataStoreInfoBase, 
                name: str, 
                trigger: TriggerContext
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureMonitorAlertSettings(_Model):
        alerts_for_all_job_failures: Optional[Union[str, AlertsState]]

        @overload
        def __init__(
                self, 
                *, 
                alerts_for_all_job_failures: Optional[Union[str, AlertsState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureOperationalStoreParameters(DataStoreParameters, discriminator='AzureOperationalStoreParameters'):
        data_store_type: Union[str, DataStoreTypes]
        object_type: Literal["AzureOperationalStoreParameters"]
        resource_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_store_type: Union[str, DataStoreTypes], 
                resource_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.AzureRetentionRule(BasePolicyRule, discriminator='AzureRetentionRule'):
        is_default: Optional[bool]
        lifecycles: list[SourceLifeCycle]
        name: str
        object_type: Literal["AzureRetentionRule"]

        @overload
        def __init__(
                self, 
                *, 
                is_default: Optional[bool] = ..., 
                lifecycles: list[SourceLifeCycle], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BCDRSecurityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCELLENT = "Excellent"
        FAIR = "Fair"
        GOOD = "Good"
        NOT_SUPPORTED = "NotSupported"
        POOR = "Poor"


    class azure.mgmt.dataprotection.models.BackupCriteria(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupDatasourceParameters(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupInstance(_Model):
        current_protection_state: Optional[Union[str, CurrentProtectionState]]
        data_source_info: Datasource
        data_source_set_info: Optional[DatasourceSet]
        datasource_auth_credentials: Optional[AuthCredentials]
        friendly_name: Optional[str]
        identity_details: Optional[IdentityDetails]
        object_type: str
        policy_info: PolicyInfo
        protection_error_details: Optional[UserFacingError]
        protection_status: Optional[ProtectionStatusDetails]
        provisioning_state: Optional[str]
        resource_guard_operation_requests: Optional[list[str]]
        validation_type: Optional[Union[str, ValidationType]]

        @overload
        def __init__(
                self, 
                *, 
                data_source_info: Datasource, 
                data_source_set_info: Optional[DatasourceSet] = ..., 
                datasource_auth_credentials: Optional[AuthCredentials] = ..., 
                friendly_name: Optional[str] = ..., 
                identity_details: Optional[IdentityDetails] = ..., 
                object_type: str, 
                policy_info: PolicyInfo, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                validation_type: Optional[Union[str, ValidationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupInstanceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[BackupInstance]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BackupInstance] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupParameters(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupPolicy(BaseBackupPolicy, discriminator='BackupPolicy'):
        datasource_types: list[str]
        object_type: Literal["BackupPolicy"]
        policy_rules: list[BasePolicyRule]

        @overload
        def __init__(
                self, 
                *, 
                datasource_types: list[str], 
                policy_rules: list[BasePolicyRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupSchedule(_Model):
        repeating_time_intervals: list[str]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                repeating_time_intervals: list[str], 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupSolutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGICAL_BACKUP = "LogicalBackup"
        PHYSICAL_BACKUP = "PhysicalBackup"


    class azure.mgmt.dataprotection.models.BackupVault(_Model):
        bcdr_security_level: Optional[Union[str, BCDRSecurityLevel]]
        feature_settings: Optional[FeatureSettings]
        is_vault_protected_by_resource_guard: Optional[bool]
        monitoring_settings: Optional[MonitoringSettings]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replicated_regions: Optional[list[str]]
        resource_guard_operation_requests: Optional[list[str]]
        resource_move_details: Optional[ResourceMoveDetails]
        resource_move_state: Optional[Union[str, ResourceMoveState]]
        secure_score: Optional[Union[str, SecureScoreLevel]]
        security_settings: Optional[SecuritySettings]
        storage_settings: Optional[list[StorageSetting]]

        @overload
        def __init__(
                self, 
                *, 
                feature_settings: Optional[FeatureSettings] = ..., 
                monitoring_settings: Optional[MonitoringSettings] = ..., 
                replicated_regions: Optional[list[str]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                security_settings: Optional[SecuritySettings] = ..., 
                storage_settings: Optional[list[StorageSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BackupVaultResource(TrackedResource):
        e_tag: Optional[str]
        id: str
        identity: Optional[DppIdentityDetails]
        location: str
        name: str
        properties: BackupVault
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                identity: Optional[DppIdentityDetails] = ..., 
                location: str, 
                properties: BackupVault, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BaseBackupPolicy(_Model):
        datasource_types: list[str]
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                datasource_types: list[str], 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BaseBackupPolicyResource(ProxyResource):
        id: str
        name: str
        properties: Optional[BaseBackupPolicy]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BaseBackupPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BasePolicyRule(_Model):
        name: str
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BaseResourceProperties(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BlobBackupAutoProtectionRule(_Model):
        mode: Union[str, BlobBackupRuleMode]
        object_type: str
        pattern: str
        type: Union[str, BlobBackupPatternType]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, BlobBackupRuleMode], 
                object_type: str, 
                pattern: str, 
                type: Union[str, BlobBackupPatternType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BlobBackupAutoProtectionSettings(_Model):
        enabled: bool
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BlobBackupDatasourceParameters(BackupDatasourceParameters, discriminator='BlobBackupDatasourceParameters'):
        containers_list: list[str]
        object_type: Literal["BlobBackupDatasourceParameters"]

        @overload
        def __init__(
                self, 
                *, 
                containers_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BlobBackupDatasourceParametersForAutoProtection(BackupDatasourceParameters, discriminator='BlobBackupDatasourceParametersForAutoProtection'):
        auto_protection_settings: BlobBackupRuleBasedAutoProtectionSettings
        object_type: Literal["BlobBackupDatasourceParametersForAutoProtection"]

        @overload
        def __init__(
                self, 
                *, 
                auto_protection_settings: BlobBackupRuleBasedAutoProtectionSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BlobBackupPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREFIX = "Prefix"


    class azure.mgmt.dataprotection.models.BlobBackupRuleBasedAutoProtectionSettings(BlobBackupAutoProtectionSettings, discriminator='BlobBackupRuleBasedAutoProtectionSettings'):
        enabled: bool
        object_type: Literal["BlobBackupRuleBasedAutoProtectionSettings"]
        rules: Optional[list[BlobBackupAutoProtectionRule]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                rules: Optional[list[BlobBackupAutoProtectionRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.BlobBackupRuleMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"


    class azure.mgmt.dataprotection.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CloudError(_Model):
        error: Optional[Error]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[Error] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CmkKekIdentity(_Model):
        identity_id: Optional[str]
        identity_type: Optional[Union[str, IdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                identity_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, IdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CmkKeyVaultProperties(_Model):
        key_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CopyOnExpiryOption(CopyOption, discriminator='CopyOnExpiryOption'):
        object_type: Literal["CopyOnExpiryOption"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CopyOption(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dataprotection.models.CrossRegionRestoreDetails(_Model):
        source_backup_instance_id: str
        source_region: str

        @overload
        def __init__(
                self, 
                *, 
                source_backup_instance_id: str, 
                source_region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CrossRegionRestoreJobRequest(_Model):
        job_id: str
        source_backup_vault_id: str
        source_region: str

        @overload
        def __init__(
                self, 
                *, 
                job_id: str, 
                source_backup_vault_id: str, 
                source_region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CrossRegionRestoreJobsRequest(_Model):
        source_backup_vault_id: str
        source_region: str

        @overload
        def __init__(
                self, 
                *, 
                source_backup_vault_id: str, 
                source_region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CrossRegionRestoreRequestObject(_Model):
        cross_region_restore_details: CrossRegionRestoreDetails
        restore_request_object: AzureBackupRestoreRequest

        @overload
        def __init__(
                self, 
                *, 
                cross_region_restore_details: CrossRegionRestoreDetails, 
                restore_request_object: AzureBackupRestoreRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CrossRegionRestoreSettings(_Model):
        state: Optional[Union[str, CrossRegionRestoreState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, CrossRegionRestoreState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CrossRegionRestoreState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dataprotection.models.CrossSubscriptionRestoreSettings(_Model):
        state: Optional[Union[str, CrossSubscriptionRestoreState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, CrossSubscriptionRestoreState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.CrossSubscriptionRestoreState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PERMANENTLY_DISABLED = "PermanentlyDisabled"


    class azure.mgmt.dataprotection.models.CurrentProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_SCHEDULES_SUSPENDED = "BackupSchedulesSuspended"
        CONFIGURING_PROTECTION = "ConfiguringProtection"
        CONFIGURING_PROTECTION_FAILED = "ConfiguringProtectionFailed"
        INVALID = "Invalid"
        NOT_PROTECTED = "NotProtected"
        PROTECTION_CONFIGURED = "ProtectionConfigured"
        PROTECTION_ERROR = "ProtectionError"
        PROTECTION_STOPPED = "ProtectionStopped"
        RETENTION_SCHEDULES_SUSPENDED = "RetentionSchedulesSuspended"
        SOFT_DELETED = "SoftDeleted"
        SOFT_DELETING = "SoftDeleting"
        UPDATING_PROTECTION = "UpdatingProtection"


    class azure.mgmt.dataprotection.models.CustomCopyOption(CopyOption, discriminator='CustomCopyOption'):
        duration: Optional[str]
        object_type: Literal["CustomCopyOption"]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DataStoreInfoBase(_Model):
        data_store_type: Union[str, DataStoreTypes]
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                data_store_type: Union[str, DataStoreTypes], 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DataStoreParameters(_Model):
        data_store_type: Union[str, DataStoreTypes]
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                data_store_type: Union[str, DataStoreTypes], 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DataStoreTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVE_STORE = "ArchiveStore"
        OPERATIONAL_STORE = "OperationalStore"
        VAULT_STORE = "VaultStore"


    class azure.mgmt.dataprotection.models.Datasource(_Model):
        datasource_type: Optional[str]
        object_type: Optional[str]
        resource_id: str
        resource_location: Optional[str]
        resource_name: Optional[str]
        resource_properties: Optional[BaseResourceProperties]
        resource_type: Optional[str]
        resource_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                datasource_type: Optional[str] = ..., 
                object_type: Optional[str] = ..., 
                resource_id: str, 
                resource_location: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_properties: Optional[BaseResourceProperties] = ..., 
                resource_type: Optional[str] = ..., 
                resource_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DatasourceSet(_Model):
        datasource_type: Optional[str]
        object_type: Optional[str]
        resource_id: str
        resource_location: Optional[str]
        resource_name: Optional[str]
        resource_properties: Optional[BaseResourceProperties]
        resource_type: Optional[str]
        resource_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                datasource_type: Optional[str] = ..., 
                object_type: Optional[str] = ..., 
                resource_id: str, 
                resource_location: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_properties: Optional[BaseResourceProperties] = ..., 
                resource_type: Optional[str] = ..., 
                resource_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.Day(_Model):
        date: Optional[int]
        is_last: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                date: Optional[int] = ..., 
                is_last: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.dataprotection.models.DefaultResourceProperties(BaseResourceProperties, discriminator='DefaultResourceProperties'):
        object_type: Literal[ResourcePropertiesObjectType.DEFAULT_RESOURCE_PROPERTIES]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DeleteOption(_Model):
        duration: str
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                duration: str, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DeletedBackupInstance(BackupInstance):
        current_protection_state: Union[str, CurrentProtectionState]
        data_source_info: Datasource
        data_source_set_info: DatasourceSet
        datasource_auth_credentials: AuthCredentials
        deletion_info: Optional[DeletionInfo]
        friendly_name: str
        identity_details: IdentityDetails
        object_type: str
        policy_info: PolicyInfo
        protection_error_details: UserFacingError
        protection_status: ProtectionStatusDetails
        provisioning_state: str
        resource_guard_operation_requests: list[str]
        validation_type: Union[str, ValidationType]

        @overload
        def __init__(
                self, 
                *, 
                data_source_info: Datasource, 
                data_source_set_info: Optional[DatasourceSet] = ..., 
                datasource_auth_credentials: Optional[AuthCredentials] = ..., 
                friendly_name: Optional[str] = ..., 
                identity_details: Optional[IdentityDetails] = ..., 
                object_type: str, 
                policy_info: PolicyInfo, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                validation_type: Optional[Union[str, ValidationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DeletedBackupInstanceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DeletedBackupInstance]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeletedBackupInstance] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DeletedBackupVault(_Model):
        bcdr_security_level: Optional[Union[str, BCDRSecurityLevel]]
        feature_settings: Optional[FeatureSettings]
        is_vault_protected_by_resource_guard: Optional[bool]
        monitoring_settings: Optional[MonitoringSettings]
        original_backup_vault_id: str
        original_backup_vault_name: str
        original_backup_vault_resource_path: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replicated_regions: Optional[list[str]]
        resource_deletion_info: ResourceDeletionInfo
        resource_guard_operation_requests: Optional[list[str]]
        resource_move_details: Optional[ResourceMoveDetails]
        resource_move_state: Optional[Union[str, ResourceMoveState]]
        secure_score: Optional[Union[str, SecureScoreLevel]]
        security_settings: Optional[SecuritySettings]
        storage_settings: Optional[list[StorageSetting]]

        @overload
        def __init__(
                self, 
                *, 
                feature_settings: Optional[FeatureSettings] = ..., 
                monitoring_settings: Optional[MonitoringSettings] = ..., 
                replicated_regions: Optional[list[str]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                security_settings: Optional[SecuritySettings] = ..., 
                storage_settings: Optional[list[StorageSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DeletedBackupVaultResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DeletedBackupVault]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeletedBackupVault] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DeletionInfo(_Model):
        billing_end_date: Optional[str]
        delete_activity_id: Optional[str]
        deletion_time: Optional[str]
        scheduled_purge_time: Optional[str]


    class azure.mgmt.dataprotection.models.DppBaseResource(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dataprotection.models.DppIdentityDetails(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[str]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DppResource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dataprotection.models.DppResourceList(_Model):
        next_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.DppTrackedResourceList(_Model):
        next_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.EncryptionSettings(_Model):
        infrastructure_encryption: Optional[Union[str, InfrastructureEncryptionState]]
        kek_identity: Optional[CmkKekIdentity]
        key_vault_properties: Optional[CmkKeyVaultProperties]
        state: Optional[Union[str, EncryptionState]]

        @overload
        def __init__(
                self, 
                *, 
                infrastructure_encryption: Optional[Union[str, InfrastructureEncryptionState]] = ..., 
                kek_identity: Optional[CmkKekIdentity] = ..., 
                key_vault_properties: Optional[CmkKeyVaultProperties] = ..., 
                state: Optional[Union[str, EncryptionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.EncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INCONSISTENT = "Inconsistent"


    class azure.mgmt.dataprotection.models.Error(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[Error]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dataprotection.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.dataprotection.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dataprotection.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ExistingResourcePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PATCH = "Patch"
        SKIP = "Skip"


    class azure.mgmt.dataprotection.models.ExportJobsResult(_Model):
        blob_sas_key: Optional[str]
        blob_url: Optional[str]
        excel_file_blob_sas_key: Optional[str]
        excel_file_blob_url: Optional[str]


    class azure.mgmt.dataprotection.models.FeatureSettings(_Model):
        cross_region_restore_settings: Optional[CrossRegionRestoreSettings]
        cross_subscription_restore_settings: Optional[CrossSubscriptionRestoreSettings]

        @overload
        def __init__(
                self, 
                *, 
                cross_region_restore_settings: Optional[CrossRegionRestoreSettings] = ..., 
                cross_subscription_restore_settings: Optional[CrossSubscriptionRestoreSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.FeatureSupportStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALPHA_PREVIEW = "AlphaPreview"
        GENERALLY_AVAILABLE = "GenerallyAvailable"
        INVALID = "Invalid"
        NOT_SUPPORTED = "NotSupported"
        PRIVATE_PREVIEW = "PrivatePreview"
        PUBLIC_PREVIEW = "PublicPreview"


    class azure.mgmt.dataprotection.models.FeatureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SOURCE_TYPE = "DataSourceType"
        INVALID = "Invalid"


    class azure.mgmt.dataprotection.models.FeatureValidationRequest(FeatureValidationRequestBase, discriminator='FeatureValidationRequest'):
        feature_name: Optional[str]
        feature_type: Optional[Union[str, FeatureType]]
        object_type: Literal["FeatureValidationRequest"]

        @overload
        def __init__(
                self, 
                *, 
                feature_name: Optional[str] = ..., 
                feature_type: Optional[Union[str, FeatureType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.FeatureValidationRequestBase(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.FeatureValidationResponse(FeatureValidationResponseBase, discriminator='FeatureValidationResponse'):
        feature_type: Optional[Union[str, FeatureType]]
        features: Optional[list[SupportedFeature]]
        object_type: Literal["FeatureValidationResponse"]

        @overload
        def __init__(
                self, 
                *, 
                feature_type: Optional[Union[str, FeatureType]] = ..., 
                features: Optional[list[SupportedFeature]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.FeatureValidationResponseBase(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.FetchSecondaryRPsRequestParameters(_Model):
        source_backup_instance_id: Optional[str]
        source_region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_backup_instance_id: Optional[str] = ..., 
                source_region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.IdentityDetails(_Model):
        use_system_assigned_identity: Optional[bool]
        user_assigned_identity_arm_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                use_system_assigned_identity: Optional[bool] = ..., 
                user_assigned_identity_arm_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.dataprotection.models.ImmediateCopyOption(CopyOption, discriminator='ImmediateCopyOption'):
        object_type: Literal["ImmediateCopyOption"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ImmutabilitySettings(_Model):
        state: Optional[Union[str, ImmutabilityState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, ImmutabilityState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ImmutabilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.dataprotection.models.InfrastructureEncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dataprotection.models.InnerError(_Model):
        additional_info: Optional[dict[str, str]]
        code: Optional[str]
        embedded_inner_error: Optional[InnerError]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[dict[str, str]] = ..., 
                code: Optional[str] = ..., 
                embedded_inner_error: Optional[InnerError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ItemLevelRestoreCriteria(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ItemLevelRestoreTargetInfo(RestoreTargetInfoBase, discriminator='ItemLevelRestoreTargetInfo'):
        datasource_auth_credentials: Optional[AuthCredentials]
        datasource_info: Datasource
        datasource_set_info: Optional[DatasourceSet]
        object_type: Literal["ItemLevelRestoreTargetInfo"]
        recovery_option: Union[str, RecoveryOption]
        restore_criteria: list[ItemLevelRestoreCriteria]
        restore_location: str

        @overload
        def __init__(
                self, 
                *, 
                datasource_auth_credentials: Optional[AuthCredentials] = ..., 
                datasource_info: Datasource, 
                datasource_set_info: Optional[DatasourceSet] = ..., 
                recovery_option: Union[str, RecoveryOption], 
                restore_criteria: list[ItemLevelRestoreCriteria], 
                restore_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ItemPathBasedRestoreCriteria(ItemLevelRestoreCriteria, discriminator='ItemPathBasedRestoreCriteria'):
        is_path_relative_to_backup_item: bool
        item_path: str
        object_type: Literal["ItemPathBasedRestoreCriteria"]
        rename_to: Optional[str]
        sub_item_path_prefix: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                is_path_relative_to_backup_item: bool, 
                item_path: str, 
                rename_to: Optional[str] = ..., 
                sub_item_path_prefix: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.JobExtendedInfo(_Model):
        additional_details: Optional[dict[str, str]]
        backup_instance_state: Optional[str]
        data_transferred_in_bytes: Optional[float]
        recovery_destination: Optional[str]
        source_recover_point: Optional[RestoreJobRecoveryPointDetails]
        sub_tasks: Optional[list[JobSubTask]]
        target_recover_point: Optional[RestoreJobRecoveryPointDetails]
        warning_details: Optional[list[UserFacingWarningDetail]]

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.JobSubTask(_Model):
        additional_details: Optional[dict[str, str]]
        task_id: int
        task_name: str
        task_progress: Optional[str]
        task_status: str

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[dict[str, str]] = ..., 
                task_id: int, 
                task_name: str, 
                task_status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.KubernetesClusterBackupDatasourceParameters(BackupDatasourceParameters, discriminator='KubernetesClusterBackupDatasourceParameters'):
        backup_hook_references: Optional[list[NamespacedNameResource]]
        excluded_namespaces: Optional[list[str]]
        excluded_resource_types: Optional[list[str]]
        include_cluster_scope_resources: bool
        included_namespaces: Optional[list[str]]
        included_resource_types: Optional[list[str]]
        included_volume_types: Optional[list[Union[str, AKSVolumeTypes]]]
        label_selectors: Optional[list[str]]
        object_type: Literal["KubernetesClusterBackupDatasourceParameters"]
        snapshot_volumes: bool

        @overload
        def __init__(
                self, 
                *, 
                backup_hook_references: Optional[list[NamespacedNameResource]] = ..., 
                excluded_namespaces: Optional[list[str]] = ..., 
                excluded_resource_types: Optional[list[str]] = ..., 
                include_cluster_scope_resources: bool, 
                included_namespaces: Optional[list[str]] = ..., 
                included_resource_types: Optional[list[str]] = ..., 
                included_volume_types: Optional[list[Union[str, AKSVolumeTypes]]] = ..., 
                label_selectors: Optional[list[str]] = ..., 
                snapshot_volumes: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.KubernetesClusterRestoreCriteria(ItemLevelRestoreCriteria, discriminator='KubernetesClusterRestoreCriteria'):
        conflict_policy: Optional[Union[str, ExistingResourcePolicy]]
        excluded_namespaces: Optional[list[str]]
        excluded_resource_types: Optional[list[str]]
        include_cluster_scope_resources: bool
        included_namespaces: Optional[list[str]]
        included_resource_types: Optional[list[str]]
        label_selectors: Optional[list[str]]
        namespace_mappings: Optional[dict[str, str]]
        object_type: Literal["KubernetesClusterRestoreCriteria"]
        persistent_volume_restore_mode: Optional[Union[str, PersistentVolumeRestoreMode]]
        resource_modifier_reference: Optional[NamespacedNameResource]
        restore_hook_references: Optional[list[NamespacedNameResource]]

        @overload
        def __init__(
                self, 
                *, 
                conflict_policy: Optional[Union[str, ExistingResourcePolicy]] = ..., 
                excluded_namespaces: Optional[list[str]] = ..., 
                excluded_resource_types: Optional[list[str]] = ..., 
                include_cluster_scope_resources: bool, 
                included_namespaces: Optional[list[str]] = ..., 
                included_resource_types: Optional[list[str]] = ..., 
                label_selectors: Optional[list[str]] = ..., 
                namespace_mappings: Optional[dict[str, str]] = ..., 
                persistent_volume_restore_mode: Optional[Union[str, PersistentVolumeRestoreMode]] = ..., 
                resource_modifier_reference: Optional[NamespacedNameResource] = ..., 
                restore_hook_references: Optional[list[NamespacedNameResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.KubernetesClusterVaultTierRestoreCriteria(ItemLevelRestoreCriteria, discriminator='KubernetesClusterVaultTierRestoreCriteria'):
        conflict_policy: Optional[Union[str, ExistingResourcePolicy]]
        excluded_namespaces: Optional[list[str]]
        excluded_resource_types: Optional[list[str]]
        include_cluster_scope_resources: bool
        included_namespaces: Optional[list[str]]
        included_resource_types: Optional[list[str]]
        label_selectors: Optional[list[str]]
        namespace_mappings: Optional[dict[str, str]]
        object_type: Literal["KubernetesClusterVaultTierRestoreCriteria"]
        persistent_volume_restore_mode: Optional[Union[str, PersistentVolumeRestoreMode]]
        resource_modifier_reference: Optional[NamespacedNameResource]
        restore_hook_references: Optional[list[NamespacedNameResource]]
        staging_resource_group_id: Optional[str]
        staging_storage_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                conflict_policy: Optional[Union[str, ExistingResourcePolicy]] = ..., 
                excluded_namespaces: Optional[list[str]] = ..., 
                excluded_resource_types: Optional[list[str]] = ..., 
                include_cluster_scope_resources: bool, 
                included_namespaces: Optional[list[str]] = ..., 
                included_resource_types: Optional[list[str]] = ..., 
                label_selectors: Optional[list[str]] = ..., 
                namespace_mappings: Optional[dict[str, str]] = ..., 
                persistent_volume_restore_mode: Optional[Union[str, PersistentVolumeRestoreMode]] = ..., 
                resource_modifier_reference: Optional[NamespacedNameResource] = ..., 
                restore_hook_references: Optional[list[NamespacedNameResource]] = ..., 
                staging_resource_group_id: Optional[str] = ..., 
                staging_storage_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.KubernetesPVRestoreCriteria(ItemLevelRestoreCriteria, discriminator='KubernetesPVRestoreCriteria'):
        name: Optional[str]
        object_type: Literal["KubernetesPVRestoreCriteria"]
        storage_class_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                storage_class_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.KubernetesStorageClassRestoreCriteria(ItemLevelRestoreCriteria, discriminator='KubernetesStorageClassRestoreCriteria'):
        object_type: Literal["KubernetesStorageClassRestoreCriteria"]
        provisioner: Optional[str]
        selected_storage_class_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provisioner: Optional[str] = ..., 
                selected_storage_class_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.MonitoringSettings(_Model):
        azure_monitor_alert_settings: Optional[AzureMonitorAlertSettings]

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_alert_settings: Optional[AzureMonitorAlertSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.Month(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APRIL = "April"
        AUGUST = "August"
        DECEMBER = "December"
        FEBRUARY = "February"
        JANUARY = "January"
        JULY = "July"
        JUNE = "June"
        MARCH = "March"
        MAY = "May"
        NOVEMBER = "November"
        OCTOBER = "October"
        SEPTEMBER = "September"


    class azure.mgmt.dataprotection.models.NamespacedNameResource(_Model):
        name: Optional[str]
        namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.Operation(_Model):
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


    class azure.mgmt.dataprotection.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.dataprotection.models.OperationExtendedInfo(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.OperationJobExtendedInfo(OperationExtendedInfo, discriminator='OperationJobExtendedInfo'):
        job_id: Optional[str]
        object_type: Literal["OperationJobExtendedInfo"]

        @overload
        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.OperationResource(_Model):
        end_time: Optional[datetime]
        error: Optional[Error]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[OperationExtendedInfo]
        start_time: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[Error] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[OperationExtendedInfo] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.dataprotection.models.PatchBackupVaultInput(_Model):
        feature_settings: Optional[FeatureSettings]
        monitoring_settings: Optional[MonitoringSettings]
        resource_guard_operation_requests: Optional[list[str]]
        security_settings: Optional[SecuritySettings]

        @overload
        def __init__(
                self, 
                *, 
                feature_settings: Optional[FeatureSettings] = ..., 
                monitoring_settings: Optional[MonitoringSettings] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                security_settings: Optional[SecuritySettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.PatchResourceGuardInput(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.PatchResourceRequestInput(_Model):
        identity: Optional[DppIdentityDetails]
        properties: Optional[PatchBackupVaultInput]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[DppIdentityDetails] = ..., 
                properties: Optional[PatchBackupVaultInput] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.PersistentVolumeRestoreMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESTORE_WITHOUT_VOLUME_DATA = "RestoreWithoutVolumeData"
        RESTORE_WITH_VOLUME_DATA = "RestoreWithVolumeData"


    class azure.mgmt.dataprotection.models.PolicyInfo(_Model):
        policy_id: str
        policy_parameters: Optional[PolicyParameters]
        policy_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: str, 
                policy_parameters: Optional[PolicyParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.PolicyParameters(_Model):
        backup_datasource_parameters_list: Optional[list[BackupDatasourceParameters]]
        data_store_parameters_list: Optional[list[DataStoreParameters]]

        @overload
        def __init__(
                self, 
                *, 
                backup_datasource_parameters_list: Optional[list[BackupDatasourceParameters]] = ..., 
                data_store_parameters_list: Optional[list[DataStoreParameters]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.PostgreSqlFlexibleServerBackupDatasourceParameters(BackupDatasourceParameters, discriminator='PostgreSqlFlexibleServerBackupDatasourceParameters'):
        backup_solution_type: Optional[Union[str, BackupSolutionType]]
        object_type: Literal["PostgreSqlFlexibleServerBackupDatasourceParameters"]

        @overload
        def __init__(
                self, 
                *, 
                backup_solution_type: Optional[Union[str, BackupSolutionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ProtectionStatusDetails(_Model):
        error_details: Optional[UserFacingError]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[UserFacingError] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.dataprotection.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dataprotection.models.RangeBasedItemLevelRestoreCriteria(ItemLevelRestoreCriteria, discriminator='RangeBasedItemLevelRestoreCriteria'):
        max_matching_value: Optional[str]
        min_matching_value: Optional[str]
        object_type: Literal["RangeBasedItemLevelRestoreCriteria"]

        @overload
        def __init__(
                self, 
                *, 
                max_matching_value: Optional[str] = ..., 
                min_matching_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RecoveryOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL_IF_EXISTS = "FailIfExists"


    class azure.mgmt.dataprotection.models.RecoveryPointCompletionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        PARTIAL = "Partial"


    class azure.mgmt.dataprotection.models.RecoveryPointDataStoreDetails(_Model):
        creation_time: Optional[datetime]
        expiry_time: Optional[datetime]
        id: Optional[str]
        meta_data: Optional[str]
        rehydration_expiry_time: Optional[datetime]
        rehydration_status: Optional[Union[str, RehydrationStatus]]
        state: Optional[str]
        type: Optional[str]
        visible: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                expiry_time: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                meta_data: Optional[str] = ..., 
                state: Optional[str] = ..., 
                type: Optional[str] = ..., 
                visible: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RehydrationPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INVALID = "Invalid"
        STANDARD = "Standard"


    class azure.mgmt.dataprotection.models.RehydrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "COMPLETED"
        CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
        DELETED = "DELETED"
        DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
        FAILED = "FAILED"


    class azure.mgmt.dataprotection.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dataprotection.models.ResourceDeletionInfo(_Model):
        delete_activity_id: Optional[str]
        deletion_time: Optional[datetime]
        scheduled_purge_time: Optional[datetime]


    class azure.mgmt.dataprotection.models.ResourceGuard(_Model):
        allow_auto_approvals: Optional[bool]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_guard_operations: Optional[list[ResourceGuardOperation]]
        vault_critical_operation_exclusion_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                vault_critical_operation_exclusion_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResourceGuardOperation(_Model):
        request_resource_type: Optional[str]
        vault_critical_operation: Optional[str]


    class azure.mgmt.dataprotection.models.ResourceGuardOperationDetail(_Model):
        default_resource_request: Optional[str]
        vault_critical_operation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_resource_request: Optional[str] = ..., 
                vault_critical_operation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResourceGuardProxyBase(_Model):
        description: Optional[str]
        last_updated_time: Optional[str]
        resource_guard_operation_details: Optional[list[ResourceGuardOperationDetail]]
        resource_guard_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                last_updated_time: Optional[str] = ..., 
                resource_guard_operation_details: Optional[list[ResourceGuardOperationDetail]] = ..., 
                resource_guard_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResourceGuardProxyBaseResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ResourceGuardProxyBase]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResourceGuardProxyBase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResourceGuardResource(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[ResourceGuard]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: str, 
                properties: Optional[ResourceGuard] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResourceMoveDetails(_Model):
        completion_time_utc: Optional[str]
        operation_id: Optional[str]
        source_resource_path: Optional[str]
        start_time_utc: Optional[str]
        target_resource_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completion_time_utc: Optional[str] = ..., 
                operation_id: Optional[str] = ..., 
                source_resource_path: Optional[str] = ..., 
                start_time_utc: Optional[str] = ..., 
                target_resource_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResourceMoveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMIT_FAILED = "CommitFailed"
        COMMIT_TIMEDOUT = "CommitTimedout"
        CRITICAL_FAILURE = "CriticalFailure"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVE_SUCCEEDED = "MoveSucceeded"
        PARTIAL_SUCCESS = "PartialSuccess"
        PREPARE_FAILED = "PrepareFailed"
        PREPARE_TIMEDOUT = "PrepareTimedout"
        UNKNOWN = "Unknown"


    class azure.mgmt.dataprotection.models.ResourcePropertiesObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT_RESOURCE_PROPERTIES = "DefaultResourceProperties"


    class azure.mgmt.dataprotection.models.RestorableTimeRange(_Model):
        end_time: str
        object_type: Optional[str]
        start_time: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: str, 
                object_type: Optional[str] = ..., 
                start_time: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RestoreFilesTargetInfo(RestoreTargetInfoBase, discriminator='RestoreFilesTargetInfo'):
        object_type: Literal["RestoreFilesTargetInfo"]
        recovery_option: Union[str, RecoveryOption]
        restore_location: str
        target_details: TargetDetails

        @overload
        def __init__(
                self, 
                *, 
                recovery_option: Union[str, RecoveryOption], 
                restore_location: Optional[str] = ..., 
                target_details: TargetDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RestoreJobRecoveryPointDetails(_Model):
        recovery_point_id: Optional[str]
        recovery_point_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RestoreSourceDataStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVE_STORE = "ArchiveStore"
        OPERATIONAL_STORE = "OperationalStore"
        VAULT_STORE = "VaultStore"


    class azure.mgmt.dataprotection.models.RestoreTargetInfo(RestoreTargetInfoBase, discriminator='RestoreTargetInfo'):
        datasource_auth_credentials: Optional[AuthCredentials]
        datasource_info: Datasource
        datasource_set_info: Optional[DatasourceSet]
        object_type: Literal["RestoreTargetInfo"]
        recovery_option: Union[str, RecoveryOption]
        restore_location: str

        @overload
        def __init__(
                self, 
                *, 
                datasource_auth_credentials: Optional[AuthCredentials] = ..., 
                datasource_info: Datasource, 
                datasource_set_info: Optional[DatasourceSet] = ..., 
                recovery_option: Union[str, RecoveryOption], 
                restore_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RestoreTargetInfoBase(_Model):
        object_type: str
        recovery_option: Union[str, RecoveryOption]
        restore_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_type: str, 
                recovery_option: Union[str, RecoveryOption], 
                restore_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.RestoreTargetLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOBS = "AzureBlobs"
        AZURE_FILES = "AzureFiles"
        INVALID = "Invalid"


    class azure.mgmt.dataprotection.models.ResumeProtectionRequest(_Model):
        identity_details: Optional[IdentityDetails]
        object_type: Union[str, ResumeProtectionRequestObjectType]

        @overload
        def __init__(
                self, 
                *, 
                identity_details: Optional[IdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ResumeProtectionRequestObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESUME_PROTECTION_REQUEST = "ResumeProtectionRequest"


    class azure.mgmt.dataprotection.models.RetentionTag(_Model):
        e_tag: Optional[str]
        id: Optional[str]
        tag_name: str

        @overload
        def __init__(
                self, 
                *, 
                tag_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ScheduleBasedBackupCriteria(BackupCriteria, discriminator='ScheduleBasedBackupCriteria'):
        absolute_criteria: Optional[list[Union[str, AbsoluteMarker]]]
        days_of_month: Optional[list[Day]]
        days_of_the_week: Optional[list[Union[str, DayOfWeek]]]
        months_of_year: Optional[list[Union[str, Month]]]
        object_type: Literal["ScheduleBasedBackupCriteria"]
        schedule_times: Optional[list[datetime]]
        weeks_of_the_month: Optional[list[Union[str, WeekNumber]]]

        @overload
        def __init__(
                self, 
                *, 
                absolute_criteria: Optional[list[Union[str, AbsoluteMarker]]] = ..., 
                days_of_month: Optional[list[Day]] = ..., 
                days_of_the_week: Optional[list[Union[str, DayOfWeek]]] = ..., 
                months_of_year: Optional[list[Union[str, Month]]] = ..., 
                schedule_times: Optional[list[datetime]] = ..., 
                weeks_of_the_month: Optional[list[Union[str, WeekNumber]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ScheduleBasedTriggerContext(TriggerContext, discriminator='ScheduleBasedTriggerContext'):
        object_type: Literal["ScheduleBasedTriggerContext"]
        schedule: BackupSchedule
        tagging_criteria: list[TaggingCriteria]

        @overload
        def __init__(
                self, 
                *, 
                schedule: BackupSchedule, 
                tagging_criteria: list[TaggingCriteria]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SecretStoreBasedAuthCredentials(AuthCredentials, discriminator='SecretStoreBasedAuthCredentials'):
        object_type: Literal["SecretStoreBasedAuthCredentials"]
        secret_store_resource: Optional[SecretStoreResource]

        @overload
        def __init__(
                self, 
                *, 
                secret_store_resource: Optional[SecretStoreResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SecretStoreResource(_Model):
        secret_store_type: Union[str, SecretStoreType]
        uri: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                secret_store_type: Union[str, SecretStoreType], 
                uri: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SecretStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        INVALID = "Invalid"


    class azure.mgmt.dataprotection.models.SecureScoreLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADEQUATE = "Adequate"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        NOT_SUPPORTED = "NotSupported"


    class azure.mgmt.dataprotection.models.SecuritySettings(_Model):
        encryption_settings: Optional[EncryptionSettings]
        immutability_settings: Optional[ImmutabilitySettings]
        soft_delete_settings: Optional[SoftDeleteSettings]

        @overload
        def __init__(
                self, 
                *, 
                encryption_settings: Optional[EncryptionSettings] = ..., 
                immutability_settings: Optional[ImmutabilitySettings] = ..., 
                soft_delete_settings: Optional[SoftDeleteSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SoftDeleteSettings(_Model):
        retention_duration_in_days: Optional[float]
        state: Optional[Union[str, SoftDeleteState]]

        @overload
        def __init__(
                self, 
                *, 
                retention_duration_in_days: Optional[float] = ..., 
                state: Optional[Union[str, SoftDeleteState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SoftDeleteState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS_ON = "AlwaysOn"
        OFF = "Off"
        ON = "On"


    class azure.mgmt.dataprotection.models.SourceDataStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVE_STORE = "ArchiveStore"
        OPERATIONAL_STORE = "OperationalStore"
        SNAPSHOT_STORE = "SnapshotStore"
        VAULT_STORE = "VaultStore"


    class azure.mgmt.dataprotection.models.SourceLifeCycle(_Model):
        delete_after: DeleteOption
        source_data_store: DataStoreInfoBase
        target_data_store_copy_settings: Optional[list[TargetCopySetting]]

        @overload
        def __init__(
                self, 
                *, 
                delete_after: DeleteOption, 
                source_data_store: DataStoreInfoBase, 
                target_data_store_copy_settings: Optional[list[TargetCopySetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURING_PROTECTION = "ConfiguringProtection"
        CONFIGURING_PROTECTION_FAILED = "ConfiguringProtectionFailed"
        PROTECTION_CONFIGURED = "ProtectionConfigured"
        PROTECTION_STOPPED = "ProtectionStopped"
        SOFT_DELETED = "SoftDeleted"
        SOFT_DELETING = "SoftDeleting"


    class azure.mgmt.dataprotection.models.StopProtectionRequest(_Model):
        resource_guard_operation_requests: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                resource_guard_operation_requests: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.StorageSetting(_Model):
        datastore_type: Optional[Union[str, StorageSettingStoreTypes]]
        type: Optional[Union[str, StorageSettingTypes]]

        @overload
        def __init__(
                self, 
                *, 
                datastore_type: Optional[Union[str, StorageSettingStoreTypes]] = ..., 
                type: Optional[Union[str, StorageSettingTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.StorageSettingStoreTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVE_STORE = "ArchiveStore"
        OPERATIONAL_STORE = "OperationalStore"
        VAULT_STORE = "VaultStore"


    class azure.mgmt.dataprotection.models.StorageSettingTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_REDUNDANT = "GeoRedundant"
        LOCALLY_REDUNDANT = "LocallyRedundant"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.dataprotection.models.SupportedFeature(_Model):
        exposure_controlled_features: Optional[list[str]]
        feature_name: Optional[str]
        support_status: Optional[Union[str, FeatureSupportStatus]]

        @overload
        def __init__(
                self, 
                *, 
                exposure_controlled_features: Optional[list[str]] = ..., 
                feature_name: Optional[str] = ..., 
                support_status: Optional[Union[str, FeatureSupportStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SuspendBackupRequest(_Model):
        resource_guard_operation_requests: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                resource_guard_operation_requests: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SyncBackupInstanceRequest(_Model):
        sync_type: Optional[Union[str, SyncType]]

        @overload
        def __init__(
                self, 
                *, 
                sync_type: Optional[Union[str, SyncType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.SyncType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        FORCE_RESYNC = "ForceResync"


    class azure.mgmt.dataprotection.models.SystemData(_Model):
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


    class azure.mgmt.dataprotection.models.TaggingCriteria(_Model):
        criteria: Optional[list[BackupCriteria]]
        is_default: bool
        tag_info: RetentionTag
        tagging_priority: int

        @overload
        def __init__(
                self, 
                *, 
                criteria: Optional[list[BackupCriteria]] = ..., 
                is_default: bool, 
                tag_info: RetentionTag, 
                tagging_priority: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.TargetCopySetting(_Model):
        copy_after: CopyOption
        data_store: DataStoreInfoBase

        @overload
        def __init__(
                self, 
                *, 
                copy_after: CopyOption, 
                data_store: DataStoreInfoBase
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.TargetDetails(_Model):
        file_prefix: str
        restore_target_location_type: Union[str, RestoreTargetLocationType]
        target_resource_arm_id: Optional[str]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                file_prefix: str, 
                restore_target_location_type: Union[str, RestoreTargetLocationType], 
                target_resource_arm_id: Optional[str] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.TrackedResource(Resource):
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


    class azure.mgmt.dataprotection.models.TriggerBackupRequest(_Model):
        backup_rule_options: AdHocBackupRuleOptions

        @overload
        def __init__(
                self, 
                *, 
                backup_rule_options: AdHocBackupRuleOptions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.TriggerContext(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.UnlockDeleteRequest(_Model):
        resource_guard_operation_requests: Optional[list[str]]
        resource_to_be_deleted: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                resource_to_be_deleted: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.UnlockDeleteResponse(_Model):
        unlock_delete_expiry_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                unlock_delete_expiry_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.dataprotection.models.UserFacingError(_Model):
        code: Optional[str]
        details: Optional[list[UserFacingError]]
        inner_error: Optional[InnerError]
        is_retryable: Optional[bool]
        is_user_error: Optional[bool]
        message: Optional[str]
        properties: Optional[dict[str, str]]
        recommended_action: Optional[list[str]]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[UserFacingError]] = ..., 
                inner_error: Optional[InnerError] = ..., 
                is_retryable: Optional[bool] = ..., 
                is_user_error: Optional[bool] = ..., 
                message: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                recommended_action: Optional[list[str]] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.UserFacingWarningDetail(_Model):
        resource_name: Optional[str]
        warning: UserFacingError

        @overload
        def __init__(
                self, 
                *, 
                resource_name: Optional[str] = ..., 
                warning: UserFacingError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ValidateCrossRegionRestoreRequestObject(_Model):
        cross_region_restore_details: CrossRegionRestoreDetails
        restore_request_object: AzureBackupRestoreRequest

        @overload
        def __init__(
                self, 
                *, 
                cross_region_restore_details: CrossRegionRestoreDetails, 
                restore_request_object: AzureBackupRestoreRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ValidateForBackupRequest(_Model):
        backup_instance: BackupInstance

        @overload
        def __init__(
                self, 
                *, 
                backup_instance: BackupInstance
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ValidateForModifyBackupRequest(_Model):
        backup_instance: BackupInstance

        @overload
        def __init__(
                self, 
                *, 
                backup_instance: BackupInstance
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ValidateRestoreRequestObject(_Model):
        restore_request_object: AzureBackupRestoreRequest

        @overload
        def __init__(
                self, 
                *, 
                restore_request_object: AzureBackupRestoreRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dataprotection.models.ValidationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEEP_VALIDATION = "DeepValidation"
        SHALLOW_VALIDATION = "ShallowValidation"


    class azure.mgmt.dataprotection.models.WeekNumber(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST = "First"
        FOURTH = "Fourth"
        LAST = "Last"
        SECOND = "Second"
        THIRD = "Third"


namespace azure.mgmt.dataprotection.operations

    class azure.mgmt.dataprotection.operations.BackupInstancesExtensionRoutingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupInstanceResource]: ...


    class azure.mgmt.dataprotection.operations.BackupInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_adhoc_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: TriggerBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_adhoc_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: TriggerBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_adhoc_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: BackupInstanceResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupInstanceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: BackupInstanceResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupInstanceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupInstanceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                *, 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resume_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[ResumeProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[ResumeProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[StopProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[StopProtectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_suspend_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[SuspendBackupRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_suspend_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[SuspendBackupRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_suspend_backups(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_sync_backup_instance(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: SyncBackupInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_sync_backup_instance(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: SyncBackupInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_sync_backup_instance(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_trigger_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_trigger_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_trigger_rehydrate(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRehydrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rehydrate(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRehydrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rehydrate(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_trigger_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupRestoreRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_trigger_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: ValidateCrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: ValidateCrossRegionRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_cross_region_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_for_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: ValidateForBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_for_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: ValidateForBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_for_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_for_modify_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateForModifyBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_for_modify_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateForModifyBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_for_modify_backup(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_for_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_for_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: ValidateRestoreRequestObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @overload
        def begin_validate_for_restore(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationJobExtendedInfo]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> BackupInstanceResource: ...

        @distributed_trace
        def get_backup_instance_operation_result(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[BackupInstanceResource]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupInstanceResource]: ...


    class azure.mgmt.dataprotection.operations.BackupPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                parameters: BaseBackupPolicyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                parameters: BaseBackupPolicyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> BaseBackupPolicyResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BaseBackupPolicyResource]: ...


    class azure.mgmt.dataprotection.operations.BackupVaultOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[BackupVaultResource]: ...


    class azure.mgmt.dataprotection.operations.BackupVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: BackupVaultResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                x_ms_deleted_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupVaultResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: BackupVaultResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                x_ms_deleted_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupVaultResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                x_ms_deleted_vault_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupVaultResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: PatchResourceRequestInput, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupVaultResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: PatchResourceRequestInput, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupVaultResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[BackupVaultResource]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> BackupVaultResource: ...

        @distributed_trace
        def get_in_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupVaultResource]: ...

        @distributed_trace
        def get_in_subscription(self, **kwargs: Any) -> ItemPaged[BackupVaultResource]: ...


    class azure.mgmt.dataprotection.operations.DataProtectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_feature_support(
                self, 
                location: str, 
                parameters: FeatureValidationRequestBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FeatureValidationResponseBase: ...

        @overload
        def check_feature_support(
                self, 
                location: str, 
                parameters: FeatureValidationRequestBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FeatureValidationResponseBase: ...

        @overload
        def check_feature_support(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FeatureValidationResponseBase: ...


    class azure.mgmt.dataprotection.operations.DataProtectionOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.dataprotection.operations.DeletedBackupInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_undelete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                **kwargs: Any
            ) -> DeletedBackupInstanceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DeletedBackupInstanceResource]: ...


    class azure.mgmt.dataprotection.operations.DeletedBackupVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01', '2026-04-01-preview'])
        def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedBackupVaultResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01', '2026-04-01-preview'])
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[DeletedBackupVaultResource]: ...


    class azure.mgmt.dataprotection.operations.DppResourceGuardProxyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: ResourceGuardProxyBaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: ResourceGuardProxyBaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceGuardProxyBaseResource]: ...

        @overload
        def unlock_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: UnlockDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        def unlock_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: UnlockDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        def unlock_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...


    class azure.mgmt.dataprotection.operations.ExportJobsOperationResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ExportJobsResult]: ...


    class azure.mgmt.dataprotection.operations.ExportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_trigger(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.dataprotection.operations.FetchCrossRegionRestoreJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...

        @overload
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...

        @overload
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...


    class azure.mgmt.dataprotection.operations.FetchCrossRegionRestoreJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupJobResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: CrossRegionRestoreJobsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupJobResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupJobResource]: ...


    class azure.mgmt.dataprotection.operations.FetchSecondaryRecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: FetchSecondaryRPsRequestParameters, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupRecoveryPointResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: FetchSecondaryRPsRequestParameters, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupRecoveryPointResource]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupRecoveryPointResource]: ...


    class azure.mgmt.dataprotection.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> AzureBackupJobResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupJobResource]: ...


    class azure.mgmt.dataprotection.operations.OperationResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                operation_id: str, 
                location: str, 
                **kwargs: Any
            ) -> Optional[OperationJobExtendedInfo]: ...


    class azure.mgmt.dataprotection.operations.OperationStatusBackupVaultContextOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...


    class azure.mgmt.dataprotection.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...


    class azure.mgmt.dataprotection.operations.OperationStatusResourceGroupContextOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...


    class azure.mgmt.dataprotection.operations.RecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                recovery_point_id: str, 
                **kwargs: Any
            ) -> AzureBackupRecoveryPointResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AzureBackupRecoveryPointResource]: ...


    class azure.mgmt.dataprotection.operations.ResourceGuardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @distributed_trace
        def get_backup_security_pin_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_default_backup_security_pin_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_default_delete_protected_item_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_default_delete_resource_guard_proxy_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_default_disable_soft_delete_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_default_update_protected_item_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_default_update_protection_policy_requests_object(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                request_name: str, 
                **kwargs: Any
            ) -> DppBaseResource: ...

        @distributed_trace
        def get_delete_protected_item_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_delete_resource_guard_proxy_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_disable_soft_delete_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_resources_in_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceGuardResource]: ...

        @distributed_trace
        def get_resources_in_subscription(self, **kwargs: Any) -> ItemPaged[ResourceGuardResource]: ...

        @distributed_trace
        def get_update_protected_item_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DppBaseResource]: ...

        @distributed_trace
        def get_update_protection_policy_requests_objects(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DppBaseResource]: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: PatchResourceGuardInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: PatchResourceGuardInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: ResourceGuardResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: ResourceGuardResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                resource_guards_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardResource: ...


    class azure.mgmt.dataprotection.operations.RestorableTimeRangesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def find(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupFindRestorableTimeRangesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupFindRestorableTimeRangesResponseResource: ...

        @overload
        def find(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: AzureBackupFindRestorableTimeRangesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupFindRestorableTimeRangesResponseResource: ...

        @overload
        def find(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBackupFindRestorableTimeRangesResponseResource: ...


namespace azure.mgmt.dataprotection.types

    class azure.mgmt.dataprotection.types.AbsoluteDeleteOption(TypedDict, total=False):
        key "duration": Required[str]
        key "objectType": Required[Literal["AbsoluteDeleteOption"]]
        duration: str
        objectType: Literal[AbsoluteDeleteOption]


    class azure.mgmt.dataprotection.types.AdHocBackupRuleOptions(TypedDict, total=False):
        key "ruleName": Required[str]
        key "triggerOption": Required[AdhocBackupTriggerOption]
        ruleName: str
        triggerOption: AdhocBackupTriggerOption


    class azure.mgmt.dataprotection.types.AdhocBackupTriggerOption(TypedDict, total=False):
        key "retentionTagOverride": str
        retentionTagOverride: str


    class azure.mgmt.dataprotection.types.AdhocBasedTaggingCriteria(TypedDict, total=False):
        key "tagInfo": ForwardRef('RetentionTag', module='types')
        tagInfo: RetentionTag


    class azure.mgmt.dataprotection.types.AdhocBasedTriggerContext(TypedDict, total=False):
        key "objectType": Required[Literal["AdhocBasedTriggerContext"]]
        key "taggingCriteria": Required[AdhocBasedTaggingCriteria]
        objectType: Literal[AdhocBasedTriggerContext]
        taggingCriteria: AdhocBasedTaggingCriteria


    class azure.mgmt.dataprotection.types.AdlsBlobBackupDatasourceParameters(TypedDict, total=False):
        key "containersList": Required[list[str]]
        key "objectType": Required[Literal["AdlsBlobBackupDatasourceParameters"]]
        containersList: list[str]
        objectType: Literal[AdlsBlobBackupDatasourceParameters]


    class azure.mgmt.dataprotection.types.AdlsBlobBackupDatasourceParametersForAutoProtection(TypedDict, total=False):
        key "autoProtectionSettings": Required[BlobBackupRuleBasedAutoProtectionSettings]
        key "objectType": Required[Literal["AdlsBlobBackupDatasourceParametersForAutoProtection"]]
        autoProtectionSettings: BlobBackupRuleBasedAutoProtectionSettings
        objectType: Literal[AdlsBlobBackupDatasourceParametersForAutoProtection]


    class azure.mgmt.dataprotection.types.AuthCredentials(TypedDict, total=False):
        key "objectType": Required[Literal["SecretStoreBasedAuthCredentials"]]
        key "secretStoreResource": ForwardRef('SecretStoreResource', module='types')
        objectType: Literal[SecretStoreBasedAuthCredentials]
        secretStoreResource: SecretStoreResource


    class azure.mgmt.dataprotection.types.AzureBackupFindRestorableTimeRangesRequest(TypedDict, total=False):
        key "endTime": str
        key "sourceDataStoreType": Required[Union[str, RestoreSourceDataStoreType]]
        key "startTime": str
        endTime: str
        sourceDataStoreType: Union[str, RestoreSourceDataStoreType]
        startTime: str


    class azure.mgmt.dataprotection.types.AzureBackupParams(TypedDict, total=False):
        key "backupType": Required[str]
        key "objectType": Required[Literal["AzureBackupParams"]]
        backupType: str
        objectType: Literal[AzureBackupParams]


    class azure.mgmt.dataprotection.types.AzureBackupRecoveryPointBasedRestoreRequest(TypedDict, total=False):
        key "identityDetails": ForwardRef('IdentityDetails', module='types')
        key "objectType": Required[Literal["AzureBackupRestoreWithRehydrationRequest"]]
        key "recoveryPointId": Required[str]
        key "rehydrationPriority": Required[Union[str, RehydrationPriority]]
        key "rehydrationRetentionDuration": Required[str]
        key "restoreTargetInfo": Required[RestoreTargetInfoBase]
        key "sourceDataStoreType": Required[Union[str, SourceDataStoreType]]
        key "sourceResourceId": str
        identityDetails: IdentityDetails
        objectType: Literal[AzureBackupRestoreWithRehydrationRequest]
        recoveryPointId: str
        rehydrationPriority: Union[str, RehydrationPriority]
        rehydrationRetentionDuration: str
        resourceGuardOperationRequests: list[str]
        restoreTargetInfo: RestoreTargetInfoBase
        sourceDataStoreType: Union[str, SourceDataStoreType]
        sourceResourceId: str


    class azure.mgmt.dataprotection.types.AzureBackupRecoveryTimeBasedRestoreRequest(TypedDict, total=False):
        key "identityDetails": ForwardRef('IdentityDetails', module='types')
        key "objectType": Required[Literal["AzureBackupRecoveryTimeBasedRestoreRequest"]]
        key "recoveryPointTime": Required[str]
        key "restoreTargetInfo": Required[RestoreTargetInfoBase]
        key "sourceDataStoreType": Required[Union[str, SourceDataStoreType]]
        key "sourceResourceId": str
        identityDetails: IdentityDetails
        objectType: Literal[AzureBackupRecoveryTimeBasedRestoreRequest]
        recoveryPointTime: str
        resourceGuardOperationRequests: list[str]
        restoreTargetInfo: RestoreTargetInfoBase
        sourceDataStoreType: Union[str, SourceDataStoreType]
        sourceResourceId: str


    class azure.mgmt.dataprotection.types.AzureBackupRehydrationRequest(TypedDict, total=False):
        key "recoveryPointId": Required[str]
        key "rehydrationPriority": Union[str, RehydrationPriority]
        key "rehydrationRetentionDuration": Required[str]
        recoveryPointId: str
        rehydrationPriority: Union[str, RehydrationPriority]
        rehydrationRetentionDuration: str


    class azure.mgmt.dataprotection.types.AzureBackupRestoreWithRehydrationRequest(TypedDict, total=False):
        key "identityDetails": ForwardRef('IdentityDetails', module='types')
        key "objectType": Required[Literal["AzureBackupRestoreWithRehydrationRequest"]]
        key "recoveryPointId": Required[str]
        key "rehydrationPriority": Required[Union[str, RehydrationPriority]]
        key "rehydrationRetentionDuration": Required[str]
        key "restoreTargetInfo": Required[RestoreTargetInfoBase]
        key "sourceDataStoreType": Required[Union[str, SourceDataStoreType]]
        key "sourceResourceId": str
        identityDetails: IdentityDetails
        objectType: Literal[AzureBackupRestoreWithRehydrationRequest]
        recoveryPointId: str
        rehydrationPriority: Union[str, RehydrationPriority]
        rehydrationRetentionDuration: str
        resourceGuardOperationRequests: list[str]
        restoreTargetInfo: RestoreTargetInfoBase
        sourceDataStoreType: Union[str, SourceDataStoreType]
        sourceResourceId: str


    class azure.mgmt.dataprotection.types.AzureBackupRule(TypedDict, total=False):
        key "backupParameters": ForwardRef('BackupParameters', module='types')
        key "dataStore": Required[DataStoreInfoBase]
        key "name": Required[str]
        key "objectType": Required[Literal["AzureBackupRule"]]
        key "trigger": Required[TriggerContext]
        backupParameters: BackupParameters
        dataStore: DataStoreInfoBase
        name: str
        objectType: Literal[AzureBackupRule]
        trigger: TriggerContext


    class azure.mgmt.dataprotection.types.AzureMonitorAlertSettings(TypedDict, total=False):
        key "alertsForAllJobFailures": Union[str, AlertsState]
        alertsForAllJobFailures: Union[str, AlertsState]


    class azure.mgmt.dataprotection.types.AzureOperationalStoreParameters(TypedDict, total=False):
        key "dataStoreType": Required[Union[str, DataStoreTypes]]
        key "objectType": Required[Literal["AzureOperationalStoreParameters"]]
        key "resourceGroupId": str
        dataStoreType: Union[str, DataStoreTypes]
        objectType: Literal[AzureOperationalStoreParameters]
        resourceGroupId: str


    class azure.mgmt.dataprotection.types.AzureRetentionRule(TypedDict, total=False):
        key "isDefault": bool
        key "lifecycles": Required[list[SourceLifeCycle]]
        key "name": Required[str]
        key "objectType": Required[Literal["AzureRetentionRule"]]
        isDefault: bool
        lifecycles: list[SourceLifeCycle]
        name: str
        objectType: Literal[AzureRetentionRule]


    class azure.mgmt.dataprotection.types.BackupCriteria(TypedDict, total=False):
        key "objectType": Required[Literal["ScheduleBasedBackupCriteria"]]
        absoluteCriteria: list[Union[str, AbsoluteMarker]]
        daysOfMonth: list[Day]
        daysOfTheWeek: list[Union[str, DayOfWeek]]
        monthsOfYear: list[Union[str, Month]]
        objectType: Literal[ScheduleBasedBackupCriteria]
        scheduleTimes: list[str]
        weeksOfTheMonth: list[Union[str, WeekNumber]]


    class azure.mgmt.dataprotection.types.BackupInstance(TypedDict, total=False):
        key "currentProtectionState": Union[str, CurrentProtectionState]
        key "dataSourceInfo": Required[Datasource]
        key "dataSourceSetInfo": ForwardRef('DatasourceSet', module='types')
        key "datasourceAuthCredentials": ForwardRef('AuthCredentials', module='types')
        key "friendlyName": str
        key "identityDetails": ForwardRef('IdentityDetails', module='types')
        key "objectType": Required[str]
        key "policyInfo": Required[PolicyInfo]
        key "protectionErrorDetails": ForwardRef('UserFacingError', module='types')
        key "protectionStatus": ForwardRef('ProtectionStatusDetails', module='types')
        key "provisioningState": str
        key "validationType": Union[str, ValidationType]
        currentProtectionState: Union[str, CurrentProtectionState]
        dataSourceInfo: Datasource
        dataSourceSetInfo: DatasourceSet
        datasourceAuthCredentials: AuthCredentials
        friendlyName: str
        identityDetails: IdentityDetails
        objectType: str
        policyInfo: PolicyInfo
        protectionErrorDetails: UserFacingError
        protectionStatus: ProtectionStatusDetails
        provisioningState: str
        resourceGuardOperationRequests: list[str]
        validationType: Union[str, ValidationType]


    class azure.mgmt.dataprotection.types.BackupInstanceResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('BackupInstance', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: BackupInstance
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dataprotection.types.BackupParameters(TypedDict, total=False):
        key "backupType": Required[str]
        key "objectType": Required[Literal["AzureBackupParams"]]
        backupType: str
        objectType: Literal[AzureBackupParams]


    class azure.mgmt.dataprotection.types.BackupPolicy(TypedDict, total=False):
        key "datasourceTypes": Required[list[str]]
        key "objectType": Required[Literal["BackupPolicy"]]
        key "policyRules": Required[list[BasePolicyRule]]
        datasourceTypes: list[str]
        objectType: Literal[BackupPolicy]
        policyRules: list[BasePolicyRule]


    class azure.mgmt.dataprotection.types.BackupSchedule(TypedDict, total=False):
        key "repeatingTimeIntervals": Required[list[str]]
        key "timeZone": str
        repeatingTimeIntervals: list[str]
        timeZone: str


    class azure.mgmt.dataprotection.types.BackupVault(TypedDict, total=False):
        key "bcdrSecurityLevel": Union[str, BCDRSecurityLevel]
        key "featureSettings": ForwardRef('FeatureSettings', module='types')
        key "isVaultProtectedByResourceGuard": bool
        key "monitoringSettings": ForwardRef('MonitoringSettings', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceMoveDetails": ForwardRef('ResourceMoveDetails', module='types')
        key "resourceMoveState": Union[str, ResourceMoveState]
        key "secureScore": Union[str, SecureScoreLevel]
        key "securitySettings": ForwardRef('SecuritySettings', module='types')
        bcdrSecurityLevel: Union[str, BCDRSecurityLevel]
        featureSettings: FeatureSettings
        isVaultProtectedByResourceGuard: bool
        monitoringSettings: MonitoringSettings
        provisioningState: Union[str, ProvisioningState]
        replicatedRegions: list[str]
        resourceGuardOperationRequests: list[str]
        resourceMoveDetails: ResourceMoveDetails
        resourceMoveState: Union[str, ResourceMoveState]
        secureScore: Union[str, SecureScoreLevel]
        securitySettings: SecuritySettings
        storageSettings: list[StorageSetting]


    class azure.mgmt.dataprotection.types.BackupVaultResource(TrackedResource):
        key "eTag": str
        key "id": str
        key "identity": ForwardRef('DppIdentityDetails', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[BackupVault]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        identity: DppIdentityDetails
        location: str
        name: str
        properties: BackupVault
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dataprotection.types.BaseBackupPolicy(TypedDict, total=False):
        key "datasourceTypes": Required[list[str]]
        key "objectType": Required[Literal["BackupPolicy"]]
        key "policyRules": Required[list[BasePolicyRule]]
        datasourceTypes: list[str]
        objectType: Literal[BackupPolicy]
        policyRules: list[BasePolicyRule]


    class azure.mgmt.dataprotection.types.BaseBackupPolicyResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('BaseBackupPolicy', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: BaseBackupPolicy
        systemData: SystemData
        type: str


    class azure.mgmt.dataprotection.types.BaseResourceProperties(TypedDict, total=False):
        key "objectType": Required[Literal[ResourcePropertiesObjectType.DEFAULT_RESOURCE_PROPERTIES]]
        objectType: Literal[ResourcePropertiesObjectType.DEFAULT_RESOURCE_PROPERTIES]


    class azure.mgmt.dataprotection.types.BlobBackupAutoProtectionRule(TypedDict, total=False):
        key "mode": Required[Union[str, BlobBackupRuleMode]]
        key "objectType": Required[str]
        key "pattern": Required[str]
        key "type": Required[Union[str, BlobBackupPatternType]]
        mode: Union[str, BlobBackupRuleMode]
        objectType: str
        pattern: str
        type: Union[str, BlobBackupPatternType]


    class azure.mgmt.dataprotection.types.BlobBackupAutoProtectionSettings(TypedDict, total=False):
        key "enabled": Required[bool]
        key "objectType": Required[Literal["BlobBackupRuleBasedAutoProtectionSettings"]]
        enabled: bool
        objectType: Literal[BlobBackupRuleBasedAutoProtectionSettings]
        rules: list[BlobBackupAutoProtectionRule]


    class azure.mgmt.dataprotection.types.BlobBackupDatasourceParameters(TypedDict, total=False):
        key "containersList": Required[list[str]]
        key "objectType": Required[Literal["AdlsBlobBackupDatasourceParameters"]]
        containersList: list[str]
        objectType: Literal[AdlsBlobBackupDatasourceParameters]


    class azure.mgmt.dataprotection.types.BlobBackupDatasourceParametersForAutoProtection(TypedDict, total=False):
        key "autoProtectionSettings": Required[BlobBackupRuleBasedAutoProtectionSettings]
        key "objectType": Required[Literal["BlobBackupDatasourceParametersForAutoProtection"]]
        autoProtectionSettings: BlobBackupRuleBasedAutoProtectionSettings
        objectType: Literal[BlobBackupDatasourceParametersForAutoProtection]


    class azure.mgmt.dataprotection.types.BlobBackupRuleBasedAutoProtectionSettings(TypedDict, total=False):
        key "enabled": Required[bool]
        key "objectType": Required[Literal["BlobBackupRuleBasedAutoProtectionSettings"]]
        enabled: bool
        objectType: Literal[BlobBackupRuleBasedAutoProtectionSettings]
        rules: list[BlobBackupAutoProtectionRule]


    class azure.mgmt.dataprotection.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.dataprotection.types.CmkKekIdentity(TypedDict, total=False):
        key "identityId": str
        key "identityType": Union[str, IdentityType]
        identityId: str
        identityType: Union[str, IdentityType]


    class azure.mgmt.dataprotection.types.CmkKeyVaultProperties(TypedDict, total=False):
        key "keyUri": str
        keyUri: str


    class azure.mgmt.dataprotection.types.CopyOnExpiryOption(TypedDict, total=False):
        key "objectType": Required[Literal["CopyOnExpiryOption"]]
        objectType: Literal[CopyOnExpiryOption]


    class azure.mgmt.dataprotection.types.CrossRegionRestoreDetails(TypedDict, total=False):
        key "sourceBackupInstanceId": Required[str]
        key "sourceRegion": Required[str]
        sourceBackupInstanceId: str
        sourceRegion: str


    class azure.mgmt.dataprotection.types.CrossRegionRestoreJobRequest(TypedDict, total=False):
        key "jobId": Required[str]
        key "sourceBackupVaultId": Required[str]
        key "sourceRegion": Required[str]
        jobId: str
        sourceBackupVaultId: str
        sourceRegion: str


    class azure.mgmt.dataprotection.types.CrossRegionRestoreJobsRequest(TypedDict, total=False):
        key "sourceBackupVaultId": Required[str]
        key "sourceRegion": Required[str]
        sourceBackupVaultId: str
        sourceRegion: str


    class azure.mgmt.dataprotection.types.CrossRegionRestoreRequestObject(TypedDict, total=False):
        key "crossRegionRestoreDetails": Required[CrossRegionRestoreDetails]
        key "restoreRequestObject": Required[AzureBackupRestoreRequest]
        crossRegionRestoreDetails: CrossRegionRestoreDetails
        restoreRequestObject: AzureBackupRestoreRequest


    class azure.mgmt.dataprotection.types.CrossRegionRestoreSettings(TypedDict, total=False):
        key "state": Union[str, CrossRegionRestoreState]
        state: Union[str, CrossRegionRestoreState]


    class azure.mgmt.dataprotection.types.CrossSubscriptionRestoreSettings(TypedDict, total=False):
        key "state": Union[str, CrossSubscriptionRestoreState]
        state: Union[str, CrossSubscriptionRestoreState]


    class azure.mgmt.dataprotection.types.CustomCopyOption(TypedDict, total=False):
        key "duration": str
        key "objectType": Required[Literal["CustomCopyOption"]]
        duration: str
        objectType: Literal[CustomCopyOption]


    class azure.mgmt.dataprotection.types.DataStoreInfoBase(TypedDict, total=False):
        key "dataStoreType": Required[Union[str, DataStoreTypes]]
        key "objectType": Required[str]
        dataStoreType: Union[str, DataStoreTypes]
        objectType: str


    class azure.mgmt.dataprotection.types.DataStoreParameters(TypedDict, total=False):
        key "dataStoreType": Required[Union[str, DataStoreTypes]]
        key "objectType": Required[Literal["AzureOperationalStoreParameters"]]
        key "resourceGroupId": str
        dataStoreType: Union[str, DataStoreTypes]
        objectType: Literal[AzureOperationalStoreParameters]
        resourceGroupId: str


    class azure.mgmt.dataprotection.types.Datasource(TypedDict, total=False):
        key "datasourceType": str
        key "objectType": str
        key "resourceID": Required[str]
        key "resourceLocation": str
        key "resourceName": str
        key "resourceProperties": ForwardRef('BaseResourceProperties', module='types')
        key "resourceType": str
        key "resourceUri": str
        datasourceType: str
        objectType: str
        resourceID: str
        resourceLocation: str
        resourceName: str
        resourceProperties: BaseResourceProperties
        resourceType: str
        resourceUri: str


    class azure.mgmt.dataprotection.types.DatasourceSet(TypedDict, total=False):
        key "datasourceType": str
        key "objectType": str
        key "resourceID": Required[str]
        key "resourceLocation": str
        key "resourceName": str
        key "resourceProperties": ForwardRef('BaseResourceProperties', module='types')
        key "resourceType": str
        key "resourceUri": str
        datasourceType: str
        objectType: str
        resourceID: str
        resourceLocation: str
        resourceName: str
        resourceProperties: BaseResourceProperties
        resourceType: str
        resourceUri: str


    class azure.mgmt.dataprotection.types.Day(TypedDict, total=False):
        key "date": int
        key "isLast": bool
        date: int
        isLast: bool


    class azure.mgmt.dataprotection.types.DefaultResourceProperties(TypedDict, total=False):
        key "objectType": Required[Literal[ResourcePropertiesObjectType.DEFAULT_RESOURCE_PROPERTIES]]
        objectType: Literal[ResourcePropertiesObjectType.DEFAULT_RESOURCE_PROPERTIES]


    class azure.mgmt.dataprotection.types.DeleteOption(TypedDict, total=False):
        key "duration": Required[str]
        key "objectType": Required[Literal["AbsoluteDeleteOption"]]
        duration: str
        objectType: Literal[AbsoluteDeleteOption]


    class azure.mgmt.dataprotection.types.DppIdentityDetails(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": str
        principalId: str
        tenantId: str
        type: str
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.dataprotection.types.EncryptionSettings(TypedDict, total=False):
        key "infrastructureEncryption": Union[str, InfrastructureEncryptionState]
        key "kekIdentity": ForwardRef('CmkKekIdentity', module='types')
        key "keyVaultProperties": ForwardRef('CmkKeyVaultProperties', module='types')
        key "state": Union[str, EncryptionState]
        infrastructureEncryption: Union[str, InfrastructureEncryptionState]
        kekIdentity: CmkKekIdentity
        keyVaultProperties: CmkKeyVaultProperties
        state: Union[str, EncryptionState]


    class azure.mgmt.dataprotection.types.FeatureSettings(TypedDict, total=False):
        key "crossRegionRestoreSettings": ForwardRef('CrossRegionRestoreSettings', module='types')
        key "crossSubscriptionRestoreSettings": ForwardRef('CrossSubscriptionRestoreSettings', module='types')
        crossRegionRestoreSettings: CrossRegionRestoreSettings
        crossSubscriptionRestoreSettings: CrossSubscriptionRestoreSettings


    class azure.mgmt.dataprotection.types.FeatureValidationRequest(TypedDict, total=False):
        key "featureName": str
        key "featureType": Union[str, FeatureType]
        key "objectType": Required[Literal["FeatureValidationRequest"]]
        featureName: str
        featureType: Union[str, FeatureType]
        objectType: Literal[FeatureValidationRequest]


    class azure.mgmt.dataprotection.types.FeatureValidationRequestBase(TypedDict, total=False):
        key "featureName": str
        key "featureType": Union[str, FeatureType]
        key "objectType": Required[Literal["FeatureValidationRequest"]]
        featureName: str
        featureType: Union[str, FeatureType]
        objectType: Literal[FeatureValidationRequest]


    class azure.mgmt.dataprotection.types.FetchSecondaryRPsRequestParameters(TypedDict, total=False):
        key "sourceBackupInstanceId": str
        key "sourceRegion": str
        sourceBackupInstanceId: str
        sourceRegion: str


    class azure.mgmt.dataprotection.types.IdentityDetails(TypedDict, total=False):
        key "useSystemAssignedIdentity": bool
        key "userAssignedIdentityArmUrl": str
        useSystemAssignedIdentity: bool
        userAssignedIdentityArmUrl: str


    class azure.mgmt.dataprotection.types.ImmediateCopyOption(TypedDict, total=False):
        key "objectType": Required[Literal["ImmediateCopyOption"]]
        objectType: Literal[ImmediateCopyOption]


    class azure.mgmt.dataprotection.types.ImmutabilitySettings(TypedDict, total=False):
        key "state": Union[str, ImmutabilityState]
        state: Union[str, ImmutabilityState]


    class azure.mgmt.dataprotection.types.InnerError(TypedDict, total=False):
        key "code": str
        key "embeddedInnerError": ForwardRef('InnerError', module='types')
        additionalInfo: dict[str, str]
        code: str
        embeddedInnerError: InnerError


    class azure.mgmt.dataprotection.types.ItemLevelRestoreTargetInfo(TypedDict, total=False):
        key "datasourceAuthCredentials": ForwardRef('AuthCredentials', module='types')
        key "datasourceInfo": Required[Datasource]
        key "datasourceSetInfo": ForwardRef('DatasourceSet', module='types')
        key "objectType": Required[Literal["ItemLevelRestoreTargetInfo"]]
        key "recoveryOption": Required[Union[str, RecoveryOption]]
        key "restoreCriteria": Required[list[ItemLevelRestoreCriteria]]
        key "restoreLocation": str
        datasourceAuthCredentials: AuthCredentials
        datasourceInfo: Datasource
        datasourceSetInfo: DatasourceSet
        objectType: Literal[ItemLevelRestoreTargetInfo]
        recoveryOption: Union[str, RecoveryOption]
        restoreCriteria: list[ItemLevelRestoreCriteria]
        restoreLocation: str


    class azure.mgmt.dataprotection.types.ItemPathBasedRestoreCriteria(TypedDict, total=False):
        key "isPathRelativeToBackupItem": Required[bool]
        key "itemPath": Required[str]
        key "objectType": Required[Literal["ItemPathBasedRestoreCriteria"]]
        key "renameTo": str
        isPathRelativeToBackupItem: bool
        itemPath: str
        objectType: Literal[ItemPathBasedRestoreCriteria]
        renameTo: str
        subItemPathPrefix: list[str]


    class azure.mgmt.dataprotection.types.KubernetesClusterBackupDatasourceParameters(TypedDict, total=False):
        key "includeClusterScopeResources": Required[bool]
        key "objectType": Required[Literal["KubernetesClusterBackupDatasourceParameters"]]
        key "snapshotVolumes": Required[bool]
        backupHookReferences: list[NamespacedNameResource]
        excludedNamespaces: list[str]
        excludedResourceTypes: list[str]
        includeClusterScopeResources: bool
        includedNamespaces: list[str]
        includedResourceTypes: list[str]
        includedVolumeTypes: list[Union[str, AKSVolumeTypes]]
        labelSelectors: list[str]
        objectType: Literal[KubernetesClusterBackupDatasourceParameters]
        snapshotVolumes: bool


    class azure.mgmt.dataprotection.types.KubernetesClusterRestoreCriteria(TypedDict, total=False):
        key "conflictPolicy": Union[str, ExistingResourcePolicy]
        key "includeClusterScopeResources": Required[bool]
        key "objectType": Required[Literal["KubernetesClusterRestoreCriteria"]]
        key "persistentVolumeRestoreMode": Union[str, PersistentVolumeRestoreMode]
        key "resourceModifierReference": ForwardRef('NamespacedNameResource', module='types')
        conflictPolicy: Union[str, ExistingResourcePolicy]
        excludedNamespaces: list[str]
        excludedResourceTypes: list[str]
        includeClusterScopeResources: bool
        includedNamespaces: list[str]
        includedResourceTypes: list[str]
        labelSelectors: list[str]
        namespaceMappings: dict[str, str]
        objectType: Literal[KubernetesClusterRestoreCriteria]
        persistentVolumeRestoreMode: Union[str, PersistentVolumeRestoreMode]
        resourceModifierReference: NamespacedNameResource
        restoreHookReferences: list[NamespacedNameResource]


    class azure.mgmt.dataprotection.types.KubernetesClusterVaultTierRestoreCriteria(TypedDict, total=False):
        key "conflictPolicy": Union[str, ExistingResourcePolicy]
        key "includeClusterScopeResources": Required[bool]
        key "objectType": Required[Literal["KubernetesClusterVaultTierRestoreCriteria"]]
        key "persistentVolumeRestoreMode": Union[str, PersistentVolumeRestoreMode]
        key "resourceModifierReference": ForwardRef('NamespacedNameResource', module='types')
        key "stagingResourceGroupId": str
        key "stagingStorageAccountId": str
        conflictPolicy: Union[str, ExistingResourcePolicy]
        excludedNamespaces: list[str]
        excludedResourceTypes: list[str]
        includeClusterScopeResources: bool
        includedNamespaces: list[str]
        includedResourceTypes: list[str]
        labelSelectors: list[str]
        namespaceMappings: dict[str, str]
        objectType: Literal[KubernetesClusterVaultTierRestoreCriteria]
        persistentVolumeRestoreMode: Union[str, PersistentVolumeRestoreMode]
        resourceModifierReference: NamespacedNameResource
        restoreHookReferences: list[NamespacedNameResource]
        stagingResourceGroupId: str
        stagingStorageAccountId: str


    class azure.mgmt.dataprotection.types.KubernetesPVRestoreCriteria(TypedDict, total=False):
        key "name": str
        key "objectType": Required[Literal["KubernetesPVRestoreCriteria"]]
        key "storageClassName": str
        name: str
        objectType: Literal[KubernetesPVRestoreCriteria]
        storageClassName: str


    class azure.mgmt.dataprotection.types.KubernetesStorageClassRestoreCriteria(TypedDict, total=False):
        key "objectType": Required[Literal["KubernetesStorageClassRestoreCriteria"]]
        key "provisioner": str
        key "selectedStorageClassName": str
        objectType: Literal[KubernetesStorageClassRestoreCriteria]
        provisioner: str
        selectedStorageClassName: str


    class azure.mgmt.dataprotection.types.MonitoringSettings(TypedDict, total=False):
        key "azureMonitorAlertSettings": ForwardRef('AzureMonitorAlertSettings', module='types')
        azureMonitorAlertSettings: AzureMonitorAlertSettings


    class azure.mgmt.dataprotection.types.NamespacedNameResource(TypedDict, total=False):
        key "name": str
        key "namespace": str
        name: str
        namespace: str


    class azure.mgmt.dataprotection.types.PatchBackupVaultInput(TypedDict, total=False):
        key "featureSettings": ForwardRef('FeatureSettings', module='types')
        key "monitoringSettings": ForwardRef('MonitoringSettings', module='types')
        key "securitySettings": ForwardRef('SecuritySettings', module='types')
        featureSettings: FeatureSettings
        monitoringSettings: MonitoringSettings
        resourceGuardOperationRequests: list[str]
        securitySettings: SecuritySettings


    class azure.mgmt.dataprotection.types.PatchResourceGuardInput(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.dataprotection.types.PatchResourceRequestInput(TypedDict, total=False):
        key "identity": ForwardRef('DppIdentityDetails', module='types')
        key "properties": ForwardRef('PatchBackupVaultInput', module='types')
        identity: DppIdentityDetails
        properties: PatchBackupVaultInput
        tags: dict[str, str]


    class azure.mgmt.dataprotection.types.PolicyInfo(TypedDict, total=False):
        key "policyId": Required[str]
        key "policyParameters": ForwardRef('PolicyParameters', module='types')
        key "policyVersion": str
        policyId: str
        policyParameters: PolicyParameters
        policyVersion: str


    class azure.mgmt.dataprotection.types.PolicyParameters(TypedDict, total=False):
        backupDatasourceParametersList: list[BackupDatasourceParameters]
        dataStoreParametersList: list[DataStoreParameters]


    class azure.mgmt.dataprotection.types.PostgreSqlFlexibleServerBackupDatasourceParameters(TypedDict, total=False):
        key "backupSolutionType": Union[str, BackupSolutionType]
        key "objectType": Required[Literal["PostgreSqlFlexibleServerBackupDatasourceParameters"]]
        backupSolutionType: Union[str, BackupSolutionType]
        objectType: Literal[PostgreSqlFlexibleServerBackupDatasourceParameters]


    class azure.mgmt.dataprotection.types.ProtectionStatusDetails(TypedDict, total=False):
        key "errorDetails": ForwardRef('UserFacingError', module='types')
        key "status": Union[str, Status]
        errorDetails: UserFacingError
        status: Union[str, Status]


    class azure.mgmt.dataprotection.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.dataprotection.types.RangeBasedItemLevelRestoreCriteria(TypedDict, total=False):
        key "maxMatchingValue": str
        key "minMatchingValue": str
        key "objectType": Required[Literal["RangeBasedItemLevelRestoreCriteria"]]
        maxMatchingValue: str
        minMatchingValue: str
        objectType: Literal[RangeBasedItemLevelRestoreCriteria]


    class azure.mgmt.dataprotection.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.dataprotection.types.ResourceGuard(TypedDict, total=False):
        key "allowAutoApprovals": bool
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        allowAutoApprovals: bool
        description: str
        provisioningState: Union[str, ProvisioningState]
        resourceGuardOperations: list[ResourceGuardOperation]
        vaultCriticalOperationExclusionList: list[str]


    class azure.mgmt.dataprotection.types.ResourceGuardOperation(TypedDict, total=False):
        key "requestResourceType": str
        key "vaultCriticalOperation": str
        requestResourceType: str
        vaultCriticalOperation: str


    class azure.mgmt.dataprotection.types.ResourceGuardOperationDetail(TypedDict, total=False):
        key "defaultResourceRequest": str
        key "vaultCriticalOperation": str
        defaultResourceRequest: str
        vaultCriticalOperation: str


    class azure.mgmt.dataprotection.types.ResourceGuardProxyBase(TypedDict, total=False):
        key "description": str
        key "lastUpdatedTime": str
        key "resourceGuardResourceId": str
        description: str
        lastUpdatedTime: str
        resourceGuardOperationDetails: list[ResourceGuardOperationDetail]
        resourceGuardResourceId: str


    class azure.mgmt.dataprotection.types.ResourceGuardProxyBaseResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ResourceGuardProxyBase', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ResourceGuardProxyBase
        systemData: SystemData
        type: str


    class azure.mgmt.dataprotection.types.ResourceGuardResource(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ResourceGuard', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        location: str
        name: str
        properties: ResourceGuard
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dataprotection.types.ResourceMoveDetails(TypedDict, total=False):
        key "completionTimeUtc": str
        key "operationId": str
        key "sourceResourcePath": str
        key "startTimeUtc": str
        key "targetResourcePath": str
        completionTimeUtc: str
        operationId: str
        sourceResourcePath: str
        startTimeUtc: str
        targetResourcePath: str


    class azure.mgmt.dataprotection.types.ResourcePropertiesObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT_RESOURCE_PROPERTIES = "DefaultResourceProperties"


    class azure.mgmt.dataprotection.types.RestoreFilesTargetInfo(TypedDict, total=False):
        key "objectType": Required[Literal["RestoreFilesTargetInfo"]]
        key "recoveryOption": Required[Union[str, RecoveryOption]]
        key "restoreLocation": str
        key "targetDetails": Required[TargetDetails]
        objectType: Literal[RestoreFilesTargetInfo]
        recoveryOption: Union[str, RecoveryOption]
        restoreLocation: str
        targetDetails: TargetDetails


    class azure.mgmt.dataprotection.types.RestoreTargetInfo(TypedDict, total=False):
        key "datasourceAuthCredentials": ForwardRef('AuthCredentials', module='types')
        key "datasourceInfo": Required[Datasource]
        key "datasourceSetInfo": ForwardRef('DatasourceSet', module='types')
        key "objectType": Required[Literal["RestoreTargetInfo"]]
        key "recoveryOption": Required[Union[str, RecoveryOption]]
        key "restoreLocation": str
        datasourceAuthCredentials: AuthCredentials
        datasourceInfo: Datasource
        datasourceSetInfo: DatasourceSet
        objectType: Literal[RestoreTargetInfo]
        recoveryOption: Union[str, RecoveryOption]
        restoreLocation: str


    class azure.mgmt.dataprotection.types.ResumeProtectionRequest(TypedDict, total=False):
        key "identityDetails": ForwardRef('IdentityDetails', module='types')
        key "objectType": Required[Union[str, ResumeProtectionRequestObjectType]]
        identityDetails: IdentityDetails
        objectType: Union[str, ResumeProtectionRequestObjectType]


    class azure.mgmt.dataprotection.types.RetentionTag(TypedDict, total=False):
        key "eTag": str
        key "id": str
        key "tagName": Required[str]
        eTag: str
        id: str
        tagName: str


    class azure.mgmt.dataprotection.types.ScheduleBasedBackupCriteria(TypedDict, total=False):
        key "objectType": Required[Literal["ScheduleBasedBackupCriteria"]]
        absoluteCriteria: list[Union[str, AbsoluteMarker]]
        daysOfMonth: list[Day]
        daysOfTheWeek: list[Union[str, DayOfWeek]]
        monthsOfYear: list[Union[str, Month]]
        objectType: Literal[ScheduleBasedBackupCriteria]
        scheduleTimes: list[str]
        weeksOfTheMonth: list[Union[str, WeekNumber]]


    class azure.mgmt.dataprotection.types.ScheduleBasedTriggerContext(TypedDict, total=False):
        key "objectType": Required[Literal["ScheduleBasedTriggerContext"]]
        key "schedule": Required[BackupSchedule]
        key "taggingCriteria": Required[list[TaggingCriteria]]
        objectType: Literal[ScheduleBasedTriggerContext]
        schedule: BackupSchedule
        taggingCriteria: list[TaggingCriteria]


    class azure.mgmt.dataprotection.types.SecretStoreBasedAuthCredentials(TypedDict, total=False):
        key "objectType": Required[Literal["SecretStoreBasedAuthCredentials"]]
        key "secretStoreResource": ForwardRef('SecretStoreResource', module='types')
        objectType: Literal[SecretStoreBasedAuthCredentials]
        secretStoreResource: SecretStoreResource


    class azure.mgmt.dataprotection.types.SecretStoreResource(TypedDict, total=False):
        key "secretStoreType": Required[Union[str, SecretStoreType]]
        key "uri": str
        key "value": str
        secretStoreType: Union[str, SecretStoreType]
        uri: str
        value: str


    class azure.mgmt.dataprotection.types.SecuritySettings(TypedDict, total=False):
        key "encryptionSettings": ForwardRef('EncryptionSettings', module='types')
        key "immutabilitySettings": ForwardRef('ImmutabilitySettings', module='types')
        key "softDeleteSettings": ForwardRef('SoftDeleteSettings', module='types')
        encryptionSettings: EncryptionSettings
        immutabilitySettings: ImmutabilitySettings
        softDeleteSettings: SoftDeleteSettings


    class azure.mgmt.dataprotection.types.SoftDeleteSettings(TypedDict, total=False):
        key "retentionDurationInDays": float
        key "state": Union[str, SoftDeleteState]
        retentionDurationInDays: float
        state: Union[str, SoftDeleteState]


    class azure.mgmt.dataprotection.types.SourceLifeCycle(TypedDict, total=False):
        key "deleteAfter": Required[DeleteOption]
        key "sourceDataStore": Required[DataStoreInfoBase]
        deleteAfter: DeleteOption
        sourceDataStore: DataStoreInfoBase
        targetDataStoreCopySettings: list[TargetCopySetting]


    class azure.mgmt.dataprotection.types.StopProtectionRequest(TypedDict, total=False):
        resourceGuardOperationRequests: list[str]


    class azure.mgmt.dataprotection.types.StorageSetting(TypedDict, total=False):
        key "datastoreType": Union[str, StorageSettingStoreTypes]
        key "type": Union[str, StorageSettingTypes]
        datastoreType: Union[str, StorageSettingStoreTypes]
        type: Union[str, StorageSettingTypes]


    class azure.mgmt.dataprotection.types.SuspendBackupRequest(TypedDict, total=False):
        resourceGuardOperationRequests: list[str]


    class azure.mgmt.dataprotection.types.SyncBackupInstanceRequest(TypedDict, total=False):
        key "syncType": Union[str, SyncType]
        syncType: Union[str, SyncType]


    class azure.mgmt.dataprotection.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.dataprotection.types.TaggingCriteria(TypedDict, total=False):
        key "isDefault": Required[bool]
        key "tagInfo": Required[RetentionTag]
        key "taggingPriority": Required[int]
        criteria: list[BackupCriteria]
        isDefault: bool
        tagInfo: RetentionTag
        taggingPriority: int


    class azure.mgmt.dataprotection.types.TargetCopySetting(TypedDict, total=False):
        key "copyAfter": Required[CopyOption]
        key "dataStore": Required[DataStoreInfoBase]
        copyAfter: CopyOption
        dataStore: DataStoreInfoBase


    class azure.mgmt.dataprotection.types.TargetDetails(TypedDict, total=False):
        key "filePrefix": Required[str]
        key "restoreTargetLocationType": Required[Union[str, RestoreTargetLocationType]]
        key "targetResourceArmId": str
        key "url": Required[str]
        filePrefix: str
        restoreTargetLocationType: Union[str, RestoreTargetLocationType]
        targetResourceArmId: str
        url: str


    class azure.mgmt.dataprotection.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dataprotection.types.TriggerBackupRequest(TypedDict, total=False):
        key "backupRuleOptions": Required[AdHocBackupRuleOptions]
        backupRuleOptions: AdHocBackupRuleOptions


    class azure.mgmt.dataprotection.types.UnlockDeleteRequest(TypedDict, total=False):
        key "resourceToBeDeleted": str
        resourceGuardOperationRequests: list[str]
        resourceToBeDeleted: str


    class azure.mgmt.dataprotection.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.dataprotection.types.UserFacingError(TypedDict, total=False):
        key "code": str
        key "innerError": ForwardRef('InnerError', module='types')
        key "isRetryable": bool
        key "isUserError": bool
        key "message": str
        key "target": str
        code: str
        details: list[UserFacingError]
        innerError: InnerError
        isRetryable: bool
        isUserError: bool
        message: str
        properties: dict[str, str]
        recommendedAction: list[str]
        target: str


    class azure.mgmt.dataprotection.types.ValidateCrossRegionRestoreRequestObject(TypedDict, total=False):
        key "crossRegionRestoreDetails": Required[CrossRegionRestoreDetails]
        key "restoreRequestObject": Required[AzureBackupRestoreRequest]
        crossRegionRestoreDetails: CrossRegionRestoreDetails
        restoreRequestObject: AzureBackupRestoreRequest


    class azure.mgmt.dataprotection.types.ValidateForBackupRequest(TypedDict, total=False):
        key "backupInstance": Required[BackupInstance]
        backupInstance: BackupInstance


    class azure.mgmt.dataprotection.types.ValidateForModifyBackupRequest(TypedDict, total=False):
        key "backupInstance": Required[BackupInstance]
        backupInstance: BackupInstance


    class azure.mgmt.dataprotection.types.ValidateRestoreRequestObject(TypedDict, total=False):
        key "restoreRequestObject": Required[AzureBackupRestoreRequest]
        restoreRequestObject: AzureBackupRestoreRequest


```