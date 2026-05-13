```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                parameters: JSON, 
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
                parameters: JSON, 
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

        @distributed_trace_async
        async def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
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
                parameters: Optional[JSON] = None, 
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
                parameters: Optional[JSON] = None, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01'])
        async def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedBackupVaultResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01'])
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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

        @distributed_trace
        def begin_resume_protection(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                backup_instance_name: str, 
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
                parameters: Optional[JSON] = None, 
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
                parameters: Optional[JSON] = None, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01'])
        def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedBackupVaultResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-09-01', '2026-03-01'])
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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


```