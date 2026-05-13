```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.recoveryservicesbackup

    class azure.mgmt.recoveryservicesbackup.RecoveryServicesBackupClient(_RecoveryServicesBackupClientOperationsMixin): implements ContextManager 
        backup_engines: BackupEnginesOperations
        backup_jobs: BackupJobsOperations
        backup_operation_results: BackupOperationResultsOperations
        backup_operation_statuses: BackupOperationStatusesOperations
        backup_policies: BackupPoliciesOperations
        backup_protectable_items: BackupProtectableItemsOperations
        backup_protected_items: BackupProtectedItemsOperations
        backup_protection_containers: BackupProtectionContainersOperations
        backup_protection_intent: BackupProtectionIntentOperations
        backup_resource_encryption_configs: BackupResourceEncryptionConfigsOperations
        backup_resource_storage_configs_non_crr: BackupResourceStorageConfigsNonCRROperations
        backup_resource_vault_configs: BackupResourceVaultConfigsOperations
        backup_status: BackupStatusOperations
        backup_usage_summaries: BackupUsageSummariesOperations
        backup_workload_items: BackupWorkloadItemsOperations
        backups: BackupsOperations
        bms_prepare_data_move_operation_result: BMSPrepareDataMoveOperationResultOperations
        deleted_protection_containers: DeletedProtectionContainersOperations
        export_jobs_operation_results: ExportJobsOperationResultsOperations
        feature_support: FeatureSupportOperations
        fetch_tiering_cost: FetchTieringCostOperations
        get_tiering_cost_operation_result: GetTieringCostOperationResultOperations
        item_level_recovery_connections: ItemLevelRecoveryConnectionsOperations
        job_cancellations: JobCancellationsOperations
        job_details: JobDetailsOperations
        job_operation_results: JobOperationResultsOperations
        jobs: JobsOperations
        operation: OperationOperations
        operations: Operations
        private_endpoint: PrivateEndpointOperations
        private_endpoint_connection: PrivateEndpointConnectionOperations
        protectable_containers: ProtectableContainersOperations
        protected_item_operation_results: ProtectedItemOperationResultsOperations
        protected_item_operation_statuses: ProtectedItemOperationStatusesOperations
        protected_items: ProtectedItemsOperations
        protection_container_operation_results: ProtectionContainerOperationResultsOperations
        protection_container_refresh_operation_results: ProtectionContainerRefreshOperationResultsOperations
        protection_containers: ProtectionContainersOperations
        protection_intent: ProtectionIntentOperations
        protection_policies: ProtectionPoliciesOperations
        protection_policy_operation_results: ProtectionPolicyOperationResultsOperations
        protection_policy_operation_statuses: ProtectionPolicyOperationStatusesOperations
        recovery_points: RecoveryPointsOperations
        recovery_points_recommended_for_move: RecoveryPointsRecommendedForMoveOperations
        resource_guard_proxies: ResourceGuardProxiesOperations
        resource_guard_proxy: ResourceGuardProxyOperations
        restores: RestoresOperations
        security_pins: SecurityPINsOperations
        tiering_cost_operation_status: TieringCostOperationStatusOperations
        validate_operation: ValidateOperationOperations
        validate_operation_results: ValidateOperationResultsOperations
        validate_operation_statuses: ValidateOperationStatusesOperations

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

        @overload
        def begin_bms_prepare_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: PrepareDataMoveRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bms_prepare_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bms_prepare_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bms_trigger_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: TriggerDataMoveRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bms_trigger_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bms_trigger_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move_recovery_point(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: MoveRPAcrossTiersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move_recovery_point(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move_recovery_point(
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
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_operation_status(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.recoveryservicesbackup.aio

    class azure.mgmt.recoveryservicesbackup.aio.RecoveryServicesBackupClient(_RecoveryServicesBackupClientOperationsMixin): implements AsyncContextManager 
        backup_engines: BackupEnginesOperations
        backup_jobs: BackupJobsOperations
        backup_operation_results: BackupOperationResultsOperations
        backup_operation_statuses: BackupOperationStatusesOperations
        backup_policies: BackupPoliciesOperations
        backup_protectable_items: BackupProtectableItemsOperations
        backup_protected_items: BackupProtectedItemsOperations
        backup_protection_containers: BackupProtectionContainersOperations
        backup_protection_intent: BackupProtectionIntentOperations
        backup_resource_encryption_configs: BackupResourceEncryptionConfigsOperations
        backup_resource_storage_configs_non_crr: BackupResourceStorageConfigsNonCRROperations
        backup_resource_vault_configs: BackupResourceVaultConfigsOperations
        backup_status: BackupStatusOperations
        backup_usage_summaries: BackupUsageSummariesOperations
        backup_workload_items: BackupWorkloadItemsOperations
        backups: BackupsOperations
        bms_prepare_data_move_operation_result: BMSPrepareDataMoveOperationResultOperations
        deleted_protection_containers: DeletedProtectionContainersOperations
        export_jobs_operation_results: ExportJobsOperationResultsOperations
        feature_support: FeatureSupportOperations
        fetch_tiering_cost: FetchTieringCostOperations
        get_tiering_cost_operation_result: GetTieringCostOperationResultOperations
        item_level_recovery_connections: ItemLevelRecoveryConnectionsOperations
        job_cancellations: JobCancellationsOperations
        job_details: JobDetailsOperations
        job_operation_results: JobOperationResultsOperations
        jobs: JobsOperations
        operation: OperationOperations
        operations: Operations
        private_endpoint: PrivateEndpointOperations
        private_endpoint_connection: PrivateEndpointConnectionOperations
        protectable_containers: ProtectableContainersOperations
        protected_item_operation_results: ProtectedItemOperationResultsOperations
        protected_item_operation_statuses: ProtectedItemOperationStatusesOperations
        protected_items: ProtectedItemsOperations
        protection_container_operation_results: ProtectionContainerOperationResultsOperations
        protection_container_refresh_operation_results: ProtectionContainerRefreshOperationResultsOperations
        protection_containers: ProtectionContainersOperations
        protection_intent: ProtectionIntentOperations
        protection_policies: ProtectionPoliciesOperations
        protection_policy_operation_results: ProtectionPolicyOperationResultsOperations
        protection_policy_operation_statuses: ProtectionPolicyOperationStatusesOperations
        recovery_points: RecoveryPointsOperations
        recovery_points_recommended_for_move: RecoveryPointsRecommendedForMoveOperations
        resource_guard_proxies: ResourceGuardProxiesOperations
        resource_guard_proxy: ResourceGuardProxyOperations
        restores: RestoresOperations
        security_pins: SecurityPINsOperations
        tiering_cost_operation_status: TieringCostOperationStatusOperations
        validate_operation: ValidateOperationOperations
        validate_operation_results: ValidateOperationResultsOperations
        validate_operation_statuses: ValidateOperationStatusesOperations

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

        @overload
        async def begin_bms_prepare_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: PrepareDataMoveRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bms_prepare_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bms_prepare_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bms_trigger_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: TriggerDataMoveRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bms_trigger_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bms_trigger_data_move(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move_recovery_point(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: MoveRPAcrossTiersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move_recovery_point(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move_recovery_point(
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
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_operation_status(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.recoveryservicesbackup.aio.operations

    class azure.mgmt.recoveryservicesbackup.aio.operations.BMSPrepareDataMoveOperationResultOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[VaultStorageConfigOperationResultResponse]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupEnginesOperations:

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
                backup_engine_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupEngineBaseResource: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupEngineBaseResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupJobsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupOperationStatusesOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupPoliciesOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionPolicyResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupProtectableItemsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadProtectableItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupProtectedItemsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectedItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupProtectionContainersOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupProtectionIntentOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionIntentResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupResourceEncryptionConfigsOperations:

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
            ) -> BackupResourceEncryptionConfigExtendedResource: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceEncryptionConfigResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupResourceStorageConfigsNonCRROperations:

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
                parameters: JSON, 
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
                parameters: JSON, 
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


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupResourceVaultConfigsOperations:

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
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        async def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceVaultConfigResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        async def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        async def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceVaultConfigResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        async def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get(
                self, 
                azure_region: str, 
                parameters: BackupStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupStatusResponse: ...

        @overload
        async def get(
                self, 
                azure_region: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupStatusResponse: ...

        @overload
        async def get(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupStatusResponse: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupUsageSummariesOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupManagementUsage]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupWorkloadItemsOperations:

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
                fabric_name: str, 
                container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.BackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: BackupRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.DeletedProtectionContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ExportJobsOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResultInfoBaseResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.FeatureSupportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate(
                self, 
                azure_region: str, 
                parameters: FeatureSupportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureVMResourceFeatureSupportResponse: ...

        @overload
        async def validate(
                self, 
                azure_region: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureVMResourceFeatureSupportResponse: ...

        @overload
        async def validate(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureVMResourceFeatureSupportResponse: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.FetchTieringCostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: FetchTieringCostInfoRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TieringCostInfo]: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TieringCostInfo]: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TieringCostInfo]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.GetTieringCostOperationResultOperations:

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
            ) -> TieringCostInfo: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ItemLevelRecoveryConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def provision(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: ILRRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def provision(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def provision(
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
            ) -> None: ...

        @distributed_trace_async
        async def revoke(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.JobCancellationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.JobDetailsOperations:

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
                job_name: str, 
                **kwargs: Any
            ) -> JobResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.JobOperationResultsOperations:

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
                job_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def export(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.OperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: ValidateOperationRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOperationsResponse: ...

        @overload
        async def validate(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOperationsResponse: ...

        @overload
        async def validate(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOperationsResponse: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ClientDiscoveryValueForSingleApi]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.PrivateEndpointConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.PrivateEndpointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_operation_status(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectableContainersOperations:

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
                fabric_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectableContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectedItemOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ProtectedItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectedItemOperationStatusesOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectedItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: ProtectedItemResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemResource]: ...

        @distributed_trace_async
        async def delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ProtectedItemResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionContainerOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ProtectionContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionContainerRefreshOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_register(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                parameters: ProtectionContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerResource]: ...

        @overload
        async def begin_register(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerResource]: ...

        @overload
        async def begin_register(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ProtectionContainerResource: ...

        @distributed_trace_async
        async def inquire(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def refresh(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def unregister(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionIntentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                parameters: ProtectionIntentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @overload
        async def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @overload
        async def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @overload
        async def validate(
                self, 
                azure_region: str, 
                parameters: PreValidateEnableBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PreValidateEnableBackupResponse: ...

        @overload
        async def validate(
                self, 
                azure_region: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PreValidateEnableBackupResponse: ...

        @overload
        async def validate(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PreValidateEnableBackupResponse: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: ProtectionPolicyResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ProtectionPolicyResource]: ...

        @overload
        async def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ProtectionPolicyResource]: ...

        @overload
        async def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ProtectionPolicyResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> ProtectionPolicyResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionPolicyOperationResultsOperations:

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
                policy_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ProtectionPolicyResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ProtectionPolicyOperationStatusesOperations:

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
                policy_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.RecoveryPointsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPointResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: UpdateRecoveryPointRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecoveryPointResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecoveryPointResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecoveryPointResource: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.RecoveryPointsRecommendedForMoveOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: ListRecoveryPointsRecommendedForMoveRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPointResource]: ...

        @overload
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPointResource]: ...

        @overload
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPointResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ResourceGuardProxiesOperations:

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
            ) -> AsyncItemPaged[ResourceGuardProxyBaseResource]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ResourceGuardProxyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        async def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: ResourceGuardProxyBaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        async def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        async def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        async def unlock_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: UnlockDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        async def unlock_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        async def unlock_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.RestoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: RestoreRequestResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger(
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
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.SecurityPINsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: Optional[SecurityPinBase] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> TokenInformation: ...

        @overload
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> TokenInformation: ...

        @overload
        async def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> TokenInformation: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.TieringCostOperationStatusOperations:

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
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ValidateOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: ValidateOperationRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ValidateOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ValidateOperationsResponse]: ...


    class azure.mgmt.recoveryservicesbackup.aio.operations.ValidateOperationStatusesOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


namespace azure.mgmt.recoveryservicesbackup.models

    class azure.mgmt.recoveryservicesbackup.models.AcquireStorageAccountLock(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACQUIRE = "Acquire"
        NOT_ACQUIRE = "NotAcquire"


    class azure.mgmt.recoveryservicesbackup.models.ArmErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ArmErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.recoveryservicesbackup.models.AzureBackupGoalFeatureSupportRequest(FeatureSupportRequest, discriminator='AzureBackupGoals'):
        feature_type: Literal["AzureBackupGoals"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureBackupServerContainer(DpmContainer, discriminator='AzureBackupServerContainer'):
        backup_management_type: Union[str, BackupManagementType]
        can_re_register: bool
        container_id: str
        container_type: Literal[ProtectableContainerType.AZURE_BACKUP_SERVER_CONTAINER]
        dpm_agent_version: str
        dpm_servers: list[str]
        extended_info: DPMContainerExtendedInfo
        friendly_name: str
        health_status: str
        protectable_object_type: str
        protected_item_count: int
        protection_status: str
        registration_status: str
        upgrade_available: bool

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                can_re_register: Optional[bool] = ..., 
                container_id: Optional[str] = ..., 
                dpm_agent_version: Optional[str] = ..., 
                dpm_servers: Optional[list[str]] = ..., 
                extended_info: Optional[DPMContainerExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                protected_item_count: Optional[int] = ..., 
                protection_status: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                upgrade_available: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureBackupServerEngine(BackupEngineBase, discriminator='AzureBackupServerEngine'):
        azure_backup_agent_version: str
        backup_engine_id: str
        backup_engine_state: str
        backup_engine_type: Literal[BackupEngineType.AZURE_BACKUP_SERVER_ENGINE]
        backup_management_type: Union[str, BackupManagementType]
        can_re_register: bool
        dpm_version: str
        extended_info: BackupEngineExtendedInfo
        friendly_name: str
        health_status: str
        is_azure_backup_agent_upgrade_available: bool
        is_dpm_upgrade_available: bool
        registration_status: str

        @overload
        def __init__(
                self, 
                *, 
                azure_backup_agent_version: Optional[str] = ..., 
                backup_engine_id: Optional[str] = ..., 
                backup_engine_state: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                can_re_register: Optional[bool] = ..., 
                dpm_version: Optional[str] = ..., 
                extended_info: Optional[BackupEngineExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                is_azure_backup_agent_upgrade_available: Optional[bool] = ..., 
                is_dpm_upgrade_available: Optional[bool] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareBackupRequest(BackupRequest, discriminator='AzureFileShareBackupRequest'):
        object_type: Literal["AzureFileShareBackupRequest"]
        recovery_point_expiry_time_in_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_expiry_time_in_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareProtectableItem(WorkloadProtectableItem, discriminator='AzureFileShare'):
        azure_file_share_type: Optional[Union[str, AzureFileShareType]]
        backup_management_type: str
        friendly_name: str
        parent_container_fabric_id: Optional[str]
        parent_container_friendly_name: Optional[str]
        protectable_item_type: Literal["AzureFileShare"]
        protection_state: Union[str, ProtectionStatus]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                azure_file_share_type: Optional[Union[str, AzureFileShareType]] = ..., 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                parent_container_fabric_id: Optional[str] = ..., 
                parent_container_friendly_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareProtectionPolicy(ProtectionPolicy, discriminator='AzureStorage'):
        backup_management_type: Literal["AzureStorage"]
        protected_items_count: int
        resource_guard_operation_requests: list[str]
        retention_policy: Optional[RetentionPolicy]
        schedule_policy: Optional[SchedulePolicy]
        time_zone: Optional[str]
        vault_retention_policy: Optional[VaultRetentionPolicy]
        work_load_type: Optional[Union[str, WorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                schedule_policy: Optional[SchedulePolicy] = ..., 
                time_zone: Optional[str] = ..., 
                vault_retention_policy: Optional[VaultRetentionPolicy] = ..., 
                work_load_type: Optional[Union[str, WorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareProvisionILRRequest(ILRRequest, discriminator='AzureFileShareProvisionILRRequest'):
        object_type: Literal["AzureFileShareProvisionILRRequest"]
        recovery_point_id: Optional[str]
        source_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_id: Optional[str] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareRecoveryPoint(RecoveryPoint, discriminator='AzureFileShareRecoveryPoint'):
        file_share_snapshot_uri: Optional[str]
        object_type: Literal["AzureFileShareRecoveryPoint"]
        recovery_point_properties: Optional[RecoveryPointProperties]
        recovery_point_size_in_gb: Optional[int]
        recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]]
        recovery_point_time: Optional[datetime]
        recovery_point_type: Optional[str]
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]

        @overload
        def __init__(
                self, 
                *, 
                file_share_snapshot_uri: Optional[str] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_size_in_gb: Optional[int] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformation]] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                recovery_point_type: Optional[str] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareRestoreRequest(RestoreRequest, discriminator='AzureFileShareRestoreRequest'):
        copy_options: Optional[Union[str, CopyOptions]]
        object_type: Literal["AzureFileShareRestoreRequest"]
        recovery_type: Optional[Union[str, RecoveryType]]
        resource_guard_operation_requests: list[str]
        restore_file_specs: Optional[list[RestoreFileSpecs]]
        restore_request_type: Optional[Union[str, RestoreRequestType]]
        source_resource_id: Optional[str]
        target_details: Optional[TargetAFSRestoreInfo]

        @overload
        def __init__(
                self, 
                *, 
                copy_options: Optional[Union[str, CopyOptions]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_file_specs: Optional[list[RestoreFileSpecs]] = ..., 
                restore_request_type: Optional[Union[str, RestoreRequestType]] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_details: Optional[TargetAFSRestoreInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileShareType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        XSMB = "XSMB"
        X_SYNC = "XSync"


    class azure.mgmt.recoveryservicesbackup.models.AzureFileshareProtectedItem(ProtectedItem, discriminator='AzureFileShareProtectedItem'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: Optional[AzureFileshareProtectedItemExtendedInfo]
        friendly_name: Optional[str]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: Optional[dict[str, KPIResourceHealthDetails]]
        last_backup_status: Optional[str]
        last_backup_time: Optional[datetime]
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        protected_item_type: Literal["AzureFileShareProtectedItem"]
        protection_state: Optional[Union[str, ProtectionState]]
        protection_status: Optional[str]
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureFileshareProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureFileshareProtectedItemExtendedInfo(_Model):
        oldest_recovery_point: Optional[datetime]
        policy_state: Optional[str]
        recovery_point_count: Optional[int]
        resource_state: Optional[str]
        resource_state_sync_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                oldest_recovery_point: Optional[datetime] = ..., 
                policy_state: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSClassicComputeVMContainer(IaaSVMContainer, discriminator='Microsoft.ClassicCompute/virtualMachines'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.MICROSOFT_CLASSIC_COMPUTE_VIRTUAL_MACHINES]
        friendly_name: str
        health_status: str
        protectable_object_type: str
        registration_status: str
        resource_group: str
        virtual_machine_id: str
        virtual_machine_version: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSClassicComputeVMProtectableItem(IaaSVMProtectableItem, discriminator='Microsoft.ClassicCompute/virtualMachines'):
        backup_management_type: str
        friendly_name: str
        protectable_item_type: Literal["ClassicCompute/virtualMachines"]
        protection_state: Union[str, ProtectionStatus]
        resource_group: str
        virtual_machine_id: str
        virtual_machine_version: str
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                resource_group: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSClassicComputeVMProtectedItem(AzureIaaSVMProtectedItem, discriminator='Microsoft.ClassicCompute/virtualMachines'):
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
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        policy_type: str
        protected_item_data_id: str
        protected_item_type: Literal["ClassicCompute/virtualMachines"]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        virtual_machine_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo] = ..., 
                extended_properties: Optional[ExtendedProperties] = ..., 
                health_details: Optional[list[AzureIaaSVMHealthDetails]] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSComputeVMContainer(IaaSVMContainer, discriminator='Microsoft.Compute/virtualMachines'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.MICROSOFT_COMPUTE_VIRTUAL_MACHINES]
        friendly_name: str
        health_status: str
        protectable_object_type: str
        registration_status: str
        resource_group: str
        virtual_machine_id: str
        virtual_machine_version: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSComputeVMProtectableItem(IaaSVMProtectableItem, discriminator='Microsoft.Compute/virtualMachines'):
        backup_management_type: str
        friendly_name: str
        protectable_item_type: Literal["Compute/virtualMachines"]
        protection_state: Union[str, ProtectionStatus]
        resource_group: str
        virtual_machine_id: str
        virtual_machine_version: str
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                resource_group: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSComputeVMProtectedItem(AzureIaaSVMProtectedItem, discriminator='Microsoft.Compute/virtualMachines'):
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
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_status: str
        last_backup_time: datetime
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        policy_type: str
        protected_item_data_id: str
        protected_item_type: Literal["Compute/virtualMachines"]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        virtual_machine_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo] = ..., 
                extended_properties: Optional[ExtendedProperties] = ..., 
                health_details: Optional[list[AzureIaaSVMHealthDetails]] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMErrorInfo(_Model):
        error_code: Optional[int]
        error_string: Optional[str]
        error_title: Optional[str]
        recommendations: Optional[list[str]]


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMHealthDetails(ResourceHealthDetails):
        code: int
        message: str
        recommendations: list[str]
        title: str


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMJob(Job, discriminator='AzureIaaSVMJob'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        container_name: Optional[str]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[AzureIaaSVMErrorInfo]]
        extended_info: Optional[AzureIaaSVMJobExtendedInfo]
        is_user_triggered: Optional[bool]
        job_type: Literal["AzureIaaSVMJob"]
        operation: str
        start_time: datetime
        status: str
        virtual_machine_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_name: Optional[str] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[AzureIaaSVMErrorInfo]] = ..., 
                extended_info: Optional[AzureIaaSVMJobExtendedInfo] = ..., 
                is_user_triggered: Optional[bool] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMJobExtendedInfo(_Model):
        dynamic_error_message: Optional[str]
        estimated_remaining_duration: Optional[str]
        internal_property_bag: Optional[dict[str, str]]
        progress_percentage: Optional[float]
        property_bag: Optional[dict[str, str]]
        tasks_list: Optional[list[AzureIaaSVMJobTaskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                estimated_remaining_duration: Optional[str] = ..., 
                internal_property_bag: Optional[dict[str, str]] = ..., 
                progress_percentage: Optional[float] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[AzureIaaSVMJobTaskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMJobTaskDetails(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        instance_id: Optional[str]
        progress_percentage: Optional[float]
        start_time: Optional[datetime]
        status: Optional[str]
        task_execution_details: Optional[str]
        task_id: Optional[str]

        @overload
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
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMJobV2(Job, discriminator='AzureIaaSVMJobV2'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        container_name: Optional[str]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[AzureIaaSVMErrorInfo]]
        extended_info: Optional[AzureIaaSVMJobExtendedInfo]
        job_type: Literal["AzureIaaSVMJobV2"]
        operation: str
        start_time: datetime
        status: str
        virtual_machine_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_name: Optional[str] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[AzureIaaSVMErrorInfo]] = ..., 
                extended_info: Optional[AzureIaaSVMJobExtendedInfo] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMProtectedItem(ProtectedItem, discriminator='AzureIaaSVMProtectedItem'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo]
        extended_properties: Optional[ExtendedProperties]
        friendly_name: Optional[str]
        health_details: Optional[list[AzureIaaSVMHealthDetails]]
        health_status: Optional[Union[str, HealthStatus]]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: Optional[dict[str, KPIResourceHealthDetails]]
        last_backup_status: Optional[str]
        last_backup_time: Optional[datetime]
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        policy_type: Optional[str]
        protected_item_data_id: Optional[str]
        protected_item_type: Literal["AzureIaaSVMProtectedItem"]
        protection_state: Optional[Union[str, ProtectionState]]
        protection_status: Optional[str]
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        virtual_machine_id: Optional[str]
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureIaaSVMProtectedItemExtendedInfo] = ..., 
                extended_properties: Optional[ExtendedProperties] = ..., 
                health_details: Optional[list[AzureIaaSVMHealthDetails]] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                protection_status: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMProtectedItemExtendedInfo(_Model):
        newest_recovery_point_in_archive: Optional[datetime]
        oldest_recovery_point: Optional[datetime]
        oldest_recovery_point_in_archive: Optional[datetime]
        oldest_recovery_point_in_vault: Optional[datetime]
        policy_inconsistent: Optional[bool]
        recovery_point_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                newest_recovery_point_in_archive: Optional[datetime] = ..., 
                oldest_recovery_point: Optional[datetime] = ..., 
                oldest_recovery_point_in_archive: Optional[datetime] = ..., 
                oldest_recovery_point_in_vault: Optional[datetime] = ..., 
                policy_inconsistent: Optional[bool] = ..., 
                recovery_point_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureIaaSVMProtectionPolicy(ProtectionPolicy, discriminator='AzureIaasVM'):
        backup_management_type: Literal["AzureIaasVM"]
        instant_rp_details: Optional[InstantRPAdditionalDetails]
        instant_rp_retention_range_in_days: Optional[int]
        policy_type: Optional[Union[str, IAASVMPolicyType]]
        protected_items_count: int
        resource_guard_operation_requests: list[str]
        retention_policy: Optional[RetentionPolicy]
        schedule_policy: Optional[SchedulePolicy]
        snapshot_consistency_type: Optional[Union[str, IaasVMSnapshotConsistencyType]]
        tiering_policy: Optional[dict[str, TieringPolicy]]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                instant_rp_details: Optional[InstantRPAdditionalDetails] = ..., 
                instant_rp_retention_range_in_days: Optional[int] = ..., 
                policy_type: Optional[Union[str, IAASVMPolicyType]] = ..., 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                schedule_policy: Optional[SchedulePolicy] = ..., 
                snapshot_consistency_type: Optional[Union[str, IaasVMSnapshotConsistencyType]] = ..., 
                tiering_policy: Optional[dict[str, TieringPolicy]] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureRecoveryServiceVaultProtectionIntent(ProtectionIntent, discriminator='RecoveryServiceVaultItem'):
        backup_management_type: Union[str, BackupManagementType]
        item_id: str
        policy_id: str
        protection_intent_item_type: Literal[ProtectionIntentItemType.RECOVERY_SERVICE_VAULT_ITEM]
        protection_state: Union[str, ProtectionStatus]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                item_id: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureResourceProtectionIntent(ProtectionIntent, discriminator='AzureResourceItem'):
        backup_management_type: Union[str, BackupManagementType]
        friendly_name: Optional[str]
        item_id: str
        policy_id: str
        protection_intent_item_type: Literal[ProtectionIntentItemType.AZURE_RESOURCE_ITEM]
        protection_state: Union[str, ProtectionStatus]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                friendly_name: Optional[str] = ..., 
                item_id: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureSQLAGWorkloadContainerProtectionContainer(AzureWorkloadContainer, discriminator='SQLAGWorkLoadContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.SQLAG_WORK_LOAD_CONTAINER]
        extended_info: AzureWorkloadContainerExtendedInfo
        friendly_name: str
        health_status: str
        last_updated_time: datetime
        operation_type: Union[str, OperationType]
        protectable_object_type: str
        registration_status: str
        source_resource_id: str
        workload_type: Union[str, WorkloadType]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                extended_info: Optional[AzureWorkloadContainerExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                last_updated_time: Optional[datetime] = ..., 
                operation_type: Optional[Union[str, OperationType]] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, WorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureSqlContainer(ProtectionContainer, discriminator='AzureSqlContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.AZURE_SQL_CONTAINER]
        friendly_name: str
        health_status: str
        protectable_object_type: str
        registration_status: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureSqlProtectedItem(ProtectedItem, discriminator='Microsoft.Sql/servers/databases'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: Optional[AzureSqlProtectedItemExtendedInfo]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        protected_item_data_id: Optional[str]
        protected_item_type: Literal["Sql/servers/databases"]
        protection_state: Optional[Union[str, ProtectedItemState]]
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureSqlProtectedItemExtendedInfo] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectedItemState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureSqlProtectedItemExtendedInfo(_Model):
        oldest_recovery_point: Optional[datetime]
        policy_state: Optional[str]
        recovery_point_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                oldest_recovery_point: Optional[datetime] = ..., 
                policy_state: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureSqlProtectionPolicy(ProtectionPolicy, discriminator='AzureSql'):
        backup_management_type: Literal["AzureSql"]
        protected_items_count: int
        resource_guard_operation_requests: list[str]
        retention_policy: Optional[RetentionPolicy]

        @overload
        def __init__(
                self, 
                *, 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                retention_policy: Optional[RetentionPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureStorageContainer(ProtectionContainer, discriminator='StorageContainer'):
        acquire_storage_account_lock: Optional[Union[str, AcquireStorageAccountLock]]
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.STORAGE_CONTAINER]
        friendly_name: str
        health_status: str
        operation_type: Optional[Union[str, OperationType]]
        protectable_object_type: str
        protected_item_count: Optional[int]
        registration_status: str
        resource_group: Optional[str]
        source_resource_id: Optional[str]
        storage_account_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                acquire_storage_account_lock: Optional[Union[str, AcquireStorageAccountLock]] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                operation_type: Optional[Union[str, OperationType]] = ..., 
                protectable_object_type: Optional[str] = ..., 
                protected_item_count: Optional[int] = ..., 
                registration_status: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                storage_account_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureStorageErrorInfo(_Model):
        error_code: Optional[int]
        error_string: Optional[str]
        recommendations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[int] = ..., 
                error_string: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureStorageJob(Job, discriminator='AzureStorageJob'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[AzureStorageErrorInfo]]
        extended_info: Optional[AzureStorageJobExtendedInfo]
        is_user_triggered: Optional[bool]
        job_type: Literal["AzureStorageJob"]
        operation: str
        start_time: datetime
        status: str
        storage_account_name: Optional[str]
        storage_account_version: Optional[str]

        @overload
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
                is_user_triggered: Optional[bool] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_account_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureStorageJobExtendedInfo(_Model):
        dynamic_error_message: Optional[str]
        property_bag: Optional[dict[str, str]]
        tasks_list: Optional[list[AzureStorageJobTaskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[AzureStorageJobTaskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureStorageJobTaskDetails(_Model):
        status: Optional[str]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureStorageProtectableContainer(ProtectableContainer, discriminator='StorageContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_id: str
        friendly_name: str
        health_status: str
        protectable_container_type: Literal[ProtectableContainerType.STORAGE_CONTAINER]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_id: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVMAppContainerProtectableContainer(ProtectableContainer, discriminator='VMAppContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_id: str
        friendly_name: str
        health_status: str
        protectable_container_type: Literal[ProtectableContainerType.VM_APP_CONTAINER]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_id: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVMAppContainerProtectionContainer(AzureWorkloadContainer, discriminator='VMAppContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.VM_APP_CONTAINER]
        extended_info: AzureWorkloadContainerExtendedInfo
        friendly_name: str
        health_status: str
        last_updated_time: datetime
        operation_type: Union[str, OperationType]
        protectable_object_type: str
        registration_status: str
        source_resource_id: str
        workload_type: Union[str, WorkloadType]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                extended_info: Optional[AzureWorkloadContainerExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                last_updated_time: Optional[datetime] = ..., 
                operation_type: Optional[Union[str, OperationType]] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, WorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVMResourceFeatureSupportRequest(FeatureSupportRequest, discriminator='AzureVMResourceBackup'):
        feature_type: Literal["AzureVMResourceBackup"]
        vm_size: Optional[str]
        vm_sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                vm_size: Optional[str] = ..., 
                vm_sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVMResourceFeatureSupportResponse(_Model):
        support_status: Optional[Union[str, SupportStatus]]

        @overload
        def __init__(
                self, 
                *, 
                support_status: Optional[Union[str, SupportStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadItem(WorkloadItem, discriminator='AzureVmWorkloadItem'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: Optional[bool]
        parent_name: Optional[str]
        protection_state: Union[str, ProtectionStatus]
        server_name: Optional[str]
        sub_workload_item_count: Optional[int]
        subinquireditemcount: Optional[int]
        workload_item_type: Literal["AzureVmWorkloadItem"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadProtectableItem(WorkloadProtectableItem, discriminator='AzureVmWorkloadProtectableItem'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: Optional[bool]
        is_auto_protected: Optional[bool]
        is_protectable: Optional[bool]
        parent_name: Optional[str]
        parent_unique_name: Optional[str]
        prebackupvalidation: Optional[PreBackupValidation]
        protectable_item_type: Literal["AzureVmWorkloadProtectableItem"]
        protection_state: Union[str, ProtectionStatus]
        server_name: Optional[str]
        subinquireditemcount: Optional[int]
        subprotectableitemcount: Optional[int]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadProtectedItem(ProtectedItem, discriminator='AzureVmWorkloadProtectedItem'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo]
        friendly_name: Optional[str]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: Optional[dict[str, KPIResourceHealthDetails]]
        last_backup_error_detail: Optional[ErrorDetail]
        last_backup_status: Optional[Union[str, LastBackupStatus]]
        last_backup_time: Optional[datetime]
        last_recovery_point: datetime
        nodes_list: Optional[list[DistributedNodesInfo]]
        parent_name: Optional[str]
        parent_type: Optional[str]
        policy_id: str
        policy_name: str
        protected_item_data_source_id: Optional[str]
        protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]]
        protected_item_type: Literal["AzureVmWorkloadProtectedItem"]
        protection_state: Optional[Union[str, ProtectionState]]
        protection_status: Optional[str]
        resource_guard_operation_requests: list[str]
        server_name: Optional[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadProtectedItemExtendedInfo(_Model):
        newest_recovery_point_in_archive: Optional[datetime]
        oldest_recovery_point: Optional[datetime]
        oldest_recovery_point_in_archive: Optional[datetime]
        oldest_recovery_point_in_vault: Optional[datetime]
        policy_state: Optional[str]
        recovery_model: Optional[str]
        recovery_point_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                newest_recovery_point_in_archive: Optional[datetime] = ..., 
                oldest_recovery_point: Optional[datetime] = ..., 
                oldest_recovery_point_in_archive: Optional[datetime] = ..., 
                oldest_recovery_point_in_vault: Optional[datetime] = ..., 
                policy_state: Optional[str] = ..., 
                recovery_model: Optional[str] = ..., 
                recovery_point_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadProtectionPolicy(ProtectionPolicy, discriminator='AzureWorkload'):
        backup_management_type: Literal["AzureWorkload"]
        make_policy_consistent: Optional[bool]
        protected_items_count: int
        resource_guard_operation_requests: list[str]
        settings: Optional[Settings]
        sub_protection_policy: Optional[list[SubProtectionPolicy]]
        vm_workload_policy_type: Optional[Union[str, VMWorkloadPolicyType]]
        work_load_type: Optional[Union[str, WorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                make_policy_consistent: Optional[bool] = ..., 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                settings: Optional[Settings] = ..., 
                sub_protection_policy: Optional[list[SubProtectionPolicy]] = ..., 
                vm_workload_policy_type: Optional[Union[str, VMWorkloadPolicyType]] = ..., 
                work_load_type: Optional[Union[str, WorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPAseDatabaseProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SAPAseDatabase'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SAPAseDatabase"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPAseDatabaseProtectedItem(AzureVmWorkloadProtectedItem, discriminator='AzureVmWorkloadSAPAseDatabase'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        nodes_list: list[DistributedNodesInfo]
        parent_name: str
        parent_type: str
        policy_id: str
        policy_name: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: Literal["AzureVmWorkloadSAPAseDatabase"]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPAseDatabaseWorkloadItem(AzureVmWorkloadItem, discriminator='SAPAseDatabase'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        parent_name: str
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        sub_workload_item_count: int
        subinquireditemcount: int
        workload_item_type: Literal["SAPAseDatabase"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPAseSystemProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SAPAseSystem'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SAPAseSystem"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPAseSystemWorkloadItem(AzureVmWorkloadItem, discriminator='SAPAseSystem'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        parent_name: str
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        sub_workload_item_count: int
        subinquireditemcount: int
        workload_item_type: Literal["SAPAseSystem"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaDBInstance(AzureVmWorkloadProtectableItem, discriminator='SAPHanaDBInstance'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SAPHanaDBInstance"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaDBInstanceProtectedItem(AzureVmWorkloadProtectedItem, discriminator='AzureVmWorkloadSAPHanaDBInstance'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        nodes_list: list[DistributedNodesInfo]
        parent_name: str
        parent_type: str
        policy_id: str
        policy_name: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: Literal["AzureVmWorkloadSAPHanaDBInstance"]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaDatabaseProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SAPHanaDatabase'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SAPHanaDatabase"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaDatabaseProtectedItem(AzureVmWorkloadProtectedItem, discriminator='AzureVmWorkloadSAPHanaDatabase'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        nodes_list: list[DistributedNodesInfo]
        parent_name: str
        parent_type: str
        policy_id: str
        policy_name: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: Literal["AzureVmWorkloadSAPHanaDatabase"]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaDatabaseWorkloadItem(AzureVmWorkloadItem, discriminator='SAPHanaDatabase'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        parent_name: str
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        sub_workload_item_count: int
        subinquireditemcount: int
        workload_item_type: Literal["SAPHanaDatabase"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaHSRProtectableItem(AzureVmWorkloadProtectableItem, discriminator='HanaHSRContainer'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["HanaHSRContainer"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaScaleoutProtectableItem(AzureVmWorkloadProtectableItem, discriminator='HanaScaleoutContainer'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["HanaScaleoutContainer"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaSystemProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SAPHanaSystem'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SAPHanaSystem"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSAPHanaSystemWorkloadItem(AzureVmWorkloadItem, discriminator='SAPHanaSystem'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        parent_name: str
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        sub_workload_item_count: int
        subinquireditemcount: int
        workload_item_type: Literal["SAPHanaSystem"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLAvailabilityGroupProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SQLAvailabilityGroupContainer'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        nodes_list: Optional[list[DistributedNodesInfo]]
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SQLAvailabilityGroupContainer"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLDatabaseProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SQLDataBase'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SQLDataBase"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLDatabaseProtectedItem(AzureVmWorkloadProtectedItem, discriminator='AzureVmWorkloadSQLDatabase'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        nodes_list: list[DistributedNodesInfo]
        parent_name: str
        parent_protected_item: Optional[str]
        parent_type: str
        policy_id: str
        policy_name: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: Literal["AzureVmWorkloadSQLDatabase"]
        protection_level: Optional[Union[str, ProtectionLevel]]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_protected_item: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_level: Optional[Union[str, ProtectionLevel]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLDatabaseWorkloadItem(AzureVmWorkloadItem, discriminator='SQLDataBase'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        parent_name: str
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        sub_workload_item_count: int
        subinquireditemcount: int
        workload_item_type: Literal["SQLDataBase"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLInstanceProtectableItem(AzureVmWorkloadProtectableItem, discriminator='SQLInstance'):
        backup_management_type: str
        friendly_name: str
        is_auto_protectable: bool
        is_auto_protected: bool
        is_protectable: bool
        parent_name: str
        parent_unique_name: str
        prebackupvalidation: PreBackupValidation
        protectable_item_type: Literal["SQLInstance"]
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        subinquireditemcount: int
        subprotectableitemcount: int
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                is_auto_protected: Optional[bool] = ..., 
                is_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                parent_unique_name: Optional[str] = ..., 
                prebackupvalidation: Optional[PreBackupValidation] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                subprotectableitemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLInstanceProtectedItem(AzureVmWorkloadProtectedItem, discriminator='AzureVmWorkloadSQLInstance'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        child_db_names: Optional[list[str]]
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: AzureVmWorkloadProtectedItemExtendedInfo
        friendly_name: str
        instance_protection_readiness: Optional[Union[str, InstanceProtectionReadiness]]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        kpis_healths: dict[str, KPIResourceHealthDetails]
        last_backup_error_detail: ErrorDetail
        last_backup_status: Union[str, LastBackupStatus]
        last_backup_time: datetime
        last_recovery_point: datetime
        nodes_list: list[DistributedNodesInfo]
        parent_name: str
        parent_type: str
        policy_id: str
        policy_name: str
        protected_item_data_source_id: str
        protected_item_health_status: Union[str, ProtectedItemHealthStatus]
        protected_item_type: Literal["AzureVmWorkloadSQLInstance"]
        protection_state: Union[str, ProtectionState]
        protection_status: str
        resource_guard_operation_requests: list[str]
        server_name: str
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                child_db_names: Optional[list[str]] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[AzureVmWorkloadProtectedItemExtendedInfo] = ..., 
                instance_protection_readiness: Optional[Union[str, InstanceProtectionReadiness]] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                kpis_healths: Optional[dict[str, KPIResourceHealthDetails]] = ..., 
                last_backup_error_detail: Optional[ErrorDetail] = ..., 
                last_backup_status: Optional[Union[str, LastBackupStatus]] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ..., 
                parent_name: Optional[str] = ..., 
                parent_type: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_data_source_id: Optional[str] = ..., 
                protected_item_health_status: Optional[Union[str, ProtectedItemHealthStatus]] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                server_name: Optional[str] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureVmWorkloadSQLInstanceWorkloadItem(AzureVmWorkloadItem, discriminator='SQLInstance'):
        backup_management_type: str
        data_directory_paths: Optional[list[SQLDataDirectory]]
        friendly_name: str
        is_auto_protectable: bool
        parent_name: str
        protection_state: Union[str, ProtectionStatus]
        server_name: str
        sub_workload_item_count: int
        subinquireditemcount: int
        workload_item_type: Literal["SQLInstance"]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                data_directory_paths: Optional[list[SQLDataDirectory]] = ..., 
                friendly_name: Optional[str] = ..., 
                is_auto_protectable: Optional[bool] = ..., 
                parent_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                server_name: Optional[str] = ..., 
                sub_workload_item_count: Optional[int] = ..., 
                subinquireditemcount: Optional[int] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadAutoProtectionIntent(AzureRecoveryServiceVaultProtectionIntent, discriminator='AzureWorkloadAutoProtectionIntent'):
        backup_management_type: Union[str, BackupManagementType]
        item_id: str
        policy_id: str
        protection_intent_item_type: Literal[ProtectionIntentItemType.AZURE_WORKLOAD_AUTO_PROTECTION_INTENT]
        protection_state: Union[str, ProtectionStatus]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                item_id: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadBackupRequest(BackupRequest, discriminator='AzureWorkloadBackupRequest'):
        backup_type: Optional[Union[str, BackupType]]
        enable_compression: Optional[bool]
        object_type: Literal["AzureWorkloadBackupRequest"]
        recovery_point_expiry_time_in_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                backup_type: Optional[Union[str, BackupType]] = ..., 
                enable_compression: Optional[bool] = ..., 
                recovery_point_expiry_time_in_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadContainer(ProtectionContainer, discriminator='AzureWorkloadContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.AZURE_WORKLOAD_CONTAINER]
        extended_info: Optional[AzureWorkloadContainerExtendedInfo]
        friendly_name: str
        health_status: str
        last_updated_time: Optional[datetime]
        operation_type: Optional[Union[str, OperationType]]
        protectable_object_type: str
        registration_status: str
        source_resource_id: Optional[str]
        workload_type: Optional[Union[str, WorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                extended_info: Optional[AzureWorkloadContainerExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                last_updated_time: Optional[datetime] = ..., 
                operation_type: Optional[Union[str, OperationType]] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                workload_type: Optional[Union[str, WorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadContainerAutoProtectionIntent(ProtectionIntent, discriminator='AzureWorkloadContainerAutoProtectionIntent'):
        backup_management_type: Union[str, BackupManagementType]
        item_id: str
        policy_id: str
        protection_intent_item_type: Literal[ProtectionIntentItemType.AZURE_WORKLOAD_CONTAINER_AUTO_PROTECTION_INTENT]
        protection_state: Union[str, ProtectionStatus]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                item_id: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadContainerExtendedInfo(_Model):
        host_server_name: Optional[str]
        inquiry_info: Optional[InquiryInfo]
        nodes_list: Optional[list[DistributedNodesInfo]]

        @overload
        def __init__(
                self, 
                *, 
                host_server_name: Optional[str] = ..., 
                inquiry_info: Optional[InquiryInfo] = ..., 
                nodes_list: Optional[list[DistributedNodesInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadErrorInfo(_Model):
        additional_details: Optional[str]
        error_code: Optional[int]
        error_string: Optional[str]
        error_title: Optional[str]
        recommendations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[str] = ..., 
                error_code: Optional[int] = ..., 
                error_string: Optional[str] = ..., 
                error_title: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadJob(Job, discriminator='AzureWorkloadJob'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[AzureWorkloadErrorInfo]]
        extended_info: Optional[AzureWorkloadJobExtendedInfo]
        job_type: Literal["AzureWorkloadJob"]
        operation: str
        start_time: datetime
        status: str
        workload_type: Optional[str]

        @overload
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
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadJobExtendedInfo(_Model):
        dynamic_error_message: Optional[str]
        property_bag: Optional[dict[str, str]]
        tasks_list: Optional[list[AzureWorkloadJobTaskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[AzureWorkloadJobTaskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadJobTaskDetails(_Model):
        status: Optional[str]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadPointInTimeRecoveryPoint(AzureWorkloadRecoveryPoint, discriminator='AzureWorkloadPointInTimeRecoveryPoint'):
        object_type: Literal["AzureWorkloadPointInTimeRecoveryPoint"]
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_properties: RecoveryPointProperties
        recovery_point_tier_details: list[RecoveryPointTierInformationV2]
        recovery_point_time_in_utc: datetime
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        time_ranges: Optional[list[PointInTimeRange]]
        type: Union[str, RestorePointType]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time_in_utc: Optional[datetime] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                time_ranges: Optional[list[PointInTimeRange]] = ..., 
                type: Optional[Union[str, RestorePointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadPointInTimeRestoreRequest(AzureWorkloadRestoreRequest, discriminator='AzureWorkloadPointInTimeRestoreRequest'):
        object_type: Literal["AzureWorkloadPointInTimeRestoreRequest"]
        point_in_time: Optional[datetime]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadRecoveryPoint(RecoveryPoint, discriminator='AzureWorkloadRecoveryPoint'):
        object_type: Literal["AzureWorkloadRecoveryPoint"]
        recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]]
        recovery_point_properties: Optional[RecoveryPointProperties]
        recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]]
        recovery_point_time_in_utc: Optional[datetime]
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        type: Optional[Union[str, RestorePointType]]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time_in_utc: Optional[datetime] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                type: Optional[Union[str, RestorePointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadRestoreRequest(RestoreRequest, discriminator='AzureWorkloadRestoreRequest'):
        object_type: Literal["AzureWorkloadRestoreRequest"]
        property_bag: Optional[dict[str, str]]
        recovery_mode: Optional[Union[str, RecoveryMode]]
        recovery_type: Optional[Union[str, RecoveryType]]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: Optional[SnapshotRestoreParameters]
        source_resource_id: Optional[str]
        target_info: Optional[TargetRestoreInfo]
        target_resource_group_name: Optional[str]
        target_virtual_machine_id: Optional[str]
        user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails]

        @overload
        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPAsePointInTimeRecoveryPoint(AzureWorkloadPointInTimeRecoveryPoint, discriminator='AzureWorkloadSAPAsePointInTimeRecoveryPoint'):
        object_type: Literal["AzureWorkloadSAPAsePointInTimeRecoveryPoint"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPAsePointInTimeRestoreRequest(AzureWorkloadSAPAseRestoreRequest, discriminator='AzureWorkloadSAPAsePointInTimeRestoreRequest'):
        object_type: Literal["AzureWorkloadSAPAsePointInTimeRestoreRequest"]
        point_in_time: Optional[datetime]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPAseRecoveryPoint(AzureWorkloadRecoveryPoint, discriminator='AzureWorkloadSAPAseRecoveryPoint'):
        object_type: Literal["AzureWorkloadSAPAseRecoveryPoint"]
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_properties: RecoveryPointProperties
        recovery_point_tier_details: list[RecoveryPointTierInformationV2]
        recovery_point_time_in_utc: datetime
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        type: Union[str, RestorePointType]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time_in_utc: Optional[datetime] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                type: Optional[Union[str, RestorePointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPAseRestoreRequest(AzureWorkloadRestoreRequest, discriminator='AzureWorkloadSAPAseRestoreRequest'):
        object_type: Literal["AzureWorkloadSAPAseRestoreRequest"]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPHanaPointInTimeRecoveryPoint(AzureWorkloadPointInTimeRecoveryPoint, discriminator='AzureWorkloadSAPHanaPointInTimeRecoveryPoint'):
        object_type: Literal["AzureWorkloadSAPHanaPointInTimeRecoveryPoint"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPHanaPointInTimeRestoreRequest(AzureWorkloadSAPHanaRestoreRequest, discriminator='AzureWorkloadSAPHanaPointInTimeRestoreRequest'):
        object_type: Literal["AzureWorkloadSAPHanaPointInTimeRestoreRequest"]
        point_in_time: Optional[datetime]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPHanaPointInTimeRestoreWithRehydrateRequest(AzureWorkloadSAPHanaPointInTimeRestoreRequest, discriminator='AzureWorkloadSAPHanaPointInTimeRestoreWithRehydrateRequest'):
        object_type: Literal["AzureWorkloadSAPHanaPointInTimeRestoreWithRehydrateRequest"]
        recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPHanaRecoveryPoint(AzureWorkloadRecoveryPoint, discriminator='AzureWorkloadSAPHanaRecoveryPoint'):
        object_type: Literal["AzureWorkloadSAPHanaRecoveryPoint"]
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_properties: RecoveryPointProperties
        recovery_point_tier_details: list[RecoveryPointTierInformationV2]
        recovery_point_time_in_utc: datetime
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        type: Union[str, RestorePointType]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time_in_utc: Optional[datetime] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                type: Optional[Union[str, RestorePointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPHanaRestoreRequest(AzureWorkloadRestoreRequest, discriminator='AzureWorkloadSAPHanaRestoreRequest'):
        object_type: Literal["AzureWorkloadSAPHanaRestoreRequest"]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSAPHanaRestoreWithRehydrateRequest(AzureWorkloadSAPHanaRestoreRequest, discriminator='AzureWorkloadSAPHanaRestoreWithRehydrateRequest'):
        object_type: Literal["AzureWorkloadSAPHanaRestoreWithRehydrateRequest"]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLAutoProtectionIntent(AzureWorkloadAutoProtectionIntent, discriminator='AzureWorkloadSQLAutoProtectionIntent'):
        protection_intent_item_type: Literal[ProtectionIntentItemType.AZURE_WORKLOAD_SQL_AUTO_PROTECTION_INTENT]
        workload_item_type: Optional[Union[str, WorkloadItemType]]

        @overload
        def __init__(
                self, 
                *, 
                workload_item_type: Optional[Union[str, WorkloadItemType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLPointInTimeRecoveryPoint(AzureWorkloadSQLRecoveryPoint, discriminator='AzureWorkloadSQLPointInTimeRecoveryPoint'):
        extended_info: AzureWorkloadSQLRecoveryPointExtendedInfo
        object_type: Literal["AzureWorkloadSQLPointInTimeRecoveryPoint"]
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_properties: RecoveryPointProperties
        recovery_point_tier_details: list[RecoveryPointTierInformationV2]
        recovery_point_time_in_utc: datetime
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        time_ranges: Optional[list[PointInTimeRange]]
        type: Union[str, RestorePointType]

        @overload
        def __init__(
                self, 
                *, 
                extended_info: Optional[AzureWorkloadSQLRecoveryPointExtendedInfo] = ..., 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time_in_utc: Optional[datetime] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                time_ranges: Optional[list[PointInTimeRange]] = ..., 
                type: Optional[Union[str, RestorePointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLPointInTimeRestoreRequest(AzureWorkloadSQLRestoreRequest, discriminator='AzureWorkloadSQLPointInTimeRestoreRequest'):
        alternate_directory_paths: list[SQLDataDirectoryMapping]
        is_non_recoverable: bool
        object_type: Literal["AzureWorkloadSQLPointInTimeRestoreRequest"]
        point_in_time: Optional[datetime]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        should_use_alternate_target_location: bool
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                alternate_directory_paths: Optional[list[SQLDataDirectoryMapping]] = ..., 
                is_non_recoverable: Optional[bool] = ..., 
                point_in_time: Optional[datetime] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                should_use_alternate_target_location: Optional[bool] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLPointInTimeRestoreWithRehydrateRequest(AzureWorkloadSQLPointInTimeRestoreRequest, discriminator='AzureWorkloadSQLPointInTimeRestoreWithRehydrateRequest'):
        object_type: Literal["AzureWorkloadSQLPointInTimeRestoreWithRehydrateRequest"]
        recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLRecoveryPoint(AzureWorkloadRecoveryPoint, discriminator='AzureWorkloadSQLRecoveryPoint'):
        extended_info: Optional[AzureWorkloadSQLRecoveryPointExtendedInfo]
        object_type: Literal["AzureWorkloadSQLRecoveryPoint"]
        recovery_point_move_readiness_info: dict[str, RecoveryPointMoveReadinessInfo]
        recovery_point_properties: RecoveryPointProperties
        recovery_point_tier_details: list[RecoveryPointTierInformationV2]
        recovery_point_time_in_utc: datetime
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        type: Union[str, RestorePointType]

        @overload
        def __init__(
                self, 
                *, 
                extended_info: Optional[AzureWorkloadSQLRecoveryPointExtendedInfo] = ..., 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time_in_utc: Optional[datetime] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                type: Optional[Union[str, RestorePointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLRecoveryPointExtendedInfo(_Model):
        data_directory_paths: Optional[list[SQLDataDirectory]]
        data_directory_time_in_utc: Optional[datetime]
        included_databases: Optional[list[DatabaseInRP]]

        @overload
        def __init__(
                self, 
                *, 
                data_directory_paths: Optional[list[SQLDataDirectory]] = ..., 
                data_directory_time_in_utc: Optional[datetime] = ..., 
                included_databases: Optional[list[DatabaseInRP]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLRestoreRequest(AzureWorkloadRestoreRequest, discriminator='AzureWorkloadSQLRestoreRequest'):
        alternate_directory_paths: Optional[list[SQLDataDirectoryMapping]]
        is_non_recoverable: Optional[bool]
        object_type: Literal["AzureWorkloadSQLRestoreRequest"]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        should_use_alternate_target_location: Optional[bool]
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                alternate_directory_paths: Optional[list[SQLDataDirectoryMapping]] = ..., 
                is_non_recoverable: Optional[bool] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                should_use_alternate_target_location: Optional[bool] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.AzureWorkloadSQLRestoreWithRehydrateRequest(AzureWorkloadSQLRestoreRequest, discriminator='AzureWorkloadSQLRestoreWithRehydrateRequest'):
        alternate_directory_paths: list[SQLDataDirectoryMapping]
        is_non_recoverable: bool
        object_type: Literal["AzureWorkloadSQLRestoreWithRehydrateRequest"]
        property_bag: dict[str, str]
        recovery_mode: Union[str, RecoveryMode]
        recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo]
        recovery_type: Union[str, RecoveryType]
        resource_guard_operation_requests: list[str]
        should_use_alternate_target_location: bool
        snapshot_restore_parameters: SnapshotRestoreParameters
        source_resource_id: str
        target_info: TargetRestoreInfo
        target_resource_group_name: str
        target_virtual_machine_id: str
        user_assigned_managed_identity_details: UserAssignedManagedIdentityDetails

        @overload
        def __init__(
                self, 
                *, 
                alternate_directory_paths: Optional[list[SQLDataDirectoryMapping]] = ..., 
                is_non_recoverable: Optional[bool] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                should_use_alternate_target_location: Optional[bool] = ..., 
                snapshot_restore_parameters: Optional[SnapshotRestoreParameters] = ..., 
                source_resource_id: Optional[str] = ..., 
                target_info: Optional[TargetRestoreInfo] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BEKDetails(_Model):
        secret_data: Optional[str]
        secret_url: Optional[str]
        secret_vault_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                secret_data: Optional[str] = ..., 
                secret_url: Optional[str] = ..., 
                secret_vault_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupEngineBase(_Model):
        azure_backup_agent_version: Optional[str]
        backup_engine_id: Optional[str]
        backup_engine_state: Optional[str]
        backup_engine_type: str
        backup_management_type: Optional[Union[str, BackupManagementType]]
        can_re_register: Optional[bool]
        dpm_version: Optional[str]
        extended_info: Optional[BackupEngineExtendedInfo]
        friendly_name: Optional[str]
        health_status: Optional[str]
        is_azure_backup_agent_upgrade_available: Optional[bool]
        is_dpm_upgrade_available: Optional[bool]
        registration_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_backup_agent_version: Optional[str] = ..., 
                backup_engine_id: Optional[str] = ..., 
                backup_engine_state: Optional[str] = ..., 
                backup_engine_type: str, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                can_re_register: Optional[bool] = ..., 
                dpm_version: Optional[str] = ..., 
                extended_info: Optional[BackupEngineExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                is_azure_backup_agent_upgrade_available: Optional[bool] = ..., 
                is_dpm_upgrade_available: Optional[bool] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupEngineBaseResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BackupEngineBase]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupEngineBase] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupEngineExtendedInfo(_Model):
        available_disk_space: Optional[float]
        azure_protected_instances: Optional[int]
        database_name: Optional[str]
        disk_count: Optional[int]
        protected_items_count: Optional[int]
        protected_servers_count: Optional[int]
        refreshed_at: Optional[datetime]
        used_disk_space: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                available_disk_space: Optional[float] = ..., 
                azure_protected_instances: Optional[int] = ..., 
                database_name: Optional[str] = ..., 
                disk_count: Optional[int] = ..., 
                protected_items_count: Optional[int] = ..., 
                protected_servers_count: Optional[int] = ..., 
                refreshed_at: Optional[datetime] = ..., 
                used_disk_space: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupEngineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP_SERVER_ENGINE = "AzureBackupServerEngine"
        DPM_BACKUP_ENGINE = "DpmBackupEngine"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.BackupItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE_SHARE = "AzureFileShare"
        AZURE_SQL_DB = "AzureSqlDb"
        CLIENT = "Client"
        EXCHANGE = "Exchange"
        FILE_FOLDER = "FileFolder"
        GENERIC_DATA_SOURCE = "GenericDataSource"
        INVALID = "Invalid"
        SAP_ASE_DATABASE = "SAPAseDatabase"
        SAP_HANA_DATABASE = "SAPHanaDatabase"
        SAP_HANA_DB_INSTANCE = "SAPHanaDBInstance"
        SHAREPOINT = "Sharepoint"
        SQLDB = "SQLDB"
        SQL_DATA_BASE = "SQLDataBase"
        SYSTEM_STATE = "SystemState"
        VM = "VM"
        V_MWARE_VM = "VMwareVM"


    class azure.mgmt.recoveryservicesbackup.models.BackupManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP_SERVER = "AzureBackupServer"
        AZURE_IAAS_VM = "AzureIaasVM"
        AZURE_SQL = "AzureSql"
        AZURE_STORAGE = "AzureStorage"
        AZURE_WORKLOAD = "AzureWorkload"
        DEFAULT_BACKUP = "DefaultBackup"
        DPM = "DPM"
        INVALID = "Invalid"
        MAB = "MAB"


    class azure.mgmt.recoveryservicesbackup.models.BackupManagementUsage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[NameInfo]
        next_reset_time: Optional[datetime]
        quota_period: Optional[str]
        unit: Optional[Union[str, UsagesUnit]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[NameInfo] = ..., 
                next_reset_time: Optional[datetime] = ..., 
                quota_period: Optional[str] = ..., 
                unit: Optional[Union[str, UsagesUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupRequest(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupRequestResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BackupRequest]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupRequest] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceConfig(_Model):
        cross_region_restore_flag: Optional[bool]
        dedup_state: Optional[Union[str, DedupState]]
        storage_model_type: Optional[Union[str, StorageType]]
        storage_type: Optional[Union[str, StorageType]]
        storage_type_state: Optional[Union[str, StorageTypeState]]
        xcool_state: Optional[Union[str, XcoolState]]

        @overload
        def __init__(
                self, 
                *, 
                cross_region_restore_flag: Optional[bool] = ..., 
                dedup_state: Optional[Union[str, DedupState]] = ..., 
                storage_model_type: Optional[Union[str, StorageType]] = ..., 
                storage_type: Optional[Union[str, StorageType]] = ..., 
                storage_type_state: Optional[Union[str, StorageTypeState]] = ..., 
                xcool_state: Optional[Union[str, XcoolState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceConfigResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BackupResourceConfig]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupResourceConfig] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceEncryptionConfig(_Model):
        encryption_at_rest_type: Optional[Union[str, EncryptionAtRestType]]
        infrastructure_encryption_state: Optional[Union[str, InfrastructureEncryptionState]]
        key_uri: Optional[str]
        last_update_status: Optional[Union[str, LastUpdateStatus]]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_at_rest_type: Optional[Union[str, EncryptionAtRestType]] = ..., 
                infrastructure_encryption_state: Optional[Union[str, InfrastructureEncryptionState]] = ..., 
                key_uri: Optional[str] = ..., 
                last_update_status: Optional[Union[str, LastUpdateStatus]] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceEncryptionConfigExtended(BackupResourceEncryptionConfig):
        encryption_at_rest_type: Union[str, EncryptionAtRestType]
        infrastructure_encryption_state: Union[str, InfrastructureEncryptionState]
        key_uri: str
        last_update_status: Union[str, LastUpdateStatus]
        subscription_id: str
        use_system_assigned_identity: Optional[bool]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_at_rest_type: Optional[Union[str, EncryptionAtRestType]] = ..., 
                infrastructure_encryption_state: Optional[Union[str, InfrastructureEncryptionState]] = ..., 
                key_uri: Optional[str] = ..., 
                last_update_status: Optional[Union[str, LastUpdateStatus]] = ..., 
                subscription_id: Optional[str] = ..., 
                use_system_assigned_identity: Optional[bool] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceEncryptionConfigExtendedResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BackupResourceEncryptionConfigExtended]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupResourceEncryptionConfigExtended] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceEncryptionConfigResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BackupResourceEncryptionConfig]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupResourceEncryptionConfig] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceVaultConfig(_Model):
        enhanced_security_state: Optional[Union[str, EnhancedSecurityState]]
        is_soft_delete_feature_state_editable: Optional[bool]
        resource_guard_operation_requests: Optional[list[str]]
        soft_delete_feature_state: Optional[Union[str, SoftDeleteFeatureState]]
        soft_delete_retention_period_in_days: Optional[int]
        storage_model_type: Optional[Union[str, StorageType]]
        storage_type: Optional[Union[str, StorageType]]
        storage_type_state: Optional[Union[str, StorageTypeState]]

        @overload
        def __init__(
                self, 
                *, 
                enhanced_security_state: Optional[Union[str, EnhancedSecurityState]] = ..., 
                is_soft_delete_feature_state_editable: Optional[bool] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_feature_state: Optional[Union[str, SoftDeleteFeatureState]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                storage_model_type: Optional[Union[str, StorageType]] = ..., 
                storage_type: Optional[Union[str, StorageType]] = ..., 
                storage_type_state: Optional[Union[str, StorageTypeState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupResourceVaultConfigResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BackupResourceVaultConfig]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BackupResourceVaultConfig] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupStatusRequest(_Model):
        po_logical_name: Optional[str]
        resource_id: Optional[str]
        resource_type: Optional[Union[str, DataSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                po_logical_name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_type: Optional[Union[str, DataSourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupStatusResponse(_Model):
        acquire_storage_account_lock: Optional[Union[str, AcquireStorageAccountLock]]
        container_name: Optional[str]
        error_code: Optional[str]
        error_message: Optional[str]
        fabric_name: Optional[Union[str, FabricName]]
        policy_name: Optional[str]
        protected_item_name: Optional[str]
        protected_items_count: Optional[int]
        protection_status: Optional[Union[str, ProtectionStatus]]
        registration_status: Optional[str]
        vault_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                acquire_storage_account_lock: Optional[Union[str, AcquireStorageAccountLock]] = ..., 
                container_name: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                fabric_name: Optional[Union[str, FabricName]] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_name: Optional[str] = ..., 
                protected_items_count: Optional[int] = ..., 
                protection_status: Optional[Union[str, ProtectionStatus]] = ..., 
                registration_status: Optional[str] = ..., 
                vault_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.BackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY_ONLY_FULL = "CopyOnlyFull"
        DIFFERENTIAL = "Differential"
        FULL = "Full"
        INCREMENTAL = "Incremental"
        INVALID = "Invalid"
        LOG = "Log"
        SNAPSHOT_COPY_ONLY_FULL = "SnapshotCopyOnlyFull"
        SNAPSHOT_FULL = "SnapshotFull"


    class azure.mgmt.recoveryservicesbackup.models.ClientDiscoveryDisplay(_Model):
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


    class azure.mgmt.recoveryservicesbackup.models.ClientDiscoveryForLogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ClientDiscoveryForProperties(_Model):
        service_specification: Optional[ClientDiscoveryForServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ClientDiscoveryForServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ClientDiscoveryForServiceSpecification(_Model):
        log_specifications: Optional[list[ClientDiscoveryForLogSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[ClientDiscoveryForLogSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ClientDiscoveryValueForSingleApi(_Model):
        display: Optional[ClientDiscoveryDisplay]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[ClientDiscoveryForProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[ClientDiscoveryDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[ClientDiscoveryForProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ClientScriptForConnect(_Model):
        os_type: Optional[str]
        script_content: Optional[str]
        script_extension: Optional[str]
        script_name_suffix: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_type: Optional[str] = ..., 
                script_content: Optional[str] = ..., 
                script_extension: Optional[str] = ..., 
                script_name_suffix: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ContainerIdentityInfo(_Model):
        aad_tenant_id: Optional[str]
        audience: Optional[str]
        service_principal_client_id: Optional[str]
        unique_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_tenant_id: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                service_principal_client_id: Optional[str] = ..., 
                unique_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.CopyOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_COPY = "CreateCopy"
        FAIL_ON_CONFLICT = "FailOnConflict"
        INVALID = "Invalid"
        OVERWRITE = "Overwrite"
        SKIP = "Skip"


    class azure.mgmt.recoveryservicesbackup.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        INVALID = "Invalid"
        RECOVER = "Recover"


    class azure.mgmt.recoveryservicesbackup.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.recoveryservicesbackup.models.DPMContainerExtendedInfo(_Model):
        last_refreshed_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                last_refreshed_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DPMProtectedItem(ProtectedItem, discriminator='DPMProtectedItem'):
        backup_engine_name: Optional[str]
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: Optional[DPMProtectedItemExtendedInfo]
        friendly_name: Optional[str]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        protected_item_type: Literal["DPMProtectedItem"]
        protection_state: Optional[Union[str, ProtectedItemState]]
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_engine_name: Optional[str] = ..., 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[DPMProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectedItemState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DPMProtectedItemExtendedInfo(_Model):
        disk_storage_used_in_bytes: Optional[str]
        is_collocated: Optional[bool]
        is_present_on_cloud: Optional[bool]
        last_backup_status: Optional[str]
        last_refreshed_at: Optional[datetime]
        oldest_recovery_point: Optional[datetime]
        on_premise_latest_recovery_point: Optional[datetime]
        on_premise_oldest_recovery_point: Optional[datetime]
        on_premise_recovery_point_count: Optional[int]
        protectable_object_load_path: Optional[dict[str, str]]
        protected: Optional[bool]
        protection_group_name: Optional[str]
        recovery_point_count: Optional[int]
        total_disk_storage_size_in_bytes: Optional[str]

        @overload
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
                total_disk_storage_size_in_bytes: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DailyRetentionFormat(_Model):
        days_of_the_month: Optional[list[Day]]

        @overload
        def __init__(
                self, 
                *, 
                days_of_the_month: Optional[list[Day]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DailyRetentionSchedule(_Model):
        retention_duration: Optional[RetentionDuration]
        retention_times: Optional[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                retention_duration: Optional[RetentionDuration] = ..., 
                retention_times: Optional[list[datetime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DailySchedule(_Model):
        schedule_run_times: Optional[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                schedule_run_times: Optional[list[datetime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DataMoveLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER = "Container"
        INVALID = "Invalid"
        VAULT = "Vault"


    class azure.mgmt.recoveryservicesbackup.models.DataSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE_SHARE = "AzureFileShare"
        AZURE_SQL_DB = "AzureSqlDb"
        CLIENT = "Client"
        EXCHANGE = "Exchange"
        FILE_FOLDER = "FileFolder"
        GENERIC_DATA_SOURCE = "GenericDataSource"
        INVALID = "Invalid"
        SAP_ASE_DATABASE = "SAPAseDatabase"
        SAP_HANA_DATABASE = "SAPHanaDatabase"
        SAP_HANA_DB_INSTANCE = "SAPHanaDBInstance"
        SHAREPOINT = "Sharepoint"
        SQLDB = "SQLDB"
        SQL_DATA_BASE = "SQLDataBase"
        SYSTEM_STATE = "SystemState"
        VM = "VM"
        V_MWARE_VM = "VMwareVM"


    class azure.mgmt.recoveryservicesbackup.models.DatabaseInRP(_Model):
        datasource_id: Optional[str]
        datasource_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                datasource_id: Optional[str] = ..., 
                datasource_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.Day(_Model):
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


    class azure.mgmt.recoveryservicesbackup.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.recoveryservicesbackup.models.DedupState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.DiskExclusionProperties(_Model):
        disk_lun_list: Optional[list[int]]
        is_inclusion_list: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disk_lun_list: Optional[list[int]] = ..., 
                is_inclusion_list: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DiskInformation(_Model):
        lun: Optional[int]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                lun: Optional[int] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DistributedNodesInfo(_Model):
        error_detail: Optional[ErrorDetail]
        node_name: Optional[str]
        source_resource_id: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_detail: Optional[ErrorDetail] = ..., 
                node_name: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DpmBackupEngine(BackupEngineBase, discriminator='DpmBackupEngine'):
        azure_backup_agent_version: str
        backup_engine_id: str
        backup_engine_state: str
        backup_engine_type: Literal[BackupEngineType.DPM_BACKUP_ENGINE]
        backup_management_type: Union[str, BackupManagementType]
        can_re_register: bool
        dpm_version: str
        extended_info: BackupEngineExtendedInfo
        friendly_name: str
        health_status: str
        is_azure_backup_agent_upgrade_available: bool
        is_dpm_upgrade_available: bool
        registration_status: str

        @overload
        def __init__(
                self, 
                *, 
                azure_backup_agent_version: Optional[str] = ..., 
                backup_engine_id: Optional[str] = ..., 
                backup_engine_state: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                can_re_register: Optional[bool] = ..., 
                dpm_version: Optional[str] = ..., 
                extended_info: Optional[BackupEngineExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                is_azure_backup_agent_upgrade_available: Optional[bool] = ..., 
                is_dpm_upgrade_available: Optional[bool] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DpmContainer(ProtectionContainer, discriminator='DPMContainer'):
        backup_management_type: Union[str, BackupManagementType]
        can_re_register: Optional[bool]
        container_id: Optional[str]
        container_type: Literal[ProtectableContainerType.DPM_CONTAINER]
        dpm_agent_version: Optional[str]
        dpm_servers: Optional[list[str]]
        extended_info: Optional[DPMContainerExtendedInfo]
        friendly_name: str
        health_status: str
        protectable_object_type: str
        protected_item_count: Optional[int]
        protection_status: Optional[str]
        registration_status: str
        upgrade_available: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                can_re_register: Optional[bool] = ..., 
                container_id: Optional[str] = ..., 
                dpm_agent_version: Optional[str] = ..., 
                dpm_servers: Optional[list[str]] = ..., 
                extended_info: Optional[DPMContainerExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                protected_item_count: Optional[int] = ..., 
                protection_status: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                upgrade_available: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DpmErrorInfo(_Model):
        error_string: Optional[str]
        recommendations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                error_string: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DpmJob(Job, discriminator='DpmJob'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        container_name: Optional[str]
        container_type: Optional[str]
        dpm_server_name: Optional[str]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[DpmErrorInfo]]
        extended_info: Optional[DpmJobExtendedInfo]
        job_type: Literal["DpmJob"]
        operation: str
        start_time: datetime
        status: str
        workload_type: Optional[str]

        @overload
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
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DpmJobExtendedInfo(_Model):
        dynamic_error_message: Optional[str]
        property_bag: Optional[dict[str, str]]
        tasks_list: Optional[list[DpmJobTaskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[DpmJobTaskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.DpmJobTaskDetails(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        start_time: Optional[datetime]
        status: Optional[str]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.EncryptionAtRestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        INVALID = "Invalid"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.recoveryservicesbackup.models.EncryptionDetails(_Model):
        encryption_enabled: Optional[bool]
        kek_url: Optional[str]
        kek_vault_id: Optional[str]
        secret_key_url: Optional[str]
        secret_key_vault_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_enabled: Optional[bool] = ..., 
                kek_url: Optional[str] = ..., 
                kek_vault_id: Optional[str] = ..., 
                secret_key_url: Optional[str] = ..., 
                secret_key_vault_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.EnhancedSecurityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.recoveryservicesbackup.models.ErrorDetail(_Model):
        code: Optional[str]
        message: Optional[str]
        recommendations: Optional[list[str]]


    class azure.mgmt.recoveryservicesbackup.models.ErrorResponse(_Model):
        error: Optional[ArmErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ArmErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ExportJobsOperationResultInfo(OperationResultInfoBase, discriminator='ExportJobsOperationResultInfo'):
        blob_sas_key: Optional[str]
        blob_url: Optional[str]
        excel_file_blob_sas_key: Optional[str]
        excel_file_blob_url: Optional[str]
        object_type: Literal["ExportJobsOperationResultInfo"]

        @overload
        def __init__(
                self, 
                *, 
                blob_sas_key: Optional[str] = ..., 
                blob_url: Optional[str] = ..., 
                excel_file_blob_sas_key: Optional[str] = ..., 
                excel_file_blob_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ExtendedLocation(_Model):
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


    class azure.mgmt.recoveryservicesbackup.models.ExtendedProperties(_Model):
        disk_exclusion_properties: Optional[DiskExclusionProperties]
        linux_vm_application_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_exclusion_properties: Optional[DiskExclusionProperties] = ..., 
                linux_vm_application_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.FabricName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.FeatureSupportRequest(_Model):
        feature_type: str

        @overload
        def __init__(
                self, 
                *, 
                feature_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.FetchTieringCostInfoForRehydrationRequest(FetchTieringCostInfoRequest, discriminator='FetchTieringCostInfoForRehydrationRequest'):
        container_name: str
        object_type: Literal["FetchTieringCostInfoForRehydrationRequest"]
        protected_item_name: str
        recovery_point_id: str
        rehydration_priority: Union[str, RehydrationPriority]
        source_tier_type: Union[str, RecoveryPointTierType]
        target_tier_type: Union[str, RecoveryPointTierType]

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                rehydration_priority: Union[str, RehydrationPriority], 
                source_tier_type: Union[str, RecoveryPointTierType], 
                target_tier_type: Union[str, RecoveryPointTierType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.FetchTieringCostInfoRequest(_Model):
        object_type: str
        source_tier_type: Union[str, RecoveryPointTierType]
        target_tier_type: Union[str, RecoveryPointTierType]

        @overload
        def __init__(
                self, 
                *, 
                object_type: str, 
                source_tier_type: Union[str, RecoveryPointTierType], 
                target_tier_type: Union[str, RecoveryPointTierType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.FetchTieringCostSavingsInfoForPolicyRequest(FetchTieringCostInfoRequest, discriminator='FetchTieringCostSavingsInfoForPolicyRequest'):
        object_type: Literal["FetchTieringCostSavingsInfoForPolicyRequest"]
        policy_name: str
        source_tier_type: Union[str, RecoveryPointTierType]
        target_tier_type: Union[str, RecoveryPointTierType]

        @overload
        def __init__(
                self, 
                *, 
                policy_name: str, 
                source_tier_type: Union[str, RecoveryPointTierType], 
                target_tier_type: Union[str, RecoveryPointTierType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.FetchTieringCostSavingsInfoForProtectedItemRequest(FetchTieringCostInfoRequest, discriminator='FetchTieringCostSavingsInfoForProtectedItemRequest'):
        container_name: str
        object_type: Literal["FetchTieringCostSavingsInfoForProtectedItemRequest"]
        protected_item_name: str
        source_tier_type: Union[str, RecoveryPointTierType]
        target_tier_type: Union[str, RecoveryPointTierType]

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                protected_item_name: str, 
                source_tier_type: Union[str, RecoveryPointTierType], 
                target_tier_type: Union[str, RecoveryPointTierType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.FetchTieringCostSavingsInfoForVaultRequest(FetchTieringCostInfoRequest, discriminator='FetchTieringCostSavingsInfoForVaultRequest'):
        object_type: Literal["FetchTieringCostSavingsInfoForVaultRequest"]
        source_tier_type: Union[str, RecoveryPointTierType]
        target_tier_type: Union[str, RecoveryPointTierType]

        @overload
        def __init__(
                self, 
                *, 
                source_tier_type: Union[str, RecoveryPointTierType], 
                target_tier_type: Union[str, RecoveryPointTierType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.GenericContainer(ProtectionContainer, discriminator='GenericContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.GENERIC_CONTAINER]
        extended_information: Optional[GenericContainerExtendedInfo]
        fabric_name: Optional[str]
        friendly_name: str
        health_status: str
        protectable_object_type: str
        registration_status: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                extended_information: Optional[GenericContainerExtendedInfo] = ..., 
                fabric_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.GenericContainerExtendedInfo(_Model):
        container_identity_info: Optional[ContainerIdentityInfo]
        raw_cert_data: Optional[str]
        service_endpoints: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                container_identity_info: Optional[ContainerIdentityInfo] = ..., 
                raw_cert_data: Optional[str] = ..., 
                service_endpoints: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.GenericProtectedItem(ProtectedItem, discriminator='GenericProtectedItem'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        fabric_name: Optional[str]
        friendly_name: Optional[str]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        policy_state: Optional[str]
        protected_item_id: Optional[int]
        protected_item_type: Literal["GenericProtectedItem"]
        protection_state: Optional[Union[str, ProtectionState]]
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_associations: Optional[dict[str, str]]
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                policy_state: Optional[str] = ..., 
                protected_item_id: Optional[int] = ..., 
                protection_state: Optional[Union[str, ProtectionState]] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_associations: Optional[dict[str, str]] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.GenericProtectionPolicy(ProtectionPolicy, discriminator='GenericProtectionPolicy'):
        backup_management_type: Literal["GenericProtectionPolicy"]
        fabric_name: Optional[str]
        protected_items_count: int
        resource_guard_operation_requests: list[str]
        sub_protection_policy: Optional[list[SubProtectionPolicy]]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_name: Optional[str] = ..., 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                sub_protection_policy: Optional[list[SubProtectionPolicy]] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.GenericRecoveryPoint(RecoveryPoint, discriminator='GenericRecoveryPoint'):
        friendly_name: Optional[str]
        object_type: Literal["GenericRecoveryPoint"]
        recovery_point_additional_info: Optional[str]
        recovery_point_properties: Optional[RecoveryPointProperties]
        recovery_point_time: Optional[datetime]
        recovery_point_type: Optional[str]
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                recovery_point_additional_info: Optional[str] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                recovery_point_type: Optional[str] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "ActionRequired"
        ACTION_SUGGESTED = "ActionSuggested"
        INVALID = "Invalid"
        PASSED = "Passed"


    class azure.mgmt.recoveryservicesbackup.models.HourlySchedule(_Model):
        interval: Optional[int]
        schedule_window_duration: Optional[int]
        schedule_window_start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                interval: Optional[int] = ..., 
                schedule_window_duration: Optional[int] = ..., 
                schedule_window_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.HttpStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        AMBIGUOUS = "Ambiguous"
        BAD_GATEWAY = "BadGateway"
        BAD_REQUEST = "BadRequest"
        CONFLICT = "Conflict"
        CONTINUE_ENUM = "Continue"
        CREATED = "Created"
        EXPECTATION_FAILED = "ExpectationFailed"
        FORBIDDEN = "Forbidden"
        FOUND = "Found"
        GATEWAY_TIMEOUT = "GatewayTimeout"
        GONE = "Gone"
        HTTP_VERSION_NOT_SUPPORTED = "HttpVersionNotSupported"
        INTERNAL_SERVER_ERROR = "InternalServerError"
        LENGTH_REQUIRED = "LengthRequired"
        METHOD_NOT_ALLOWED = "MethodNotAllowed"
        MOVED = "Moved"
        MOVED_PERMANENTLY = "MovedPermanently"
        MULTIPLE_CHOICES = "MultipleChoices"
        NON_AUTHORITATIVE_INFORMATION = "NonAuthoritativeInformation"
        NOT_ACCEPTABLE = "NotAcceptable"
        NOT_FOUND = "NotFound"
        NOT_IMPLEMENTED = "NotImplemented"
        NOT_MODIFIED = "NotModified"
        NO_CONTENT = "NoContent"
        OK = "OK"
        PARTIAL_CONTENT = "PartialContent"
        PAYMENT_REQUIRED = "PaymentRequired"
        PRECONDITION_FAILED = "PreconditionFailed"
        PROXY_AUTHENTICATION_REQUIRED = "ProxyAuthenticationRequired"
        REDIRECT = "Redirect"
        REDIRECT_KEEP_VERB = "RedirectKeepVerb"
        REDIRECT_METHOD = "RedirectMethod"
        REQUESTED_RANGE_NOT_SATISFIABLE = "RequestedRangeNotSatisfiable"
        REQUEST_ENTITY_TOO_LARGE = "RequestEntityTooLarge"
        REQUEST_TIMEOUT = "RequestTimeout"
        REQUEST_URI_TOO_LONG = "RequestUriTooLong"
        RESET_CONTENT = "ResetContent"
        SEE_OTHER = "SeeOther"
        SERVICE_UNAVAILABLE = "ServiceUnavailable"
        SWITCHING_PROTOCOLS = "SwitchingProtocols"
        TEMPORARY_REDIRECT = "TemporaryRedirect"
        UNAUTHORIZED = "Unauthorized"
        UNSUPPORTED_MEDIA_TYPE = "UnsupportedMediaType"
        UNUSED = "Unused"
        UPGRADE_REQUIRED = "UpgradeRequired"
        USE_PROXY = "UseProxy"


    class azure.mgmt.recoveryservicesbackup.models.IAASVMPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.recoveryservicesbackup.models.ILRRequest(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ILRRequestResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ILRRequest]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ILRRequest] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaaSVMContainer(ProtectionContainer, discriminator='IaasVMContainer'):
        backup_management_type: Union[str, BackupManagementType]
        container_type: Literal[ProtectableContainerType.IAAS_VM_CONTAINER]
        friendly_name: str
        health_status: str
        protectable_object_type: str
        registration_status: str
        resource_group: Optional[str]
        virtual_machine_id: Optional[str]
        virtual_machine_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaaSVMProtectableItem(WorkloadProtectableItem, discriminator='IaaSVMProtectableItem'):
        backup_management_type: str
        friendly_name: str
        protectable_item_type: Literal["IaaSVMProtectableItem"]
        protection_state: Union[str, ProtectionStatus]
        resource_group: Optional[str]
        virtual_machine_id: Optional[str]
        virtual_machine_version: Optional[str]
        workload_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                resource_group: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ..., 
                virtual_machine_version: Optional[str] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaasVMBackupRequest(BackupRequest, discriminator='IaasVMBackupRequest'):
        object_type: Literal["IaasVMBackupRequest"]
        recovery_point_expiry_time_in_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_expiry_time_in_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaasVMILRRegistrationRequest(ILRRequest, discriminator='IaasVMILRRegistrationRequest'):
        initiator_name: Optional[str]
        object_type: Literal["IaasVMILRRegistrationRequest"]
        recovery_point_id: Optional[str]
        renew_existing_registration: Optional[bool]
        virtual_machine_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initiator_name: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                renew_existing_registration: Optional[bool] = ..., 
                virtual_machine_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaasVMRecoveryPoint(RecoveryPoint, discriminator='IaasVMRecoveryPoint'):
        extended_location: Optional[ExtendedLocation]
        is_instant_ilr_session_active: Optional[bool]
        is_managed_virtual_machine: Optional[bool]
        is_private_access_enabled_on_any_disk: Optional[bool]
        is_source_vm_encrypted: Optional[bool]
        key_and_secret: Optional[KeyAndSecretDetails]
        object_type: Literal["IaasVMRecoveryPoint"]
        original_storage_account_option: Optional[bool]
        os_type: Optional[str]
        recovery_point_additional_info: Optional[str]
        recovery_point_disk_configuration: Optional[RecoveryPointDiskConfiguration]
        recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]]
        recovery_point_properties: Optional[RecoveryPointProperties]
        recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]]
        recovery_point_time: Optional[datetime]
        recovery_point_type: Optional[str]
        security_type: Optional[str]
        source_vm_storage_type: Optional[str]
        threat_info: list[ThreatInfo]
        threat_status: Union[str, ThreatStatus]
        virtual_machine_size: Optional[str]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                is_instant_ilr_session_active: Optional[bool] = ..., 
                is_managed_virtual_machine: Optional[bool] = ..., 
                is_private_access_enabled_on_any_disk: Optional[bool] = ..., 
                is_source_vm_encrypted: Optional[bool] = ..., 
                key_and_secret: Optional[KeyAndSecretDetails] = ..., 
                original_storage_account_option: Optional[bool] = ..., 
                os_type: Optional[str] = ..., 
                recovery_point_additional_info: Optional[str] = ..., 
                recovery_point_disk_configuration: Optional[RecoveryPointDiskConfiguration] = ..., 
                recovery_point_move_readiness_info: Optional[dict[str, RecoveryPointMoveReadinessInfo]] = ..., 
                recovery_point_properties: Optional[RecoveryPointProperties] = ..., 
                recovery_point_tier_details: Optional[list[RecoveryPointTierInformationV2]] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                recovery_point_type: Optional[str] = ..., 
                security_type: Optional[str] = ..., 
                source_vm_storage_type: Optional[str] = ..., 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ..., 
                virtual_machine_size: Optional[str] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaasVMRestoreRequest(RestoreRequest, discriminator='IaasVMRestoreRequest'):
        affinity_group: Optional[str]
        create_new_cloud_service: Optional[bool]
        disk_encryption_set_id: Optional[str]
        encryption_details: Optional[EncryptionDetails]
        extended_location: Optional[ExtendedLocation]
        identity_based_restore_details: Optional[IdentityBasedRestoreDetails]
        identity_info: Optional[IdentityInfo]
        object_type: Literal["IaasVMRestoreRequest"]
        original_storage_account_option: Optional[bool]
        recovery_point_id: Optional[str]
        recovery_type: Optional[Union[str, RecoveryType]]
        region: Optional[str]
        resource_guard_operation_requests: list[str]
        restore_disk_lun_list: Optional[list[int]]
        restore_with_managed_disks: Optional[bool]
        secured_vm_details: Optional[SecuredVMDetails]
        source_resource_id: Optional[str]
        storage_account_id: Optional[str]
        subnet_id: Optional[str]
        target_disk_network_access_settings: Optional[TargetDiskNetworkAccessSettings]
        target_domain_name_id: Optional[str]
        target_resource_group_id: Optional[str]
        target_virtual_machine_id: Optional[str]
        virtual_network_id: Optional[str]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                affinity_group: Optional[str] = ..., 
                create_new_cloud_service: Optional[bool] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                encryption_details: Optional[EncryptionDetails] = ..., 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity_based_restore_details: Optional[IdentityBasedRestoreDetails] = ..., 
                identity_info: Optional[IdentityInfo] = ..., 
                original_storage_account_option: Optional[bool] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                region: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_disk_lun_list: Optional[list[int]] = ..., 
                restore_with_managed_disks: Optional[bool] = ..., 
                secured_vm_details: Optional[SecuredVMDetails] = ..., 
                source_resource_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                target_disk_network_access_settings: Optional[TargetDiskNetworkAccessSettings] = ..., 
                target_domain_name_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaasVMRestoreWithRehydrationRequest(IaasVMRestoreRequest, discriminator='IaasVMRestoreWithRehydrationRequest'):
        affinity_group: str
        create_new_cloud_service: bool
        disk_encryption_set_id: str
        encryption_details: EncryptionDetails
        extended_location: ExtendedLocation
        identity_based_restore_details: IdentityBasedRestoreDetails
        identity_info: IdentityInfo
        object_type: Literal["IaasVMRestoreWithRehydrationRequest"]
        original_storage_account_option: bool
        recovery_point_id: str
        recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo]
        recovery_type: Union[str, RecoveryType]
        region: str
        resource_guard_operation_requests: list[str]
        restore_disk_lun_list: list[int]
        restore_with_managed_disks: bool
        secured_vm_details: SecuredVMDetails
        source_resource_id: str
        storage_account_id: str
        subnet_id: str
        target_disk_network_access_settings: TargetDiskNetworkAccessSettings
        target_domain_name_id: str
        target_resource_group_id: str
        target_virtual_machine_id: str
        virtual_network_id: str
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                affinity_group: Optional[str] = ..., 
                create_new_cloud_service: Optional[bool] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                encryption_details: Optional[EncryptionDetails] = ..., 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity_based_restore_details: Optional[IdentityBasedRestoreDetails] = ..., 
                identity_info: Optional[IdentityInfo] = ..., 
                original_storage_account_option: Optional[bool] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_rehydration_info: Optional[RecoveryPointRehydrationInfo] = ..., 
                recovery_type: Optional[Union[str, RecoveryType]] = ..., 
                region: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_disk_lun_list: Optional[list[int]] = ..., 
                restore_with_managed_disks: Optional[bool] = ..., 
                secured_vm_details: Optional[SecuredVMDetails] = ..., 
                source_resource_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                target_disk_network_access_settings: Optional[TargetDiskNetworkAccessSettings] = ..., 
                target_domain_name_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_virtual_machine_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IaasVMSnapshotConsistencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONLY_CRASH_CONSISTENT = "OnlyCrashConsistent"


    class azure.mgmt.recoveryservicesbackup.models.IdentityBasedRestoreDetails(_Model):
        object_type: Optional[str]
        target_storage_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_type: Optional[str] = ..., 
                target_storage_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.IdentityInfo(_Model):
        is_system_assigned_identity: Optional[bool]
        managed_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_system_assigned_identity: Optional[bool] = ..., 
                managed_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.InfrastructureEncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.InquiryInfo(_Model):
        error_detail: Optional[ErrorDetail]
        inquiry_details: Optional[list[WorkloadInquiryDetails]]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_detail: Optional[ErrorDetail] = ..., 
                inquiry_details: Optional[list[WorkloadInquiryDetails]] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.InquiryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INVALID = "Invalid"
        SUCCESS = "Success"


    class azure.mgmt.recoveryservicesbackup.models.InquiryValidation(_Model):
        additional_detail: Optional[str]
        error_detail: Optional[ErrorDetail]
        protectable_item_count: Optional[Any]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_detail: Optional[ErrorDetail] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.InstanceProtectionReadiness(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PARTIAL_PROTECTION = "PartialProtection"
        PROTECTION_ERROR = "ProtectionError"
        READY = "Ready"
        SCHEDULE_DISABLED = "ScheduleDisabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.recoveryservicesbackup.models.InstantItemRecoveryTarget(_Model):
        client_scripts: Optional[list[ClientScriptForConnect]]

        @overload
        def __init__(
                self, 
                *, 
                client_scripts: Optional[list[ClientScriptForConnect]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.InstantRPAdditionalDetails(_Model):
        azure_backup_rg_name_prefix: Optional[str]
        azure_backup_rg_name_suffix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_backup_rg_name_prefix: Optional[str] = ..., 
                azure_backup_rg_name_suffix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.Job(_Model):
        activity_id: Optional[str]
        backup_management_type: Optional[Union[str, BackupManagementType]]
        end_time: Optional[datetime]
        entity_friendly_name: Optional[str]
        job_type: str
        operation: Optional[str]
        start_time: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                job_type: str, 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.JobResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[Job]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Job] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.JobSupportedAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLABLE = "Cancellable"
        INVALID = "Invalid"
        RETRIABLE = "Retriable"


    class azure.mgmt.recoveryservicesbackup.models.KEKDetails(_Model):
        key_backup_data: Optional[str]
        key_url: Optional[str]
        key_vault_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_backup_data: Optional[str] = ..., 
                key_url: Optional[str] = ..., 
                key_vault_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.KPIResourceHealthDetails(_Model):
        resource_health_details: Optional[list[ResourceHealthDetails]]
        resource_health_status: Optional[Union[str, ResourceHealthStatus]]

        @overload
        def __init__(
                self, 
                *, 
                resource_health_details: Optional[list[ResourceHealthDetails]] = ..., 
                resource_health_status: Optional[Union[str, ResourceHealthStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.KeyAndSecretDetails(_Model):
        bek_details: Optional[BEKDetails]
        encryption_mechanism: Optional[str]
        kek_details: Optional[KEKDetails]

        @overload
        def __init__(
                self, 
                *, 
                bek_details: Optional[BEKDetails] = ..., 
                encryption_mechanism: Optional[str] = ..., 
                kek_details: Optional[KEKDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.LastBackupStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.recoveryservicesbackup.models.LastUpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        FIRST_INITIALIZATION = "FirstInitialization"
        INITIALIZED = "Initialized"
        INVALID = "Invalid"
        NOT_ENABLED = "NotEnabled"
        PARTIALLY_FAILED = "PartiallyFailed"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesbackup.models.ListRecoveryPointsRecommendedForMoveRequest(_Model):
        excluded_rp_list: Optional[list[str]]
        object_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                excluded_rp_list: Optional[list[str]] = ..., 
                object_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.LogSchedulePolicy(SchedulePolicy, discriminator='LogSchedulePolicy'):
        schedule_frequency_in_mins: Optional[int]
        schedule_policy_type: Literal["LogSchedulePolicy"]

        @overload
        def __init__(
                self, 
                *, 
                schedule_frequency_in_mins: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.LongTermRetentionPolicy(RetentionPolicy, discriminator='LongTermRetentionPolicy'):
        daily_schedule: Optional[DailyRetentionSchedule]
        monthly_schedule: Optional[MonthlyRetentionSchedule]
        retention_policy_type: Literal["LongTermRetentionPolicy"]
        weekly_schedule: Optional[WeeklyRetentionSchedule]
        yearly_schedule: Optional[YearlyRetentionSchedule]

        @overload
        def __init__(
                self, 
                *, 
                daily_schedule: Optional[DailyRetentionSchedule] = ..., 
                monthly_schedule: Optional[MonthlyRetentionSchedule] = ..., 
                weekly_schedule: Optional[WeeklyRetentionSchedule] = ..., 
                yearly_schedule: Optional[YearlyRetentionSchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.LongTermSchedulePolicy(SchedulePolicy, discriminator='LongTermSchedulePolicy'):
        schedule_policy_type: Literal["LongTermSchedulePolicy"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MABContainerHealthDetails(_Model):
        code: Optional[int]
        message: Optional[str]
        recommendations: Optional[list[str]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[int] = ..., 
                message: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabContainer(ProtectionContainer, discriminator='Windows'):
        agent_version: Optional[str]
        backup_management_type: Union[str, BackupManagementType]
        can_re_register: Optional[bool]
        container_health_state: Optional[str]
        container_id: Optional[int]
        container_type: Literal[ProtectableContainerType.WINDOWS]
        extended_info: Optional[MabContainerExtendedInfo]
        friendly_name: str
        health_status: str
        mab_container_health_details: Optional[list[MABContainerHealthDetails]]
        protectable_object_type: str
        protected_item_count: Optional[int]
        registration_status: str

        @overload
        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                can_re_register: Optional[bool] = ..., 
                container_health_state: Optional[str] = ..., 
                container_id: Optional[int] = ..., 
                extended_info: Optional[MabContainerExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                mab_container_health_details: Optional[list[MABContainerHealthDetails]] = ..., 
                protectable_object_type: Optional[str] = ..., 
                protected_item_count: Optional[int] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabContainerExtendedInfo(_Model):
        backup_item_type: Optional[Union[str, BackupItemType]]
        backup_items: Optional[list[str]]
        last_backup_status: Optional[str]
        last_refreshed_at: Optional[datetime]
        policy_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_item_type: Optional[Union[str, BackupItemType]] = ..., 
                backup_items: Optional[list[str]] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_refreshed_at: Optional[datetime] = ..., 
                policy_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabErrorInfo(_Model):
        error_string: Optional[str]
        recommendations: Optional[list[str]]


    class azure.mgmt.recoveryservicesbackup.models.MabFileFolderProtectedItem(ProtectedItem, discriminator='MabFileFolderProtectedItem'):
        backup_management_type: Union[str, BackupManagementType]
        backup_set_name: str
        computer_name: Optional[str]
        container_name: str
        create_mode: Union[str, CreateMode]
        deferred_delete_sync_time_in_utc: Optional[int]
        deferred_delete_time_in_utc: datetime
        deferred_delete_time_remaining: str
        extended_info: Optional[MabFileFolderProtectedItemExtendedInfo]
        friendly_name: Optional[str]
        is_archive_enabled: bool
        is_deferred_delete_schedule_upcoming: bool
        is_rehydrate: bool
        is_scheduled_for_deferred_delete: bool
        last_backup_status: Optional[str]
        last_backup_time: Optional[datetime]
        last_recovery_point: datetime
        policy_id: str
        policy_name: str
        protected_item_type: Literal["MabFileFolderProtectedItem"]
        protection_state: Optional[str]
        resource_guard_operation_requests: list[str]
        soft_delete_retention_period_in_days: int
        source_resource_id: str
        source_side_scan_info: SourceSideScanInfo
        vault_id: str
        workload_type: Union[str, DataSourceType]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                computer_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_sync_time_in_utc: Optional[int] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                extended_info: Optional[MabFileFolderProtectedItemExtendedInfo] = ..., 
                friendly_name: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_backup_status: Optional[str] = ..., 
                last_backup_time: Optional[datetime] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protection_state: Optional[str] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabFileFolderProtectedItemExtendedInfo(_Model):
        last_refreshed_at: Optional[datetime]
        oldest_recovery_point: Optional[datetime]
        recovery_point_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                last_refreshed_at: Optional[datetime] = ..., 
                oldest_recovery_point: Optional[datetime] = ..., 
                recovery_point_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabJob(Job, discriminator='MabJob'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[MabErrorInfo]]
        extended_info: Optional[MabJobExtendedInfo]
        job_type: Literal["MabJob"]
        mab_server_name: Optional[str]
        mab_server_type: Optional[Union[str, MabServerType]]
        operation: str
        start_time: datetime
        status: str
        workload_type: Optional[Union[str, WorkloadType]]

        @overload
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
                workload_type: Optional[Union[str, WorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabJobExtendedInfo(_Model):
        dynamic_error_message: Optional[str]
        property_bag: Optional[dict[str, str]]
        tasks_list: Optional[list[MabJobTaskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_error_message: Optional[str] = ..., 
                property_bag: Optional[dict[str, str]] = ..., 
                tasks_list: Optional[list[MabJobTaskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabJobTaskDetails(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        start_time: Optional[datetime]
        status: Optional[str]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabProtectionPolicy(ProtectionPolicy, discriminator='MAB'):
        backup_management_type: Literal["MAB"]
        protected_items_count: int
        resource_guard_operation_requests: list[str]
        retention_policy: Optional[RetentionPolicy]
        schedule_policy: Optional[SchedulePolicy]

        @overload
        def __init__(
                self, 
                *, 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                schedule_policy: Optional[SchedulePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MabServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.recoveryservicesbackup.models.MonthOfYear(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APRIL = "April"
        AUGUST = "August"
        DECEMBER = "December"
        FEBRUARY = "February"
        INVALID = "Invalid"
        JANUARY = "January"
        JULY = "July"
        JUNE = "June"
        MARCH = "March"
        MAY = "May"
        NOVEMBER = "November"
        OCTOBER = "October"
        SEPTEMBER = "September"


    class azure.mgmt.recoveryservicesbackup.models.MonthlyRetentionSchedule(_Model):
        retention_duration: Optional[RetentionDuration]
        retention_schedule_daily: Optional[DailyRetentionFormat]
        retention_schedule_format_type: Optional[Union[str, RetentionScheduleFormat]]
        retention_schedule_weekly: Optional[WeeklyRetentionFormat]
        retention_times: Optional[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                retention_duration: Optional[RetentionDuration] = ..., 
                retention_schedule_daily: Optional[DailyRetentionFormat] = ..., 
                retention_schedule_format_type: Optional[Union[str, RetentionScheduleFormat]] = ..., 
                retention_schedule_weekly: Optional[WeeklyRetentionFormat] = ..., 
                retention_times: Optional[list[datetime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.MoveRPAcrossTiersRequest(_Model):
        object_type: Optional[str]
        source_tier_type: Optional[Union[str, RecoveryPointTierType]]
        target_tier_type: Optional[Union[str, RecoveryPointTierType]]

        @overload
        def __init__(
                self, 
                *, 
                object_type: Optional[str] = ..., 
                source_tier_type: Optional[Union[str, RecoveryPointTierType]] = ..., 
                target_tier_type: Optional[Union[str, RecoveryPointTierType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.NameInfo(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationResultInfo(OperationResultInfoBase, discriminator='OperationResultInfo'):
        job_list: Optional[list[str]]
        object_type: Literal["OperationResultInfo"]

        @overload
        def __init__(
                self, 
                *, 
                job_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationResultInfoBase(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationResultInfoBaseResource(OperationWorkerResponse):
        headers: dict[str, list[str]]
        operation: Optional[OperationResultInfoBase]
        status_code: Union[str, HttpStatusCode]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[dict[str, list[str]]] = ..., 
                operation: Optional[OperationResultInfoBase] = ..., 
                status_code: Optional[Union[str, HttpStatusCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatus(_Model):
        end_time: Optional[datetime]
        error: Optional[OperationStatusError]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[OperationStatusExtendedInfo]
        start_time: Optional[datetime]
        status: Optional[Union[str, OperationStatusValues]]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[OperationStatusError] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[OperationStatusExtendedInfo] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, OperationStatusValues]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusError(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusExtendedInfo(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusJobExtendedInfo(OperationStatusExtendedInfo, discriminator='OperationStatusJobExtendedInfo'):
        job_id: Optional[str]
        object_type: Literal["OperationStatusJobExtendedInfo"]

        @overload
        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusJobsExtendedInfo(OperationStatusExtendedInfo, discriminator='OperationStatusJobsExtendedInfo'):
        failed_jobs_error: Optional[dict[str, str]]
        job_ids: Optional[list[str]]
        object_type: Literal["OperationStatusJobsExtendedInfo"]

        @overload
        def __init__(
                self, 
                *, 
                failed_jobs_error: Optional[dict[str, str]] = ..., 
                job_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusProvisionILRExtendedInfo(OperationStatusExtendedInfo, discriminator='OperationStatusProvisionILRExtendedInfo'):
        object_type: Literal["OperationStatusProvisionILRExtendedInfo"]
        recovery_target: Optional[InstantItemRecoveryTarget]

        @overload
        def __init__(
                self, 
                *, 
                recovery_target: Optional[InstantItemRecoveryTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusValidateOperationExtendedInfo(OperationStatusExtendedInfo, discriminator='OperationStatusValidateOperationExtendedInfo'):
        object_type: Literal["OperationStatusValidateOperationExtendedInfo"]
        validate_operation_response: Optional[ValidateOperationResponse]

        @overload
        def __init__(
                self, 
                *, 
                validate_operation_response: Optional[ValidateOperationResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OperationStatusValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesbackup.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        REGISTER = "Register"
        REHYDRATE = "Rehydrate"
        REREGISTER = "Reregister"


    class azure.mgmt.recoveryservicesbackup.models.OperationWorkerResponse(_Model):
        headers: Optional[dict[str, list[str]]]
        status_code: Optional[Union[str, HttpStatusCode]]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[dict[str, list[str]]] = ..., 
                status_code: Optional[Union[str, HttpStatusCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.OverwriteOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL_ON_CONFLICT = "FailOnConflict"
        INVALID = "Invalid"
        OVERWRITE = "Overwrite"


    class azure.mgmt.recoveryservicesbackup.models.PatchRecoveryPointInput(_Model):
        recovery_point_properties: Optional[PatchRecoveryPointPropertiesInput]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_properties: Optional[PatchRecoveryPointPropertiesInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PatchRecoveryPointPropertiesInput(_Model):
        expiry_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PointInTimeRange(_Model):
        end_time: Optional[datetime]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY_ONLY_FULL = "CopyOnlyFull"
        DIFFERENTIAL = "Differential"
        FULL = "Full"
        INCREMENTAL = "Incremental"
        INVALID = "Invalid"
        LOG = "Log"
        SNAPSHOT_COPY_ONLY_FULL = "SnapshotCopyOnlyFull"
        SNAPSHOT_FULL = "SnapshotFull"


    class azure.mgmt.recoveryservicesbackup.models.PreBackupValidation(_Model):
        code: Optional[str]
        message: Optional[str]
        status: Optional[Union[str, InquiryStatus]]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                status: Optional[Union[str, InquiryStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PreValidateEnableBackupRequest(_Model):
        properties: Optional[str]
        resource_id: Optional[str]
        resource_type: Optional[Union[str, DataSourceType]]
        vault_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_type: Optional[Union[str, DataSourceType]] = ..., 
                vault_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PreValidateEnableBackupResponse(_Model):
        container_name: Optional[str]
        error_code: Optional[str]
        error_message: Optional[str]
        protected_item_name: Optional[str]
        recommendation: Optional[str]
        status: Optional[Union[str, ValidationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                protected_item_name: Optional[str] = ..., 
                recommendation: Optional[str] = ..., 
                status: Optional[Union[str, ValidationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PrepareDataMoveRequest(_Model):
        data_move_level: Union[str, DataMoveLevel]
        ignore_moved: Optional[bool]
        source_container_arm_ids: Optional[list[str]]
        target_region: str
        target_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_move_level: Union[str, DataMoveLevel], 
                ignore_moved: Optional[bool] = ..., 
                source_container_arm_ids: Optional[list[str]] = ..., 
                target_region: str, 
                target_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PrepareDataMoveResponse(VaultStorageConfigOperationResultResponse, discriminator='PrepareDataMoveResponse'):
        correlation_id: Optional[str]
        object_type: Literal["PrepareDataMoveResponse"]
        source_vault_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                correlation_id: Optional[str] = ..., 
                source_vault_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PrivateEndpointConnection(_Model):
        group_ids: Optional[list[Union[str, VaultSubResourceType]]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[Union[str, VaultSubResourceType]]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PrivateEndpointConnectionResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PrivateEndpointConnection]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnection] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.PrivateEndpointConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.recoveryservicesbackup.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectableContainer(_Model):
        backup_management_type: Optional[Union[str, BackupManagementType]]
        container_id: Optional[str]
        friendly_name: Optional[str]
        health_status: Optional[str]
        protectable_container_type: str

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_id: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_container_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectableContainerResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectableContainer]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProtectableContainer] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectableContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP_SERVER_CONTAINER = "AzureBackupServerContainer"
        AZURE_SQL_CONTAINER = "AzureSqlContainer"
        AZURE_WORKLOAD_CONTAINER = "AzureWorkloadContainer"
        CLUSTER = "Cluster"
        DPM_CONTAINER = "DPMContainer"
        GENERIC_CONTAINER = "GenericContainer"
        IAAS_VM_CONTAINER = "IaasVMContainer"
        IAAS_VM_SERVICE_CONTAINER = "IaasVMServiceContainer"
        INVALID = "Invalid"
        MAB_CONTAINER = "MABContainer"
        MICROSOFT_CLASSIC_COMPUTE_VIRTUAL_MACHINES = "Microsoft.ClassicCompute/virtualMachines"
        MICROSOFT_COMPUTE_VIRTUAL_MACHINES = "Microsoft.Compute/virtualMachines"
        SQLAG_WORK_LOAD_CONTAINER = "SQLAGWorkLoadContainer"
        STORAGE_CONTAINER = "StorageContainer"
        UNKNOWN = "Unknown"
        VM_APP_CONTAINER = "VMAppContainer"
        V_CENTER = "VCenter"
        WINDOWS = "Windows"


    class azure.mgmt.recoveryservicesbackup.models.ProtectedItem(_Model):
        backup_management_type: Optional[Union[str, BackupManagementType]]
        backup_set_name: Optional[str]
        container_name: Optional[str]
        create_mode: Optional[Union[str, CreateMode]]
        deferred_delete_time_in_utc: Optional[datetime]
        deferred_delete_time_remaining: Optional[str]
        is_archive_enabled: Optional[bool]
        is_deferred_delete_schedule_upcoming: Optional[bool]
        is_rehydrate: Optional[bool]
        is_scheduled_for_deferred_delete: Optional[bool]
        last_recovery_point: Optional[datetime]
        policy_id: Optional[str]
        policy_name: Optional[str]
        protected_item_type: str
        resource_guard_operation_requests: Optional[list[str]]
        soft_delete_retention_period_in_days: Optional[int]
        source_resource_id: Optional[str]
        source_side_scan_info: Optional[SourceSideScanInfo]
        vault_id: Optional[str]
        workload_type: Optional[Union[str, DataSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                backup_set_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                deferred_delete_time_in_utc: Optional[datetime] = ..., 
                deferred_delete_time_remaining: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_deferred_delete_schedule_upcoming: Optional[bool] = ..., 
                is_rehydrate: Optional[bool] = ..., 
                is_scheduled_for_deferred_delete: Optional[bool] = ..., 
                last_recovery_point: Optional[datetime] = ..., 
                policy_id: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                protected_item_type: str, 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_side_scan_info: Optional[SourceSideScanInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectedItemHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        NOT_REACHABLE = "NotReachable"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.recoveryservicesbackup.models.ProtectedItemResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectedItem]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProtectedItem] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectedItemState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUPS_SUSPENDED = "BackupsSuspended"
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        PROTECTED = "Protected"
        PROTECTION_ERROR = "ProtectionError"
        PROTECTION_PAUSED = "ProtectionPaused"
        PROTECTION_STOPPED = "ProtectionStopped"


    class azure.mgmt.recoveryservicesbackup.models.ProtectionContainer(_Model):
        backup_management_type: Optional[Union[str, BackupManagementType]]
        container_type: str
        friendly_name: Optional[str]
        health_status: Optional[str]
        protectable_object_type: Optional[str]
        registration_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                container_type: str, 
                friendly_name: Optional[str] = ..., 
                health_status: Optional[str] = ..., 
                protectable_object_type: Optional[str] = ..., 
                registration_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectionContainerResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectionContainer]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProtectionContainer] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectionIntent(_Model):
        backup_management_type: Optional[Union[str, BackupManagementType]]
        item_id: Optional[str]
        policy_id: Optional[str]
        protection_intent_item_type: str
        protection_state: Optional[Union[str, ProtectionStatus]]
        source_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                item_id: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                protection_intent_item_type: str, 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectionIntentItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESOURCE_ITEM = "AzureResourceItem"
        AZURE_WORKLOAD_AUTO_PROTECTION_INTENT = "AzureWorkloadAutoProtectionIntent"
        AZURE_WORKLOAD_CONTAINER_AUTO_PROTECTION_INTENT = "AzureWorkloadContainerAutoProtectionIntent"
        AZURE_WORKLOAD_SQL_AUTO_PROTECTION_INTENT = "AzureWorkloadSQLAutoProtectionIntent"
        INVALID = "Invalid"
        RECOVERY_SERVICE_VAULT_ITEM = "RecoveryServiceVaultItem"


    class azure.mgmt.recoveryservicesbackup.models.ProtectionIntentResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectionIntent]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProtectionIntent] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATABASE = "Database"
        DATABASE_UNDER_INSTANCE = "DatabaseUnderInstance"


    class azure.mgmt.recoveryservicesbackup.models.ProtectionPolicy(_Model):
        backup_management_type: str
        protected_items_count: Optional[int]
        resource_guard_operation_requests: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: str, 
                protected_items_count: Optional[int] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectionPolicyResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectionPolicy]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProtectionPolicy] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUPS_SUSPENDED = "BackupsSuspended"
        INVALID = "Invalid"
        IR_PENDING = "IRPending"
        PROTECTED = "Protected"
        PROTECTION_ERROR = "ProtectionError"
        PROTECTION_PAUSED = "ProtectionPaused"
        PROTECTION_STOPPED = "ProtectionStopped"


    class azure.mgmt.recoveryservicesbackup.models.ProtectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        NOT_PROTECTED = "NotProtected"
        PROTECTED = "Protected"
        PROTECTING = "Protecting"
        PROTECTION_FAILED = "ProtectionFailed"


    class azure.mgmt.recoveryservicesbackup.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesbackup.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservicesbackup.models.RecoveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_RECOVERY = "FileRecovery"
        INVALID = "Invalid"
        RECOVERY_USING_SNAPSHOT = "RecoveryUsingSnapshot"
        SNAPSHOT_ATTACH = "SnapshotAttach"
        SNAPSHOT_ATTACH_AND_RECOVER = "SnapshotAttachAndRecover"
        WORKLOAD_RECOVERY = "WorkloadRecovery"


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPoint(_Model):
        object_type: str
        threat_info: Optional[list[ThreatInfo]]
        threat_status: Optional[Union[str, ThreatStatus]]

        @overload
        def __init__(
                self, 
                *, 
                object_type: str, 
                threat_info: Optional[list[ThreatInfo]] = ..., 
                threat_status: Optional[Union[str, ThreatStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointDiskConfiguration(_Model):
        excluded_disk_list: Optional[list[DiskInformation]]
        included_disk_list: Optional[list[DiskInformation]]
        number_of_disks_attached_to_vm: Optional[int]
        number_of_disks_included_in_backup: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                excluded_disk_list: Optional[list[DiskInformation]] = ..., 
                included_disk_list: Optional[list[DiskInformation]] = ..., 
                number_of_disks_attached_to_vm: Optional[int] = ..., 
                number_of_disks_included_in_backup: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointMoveReadinessInfo(_Model):
        additional_info: Optional[str]
        is_ready_for_move: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[str] = ..., 
                is_ready_for_move: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointProperties(_Model):
        expiry_time: Optional[str]
        is_soft_deleted: Optional[bool]
        rule_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[str] = ..., 
                is_soft_deleted: Optional[bool] = ..., 
                rule_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointRehydrationInfo(_Model):
        rehydration_priority: Optional[Union[str, RehydrationPriority]]
        rehydration_retention_duration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                rehydration_priority: Optional[Union[str, RehydrationPriority]] = ..., 
                rehydration_retention_duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[RecoveryPoint]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[RecoveryPoint] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointTierInformation(_Model):
        extended_info: Optional[dict[str, str]]
        status: Optional[Union[str, RecoveryPointTierStatus]]
        type: Optional[Union[str, RecoveryPointTierType]]

        @overload
        def __init__(
                self, 
                *, 
                extended_info: Optional[dict[str, str]] = ..., 
                status: Optional[Union[str, RecoveryPointTierStatus]] = ..., 
                type: Optional[Union[str, RecoveryPointTierType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointTierInformationV2(RecoveryPointTierInformation):
        extended_info: dict[str, str]
        status: Union[str, RecoveryPointTierStatus]
        type: Union[str, RecoveryPointTierType]

        @overload
        def __init__(
                self, 
                *, 
                extended_info: Optional[dict[str, str]] = ..., 
                status: Optional[Union[str, RecoveryPointTierStatus]] = ..., 
                type: Optional[Union[str, RecoveryPointTierType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointTierStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DISABLED = "Disabled"
        INVALID = "Invalid"
        REHYDRATED = "Rehydrated"
        VALID = "Valid"


    class azure.mgmt.recoveryservicesbackup.models.RecoveryPointTierType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVED_RP = "ArchivedRP"
        HARDENED_RP = "HardenedRP"
        INSTANT_RP = "InstantRP"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.RecoveryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALTERNATE_LOCATION = "AlternateLocation"
        INVALID = "Invalid"
        OFFLINE = "Offline"
        ORIGINAL_LOCATION = "OriginalLocation"
        RESTORE_DISKS = "RestoreDisks"


    class azure.mgmt.recoveryservicesbackup.models.RehydrationPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        STANDARD = "Standard"


    class azure.mgmt.recoveryservicesbackup.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.recoveryservicesbackup.models.ResourceGuardOperationDetail(_Model):
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


    class azure.mgmt.recoveryservicesbackup.models.ResourceGuardProxyBase(_Model):
        description: Optional[str]
        last_updated_time: Optional[str]
        resource_guard_operation_details: Optional[list[ResourceGuardOperationDetail]]
        resource_guard_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                last_updated_time: Optional[str] = ..., 
                resource_guard_operation_details: Optional[list[ResourceGuardOperationDetail]] = ..., 
                resource_guard_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ResourceGuardProxyBaseResource(ProxyResource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ResourceGuardProxyBase]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ResourceGuardProxyBase] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ResourceHealthDetails(_Model):
        code: Optional[int]
        message: Optional[str]
        recommendations: Optional[list[str]]
        title: Optional[str]


    class azure.mgmt.recoveryservicesbackup.models.ResourceHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        PERSISTENT_DEGRADED = "PersistentDegraded"
        PERSISTENT_UNHEALTHY = "PersistentUnhealthy"
        TRANSIENT_DEGRADED = "TransientDegraded"
        TRANSIENT_UNHEALTHY = "TransientUnhealthy"


    class azure.mgmt.recoveryservicesbackup.models.ResourceList(_Model):
        next_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RestoreFileSpecs(_Model):
        file_spec_type: Optional[str]
        path: Optional[str]
        target_folder_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_spec_type: Optional[str] = ..., 
                path: Optional[str] = ..., 
                target_folder_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RestorePointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIFFERENTIAL = "Differential"
        FULL = "Full"
        INCREMENTAL = "Incremental"
        INVALID = "Invalid"
        LOG = "Log"
        SNAPSHOT_COPY_ONLY_FULL = "SnapshotCopyOnlyFull"
        SNAPSHOT_FULL = "SnapshotFull"


    class azure.mgmt.recoveryservicesbackup.models.RestoreRequest(_Model):
        object_type: str
        resource_guard_operation_requests: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                object_type: str, 
                resource_guard_operation_requests: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RestoreRequestResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[RestoreRequest]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[RestoreRequest] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RestoreRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_SHARE_RESTORE = "FullShareRestore"
        INVALID = "Invalid"
        ITEM_LEVEL_RESTORE = "ItemLevelRestore"


    class azure.mgmt.recoveryservicesbackup.models.RetentionDuration(_Model):
        count: Optional[int]
        duration_type: Optional[Union[str, RetentionDurationType]]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                duration_type: Optional[Union[str, RetentionDurationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RetentionDurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAYS = "Days"
        INVALID = "Invalid"
        MONTHS = "Months"
        WEEKS = "Weeks"
        YEARS = "Years"


    class azure.mgmt.recoveryservicesbackup.models.RetentionPolicy(_Model):
        retention_policy_type: str

        @overload
        def __init__(
                self, 
                *, 
                retention_policy_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.RetentionScheduleFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        INVALID = "Invalid"
        WEEKLY = "Weekly"


    class azure.mgmt.recoveryservicesbackup.models.SQLDataDirectory(_Model):
        logical_name: Optional[str]
        path: Optional[str]
        type: Optional[Union[str, SQLDataDirectoryType]]

        @overload
        def __init__(
                self, 
                *, 
                logical_name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                type: Optional[Union[str, SQLDataDirectoryType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SQLDataDirectoryMapping(_Model):
        mapping_type: Optional[Union[str, SQLDataDirectoryType]]
        source_logical_name: Optional[str]
        source_path: Optional[str]
        target_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mapping_type: Optional[Union[str, SQLDataDirectoryType]] = ..., 
                source_logical_name: Optional[str] = ..., 
                source_path: Optional[str] = ..., 
                target_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SQLDataDirectoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        INVALID = "Invalid"
        LOG = "Log"


    class azure.mgmt.recoveryservicesbackup.models.SchedulePolicy(_Model):
        schedule_policy_type: str

        @overload
        def __init__(
                self, 
                *, 
                schedule_policy_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ScheduleRunType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        INVALID = "Invalid"
        WEEKLY = "Weekly"


    class azure.mgmt.recoveryservicesbackup.models.SecuredVMDetails(_Model):
        secured_vmos_disk_encryption_set_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                secured_vmos_disk_encryption_set_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SecurityPinBase(_Model):
        resource_guard_operation_requests: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                resource_guard_operation_requests: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.Settings(_Model):
        is_compression: Optional[bool]
        issqlcompression: Optional[bool]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_compression: Optional[bool] = ..., 
                issqlcompression: Optional[bool] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SimpleRetentionPolicy(RetentionPolicy, discriminator='SimpleRetentionPolicy'):
        retention_duration: Optional[RetentionDuration]
        retention_policy_type: Literal["SimpleRetentionPolicy"]

        @overload
        def __init__(
                self, 
                *, 
                retention_duration: Optional[RetentionDuration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SimpleSchedulePolicy(SchedulePolicy, discriminator='SimpleSchedulePolicy'):
        hourly_schedule: Optional[HourlySchedule]
        schedule_policy_type: Literal["SimpleSchedulePolicy"]
        schedule_run_days: Optional[list[Union[str, DayOfWeek]]]
        schedule_run_frequency: Optional[Union[str, ScheduleRunType]]
        schedule_run_times: Optional[list[datetime]]
        schedule_weekly_frequency: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                hourly_schedule: Optional[HourlySchedule] = ..., 
                schedule_run_days: Optional[list[Union[str, DayOfWeek]]] = ..., 
                schedule_run_frequency: Optional[Union[str, ScheduleRunType]] = ..., 
                schedule_run_times: Optional[list[datetime]] = ..., 
                schedule_weekly_frequency: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SimpleSchedulePolicyV2(SchedulePolicy, discriminator='SimpleSchedulePolicyV2'):
        daily_schedule: Optional[DailySchedule]
        hourly_schedule: Optional[HourlySchedule]
        schedule_policy_type: Literal["SimpleSchedulePolicyV2"]
        schedule_run_frequency: Optional[Union[str, ScheduleRunType]]
        weekly_schedule: Optional[WeeklySchedule]

        @overload
        def __init__(
                self, 
                *, 
                daily_schedule: Optional[DailySchedule] = ..., 
                hourly_schedule: Optional[HourlySchedule] = ..., 
                schedule_run_frequency: Optional[Union[str, ScheduleRunType]] = ..., 
                weekly_schedule: Optional[WeeklySchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SnapshotBackupAdditionalDetails(_Model):
        instant_rp_details: Optional[str]
        instant_rp_retention_range_in_days: Optional[int]
        user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails]

        @overload
        def __init__(
                self, 
                *, 
                instant_rp_details: Optional[str] = ..., 
                instant_rp_retention_range_in_days: Optional[int] = ..., 
                user_assigned_managed_identity_details: Optional[UserAssignedManagedIdentityDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SnapshotRestoreParameters(_Model):
        log_point_in_time_for_db_recovery: Optional[str]
        skip_attach_and_mount: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                log_point_in_time_for_db_recovery: Optional[str] = ..., 
                skip_attach_and_mount: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SoftDeleteFeatureState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS_ON = "AlwaysON"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.SourceSideScanInfo(_Model):
        source_side_scan_status: Optional[Union[str, SourceSideScanStatus]]
        source_side_scan_summary: Optional[Union[str, SourceSideScanSummary]]

        @overload
        def __init__(
                self, 
                *, 
                source_side_scan_status: Optional[Union[str, SourceSideScanStatus]] = ..., 
                source_side_scan_summary: Optional[Union[str, SourceSideScanSummary]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SourceSideScanStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURED = "Configured"
        NOT_APPLICABLE = "NotApplicable"
        NOT_CONFIGURED = "NotConfigured"


    class azure.mgmt.recoveryservicesbackup.models.SourceSideScanSummary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        SUSPICIOUS = "Suspicious"
        UNKNOWN = "Unknown"


    class azure.mgmt.recoveryservicesbackup.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_REDUNDANT = "GeoRedundant"
        INVALID = "Invalid"
        LOCALLY_REDUNDANT = "LocallyRedundant"
        READ_ACCESS_GEO_ZONE_REDUNDANT = "ReadAccessGeoZoneRedundant"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.recoveryservicesbackup.models.StorageTypeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.recoveryservicesbackup.models.SubProtectionPolicy(_Model):
        policy_type: Optional[Union[str, PolicyType]]
        retention_policy: Optional[RetentionPolicy]
        schedule_policy: Optional[SchedulePolicy]
        snapshot_backup_additional_details: Optional[SnapshotBackupAdditionalDetails]
        tiering_policy: Optional[dict[str, TieringPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                schedule_policy: Optional[SchedulePolicy] = ..., 
                snapshot_backup_additional_details: Optional[SnapshotBackupAdditionalDetails] = ..., 
                tiering_policy: Optional[dict[str, TieringPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.SupportStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT_OFF = "DefaultOFF"
        DEFAULT_ON = "DefaultON"
        INVALID = "Invalid"
        NOT_SUPPORTED = "NotSupported"
        SUPPORTED = "Supported"


    class azure.mgmt.recoveryservicesbackup.models.SystemData(_Model):
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


    class azure.mgmt.recoveryservicesbackup.models.TargetAFSRestoreInfo(_Model):
        name: Optional[str]
        target_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                target_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TargetDiskNetworkAccessOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLE_PRIVATE_ACCESS_FOR_ALL_DISKS = "EnablePrivateAccessForAllDisks"
        ENABLE_PUBLIC_ACCESS_FOR_ALL_DISKS = "EnablePublicAccessForAllDisks"
        SAME_AS_ON_SOURCE_DISKS = "SameAsOnSourceDisks"


    class azure.mgmt.recoveryservicesbackup.models.TargetDiskNetworkAccessSettings(_Model):
        target_disk_access_id: Optional[str]
        target_disk_network_access_option: Optional[Union[str, TargetDiskNetworkAccessOption]]

        @overload
        def __init__(
                self, 
                *, 
                target_disk_access_id: Optional[str] = ..., 
                target_disk_network_access_option: Optional[Union[str, TargetDiskNetworkAccessOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TargetRestoreInfo(_Model):
        container_id: Optional[str]
        database_name: Optional[str]
        overwrite_option: Optional[Union[str, OverwriteOptions]]
        target_directory_for_file_restore: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_id: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                overwrite_option: Optional[Union[str, OverwriteOptions]] = ..., 
                target_directory_for_file_restore: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ThreatInfo(_Model):
        last_updated_time: Optional[datetime]
        threat_description: Optional[str]
        threat_end_time: Optional[datetime]
        threat_severity: Optional[Union[str, ThreatSeverity]]
        threat_start_time: Optional[datetime]
        threat_state: Optional[Union[str, ThreatState]]
        threat_title: Optional[str]
        threat_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                threat_severity: Optional[Union[str, ThreatSeverity]] = ..., 
                threat_state: Optional[Union[str, ThreatState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ThreatSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        INFORMATIONAL = "Informational"
        WARNING = "Warning"


    class azure.mgmt.recoveryservicesbackup.models.ThreatState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        IGNORED = "Ignored"
        IN_PROGRESS = "InProgress"
        RESOLVED = "Resolved"


    class azure.mgmt.recoveryservicesbackup.models.ThreatStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_AVAILABLE = "NotAvailable"
        UNKNOWN = "Unknown"
        UN_HEALTHY = "UnHealthy"
        WARNING = "Warning"


    class azure.mgmt.recoveryservicesbackup.models.TieringCostInfo(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TieringCostRehydrationInfo(TieringCostInfo, discriminator='TieringCostRehydrationInfo'):
        object_type: Literal["TieringCostRehydrationInfo"]
        rehydration_size_in_bytes: int
        retail_rehydration_cost_per_gb_per_month: float

        @overload
        def __init__(
                self, 
                *, 
                rehydration_size_in_bytes: int, 
                retail_rehydration_cost_per_gb_per_month: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TieringCostSavingInfo(TieringCostInfo, discriminator='TieringCostSavingInfo'):
        object_type: Literal["TieringCostSavingInfo"]
        retail_source_tier_cost_per_gb_per_month: float
        retail_target_tier_cost_per_gb_per_month: float
        source_tier_size_reduction_in_bytes: int
        target_tier_size_increase_in_bytes: int

        @overload
        def __init__(
                self, 
                *, 
                retail_source_tier_cost_per_gb_per_month: float, 
                retail_target_tier_cost_per_gb_per_month: float, 
                source_tier_size_reduction_in_bytes: int, 
                target_tier_size_increase_in_bytes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TieringMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DO_NOT_TIER = "DoNotTier"
        INVALID = "Invalid"
        TIER_AFTER = "TierAfter"
        TIER_RECOMMENDED = "TierRecommended"


    class azure.mgmt.recoveryservicesbackup.models.TieringPolicy(_Model):
        duration: Optional[int]
        duration_type: Optional[Union[str, RetentionDurationType]]
        tiering_mode: Optional[Union[str, TieringMode]]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[int] = ..., 
                duration_type: Optional[Union[str, RetentionDurationType]] = ..., 
                tiering_mode: Optional[Union[str, TieringMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TokenInformation(_Model):
        expiry_time_in_utc_ticks: Optional[int]
        security_pin: Optional[str]
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time_in_utc_ticks: Optional[int] = ..., 
                security_pin: Optional[str] = ..., 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.TriggerDataMoveRequest(_Model):
        correlation_id: str
        data_move_level: Union[str, DataMoveLevel]
        pause_gc: Optional[bool]
        source_container_arm_ids: Optional[list[str]]
        source_region: str
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                correlation_id: str, 
                data_move_level: Union[str, DataMoveLevel], 
                pause_gc: Optional[bool] = ..., 
                source_container_arm_ids: Optional[list[str]] = ..., 
                source_region: str, 
                source_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.UnlockDeleteRequest(_Model):
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


    class azure.mgmt.recoveryservicesbackup.models.UnlockDeleteResponse(_Model):
        unlock_delete_expiry_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                unlock_delete_expiry_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.UpdateRecoveryPointRequest(_Model):
        properties: Optional[PatchRecoveryPointInput]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PatchRecoveryPointInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.UsagesUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.recoveryservicesbackup.models.UserAssignedIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.UserAssignedManagedIdentityDetails(_Model):
        identity_arm_id: Optional[str]
        identity_name: Optional[str]
        user_assigned_identity_properties: Optional[UserAssignedIdentityProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity_arm_id: Optional[str] = ..., 
                identity_name: Optional[str] = ..., 
                user_assigned_identity_properties: Optional[UserAssignedIdentityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.VMWorkloadPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        SNAPSHOT_V1 = "SnapshotV1"
        SNAPSHOT_V2 = "SnapshotV2"
        STREAMING = "Streaming"


    class azure.mgmt.recoveryservicesbackup.models.ValidateIaasVMRestoreOperationRequest(ValidateRestoreOperationRequest, discriminator='ValidateIaasVMRestoreOperationRequest'):
        object_type: Literal["ValidateIaasVMRestoreOperationRequest"]
        restore_request: RestoreRequest

        @overload
        def __init__(
                self, 
                *, 
                restore_request: Optional[RestoreRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ValidateOperationRequest(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ValidateOperationRequestResource(_Model):
        id: str
        properties: ValidateOperationRequest

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                properties: ValidateOperationRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ValidateOperationResponse(_Model):
        validation_results: Optional[list[ErrorDetail]]

        @overload
        def __init__(
                self, 
                *, 
                validation_results: Optional[list[ErrorDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ValidateOperationsResponse(_Model):
        validate_operation_response: Optional[ValidateOperationResponse]

        @overload
        def __init__(
                self, 
                *, 
                validate_operation_response: Optional[ValidateOperationResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ValidateRestoreOperationRequest(ValidateOperationRequest, discriminator='ValidateRestoreOperationRequest'):
        object_type: Literal["ValidateRestoreOperationRequest"]
        restore_request: Optional[RestoreRequest]

        @overload
        def __init__(
                self, 
                *, 
                restore_request: Optional[RestoreRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INVALID = "Invalid"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesbackup.models.VaultJob(Job, discriminator='VaultJob'):
        actions_info: Optional[list[Union[str, JobSupportedAction]]]
        activity_id: str
        backup_management_type: Union[str, BackupManagementType]
        duration: Optional[timedelta]
        end_time: datetime
        entity_friendly_name: str
        error_details: Optional[list[VaultJobErrorInfo]]
        extended_info: Optional[VaultJobExtendedInfo]
        job_type: Literal["VaultJob"]
        operation: str
        start_time: datetime
        status: str

        @overload
        def __init__(
                self, 
                *, 
                actions_info: Optional[list[Union[str, JobSupportedAction]]] = ..., 
                activity_id: Optional[str] = ..., 
                backup_management_type: Optional[Union[str, BackupManagementType]] = ..., 
                duration: Optional[timedelta] = ..., 
                end_time: Optional[datetime] = ..., 
                entity_friendly_name: Optional[str] = ..., 
                error_details: Optional[list[VaultJobErrorInfo]] = ..., 
                extended_info: Optional[VaultJobExtendedInfo] = ..., 
                operation: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.VaultJobErrorInfo(_Model):
        error_code: Optional[int]
        error_string: Optional[str]
        recommendations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[int] = ..., 
                error_string: Optional[str] = ..., 
                recommendations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.VaultJobExtendedInfo(_Model):
        property_bag: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                property_bag: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.VaultRetentionPolicy(_Model):
        snapshot_retention_in_days: int
        vault_retention: RetentionPolicy

        @overload
        def __init__(
                self, 
                *, 
                snapshot_retention_in_days: int, 
                vault_retention: RetentionPolicy
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.VaultStorageConfigOperationResultResponse(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.VaultSubResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP = "AzureBackup"
        AZURE_BACKUP_SECONDARY = "AzureBackup_secondary"
        AZURE_SITE_RECOVERY = "AzureSiteRecovery"


    class azure.mgmt.recoveryservicesbackup.models.WeekOfMonth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST = "First"
        FOURTH = "Fourth"
        INVALID = "Invalid"
        LAST = "Last"
        SECOND = "Second"
        THIRD = "Third"


    class azure.mgmt.recoveryservicesbackup.models.WeeklyRetentionFormat(_Model):
        days_of_the_week: Optional[list[Union[str, DayOfWeek]]]
        weeks_of_the_month: Optional[list[Union[str, WeekOfMonth]]]

        @overload
        def __init__(
                self, 
                *, 
                days_of_the_week: Optional[list[Union[str, DayOfWeek]]] = ..., 
                weeks_of_the_month: Optional[list[Union[str, WeekOfMonth]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WeeklyRetentionSchedule(_Model):
        days_of_the_week: Optional[list[Union[str, DayOfWeek]]]
        retention_duration: Optional[RetentionDuration]
        retention_times: Optional[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                days_of_the_week: Optional[list[Union[str, DayOfWeek]]] = ..., 
                retention_duration: Optional[RetentionDuration] = ..., 
                retention_times: Optional[list[datetime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WeeklySchedule(_Model):
        schedule_run_days: Optional[list[Union[str, DayOfWeek]]]
        schedule_run_times: Optional[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                schedule_run_days: Optional[list[Union[str, DayOfWeek]]] = ..., 
                schedule_run_times: Optional[list[datetime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WorkloadInquiryDetails(_Model):
        inquiry_validation: Optional[InquiryValidation]
        item_count: Optional[int]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inquiry_validation: Optional[InquiryValidation] = ..., 
                item_count: Optional[int] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WorkloadItem(_Model):
        backup_management_type: Optional[str]
        friendly_name: Optional[str]
        protection_state: Optional[Union[str, ProtectionStatus]]
        workload_item_type: str
        workload_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                workload_item_type: str, 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WorkloadItemResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[WorkloadItem]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[WorkloadItem] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WorkloadItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        SAP_ASE_DATABASE = "SAPAseDatabase"
        SAP_ASE_SYSTEM = "SAPAseSystem"
        SAP_HANA_DATABASE = "SAPHanaDatabase"
        SAP_HANA_DB_INSTANCE = "SAPHanaDBInstance"
        SAP_HANA_SYSTEM = "SAPHanaSystem"
        SQL_DATA_BASE = "SQLDataBase"
        SQL_INSTANCE = "SQLInstance"


    class azure.mgmt.recoveryservicesbackup.models.WorkloadProtectableItem(_Model):
        backup_management_type: Optional[str]
        friendly_name: Optional[str]
        protectable_item_type: str
        protection_state: Optional[Union[str, ProtectionStatus]]
        workload_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_management_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                protectable_item_type: str, 
                protection_state: Optional[Union[str, ProtectionStatus]] = ..., 
                workload_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WorkloadProtectableItemResource(Resource):
        e_tag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[WorkloadProtectableItem]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[WorkloadProtectableItem] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesbackup.models.WorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE_SHARE = "AzureFileShare"
        AZURE_SQL_DB = "AzureSqlDb"
        CLIENT = "Client"
        EXCHANGE = "Exchange"
        FILE_FOLDER = "FileFolder"
        GENERIC_DATA_SOURCE = "GenericDataSource"
        INVALID = "Invalid"
        SAP_ASE_DATABASE = "SAPAseDatabase"
        SAP_HANA_DATABASE = "SAPHanaDatabase"
        SAP_HANA_DB_INSTANCE = "SAPHanaDBInstance"
        SHAREPOINT = "Sharepoint"
        SQLDB = "SQLDB"
        SQL_DATA_BASE = "SQLDataBase"
        SYSTEM_STATE = "SystemState"
        VM = "VM"
        V_MWARE_VM = "VMwareVM"


    class azure.mgmt.recoveryservicesbackup.models.XcoolState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservicesbackup.models.YearlyRetentionSchedule(_Model):
        months_of_year: Optional[list[Union[str, MonthOfYear]]]
        retention_duration: Optional[RetentionDuration]
        retention_schedule_daily: Optional[DailyRetentionFormat]
        retention_schedule_format_type: Optional[Union[str, RetentionScheduleFormat]]
        retention_schedule_weekly: Optional[WeeklyRetentionFormat]
        retention_times: Optional[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                months_of_year: Optional[list[Union[str, MonthOfYear]]] = ..., 
                retention_duration: Optional[RetentionDuration] = ..., 
                retention_schedule_daily: Optional[DailyRetentionFormat] = ..., 
                retention_schedule_format_type: Optional[Union[str, RetentionScheduleFormat]] = ..., 
                retention_schedule_weekly: Optional[WeeklyRetentionFormat] = ..., 
                retention_times: Optional[list[datetime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.recoveryservicesbackup.operations

    class azure.mgmt.recoveryservicesbackup.operations.BMSPrepareDataMoveOperationResultOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[VaultStorageConfigOperationResultResponse]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupEnginesOperations:

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
                backup_engine_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupEngineBaseResource: ...

        @distributed_trace
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BackupEngineBaseResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupJobsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupOperationStatusesOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupPoliciesOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectionPolicyResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupProtectableItemsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WorkloadProtectableItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupProtectedItemsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectedItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupProtectionContainersOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectionContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupProtectionIntentOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectionIntentResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupResourceEncryptionConfigsOperations:

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
            ) -> BackupResourceEncryptionConfigExtendedResource: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceEncryptionConfigResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupResourceStorageConfigsNonCRROperations:

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
                parameters: JSON, 
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
                parameters: JSON, 
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


    class azure.mgmt.recoveryservicesbackup.operations.BackupResourceVaultConfigsOperations:

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
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceVaultConfigResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: BackupResourceVaultConfigResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...

        @overload
        def update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> BackupResourceVaultConfigResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get(
                self, 
                azure_region: str, 
                parameters: BackupStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupStatusResponse: ...

        @overload
        def get(
                self, 
                azure_region: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupStatusResponse: ...

        @overload
        def get(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupStatusResponse: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupUsageSummariesOperations:

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
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BackupManagementUsage]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupWorkloadItemsOperations:

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
                fabric_name: str, 
                container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WorkloadItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.BackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: BackupRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.DeletedProtectionContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectionContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ExportJobsOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResultInfoBaseResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.FeatureSupportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate(
                self, 
                azure_region: str, 
                parameters: FeatureSupportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureVMResourceFeatureSupportResponse: ...

        @overload
        def validate(
                self, 
                azure_region: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureVMResourceFeatureSupportResponse: ...

        @overload
        def validate(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureVMResourceFeatureSupportResponse: ...


    class azure.mgmt.recoveryservicesbackup.operations.FetchTieringCostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: FetchTieringCostInfoRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TieringCostInfo]: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TieringCostInfo]: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TieringCostInfo]: ...


    class azure.mgmt.recoveryservicesbackup.operations.GetTieringCostOperationResultOperations:

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
            ) -> TieringCostInfo: ...


    class azure.mgmt.recoveryservicesbackup.operations.ItemLevelRecoveryConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def provision(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: ILRRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def provision(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def provision(
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
            ) -> None: ...

        @distributed_trace
        def revoke(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.JobCancellationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.JobDetailsOperations:

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
                job_name: str, 
                **kwargs: Any
            ) -> JobResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.JobOperationResultsOperations:

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
                job_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def export(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.OperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: ValidateOperationRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOperationsResponse: ...

        @overload
        def validate(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOperationsResponse: ...

        @overload
        def validate(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOperationsResponse: ...


    class azure.mgmt.recoveryservicesbackup.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ClientDiscoveryValueForSingleApi]: ...


    class azure.mgmt.recoveryservicesbackup.operations.PrivateEndpointConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.PrivateEndpointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_operation_status(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectableContainersOperations:

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
                fabric_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectableContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectedItemOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ProtectedItemResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectedItemOperationStatusesOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectedItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: ProtectedItemResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemResource]: ...

        @distributed_trace
        def delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ProtectedItemResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionContainerOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ProtectionContainerResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionContainerRefreshOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_register(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                parameters: ProtectionContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerResource]: ...

        @overload
        def begin_register(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerResource]: ...

        @overload
        def begin_register(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerResource]: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ProtectionContainerResource: ...

        @distributed_trace
        def inquire(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def refresh(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def unregister(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionIntentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                parameters: ProtectionIntentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @overload
        def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @overload
        def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @distributed_trace
        def delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                intent_object_name: str, 
                **kwargs: Any
            ) -> ProtectionIntentResource: ...

        @overload
        def validate(
                self, 
                azure_region: str, 
                parameters: PreValidateEnableBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PreValidateEnableBackupResponse: ...

        @overload
        def validate(
                self, 
                azure_region: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PreValidateEnableBackupResponse: ...

        @overload
        def validate(
                self, 
                azure_region: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PreValidateEnableBackupResponse: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: ProtectionPolicyResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ProtectionPolicyResource]: ...

        @overload
        def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ProtectionPolicyResource]: ...

        @overload
        def create_or_update(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ProtectionPolicyResource]: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> ProtectionPolicyResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionPolicyOperationResultsOperations:

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
                policy_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ProtectionPolicyResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.ProtectionPolicyOperationStatusesOperations:

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
                policy_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.operations.RecoveryPointsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPointResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: UpdateRecoveryPointRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecoveryPointResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecoveryPointResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecoveryPointResource: ...


    class azure.mgmt.recoveryservicesbackup.operations.RecoveryPointsRecommendedForMoveOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: ListRecoveryPointsRecommendedForMoveRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPointResource]: ...

        @overload
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPointResource]: ...

        @overload
        def list(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPointResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ResourceGuardProxiesOperations:

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
            ) -> ItemPaged[ResourceGuardProxyBaseResource]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ResourceGuardProxyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: ResourceGuardProxyBaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        def put(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGuardProxyBaseResource: ...

        @overload
        def unlock_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: UnlockDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        def unlock_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...

        @overload
        def unlock_delete(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                resource_guard_proxy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UnlockDeleteResponse: ...


    class azure.mgmt.recoveryservicesbackup.operations.RestoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: RestoreRequestResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                fabric_name: str, 
                container_name: str, 
                protected_item_name: str, 
                recovery_point_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger(
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
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.recoveryservicesbackup.operations.SecurityPINsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: Optional[SecurityPinBase] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> TokenInformation: ...

        @overload
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> TokenInformation: ...

        @overload
        def get(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> TokenInformation: ...


    class azure.mgmt.recoveryservicesbackup.operations.TieringCostOperationStatusOperations:

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
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesbackup.operations.ValidateOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: ValidateOperationRequestResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger(
                self, 
                vault_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ValidateOperationResultsOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[ValidateOperationsResponse]: ...


    class azure.mgmt.recoveryservicesbackup.operations.ValidateOperationStatusesOperations:

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
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


```