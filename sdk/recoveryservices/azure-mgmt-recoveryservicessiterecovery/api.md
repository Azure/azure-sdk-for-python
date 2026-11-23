```py
namespace azure.mgmt.recoveryservicessiterecovery

    class azure.mgmt.recoveryservicessiterecovery.SiteRecoveryManagementClient: implements ContextManager 
        cluster_recovery_point: ClusterRecoveryPointOperations
        cluster_recovery_points: ClusterRecoveryPointsOperations
        migration_recovery_points: MigrationRecoveryPointsOperations
        operations: Operations
        recovery_points: RecoveryPointsOperations
        replication_alert_settings: ReplicationAlertSettingsOperations
        replication_appliances: ReplicationAppliancesOperations
        replication_eligibility_results: ReplicationEligibilityResultsOperations
        replication_events: ReplicationEventsOperations
        replication_fabrics: ReplicationFabricsOperations
        replication_jobs: ReplicationJobsOperations
        replication_logical_networks: ReplicationLogicalNetworksOperations
        replication_migration_items: ReplicationMigrationItemsOperations
        replication_network_mappings: ReplicationNetworkMappingsOperations
        replication_networks: ReplicationNetworksOperations
        replication_policies: ReplicationPoliciesOperations
        replication_protectable_items: ReplicationProtectableItemsOperations
        replication_protected_items: ReplicationProtectedItemsOperations
        replication_protection_clusters: ReplicationProtectionClustersOperations
        replication_protection_container_mappings: ReplicationProtectionContainerMappingsOperations
        replication_protection_containers: ReplicationProtectionContainersOperations
        replication_protection_intents: ReplicationProtectionIntentsOperations
        replication_recovery_plans: ReplicationRecoveryPlansOperations
        replication_recovery_services_providers: ReplicationRecoveryServicesProvidersOperations
        replication_storage_classification_mappings: ReplicationStorageClassificationMappingsOperations
        replication_storage_classifications: ReplicationStorageClassificationsOperations
        replication_vault_health: ReplicationVaultHealthOperations
        replication_vault_setting: ReplicationVaultSettingOperations
        replicationv_centers: ReplicationvCentersOperations
        supported_operating_systems: SupportedOperatingSystemsOperations
        target_compute_sizes: TargetComputeSizesOperations

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


namespace azure.mgmt.recoveryservicessiterecovery.aio

    class azure.mgmt.recoveryservicessiterecovery.aio.SiteRecoveryManagementClient: implements AsyncContextManager 
        cluster_recovery_point: ClusterRecoveryPointOperations
        cluster_recovery_points: ClusterRecoveryPointsOperations
        migration_recovery_points: MigrationRecoveryPointsOperations
        operations: Operations
        recovery_points: RecoveryPointsOperations
        replication_alert_settings: ReplicationAlertSettingsOperations
        replication_appliances: ReplicationAppliancesOperations
        replication_eligibility_results: ReplicationEligibilityResultsOperations
        replication_events: ReplicationEventsOperations
        replication_fabrics: ReplicationFabricsOperations
        replication_jobs: ReplicationJobsOperations
        replication_logical_networks: ReplicationLogicalNetworksOperations
        replication_migration_items: ReplicationMigrationItemsOperations
        replication_network_mappings: ReplicationNetworkMappingsOperations
        replication_networks: ReplicationNetworksOperations
        replication_policies: ReplicationPoliciesOperations
        replication_protectable_items: ReplicationProtectableItemsOperations
        replication_protected_items: ReplicationProtectedItemsOperations
        replication_protection_clusters: ReplicationProtectionClustersOperations
        replication_protection_container_mappings: ReplicationProtectionContainerMappingsOperations
        replication_protection_containers: ReplicationProtectionContainersOperations
        replication_protection_intents: ReplicationProtectionIntentsOperations
        replication_recovery_plans: ReplicationRecoveryPlansOperations
        replication_recovery_services_providers: ReplicationRecoveryServicesProvidersOperations
        replication_storage_classification_mappings: ReplicationStorageClassificationMappingsOperations
        replication_storage_classifications: ReplicationStorageClassificationsOperations
        replication_vault_health: ReplicationVaultHealthOperations
        replication_vault_setting: ReplicationVaultSettingOperations
        replicationv_centers: ReplicationvCentersOperations
        supported_operating_systems: SupportedOperatingSystemsOperations
        target_compute_sizes: TargetComputeSizesOperations

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


namespace azure.mgmt.recoveryservicessiterecovery.aio.operations

    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ClusterRecoveryPointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                recovery_point_name: str, 
                **kwargs: Any
            ) -> ClusterRecoveryPoint: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ClusterRecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_replication_protection_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterRecoveryPoint]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.MigrationRecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migration_recovery_point_name: str, 
                **kwargs: Any
            ) -> MigrationRecoveryPoint: ...

        @distributed_trace
        def list_by_replication_migration_items(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationRecoveryPoint]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OperationsDiscovery]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.RecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                recovery_point_name: str, 
                **kwargs: Any
            ) -> RecoveryPoint: ...

        @distributed_trace
        def list_by_replication_protected_items(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPoint]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationAlertSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                request: ConfigureAlertRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                request: ConfigureAlertRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Alert]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationAppliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationAppliance]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationEligibilityResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> ReplicationEligibilityResults: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> ReplicationEligibilityResultsCollection: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_name: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Event]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_check_consistency(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                input: FabricCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                input: FabricCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_migrate_to_aad(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reassociate_gateway(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                failover_process_server_request: FailoverProcessServerRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_reassociate_gateway(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                failover_process_server_request: FailoverProcessServerRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_reassociate_gateway(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                failover_process_server_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @distributed_trace_async
        async def begin_remove_infra(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_renew_certificate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                renew_certificate: RenewCertificateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_renew_certificate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                renew_certificate: RenewCertificateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_renew_certificate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                renew_certificate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Fabric: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Fabric]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_export(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_query_parameter: JobQueryParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_export(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_query_parameter: JobQueryParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_export(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_query_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_resume(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                resume_job_params: ResumeJobParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_resume(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                resume_job_params: ResumeJobParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_resume(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                resume_job_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Job]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationLogicalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                logical_network_name: str, 
                **kwargs: Any
            ) -> LogicalNetwork: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LogicalNetwork]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationMigrationItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: EnableMigrationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: EnableMigrationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                *, 
                delete_option: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migrate_input: MigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migrate_input: MigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migrate_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_pause_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                pause_replication_input: PauseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_pause_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                pause_replication_input: PauseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_pause_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                pause_replication_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_resume_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                resume_replication_input: ResumeReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_resume_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                resume_replication_input: ResumeReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_resume_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                resume_replication_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_resync(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: ResyncInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_resync(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: ResyncInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_resync(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_test_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_input: TestMigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_test_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_input: TestMigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_test_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_test_migrate_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_cleanup_input: TestMigrateCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_test_migrate_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_cleanup_input: TestMigrateCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_test_migrate_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_cleanup_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: UpdateMigrationItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: UpdateMigrationItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationItem]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                **kwargs: Any
            ) -> MigrationItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                take_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationItem]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                take_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationItem]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationNetworkMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: CreateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMapping]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: CreateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMapping]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMapping]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: UpdateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMapping]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: UpdateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMapping]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMapping]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                **kwargs: Any
            ) -> NetworkMapping: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkMapping]: ...

        @distributed_trace
        def list_by_replication_networks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkMapping]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                **kwargs: Any
            ) -> Network: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Network]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Network]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: CreatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: CreatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: UpdatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: UpdatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Policy]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationProtectableItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                protectable_item_name: str, 
                **kwargs: Any
            ) -> ProtectableItem: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                take: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectableItem]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationProtectedItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                add_disks_input: AddDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_add_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                add_disks_input: AddDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_add_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                add_disks_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                apply_recovery_point_input: ApplyRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                apply_recovery_point_input: ApplyRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                apply_recovery_point_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                input: EnableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                input: EnableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                disable_protection_input: DisableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                disable_protection_input: DisableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                disable_protection_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_failover_cancel(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @distributed_trace_async
        async def begin_failover_commit(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: PlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: PlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @distributed_trace_async
        async def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reinstall_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: ReinstallMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_reinstall_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: ReinstallMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_reinstall_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_remove_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                remove_disks_input: RemoveDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_remove_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                remove_disks_input: RemoveDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_remove_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                remove_disks_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @distributed_trace_async
        async def begin_repair_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                reprotect_input: ReverseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                reprotect_input: ReverseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                reprotect_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_resolve_health_errors(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                resolve_health_input: ResolveHealthInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_resolve_health_errors(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                resolve_health_input: ResolveHealthInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_resolve_health_errors(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                resolve_health_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_switch_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                switch_provider_input: SwitchProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_switch_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                switch_provider_input: SwitchProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_switch_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                switch_provider_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                testfailover_input: TestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                testfailover_input: TestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                testfailover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                cleanup_input: TestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                cleanup_input: TestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                cleanup_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: UnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: UnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_protection_input: UpdateReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_protection_input: UpdateReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_protection_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update_appliance(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                appliance_update_input: UpdateApplianceForReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update_appliance(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                appliance_update_input: UpdateApplianceForReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update_appliance(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                appliance_update_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: UpdateMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: UpdateMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @overload
        async def begin_update_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectedItem]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> ReplicationProtectedItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationProtectedItem]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationProtectedItem]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationProtectionClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                apply_cluster_recovery_point_input: ApplyClusterRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                apply_cluster_recovery_point_input: ApplyClusterRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                apply_cluster_recovery_point_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                replication_protection_cluster: ReplicationProtectionCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                replication_protection_cluster: ReplicationProtectionCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                replication_protection_cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @distributed_trace_async
        async def begin_failover_commit(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @distributed_trace_async
        async def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_repair_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                cleanup_input: ClusterTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                cleanup_input: ClusterTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                cleanup_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationProtectionCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> ReplicationProtectionCluster: ...

        @distributed_trace_async
        async def get_operation_results(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> ReplicationProtectionCluster: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationProtectionCluster]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationProtectionCluster]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationProtectionContainerMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                creation_input: CreateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerMapping]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                creation_input: CreateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerMapping]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                creation_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerMapping]: ...

        @overload
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                removal_input: RemoveProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                removal_input: RemoveProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                removal_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                update_input: UpdateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerMapping]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                update_input: UpdateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerMapping]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                update_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainerMapping]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                **kwargs: Any
            ) -> ProtectionContainerMapping: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionContainerMapping]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionContainerMapping]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationProtectionContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                creation_input: CreateProtectionContainerInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                creation_input: CreateProtectionContainerInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                creation_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_discover_protectable_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                discover_protectable_item_request: DiscoverProtectableItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_discover_protectable_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                discover_protectable_item_request: DiscoverProtectableItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_discover_protectable_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                discover_protectable_item_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_switch_cluster_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchClusterProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_switch_cluster_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchClusterProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_switch_cluster_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_switch_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_switch_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @overload
        async def begin_switch_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionContainer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> ProtectionContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionContainer]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionContainer]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationProtectionIntentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                input: CreateProtectionIntentInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                input: CreateProtectionIntentInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                take_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationProtectionIntent]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationRecoveryPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: CreateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: CreateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_failover_cancel(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @distributed_trace_async
        async def begin_failover_commit(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanPlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanPlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @distributed_trace_async
        async def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: UpdateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: UpdateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> RecoveryPlan: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPlan]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationRecoveryServicesProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                add_provider_input: AddRecoveryServicesProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryServicesProvider]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                add_provider_input: AddRecoveryServicesProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryServicesProvider]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                add_provider_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryServicesProvider]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryServicesProvider]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> RecoveryServicesProvider: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryServicesProvider]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryServicesProvider]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationStorageClassificationMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                pairing_input: StorageClassificationMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassificationMapping]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                pairing_input: StorageClassificationMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassificationMapping]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                pairing_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageClassificationMapping]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                **kwargs: Any
            ) -> StorageClassificationMapping: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageClassificationMapping]: ...

        @distributed_trace
        def list_by_replication_storage_classifications(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageClassificationMapping]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationStorageClassificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                **kwargs: Any
            ) -> StorageClassification: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageClassification]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageClassification]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationVaultHealthOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_refresh(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultHealthDetails]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> VaultHealthDetails: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationVaultSettingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                input: VaultSettingCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultSetting]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                input: VaultSettingCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultSetting]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultSetting]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                **kwargs: Any
            ) -> VaultSetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VaultSetting]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.ReplicationvCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                add_v_center_request: AddVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                add_v_center_request: AddVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                add_v_center_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                update_v_center_request: UpdateVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                update_v_center_request: UpdateVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                update_v_center_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                **kwargs: Any
            ) -> VCenter: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VCenter]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VCenter]: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.SupportedOperatingSystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                instance_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> SupportedOperatingSystems: ...


    class azure.mgmt.recoveryservicessiterecovery.aio.operations.TargetComputeSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_replication_protected_items(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TargetComputeSize]: ...


namespace azure.mgmt.recoveryservicessiterecovery.models

    class azure.mgmt.recoveryservicessiterecovery.models.A2AAddDisksInput(AddDisksProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]
        vm_disks: Optional[list[A2AVmDiskInputDetails]]
        vm_managed_disks: Optional[list[A2AVmManagedDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                vm_disks: Optional[list[A2AVmDiskInputDetails]] = ..., 
                vm_managed_disks: Optional[list[A2AVmManagedDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AAgentReinstallBlockingErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                error_message_parameters: Optional[dict[str, str]] = ..., 
                error_tags: Optional[dict[str, str]] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AApplyClusterRecoveryPointInput(ApplyClusterRecoveryPointProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AApplyRecoveryPointInput(ApplyRecoveryPointProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AClusterRecoveryPointDetails(ClusterProviderSpecificRecoveryPointDetails, discriminator='A2A'):
        instance_type: Literal["A2A"]
        nodes: Optional[list[str]]
        recovery_point_sync_type: Optional[Union[str, RecoveryPointSyncType]]

        @overload
        def __init__(
                self, 
                *, 
                nodes: Optional[list[str]] = ..., 
                recovery_point_sync_type: Optional[Union[str, RecoveryPointSyncType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AClusterTestFailoverInput(ClusterTestFailoverProviderSpecificInput, discriminator='A2A'):
        cluster_recovery_point_id: Optional[str]
        individual_node_recovery_points: Optional[list[str]]
        instance_type: Literal["A2A"]

        @overload
        def __init__(
                self, 
                *, 
                cluster_recovery_point_id: Optional[str] = ..., 
                individual_node_recovery_points: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AClusterUnplannedFailoverInput(ClusterUnplannedFailoverProviderSpecificInput, discriminator='A2A'):
        cluster_recovery_point_id: Optional[str]
        individual_node_recovery_points: Optional[list[str]]
        instance_type: Literal["A2A"]

        @overload
        def __init__(
                self, 
                *, 
                cluster_recovery_point_id: Optional[str] = ..., 
                individual_node_recovery_points: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AClusterVmManagedDiskInputDetails(_Model):
        disk_encryption_info: Optional[DiskEncryptionInfo]
        disk_id: str
        primary_staging_azure_storage_account_id: str
        recovery_disk_access_id: Optional[str]
        recovery_disk_encryption_set_id: Optional[str]
        recovery_network_access_policy: Optional[Union[str, DiskNetworkAccessPolicy]]
        recovery_public_network_access: Optional[Union[str, DiskPublicNetworkAccess]]
        recovery_replica_disk_account_type: Optional[str]
        recovery_resource_group_id: str
        recovery_target_disk_account_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                disk_id: str, 
                primary_staging_azure_storage_account_id: str, 
                recovery_disk_access_id: Optional[str] = ..., 
                recovery_disk_encryption_set_id: Optional[str] = ..., 
                recovery_network_access_policy: Optional[Union[str, DiskNetworkAccessPolicy]] = ..., 
                recovery_public_network_access: Optional[Union[str, DiskPublicNetworkAccess]] = ..., 
                recovery_replica_disk_account_type: Optional[str] = ..., 
                recovery_resource_group_id: str, 
                recovery_target_disk_account_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AContainerCreationInput(ReplicationProviderSpecificContainerCreationInput, discriminator='A2A'):
        instance_type: Literal["A2A"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AContainerMappingInput(ReplicationProviderSpecificContainerMappingInput, discriminator='A2A'):
        agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]]
        automation_account_arm_id: Optional[str]
        automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]]
        instance_type: Literal["A2A"]

        @overload
        def __init__(
                self, 
                *, 
                agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]] = ..., 
                automation_account_arm_id: Optional[str] = ..., 
                automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ACreateProtectionIntentInput(CreateProtectionIntentProviderSpecificDetails, discriminator='A2A'):
        agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]]
        auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]]
        automation_account_arm_id: Optional[str]
        automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]]
        disk_encryption_info: Optional[DiskEncryptionInfo]
        fabric_object_id: str
        instance_type: Literal["A2A"]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        primary_location: str
        primary_staging_storage_account_custom_input: Optional[StorageAccountCustomDetails]
        protection_profile_custom_input: Optional[ProtectionProfileCustomDetails]
        recovery_availability_set_custom_input: Optional[RecoveryAvailabilitySetCustomDetails]
        recovery_availability_type: Union[str, A2ARecoveryAvailabilityType]
        recovery_availability_zone: Optional[str]
        recovery_boot_diag_storage_account: Optional[StorageAccountCustomDetails]
        recovery_location: str
        recovery_proximity_placement_group_custom_input: Optional[RecoveryProximityPlacementGroupCustomDetails]
        recovery_resource_group_id: str
        recovery_subscription_id: str
        recovery_virtual_network_custom_input: Optional[RecoveryVirtualNetworkCustomDetails]
        vm_disks: Optional[list[A2AProtectionIntentDiskInputDetails]]
        vm_managed_disks: Optional[list[A2AProtectionIntentManagedDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]] = ..., 
                auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]] = ..., 
                automation_account_arm_id: Optional[str] = ..., 
                automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]] = ..., 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                fabric_object_id: str, 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                primary_location: str, 
                primary_staging_storage_account_custom_input: Optional[StorageAccountCustomDetails] = ..., 
                protection_profile_custom_input: Optional[ProtectionProfileCustomDetails] = ..., 
                recovery_availability_set_custom_input: Optional[RecoveryAvailabilitySetCustomDetails] = ..., 
                recovery_availability_type: Union[str, A2ARecoveryAvailabilityType], 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_boot_diag_storage_account: Optional[StorageAccountCustomDetails] = ..., 
                recovery_location: str, 
                recovery_proximity_placement_group_custom_input: Optional[RecoveryProximityPlacementGroupCustomDetails] = ..., 
                recovery_resource_group_id: str, 
                recovery_subscription_id: str, 
                recovery_virtual_network_custom_input: Optional[RecoveryVirtualNetworkCustomDetails] = ..., 
                vm_disks: Optional[list[A2AProtectionIntentDiskInputDetails]] = ..., 
                vm_managed_disks: Optional[list[A2AProtectionIntentManagedDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ACrossClusterMigrationApplyRecoveryPointInput(ApplyRecoveryPointProviderSpecificInput, discriminator='A2ACrossClusterMigration'):
        instance_type: Literal["A2ACrossClusterMigration"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ACrossClusterMigrationContainerCreationInput(ReplicationProviderSpecificContainerCreationInput, discriminator='A2ACrossClusterMigration'):
        instance_type: Literal["A2ACrossClusterMigration"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ACrossClusterMigrationEnableProtectionInput(EnableProtectionProviderSpecificInput, discriminator='A2ACrossClusterMigration'):
        fabric_object_id: Optional[str]
        instance_type: Literal["A2ACrossClusterMigration"]
        recovery_container_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_object_id: Optional[str] = ..., 
                recovery_container_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ACrossClusterMigrationPolicyCreationInput(PolicyProviderSpecificInput, discriminator='A2ACrossClusterMigration'):
        instance_type: Literal["A2ACrossClusterMigration"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ACrossClusterMigrationReplicationDetails(ReplicationProviderSpecificSettings, discriminator='A2ACrossClusterMigration'):
        fabric_object_id: Optional[str]
        instance_type: Literal["A2ACrossClusterMigration"]
        lifecycle_id: Optional[str]
        os_type: Optional[str]
        primary_fabric_location: Optional[str]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_object_id: Optional[str] = ..., 
                lifecycle_id: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                primary_fabric_location: Optional[str] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AEnableProtectionInput(EnableProtectionProviderSpecificInput, discriminator='A2A'):
        auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]]
        disk_encryption_info: Optional[DiskEncryptionInfo]
        fabric_object_id: str
        instance_type: Literal["A2A"]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        platform_fault_domain: Optional[int]
        protection_cluster_id: Optional[str]
        recovery_availability_set_id: Optional[str]
        recovery_availability_zone: Optional[str]
        recovery_azure_network_id: Optional[str]
        recovery_boot_diag_storage_account_id: Optional[str]
        recovery_capacity_reservation_group_id: Optional[str]
        recovery_cloud_service_id: Optional[str]
        recovery_confidential_data_disk_encryption_identity: Optional[str]
        recovery_container_id: Optional[str]
        recovery_extended_location: Optional[ExtendedLocation]
        recovery_proximity_placement_group_id: Optional[str]
        recovery_resource_group_id: Optional[str]
        recovery_subnet_name: Optional[str]
        recovery_virtual_machine_scale_set_id: Optional[str]
        vm_disks: Optional[list[A2AVmDiskInputDetails]]
        vm_managed_disks: Optional[list[A2AVmManagedDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]] = ..., 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                fabric_object_id: str, 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                protection_cluster_id: Optional[str] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_azure_network_id: Optional[str] = ..., 
                recovery_boot_diag_storage_account_id: Optional[str] = ..., 
                recovery_capacity_reservation_group_id: Optional[str] = ..., 
                recovery_cloud_service_id: Optional[str] = ..., 
                recovery_confidential_data_disk_encryption_identity: Optional[str] = ..., 
                recovery_container_id: Optional[str] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_proximity_placement_group_id: Optional[str] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                recovery_subnet_name: Optional[str] = ..., 
                recovery_virtual_machine_scale_set_id: Optional[str] = ..., 
                vm_disks: Optional[list[A2AVmDiskInputDetails]] = ..., 
                vm_managed_disks: Optional[list[A2AVmManagedDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AEventDetails(EventProviderSpecificDetails, discriminator='A2A'):
        fabric_location: Optional[str]
        fabric_name: Optional[str]
        fabric_object_id: Optional[str]
        instance_type: Literal["A2A"]
        protected_item_name: Optional[str]
        remote_fabric_location: Optional[str]
        remote_fabric_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_location: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                fabric_object_id: Optional[str] = ..., 
                protected_item_name: Optional[str] = ..., 
                remote_fabric_location: Optional[str] = ..., 
                remote_fabric_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AExtendedLocationDetails(_Model):
        primary_extended_location: Optional[ExtendedLocation]
        recovery_extended_location: Optional[ExtendedLocation]

        @overload
        def __init__(
                self, 
                *, 
                primary_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AFabricSpecificLocationDetails(_Model):
        initial_primary_extended_location: Optional[ExtendedLocation]
        initial_primary_fabric_location: Optional[str]
        initial_primary_zone: Optional[str]
        initial_recovery_extended_location: Optional[ExtendedLocation]
        initial_recovery_fabric_location: Optional[str]
        initial_recovery_zone: Optional[str]
        primary_extended_location: Optional[ExtendedLocation]
        primary_fabric_location: Optional[str]
        primary_zone: Optional[str]
        recovery_extended_location: Optional[ExtendedLocation]
        recovery_fabric_location: Optional[str]
        recovery_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initial_primary_extended_location: Optional[ExtendedLocation] = ..., 
                initial_primary_fabric_location: Optional[str] = ..., 
                initial_primary_zone: Optional[str] = ..., 
                initial_recovery_extended_location: Optional[ExtendedLocation] = ..., 
                initial_recovery_fabric_location: Optional[str] = ..., 
                initial_recovery_zone: Optional[str] = ..., 
                primary_extended_location: Optional[ExtendedLocation] = ..., 
                primary_fabric_location: Optional[str] = ..., 
                primary_zone: Optional[str] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_fabric_location: Optional[str] = ..., 
                recovery_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2APolicyCreationInput(PolicyProviderSpecificInput, discriminator='A2A'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["A2A"]
        multi_vm_sync_status: Union[str, SetMultiVmSyncStatus]
        recovery_point_history: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Union[str, SetMultiVmSyncStatus], 
                recovery_point_history: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2APolicyDetails(PolicyProviderSpecificDetails, discriminator='A2A'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["A2A"]
        multi_vm_sync_status: Optional[str]
        recovery_point_history: Optional[int]
        recovery_point_threshold_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Optional[str] = ..., 
                recovery_point_history: Optional[int] = ..., 
                recovery_point_threshold_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AProtectedDiskDetails(_Model):
        allowed_disk_level_operation: Optional[list[str]]
        data_pending_at_source_agent_in_mb: Optional[float]
        data_pending_in_staging_storage_account_in_mb: Optional[float]
        dek_key_vault_arm_id: Optional[str]
        disk_capacity_in_bytes: Optional[int]
        disk_name: Optional[str]
        disk_state: Optional[str]
        disk_type: Optional[str]
        disk_uri: Optional[str]
        failover_disk_name: Optional[str]
        is_disk_encrypted: Optional[bool]
        is_disk_key_encrypted: Optional[bool]
        kek_key_vault_arm_id: Optional[str]
        key_identifier: Optional[str]
        monitoring_job_type: Optional[str]
        monitoring_percentage_completion: Optional[int]
        primary_disk_azure_storage_account_id: Optional[str]
        primary_staging_azure_storage_account_id: Optional[str]
        recovery_azure_storage_account_id: Optional[str]
        recovery_disk_uri: Optional[str]
        resync_required: Optional[bool]
        secret_identifier: Optional[str]
        tfo_disk_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_disk_level_operation: Optional[list[str]] = ..., 
                data_pending_at_source_agent_in_mb: Optional[float] = ..., 
                data_pending_in_staging_storage_account_in_mb: Optional[float] = ..., 
                dek_key_vault_arm_id: Optional[str] = ..., 
                disk_capacity_in_bytes: Optional[int] = ..., 
                disk_name: Optional[str] = ..., 
                disk_state: Optional[str] = ..., 
                disk_type: Optional[str] = ..., 
                disk_uri: Optional[str] = ..., 
                failover_disk_name: Optional[str] = ..., 
                is_disk_encrypted: Optional[bool] = ..., 
                is_disk_key_encrypted: Optional[bool] = ..., 
                kek_key_vault_arm_id: Optional[str] = ..., 
                key_identifier: Optional[str] = ..., 
                monitoring_job_type: Optional[str] = ..., 
                monitoring_percentage_completion: Optional[int] = ..., 
                primary_disk_azure_storage_account_id: Optional[str] = ..., 
                primary_staging_azure_storage_account_id: Optional[str] = ..., 
                recovery_azure_storage_account_id: Optional[str] = ..., 
                recovery_disk_uri: Optional[str] = ..., 
                resync_required: Optional[bool] = ..., 
                secret_identifier: Optional[str] = ..., 
                tfo_disk_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AProtectedItemDetail(_Model):
        disk_encryption_info: Optional[DiskEncryptionInfo]
        recovery_availability_set_id: Optional[str]
        recovery_availability_zone: Optional[str]
        recovery_boot_diag_storage_account_id: Optional[str]
        recovery_capacity_reservation_group_id: Optional[str]
        recovery_proximity_placement_group_id: Optional[str]
        recovery_resource_group_id: Optional[str]
        recovery_virtual_machine_scale_set_id: Optional[str]
        replication_protected_item_name: Optional[str]
        vm_managed_disks: Optional[list[A2AClusterVmManagedDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_boot_diag_storage_account_id: Optional[str] = ..., 
                recovery_capacity_reservation_group_id: Optional[str] = ..., 
                recovery_proximity_placement_group_id: Optional[str] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                recovery_virtual_machine_scale_set_id: Optional[str] = ..., 
                replication_protected_item_name: Optional[str] = ..., 
                vm_managed_disks: Optional[list[A2AClusterVmManagedDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AProtectedManagedDiskDetails(_Model):
        allowed_disk_level_operation: Optional[list[str]]
        confidential_disk_encryption_info: Optional[ConfidentialDiskEncryptionInfo]
        data_pending_at_source_agent_in_mb: Optional[float]
        data_pending_in_staging_storage_account_in_mb: Optional[float]
        dek_key_vault_arm_id: Optional[str]
        disk_capacity_in_bytes: Optional[int]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_state: Optional[str]
        disk_type: Optional[str]
        failover_disk_name: Optional[str]
        is_disk_encrypted: Optional[bool]
        is_disk_key_encrypted: Optional[bool]
        kek_key_vault_arm_id: Optional[str]
        key_identifier: Optional[str]
        monitoring_job_type: Optional[str]
        monitoring_percentage_completion: Optional[int]
        primary_disk_encryption_set_id: Optional[str]
        primary_staging_azure_storage_account_id: Optional[str]
        recovery_disk_access_id: Optional[str]
        recovery_disk_encryption_set_id: Optional[str]
        recovery_network_access_policy: Optional[Union[str, DiskNetworkAccessPolicy]]
        recovery_orignal_target_disk_id: Optional[str]
        recovery_public_network_access: Optional[Union[str, DiskPublicNetworkAccess]]
        recovery_replica_disk_account_type: Optional[str]
        recovery_replica_disk_id: Optional[str]
        recovery_resource_group_id: Optional[str]
        recovery_target_disk_account_type: Optional[str]
        recovery_target_disk_id: Optional[str]
        resync_required: Optional[bool]
        secret_identifier: Optional[str]
        tfo_disk_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_disk_level_operation: Optional[list[str]] = ..., 
                data_pending_at_source_agent_in_mb: Optional[float] = ..., 
                data_pending_in_staging_storage_account_in_mb: Optional[float] = ..., 
                dek_key_vault_arm_id: Optional[str] = ..., 
                disk_capacity_in_bytes: Optional[int] = ..., 
                disk_id: Optional[str] = ..., 
                disk_name: Optional[str] = ..., 
                disk_state: Optional[str] = ..., 
                disk_type: Optional[str] = ..., 
                failover_disk_name: Optional[str] = ..., 
                is_disk_encrypted: Optional[bool] = ..., 
                is_disk_key_encrypted: Optional[bool] = ..., 
                kek_key_vault_arm_id: Optional[str] = ..., 
                key_identifier: Optional[str] = ..., 
                monitoring_job_type: Optional[str] = ..., 
                monitoring_percentage_completion: Optional[int] = ..., 
                primary_disk_encryption_set_id: Optional[str] = ..., 
                primary_staging_azure_storage_account_id: Optional[str] = ..., 
                recovery_disk_access_id: Optional[str] = ..., 
                recovery_disk_encryption_set_id: Optional[str] = ..., 
                recovery_network_access_policy: Optional[Union[str, DiskNetworkAccessPolicy]] = ..., 
                recovery_orignal_target_disk_id: Optional[str] = ..., 
                recovery_public_network_access: Optional[Union[str, DiskPublicNetworkAccess]] = ..., 
                recovery_replica_disk_account_type: Optional[str] = ..., 
                recovery_replica_disk_id: Optional[str] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                recovery_target_disk_account_type: Optional[str] = ..., 
                recovery_target_disk_id: Optional[str] = ..., 
                resync_required: Optional[bool] = ..., 
                secret_identifier: Optional[str] = ..., 
                tfo_disk_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AProtectionContainerMappingDetails(ProtectionContainerMappingProviderSpecificDetails, discriminator='A2A'):
        agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]]
        automation_account_arm_id: Optional[str]
        automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]]
        instance_type: Literal["A2A"]
        job_schedule_name: Optional[str]
        schedule_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]] = ..., 
                automation_account_arm_id: Optional[str] = ..., 
                automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]] = ..., 
                job_schedule_name: Optional[str] = ..., 
                schedule_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AProtectionIntentDiskInputDetails(_Model):
        disk_uri: str
        primary_staging_storage_account_custom_input: Optional[StorageAccountCustomDetails]
        recovery_azure_storage_account_custom_input: Optional[StorageAccountCustomDetails]

        @overload
        def __init__(
                self, 
                *, 
                disk_uri: str, 
                primary_staging_storage_account_custom_input: Optional[StorageAccountCustomDetails] = ..., 
                recovery_azure_storage_account_custom_input: Optional[StorageAccountCustomDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AProtectionIntentManagedDiskInputDetails(_Model):
        disk_encryption_info: Optional[DiskEncryptionInfo]
        disk_id: str
        primary_staging_storage_account_custom_input: Optional[StorageAccountCustomDetails]
        recovery_disk_encryption_set_id: Optional[str]
        recovery_replica_disk_account_type: Optional[str]
        recovery_resource_group_custom_input: Optional[RecoveryResourceGroupCustomDetails]
        recovery_target_disk_account_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                disk_id: str, 
                primary_staging_storage_account_custom_input: Optional[StorageAccountCustomDetails] = ..., 
                recovery_disk_encryption_set_id: Optional[str] = ..., 
                recovery_replica_disk_account_type: Optional[str] = ..., 
                recovery_resource_group_custom_input: Optional[RecoveryResourceGroupCustomDetails] = ..., 
                recovery_target_disk_account_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ARecoveryAvailabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY_SET = "AvailabilitySet"
        AVAILABILITY_ZONE = "AvailabilityZone"
        SINGLE = "Single"


    class azure.mgmt.recoveryservicessiterecovery.models.A2ARecoveryPointDetails(ProviderSpecificRecoveryPointDetails, discriminator='A2A'):
        disks: Optional[list[str]]
        instance_type: Literal["A2A"]
        recovery_point_sync_type: Optional[Union[str, RecoveryPointSyncType]]

        @overload
        def __init__(
                self, 
                *, 
                disks: Optional[list[str]] = ..., 
                recovery_point_sync_type: Optional[Union[str, RecoveryPointSyncType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ARemoveDisksInput(RemoveDisksProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]
        vm_disks_uris: Optional[list[str]]
        vm_managed_disks_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                vm_disks_uris: Optional[list[str]] = ..., 
                vm_managed_disks_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AReplicationDetails(ReplicationProviderSpecificSettings, discriminator='A2A'):
        agent_certificate_expiry_date: Optional[datetime]
        agent_expiry_date: Optional[datetime]
        agent_reinstall_attempt_to_version: Optional[str]
        agent_version: Optional[str]
        auto_agent_upgrade_retry_count: Optional[int]
        auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]]
        churn_option_selected: Optional[Union[str, ChurnOptionSelected]]
        distro_name: Optional[str]
        distro_name_for_which_agent_is_installed: Optional[str]
        fabric_object_id: Optional[str]
        initial_primary_extended_location: Optional[ExtendedLocation]
        initial_primary_fabric_location: Optional[str]
        initial_primary_zone: Optional[str]
        initial_recovery_extended_location: Optional[ExtendedLocation]
        initial_recovery_fabric_location: Optional[str]
        initial_recovery_zone: Optional[str]
        instance_type: Literal["A2A"]
        is_agent_reinstall_required: Optional[bool]
        is_agent_upgrade_in_progress: Optional[bool]
        is_agent_upgrade_retry_threshold_exhausted: Optional[bool]
        is_agent_upgradeable: Optional[bool]
        is_cluster_infra_ready: Optional[bool]
        is_replication_agent_certificate_update_required: Optional[bool]
        is_replication_agent_update_required: Optional[bool]
        last_heartbeat: Optional[datetime]
        last_rpo_calculated_time: Optional[datetime]
        lifecycle_id: Optional[str]
        management_id: Optional[str]
        monitoring_job_type: Optional[str]
        monitoring_percentage_completion: Optional[int]
        multi_vm_group_create_option: Optional[Union[str, MultiVmGroupCreateOption]]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        os_family_name: Optional[str]
        os_type: Optional[str]
        platform_fault_domain: Optional[int]
        primary_availability_zone: Optional[str]
        primary_extended_location: Optional[ExtendedLocation]
        primary_fabric_location: Optional[str]
        protected_disks: Optional[list[A2AProtectedDiskDetails]]
        protected_managed_disks: Optional[list[A2AProtectedManagedDiskDetails]]
        protection_cluster_id: Optional[str]
        reasons_blocking_re_install: Optional[str]
        reasons_blocking_reinstall_details: Optional[list[A2AAgentReinstallBlockingErrorDetails]]
        recovery_availability_set: Optional[str]
        recovery_availability_zone: Optional[str]
        recovery_azure_generation: Optional[str]
        recovery_azure_resource_group_id: Optional[str]
        recovery_azure_vm_name: Optional[str]
        recovery_azure_vm_size: Optional[str]
        recovery_boot_diag_storage_account_id: Optional[str]
        recovery_capacity_reservation_group_id: Optional[str]
        recovery_cloud_service: Optional[str]
        recovery_confidential_data_disk_encryption_identity: Optional[str]
        recovery_extended_location: Optional[ExtendedLocation]
        recovery_fabric_location: Optional[str]
        recovery_fabric_object_id: Optional[str]
        recovery_proximity_placement_group_id: Optional[str]
        recovery_virtual_machine_scale_set_id: Optional[str]
        rpo_in_seconds: Optional[int]
        selected_recovery_azure_network_id: Optional[str]
        selected_tfo_azure_network_id: Optional[str]
        test_failover_recovery_fabric_object_id: Optional[str]
        tfo_azure_vm_name: Optional[str]
        unprotected_disks: Optional[list[A2AUnprotectedDiskDetails]]
        vm_encryption_type: Optional[Union[str, VmEncryptionType]]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]
        vm_synced_config_details: Optional[AzureToAzureVmSyncedConfigDetails]

        @overload
        def __init__(
                self, 
                *, 
                agent_expiry_date: Optional[datetime] = ..., 
                agent_reinstall_attempt_to_version: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                auto_agent_upgrade_retry_count: Optional[int] = ..., 
                auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]] = ..., 
                distro_name: Optional[str] = ..., 
                distro_name_for_which_agent_is_installed: Optional[str] = ..., 
                fabric_object_id: Optional[str] = ..., 
                initial_primary_extended_location: Optional[ExtendedLocation] = ..., 
                initial_recovery_extended_location: Optional[ExtendedLocation] = ..., 
                is_agent_reinstall_required: Optional[bool] = ..., 
                is_agent_upgrade_in_progress: Optional[bool] = ..., 
                is_agent_upgrade_retry_threshold_exhausted: Optional[bool] = ..., 
                is_agent_upgradeable: Optional[bool] = ..., 
                is_cluster_infra_ready: Optional[bool] = ..., 
                is_replication_agent_certificate_update_required: Optional[bool] = ..., 
                is_replication_agent_update_required: Optional[bool] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                lifecycle_id: Optional[str] = ..., 
                management_id: Optional[str] = ..., 
                monitoring_job_type: Optional[str] = ..., 
                monitoring_percentage_completion: Optional[int] = ..., 
                multi_vm_group_create_option: Optional[Union[str, MultiVmGroupCreateOption]] = ..., 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                os_family_name: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                primary_availability_zone: Optional[str] = ..., 
                primary_extended_location: Optional[ExtendedLocation] = ..., 
                primary_fabric_location: Optional[str] = ..., 
                protected_disks: Optional[list[A2AProtectedDiskDetails]] = ..., 
                protected_managed_disks: Optional[list[A2AProtectedManagedDiskDetails]] = ..., 
                protection_cluster_id: Optional[str] = ..., 
                reasons_blocking_re_install: Optional[str] = ..., 
                reasons_blocking_reinstall_details: Optional[list[A2AAgentReinstallBlockingErrorDetails]] = ..., 
                recovery_availability_set: Optional[str] = ..., 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_azure_resource_group_id: Optional[str] = ..., 
                recovery_azure_vm_name: Optional[str] = ..., 
                recovery_azure_vm_size: Optional[str] = ..., 
                recovery_boot_diag_storage_account_id: Optional[str] = ..., 
                recovery_capacity_reservation_group_id: Optional[str] = ..., 
                recovery_cloud_service: Optional[str] = ..., 
                recovery_confidential_data_disk_encryption_identity: Optional[str] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_fabric_location: Optional[str] = ..., 
                recovery_fabric_object_id: Optional[str] = ..., 
                recovery_proximity_placement_group_id: Optional[str] = ..., 
                recovery_virtual_machine_scale_set_id: Optional[str] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                selected_recovery_azure_network_id: Optional[str] = ..., 
                selected_tfo_azure_network_id: Optional[str] = ..., 
                test_failover_recovery_fabric_object_id: Optional[str] = ..., 
                tfo_azure_vm_name: Optional[str] = ..., 
                unprotected_disks: Optional[list[A2AUnprotectedDiskDetails]] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ..., 
                vm_synced_config_details: Optional[AzureToAzureVmSyncedConfigDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AReplicationIntentDetails(ReplicationProtectionIntentProviderSpecificSettings, discriminator='A2A'):
        agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]]
        auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]]
        automation_account_arm_id: Optional[str]
        automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]]
        disk_encryption_info: Optional[DiskEncryptionInfo]
        fabric_object_id: Optional[str]
        instance_type: Literal["A2A"]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        primary_location: Optional[str]
        primary_staging_storage_account: Optional[StorageAccountCustomDetails]
        protection_profile: Optional[ProtectionProfileCustomDetails]
        recovery_availability_set: Optional[RecoveryAvailabilitySetCustomDetails]
        recovery_availability_type: str
        recovery_availability_zone: Optional[str]
        recovery_boot_diag_storage_account: Optional[StorageAccountCustomDetails]
        recovery_location: Optional[str]
        recovery_proximity_placement_group: Optional[RecoveryProximityPlacementGroupCustomDetails]
        recovery_resource_group_id: Optional[str]
        recovery_subscription_id: Optional[str]
        recovery_virtual_network: Optional[RecoveryVirtualNetworkCustomDetails]
        vm_disks: Optional[list[A2AProtectionIntentDiskInputDetails]]
        vm_managed_disks: Optional[list[A2AProtectionIntentManagedDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]] = ..., 
                auto_protection_of_data_disk: Optional[Union[str, AutoProtectionOfDataDisk]] = ..., 
                automation_account_arm_id: Optional[str] = ..., 
                automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]] = ..., 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                fabric_object_id: Optional[str] = ..., 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                primary_location: Optional[str] = ..., 
                primary_staging_storage_account: Optional[StorageAccountCustomDetails] = ..., 
                protection_profile: Optional[ProtectionProfileCustomDetails] = ..., 
                recovery_availability_set: Optional[RecoveryAvailabilitySetCustomDetails] = ..., 
                recovery_availability_type: str, 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_boot_diag_storage_account: Optional[StorageAccountCustomDetails] = ..., 
                recovery_location: Optional[str] = ..., 
                recovery_proximity_placement_group: Optional[RecoveryProximityPlacementGroupCustomDetails] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                recovery_subscription_id: Optional[str] = ..., 
                recovery_virtual_network: Optional[RecoveryVirtualNetworkCustomDetails] = ..., 
                vm_disks: Optional[list[A2AProtectionIntentDiskInputDetails]] = ..., 
                vm_managed_disks: Optional[list[A2AProtectionIntentManagedDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AReplicationProtectionClusterDetails(ReplicationClusterProviderSpecificSettings, discriminator='A2A'):
        cluster_management_id: Optional[str]
        failover_recovery_point_id: Optional[str]
        initial_primary_extended_location: Optional[ExtendedLocation]
        initial_primary_fabric_location: Optional[str]
        initial_primary_zone: Optional[str]
        initial_recovery_extended_location: Optional[ExtendedLocation]
        initial_recovery_fabric_location: Optional[str]
        initial_recovery_zone: Optional[str]
        instance_type: Literal["A2A"]
        last_rpo_calculated_time: Optional[datetime]
        lifecycle_id: Optional[str]
        multi_vm_group_create_option: Optional[Union[str, MultiVmGroupCreateOption]]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        primary_availability_zone: Optional[str]
        primary_extended_location: Optional[ExtendedLocation]
        primary_fabric_location: Optional[str]
        recovery_availability_zone: Optional[str]
        recovery_extended_location: Optional[ExtendedLocation]
        recovery_fabric_location: Optional[str]
        rpo_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cluster_management_id: Optional[str] = ..., 
                failover_recovery_point_id: Optional[str] = ..., 
                initial_primary_extended_location: Optional[ExtendedLocation] = ..., 
                initial_primary_fabric_location: Optional[str] = ..., 
                initial_primary_zone: Optional[str] = ..., 
                initial_recovery_extended_location: Optional[ExtendedLocation] = ..., 
                initial_recovery_fabric_location: Optional[str] = ..., 
                initial_recovery_zone: Optional[str] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                lifecycle_id: Optional[str] = ..., 
                multi_vm_group_create_option: Optional[Union[str, MultiVmGroupCreateOption]] = ..., 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                primary_availability_zone: Optional[str] = ..., 
                primary_extended_location: Optional[ExtendedLocation] = ..., 
                primary_fabric_location: Optional[str] = ..., 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_fabric_location: Optional[str] = ..., 
                rpo_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AReprotectInput(ReverseReplicationProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]
        policy_id: Optional[str]
        recovery_availability_set_id: Optional[str]
        recovery_cloud_service_id: Optional[str]
        recovery_container_id: Optional[str]
        recovery_resource_group_id: Optional[str]
        vm_disks: Optional[list[A2AVmDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: Optional[str] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_cloud_service_id: Optional[str] = ..., 
                recovery_container_id: Optional[str] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                vm_disks: Optional[list[A2AVmDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ARpRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATEST = "Latest"
        LATEST_APPLICATION_CONSISTENT = "LatestApplicationConsistent"
        LATEST_CRASH_CONSISTENT = "LatestCrashConsistent"
        LATEST_PROCESSED = "LatestProcessed"


    class azure.mgmt.recoveryservicessiterecovery.models.A2ASharedDiskIRErrorDetails(_Model):
        error_code: Optional[str]
        error_code_enum: Optional[str]
        error_message: Optional[str]
        possible_causes: Optional[str]
        recommended_action: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.A2ASharedDiskReplicationDetails(SharedDiskReplicationProviderSpecificSettings, discriminator='A2A'):
        failover_recovery_point_id: Optional[str]
        instance_type: Literal["A2A"]
        last_rpo_calculated_time: Optional[datetime]
        management_id: Optional[str]
        monitoring_job_type: Optional[str]
        monitoring_percentage_completion: Optional[int]
        primary_fabric_location: Optional[str]
        protected_managed_disks: Optional[list[A2AProtectedManagedDiskDetails]]
        recovery_fabric_location: Optional[str]
        rpo_in_seconds: Optional[int]
        shared_disk_ir_errors: Optional[list[A2ASharedDiskIRErrorDetails]]
        unprotected_disks: Optional[list[A2AUnprotectedDiskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                failover_recovery_point_id: Optional[str] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                management_id: Optional[str] = ..., 
                monitoring_job_type: Optional[str] = ..., 
                monitoring_percentage_completion: Optional[int] = ..., 
                primary_fabric_location: Optional[str] = ..., 
                protected_managed_disks: Optional[list[A2AProtectedManagedDiskDetails]] = ..., 
                recovery_fabric_location: Optional[str] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                shared_disk_ir_errors: Optional[list[A2ASharedDiskIRErrorDetails]] = ..., 
                unprotected_disks: Optional[list[A2AUnprotectedDiskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ASwitchClusterProtectionInput(SwitchClusterProtectionProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]
        policy_id: Optional[str]
        protected_items_detail: Optional[list[A2AProtectedItemDetail]]
        recovery_container_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: Optional[str] = ..., 
                protected_items_detail: Optional[list[A2AProtectedItemDetail]] = ..., 
                recovery_container_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ASwitchProtectionInput(SwitchProtectionProviderSpecificInput, discriminator='A2A'):
        disk_encryption_info: Optional[DiskEncryptionInfo]
        instance_type: Literal["A2A"]
        platform_fault_domain: Optional[int]
        policy_id: Optional[str]
        recovery_availability_set_id: Optional[str]
        recovery_availability_zone: Optional[str]
        recovery_boot_diag_storage_account_id: Optional[str]
        recovery_capacity_reservation_group_id: Optional[str]
        recovery_cloud_service_id: Optional[str]
        recovery_confidential_data_disk_encryption_identity: Optional[str]
        recovery_container_id: Optional[str]
        recovery_proximity_placement_group_id: Optional[str]
        recovery_resource_group_id: Optional[str]
        recovery_virtual_machine_scale_set_id: Optional[str]
        vm_disks: Optional[list[A2AVmDiskInputDetails]]
        vm_managed_disks: Optional[list[A2AVmManagedDiskInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                policy_id: Optional[str] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_boot_diag_storage_account_id: Optional[str] = ..., 
                recovery_capacity_reservation_group_id: Optional[str] = ..., 
                recovery_cloud_service_id: Optional[str] = ..., 
                recovery_confidential_data_disk_encryption_identity: Optional[str] = ..., 
                recovery_container_id: Optional[str] = ..., 
                recovery_proximity_placement_group_id: Optional[str] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                recovery_virtual_machine_scale_set_id: Optional[str] = ..., 
                vm_disks: Optional[list[A2AVmDiskInputDetails]] = ..., 
                vm_managed_disks: Optional[list[A2AVmManagedDiskInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2ATestFailoverInput(TestFailoverProviderSpecificInput, discriminator='A2A'):
        cloud_service_creation_option: Optional[str]
        instance_type: Literal["A2A"]
        recovery_point_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_service_creation_option: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AUnplannedFailoverInput(UnplannedFailoverProviderSpecificInput, discriminator='A2A'):
        cloud_service_creation_option: Optional[str]
        instance_type: Literal["A2A"]
        recovery_point_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_service_creation_option: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AUnprotectedDiskDetails(_Model):
        disk_auto_protection_status: Optional[Union[str, AutoProtectionOfDataDisk]]
        disk_lun_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_auto_protection_status: Optional[Union[str, AutoProtectionOfDataDisk]] = ..., 
                disk_lun_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AUpdateContainerMappingInput(ReplicationProviderSpecificUpdateContainerMappingInput, discriminator='A2A'):
        agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]]
        automation_account_arm_id: Optional[str]
        automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]]
        instance_type: Literal["A2A"]

        @overload
        def __init__(
                self, 
                *, 
                agent_auto_update_status: Optional[Union[str, AgentAutoUpdateStatus]] = ..., 
                automation_account_arm_id: Optional[str] = ..., 
                automation_account_authentication_type: Optional[Union[str, AutomationAccountAuthenticationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AUpdateReplicationProtectedItemInput(UpdateReplicationProtectedItemProviderInput, discriminator='A2A'):
        disk_encryption_info: Optional[DiskEncryptionInfo]
        instance_type: Literal["A2A"]
        managed_disk_update_details: Optional[list[A2AVmManagedDiskUpdateDetails]]
        platform_fault_domain: Optional[int]
        recovery_availability_zone: Optional[str]
        recovery_boot_diag_storage_account_id: Optional[str]
        recovery_capacity_reservation_group_id: Optional[str]
        recovery_cloud_service_id: Optional[str]
        recovery_confidential_data_disk_encryption_identity: Optional[str]
        recovery_proximity_placement_group_id: Optional[str]
        recovery_resource_group_id: Optional[str]
        recovery_virtual_machine_scale_set_id: Optional[str]
        tfo_azure_vm_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                managed_disk_update_details: Optional[list[A2AVmManagedDiskUpdateDetails]] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                recovery_availability_zone: Optional[str] = ..., 
                recovery_boot_diag_storage_account_id: Optional[str] = ..., 
                recovery_capacity_reservation_group_id: Optional[str] = ..., 
                recovery_cloud_service_id: Optional[str] = ..., 
                recovery_confidential_data_disk_encryption_identity: Optional[str] = ..., 
                recovery_proximity_placement_group_id: Optional[str] = ..., 
                recovery_resource_group_id: Optional[str] = ..., 
                recovery_virtual_machine_scale_set_id: Optional[str] = ..., 
                tfo_azure_vm_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AVmDiskInputDetails(_Model):
        disk_uri: str
        primary_staging_azure_storage_account_id: str
        recovery_azure_storage_account_id: str

        @overload
        def __init__(
                self, 
                *, 
                disk_uri: str, 
                primary_staging_azure_storage_account_id: str, 
                recovery_azure_storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AVmManagedDiskInputDetails(_Model):
        confidential_disk_encryption_info: Optional[ConfidentialDiskEncryptionInfo]
        disk_encryption_info: Optional[DiskEncryptionInfo]
        disk_id: str
        primary_staging_azure_storage_account_id: str
        recovery_disk_access_id: Optional[str]
        recovery_disk_encryption_set_id: Optional[str]
        recovery_network_access_policy: Optional[Union[str, DiskNetworkAccessPolicy]]
        recovery_public_network_access: Optional[Union[str, DiskPublicNetworkAccess]]
        recovery_replica_disk_account_type: Optional[str]
        recovery_resource_group_id: str
        recovery_target_disk_account_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidential_disk_encryption_info: Optional[ConfidentialDiskEncryptionInfo] = ..., 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                disk_id: str, 
                primary_staging_azure_storage_account_id: str, 
                recovery_disk_access_id: Optional[str] = ..., 
                recovery_disk_encryption_set_id: Optional[str] = ..., 
                recovery_network_access_policy: Optional[Union[str, DiskNetworkAccessPolicy]] = ..., 
                recovery_public_network_access: Optional[Union[str, DiskPublicNetworkAccess]] = ..., 
                recovery_replica_disk_account_type: Optional[str] = ..., 
                recovery_resource_group_id: str, 
                recovery_target_disk_account_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AVmManagedDiskUpdateDetails(_Model):
        confidential_disk_encryption_info: Optional[UpdateConfidentialDiskEncryptionInfo]
        disk_encryption_info: Optional[DiskEncryptionInfo]
        disk_id: Optional[str]
        failover_disk_name: Optional[str]
        recovery_replica_disk_account_type: Optional[str]
        recovery_target_disk_account_type: Optional[str]
        tfo_disk_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidential_disk_encryption_info: Optional[UpdateConfidentialDiskEncryptionInfo] = ..., 
                disk_encryption_info: Optional[DiskEncryptionInfo] = ..., 
                disk_id: Optional[str] = ..., 
                failover_disk_name: Optional[str] = ..., 
                recovery_replica_disk_account_type: Optional[str] = ..., 
                recovery_target_disk_account_type: Optional[str] = ..., 
                tfo_disk_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.A2AZoneDetails(_Model):
        source: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ASRTask(_Model):
        allowed_actions: Optional[list[str]]
        custom_details: Optional[TaskTypeDetails]
        end_time: Optional[datetime]
        errors: Optional[list[JobErrorDetails]]
        friendly_name: Optional[str]
        group_task_custom_details: Optional[GroupTaskDetails]
        name: Optional[str]
        start_time: Optional[datetime]
        state: Optional[str]
        state_description: Optional[str]
        task_id: Optional[str]
        task_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_actions: Optional[list[str]] = ..., 
                custom_details: Optional[TaskTypeDetails] = ..., 
                end_time: Optional[datetime] = ..., 
                errors: Optional[list[JobErrorDetails]] = ..., 
                friendly_name: Optional[str] = ..., 
                group_task_custom_details: Optional[GroupTaskDetails] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                state: Optional[str] = ..., 
                state_description: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
                task_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddDisksInput(_Model):
        properties: Optional[AddDisksInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AddDisksInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddDisksInputProperties(_Model):
        provider_specific_details: AddDisksProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: AddDisksProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddDisksProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddRecoveryServicesProviderInput(_Model):
        properties: AddRecoveryServicesProviderInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: AddRecoveryServicesProviderInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddRecoveryServicesProviderInputProperties(_Model):
        authentication_identity_input: IdentityProviderInput
        bios_id: Optional[str]
        data_plane_authentication_identity_input: Optional[IdentityProviderInput]
        machine_id: Optional[str]
        machine_name: str
        resource_access_identity_input: IdentityProviderInput

        @overload
        def __init__(
                self, 
                *, 
                authentication_identity_input: IdentityProviderInput, 
                bios_id: Optional[str] = ..., 
                data_plane_authentication_identity_input: Optional[IdentityProviderInput] = ..., 
                machine_id: Optional[str] = ..., 
                machine_name: str, 
                resource_access_identity_input: IdentityProviderInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddVCenterRequest(_Model):
        properties: Optional[AddVCenterRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AddVCenterRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AddVCenterRequestProperties(_Model):
        friendly_name: Optional[str]
        ip_address: Optional[str]
        port: Optional[str]
        process_server_id: Optional[str]
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                port: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AgentAutoUpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservicessiterecovery.models.AgentDetails(_Model):
        agent_id: Optional[str]
        bios_id: Optional[str]
        disks: Optional[list[AgentDiskDetails]]
        fqdn: Optional[str]
        machine_id: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.AgentDiskDetails(_Model):
        capacity_in_bytes: Optional[int]
        disk_id: Optional[str]
        disk_name: Optional[str]
        is_os_disk: Optional[str]
        lun_id: Optional[int]


    class azure.mgmt.recoveryservicessiterecovery.models.AgentReinstallBlockedReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_NO_HEARTBEAT = "AgentNoHeartbeat"
        DISTRO_NOT_SUPPORTED = "DistroNotSupported"
        UNKNOWN = "Unknown"


    class azure.mgmt.recoveryservicessiterecovery.models.AgentUpgradeBlockedReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_NO_HEARTBEAT = "AgentNoHeartbeat"
        ALREADY_ON_LATEST_VERSION = "AlreadyOnLatestVersion"
        DISTRO_IS_NOT_REPORTED = "DistroIsNotReported"
        DISTRO_NOT_SUPPORTED_FOR_UPGRADE = "DistroNotSupportedForUpgrade"
        INCOMPATIBLE_APPLIANCE_VERSION = "IncompatibleApplianceVersion"
        INVALID_AGENT_VERSION = "InvalidAgentVersion"
        INVALID_DRIVER_VERSION = "InvalidDriverVersion"
        MISSING_UPGRADE_PATH = "MissingUpgradePath"
        NOT_PROTECTED = "NotProtected"
        PROCESS_SERVER_NO_HEARTBEAT = "ProcessServerNoHeartbeat"
        RCM_PROXY_NO_HEARTBEAT = "RcmProxyNoHeartbeat"
        REBOOT_REQUIRED = "RebootRequired"
        RE_INSTALL_REQUIRED = "ReInstallRequired"
        UNKNOWN = "Unknown"
        UNSUPPORTED_PROTECTION_SCENARIO = "UnsupportedProtectionScenario"


    class azure.mgmt.recoveryservicessiterecovery.models.AgentVersionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPRECATED = "Deprecated"
        NOT_SUPPORTED = "NotSupported"
        SECURITY_UPDATE_REQUIRED = "SecurityUpdateRequired"
        SUPPORTED = "Supported"
        UPDATE_REQUIRED = "UpdateRequired"


    class azure.mgmt.recoveryservicessiterecovery.models.Alert(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[AlertProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[AlertProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AlertProperties(_Model):
        custom_email_addresses: Optional[list[str]]
        locale: Optional[str]
        send_to_owners: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_email_addresses: Optional[list[str]] = ..., 
                locale: Optional[str] = ..., 
                send_to_owners: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AlternateLocationRecoveryOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_VM_IF_NOT_FOUND = "CreateVmIfNotFound"
        NO_ACTION = "NoAction"


    class azure.mgmt.recoveryservicessiterecovery.models.ApplianceMonitoringDetails(_Model):
        cpu_details: Optional[ApplianceResourceDetails]
        datastore_snapshot: Optional[list[DataStoreUtilizationDetails]]
        disks_replication_details: Optional[ApplianceResourceDetails]
        esxi_nfc_buffer: Optional[ApplianceResourceDetails]
        network_bandwidth: Optional[ApplianceResourceDetails]
        ram_details: Optional[ApplianceResourceDetails]


    class azure.mgmt.recoveryservicessiterecovery.models.ApplianceResourceDetails(_Model):
        capacity: Optional[int]
        process_utilization: Optional[float]
        status: Optional[str]
        total_utilization: Optional[float]


    class azure.mgmt.recoveryservicessiterecovery.models.ApplianceSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ApplyClusterRecoveryPointInput(_Model):
        properties: ApplyClusterRecoveryPointInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ApplyClusterRecoveryPointInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ApplyClusterRecoveryPointInputProperties(_Model):
        cluster_recovery_point_id: Optional[str]
        individual_node_recovery_points: Optional[list[str]]
        provider_specific_details: ApplyClusterRecoveryPointProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                cluster_recovery_point_id: Optional[str] = ..., 
                individual_node_recovery_points: Optional[list[str]] = ..., 
                provider_specific_details: ApplyClusterRecoveryPointProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ApplyClusterRecoveryPointProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ApplyRecoveryPointInput(_Model):
        properties: ApplyRecoveryPointInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ApplyRecoveryPointInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ApplyRecoveryPointInputProperties(_Model):
        provider_specific_details: ApplyRecoveryPointProviderSpecificInput
        recovery_point_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: ApplyRecoveryPointProviderSpecificInput, 
                recovery_point_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ApplyRecoveryPointProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AsrJobDetails(JobDetails, discriminator='AsrJobDetails'):
        affected_object_details: dict[str, str]
        instance_type: Literal["AsrJobDetails"]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AutoProtectionOfDataDisk(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservicessiterecovery.models.AutomationAccountAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUN_AS_ACCOUNT = "RunAsAccount"
        SYSTEM_ASSIGNED_IDENTITY = "SystemAssignedIdentity"


    class azure.mgmt.recoveryservicessiterecovery.models.AutomationRunbookTaskDetails(TaskTypeDetails, discriminator='AutomationRunbookTaskDetails'):
        account_name: Optional[str]
        cloud_service_name: Optional[str]
        instance_type: Literal["AutomationRunbookTaskDetails"]
        is_primary_side_script: Optional[bool]
        job_id: Optional[str]
        job_output: Optional[str]
        name: Optional[str]
        runbook_id: Optional[str]
        runbook_name: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                cloud_service_name: Optional[str] = ..., 
                is_primary_side_script: Optional[bool] = ..., 
                job_id: Optional[str] = ..., 
                job_output: Optional[str] = ..., 
                name: Optional[str] = ..., 
                runbook_id: Optional[str] = ..., 
                runbook_name: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureFabricCreationInput(FabricSpecificCreationInput, discriminator='Azure'):
        instance_type: Literal["Azure"]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureFabricSpecificDetails(FabricSpecificDetails, discriminator='Azure'):
        container_ids: Optional[list[str]]
        extended_locations: Optional[list[A2AExtendedLocationDetails]]
        instance_type: Literal["Azure"]
        location: Optional[str]
        location_details: Optional[list[A2AFabricSpecificLocationDetails]]
        zones: Optional[list[A2AZoneDetails]]

        @overload
        def __init__(
                self, 
                *, 
                container_ids: Optional[list[str]] = ..., 
                extended_locations: Optional[list[A2AExtendedLocationDetails]] = ..., 
                location: Optional[str] = ..., 
                location_details: Optional[list[A2AFabricSpecificLocationDetails]] = ..., 
                zones: Optional[list[A2AZoneDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureToAzureCreateNetworkMappingInput(FabricSpecificCreateNetworkMappingInput, discriminator='AzureToAzure'):
        instance_type: Literal["AzureToAzure"]
        primary_network_id: str

        @overload
        def __init__(
                self, 
                *, 
                primary_network_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureToAzureNetworkMappingSettings(NetworkMappingFabricSpecificSettings, discriminator='AzureToAzure'):
        instance_type: Literal["AzureToAzure"]
        primary_fabric_location: Optional[str]
        recovery_fabric_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_fabric_location: Optional[str] = ..., 
                recovery_fabric_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureToAzureUpdateNetworkMappingInput(FabricSpecificUpdateNetworkMappingInput, discriminator='AzureToAzure'):
        instance_type: Literal["AzureToAzure"]
        primary_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureToAzureVmSyncedConfigDetails(_Model):
        input_endpoints: Optional[list[InputEndpoint]]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                input_endpoints: Optional[list[InputEndpoint]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.AzureVmDiskDetails(_Model):
        custom_target_disk_name: Optional[str]
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        lun_id: Optional[str]
        max_size_mb: Optional[str]
        target_disk_location: Optional[str]
        target_disk_name: Optional[str]
        vhd_id: Optional[str]
        vhd_name: Optional[str]
        vhd_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_target_disk_name: Optional[str] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                lun_id: Optional[str] = ..., 
                max_size_mb: Optional[str] = ..., 
                target_disk_location: Optional[str] = ..., 
                target_disk_name: Optional[str] = ..., 
                vhd_id: Optional[str] = ..., 
                vhd_name: Optional[str] = ..., 
                vhd_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ChurnOptionSelected(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        NORMAL = "Normal"


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterFailoverJobDetails(JobDetails, discriminator='ClusterFailoverJobDetails'):
        affected_object_details: dict[str, str]
        instance_type: Literal["ClusterFailoverJobDetails"]
        protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterProviderSpecificRecoveryPointDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterRecoveryPoint(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ClusterRecoveryPointProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ClusterRecoveryPointProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterRecoveryPointProperties(_Model):
        provider_specific_details: Optional[ClusterProviderSpecificRecoveryPointDetails]
        recovery_point_time: Optional[datetime]
        recovery_point_type: Optional[Union[str, ClusterRecoveryPointType]]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[ClusterProviderSpecificRecoveryPointDetails] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                recovery_point_type: Optional[Union[str, ClusterRecoveryPointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_CONSISTENT = "ApplicationConsistent"
        CRASH_CONSISTENT = "CrashConsistent"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterSwitchProtectionJobDetails(JobDetails, discriminator='ClusterSwitchProtectionJobDetails'):
        affected_object_details: dict[str, str]
        instance_type: Literal["ClusterSwitchProtectionJobDetails"]
        new_replication_protection_cluster_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                new_replication_protection_cluster_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterTestFailoverCleanupInput(_Model):
        properties: ClusterTestFailoverCleanupInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ClusterTestFailoverCleanupInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterTestFailoverCleanupInputProperties(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterTestFailoverInput(_Model):
        properties: ClusterTestFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ClusterTestFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterTestFailoverInputProperties(_Model):
        failover_direction: Optional[Union[str, FailoverDirection]]
        network_id: Optional[str]
        network_type: Optional[str]
        provider_specific_details: Optional[ClusterTestFailoverProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Optional[Union[str, FailoverDirection]] = ..., 
                network_id: Optional[str] = ..., 
                network_type: Optional[str] = ..., 
                provider_specific_details: Optional[ClusterTestFailoverProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterTestFailoverJobDetails(JobDetails, discriminator='ClusterTestFailoverJobDetails'):
        affected_object_details: dict[str, str]
        comments: Optional[str]
        instance_type: Literal["ClusterTestFailoverJobDetails"]
        network_friendly_name: Optional[str]
        network_name: Optional[str]
        network_type: Optional[str]
        protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]]
        test_failover_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                comments: Optional[str] = ..., 
                network_friendly_name: Optional[str] = ..., 
                network_name: Optional[str] = ..., 
                network_type: Optional[str] = ..., 
                protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]] = ..., 
                test_failover_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterTestFailoverProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterUnplannedFailoverInput(_Model):
        properties: ClusterUnplannedFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ClusterUnplannedFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterUnplannedFailoverInputProperties(_Model):
        failover_direction: Optional[str]
        provider_specific_details: Optional[ClusterUnplannedFailoverProviderSpecificInput]
        source_site_operations: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Optional[str] = ..., 
                provider_specific_details: Optional[ClusterUnplannedFailoverProviderSpecificInput] = ..., 
                source_site_operations: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ClusterUnplannedFailoverProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ComputeSizeErrorDetails(_Model):
        message: Optional[str]
        severity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                severity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ConfidentialDiskEncryptionInfo(_Model):
        recovery_replica_confidential_disk_encryption_set_id: Optional[str]
        recovery_target_confidential_disk_encryption_set_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recovery_replica_confidential_disk_encryption_set_id: Optional[str] = ..., 
                recovery_target_confidential_disk_encryption_set_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ConfigurationSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ConfigureAlertRequest(_Model):
        properties: Optional[ConfigureAlertRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigureAlertRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ConfigureAlertRequestProperties(_Model):
        custom_email_addresses: Optional[list[str]]
        locale: Optional[str]
        send_to_owners: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_email_addresses: Optional[list[str]] = ..., 
                locale: Optional[str] = ..., 
                send_to_owners: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ConsistencyCheckTaskDetails(TaskTypeDetails, discriminator='ConsistencyCheckTaskDetails'):
        instance_type: Literal["ConsistencyCheckTaskDetails"]
        vm_details: Optional[list[InconsistentVmDetails]]

        @overload
        def __init__(
                self, 
                *, 
                vm_details: Optional[list[InconsistentVmDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateNetworkMappingInput(_Model):
        properties: CreateNetworkMappingInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: CreateNetworkMappingInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateNetworkMappingInputProperties(_Model):
        fabric_specific_details: Optional[FabricSpecificCreateNetworkMappingInput]
        recovery_fabric_name: Optional[str]
        recovery_network_id: str

        @overload
        def __init__(
                self, 
                *, 
                fabric_specific_details: Optional[FabricSpecificCreateNetworkMappingInput] = ..., 
                recovery_fabric_name: Optional[str] = ..., 
                recovery_network_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreatePolicyInput(_Model):
        properties: Optional[CreatePolicyInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreatePolicyInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreatePolicyInputProperties(_Model):
        provider_specific_input: Optional[PolicyProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_input: Optional[PolicyProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionContainerInput(_Model):
        properties: Optional[CreateProtectionContainerInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreateProtectionContainerInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionContainerInputProperties(_Model):
        provider_specific_input: Optional[list[ReplicationProviderSpecificContainerCreationInput]]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_input: Optional[list[ReplicationProviderSpecificContainerCreationInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionContainerMappingInput(_Model):
        properties: Optional[CreateProtectionContainerMappingInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreateProtectionContainerMappingInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionContainerMappingInputProperties(_Model):
        policy_id: Optional[str]
        provider_specific_input: Optional[ReplicationProviderSpecificContainerMappingInput]
        target_protection_container_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: Optional[str] = ..., 
                provider_specific_input: Optional[ReplicationProviderSpecificContainerMappingInput] = ..., 
                target_protection_container_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionIntentInput(_Model):
        properties: Optional[CreateProtectionIntentProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreateProtectionIntentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionIntentProperties(_Model):
        provider_specific_details: Optional[CreateProtectionIntentProviderSpecificDetails]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[CreateProtectionIntentProviderSpecificDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateProtectionIntentProviderSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateRecoveryPlanInput(_Model):
        properties: CreateRecoveryPlanInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: CreateRecoveryPlanInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreateRecoveryPlanInputProperties(_Model):
        failover_deployment_model: Optional[Union[str, FailoverDeploymentModel]]
        groups: list[RecoveryPlanGroup]
        primary_fabric_id: str
        provider_specific_input: Optional[list[RecoveryPlanProviderSpecificInput]]
        recovery_fabric_id: str

        @overload
        def __init__(
                self, 
                *, 
                failover_deployment_model: Optional[Union[str, FailoverDeploymentModel]] = ..., 
                groups: list[RecoveryPlanGroup], 
                primary_fabric_id: str, 
                provider_specific_input: Optional[list[RecoveryPlanProviderSpecificInput]] = ..., 
                recovery_fabric_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.recoveryservicessiterecovery.models.CriticalJobHistoryDetails(_Model):
        job_id: Optional[str]
        job_name: Optional[str]
        job_status: Optional[str]
        start_time: Optional[datetime]


    class azure.mgmt.recoveryservicessiterecovery.models.CurrentJobDetails(_Model):
        job_id: Optional[str]
        job_name: Optional[str]
        start_time: Optional[datetime]


    class azure.mgmt.recoveryservicessiterecovery.models.CurrentScenarioDetails(_Model):
        job_id: Optional[str]
        scenario_name: Optional[str]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
                scenario_name: Optional[str] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DataStore(_Model):
        capacity: Optional[str]
        free_space: Optional[str]
        symbolic_name: Optional[str]
        type: Optional[str]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[str] = ..., 
                free_space: Optional[str] = ..., 
                symbolic_name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                uuid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DataStoreUtilizationDetails(_Model):
        data_store_name: Optional[str]
        total_snapshots_created: Optional[int]
        total_snapshots_supported: Optional[int]


    class azure.mgmt.recoveryservicessiterecovery.models.DataSyncStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOR_DOWN_TIME = "ForDownTime"
        FOR_SYNCHRONIZATION = "ForSynchronization"


    class azure.mgmt.recoveryservicessiterecovery.models.DisableProtectionInput(_Model):
        properties: DisableProtectionInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: DisableProtectionInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DisableProtectionInputProperties(_Model):
        disable_protection_reason: Optional[Union[str, DisableProtectionReason]]
        replication_provider_input: Optional[DisableProtectionProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                disable_protection_reason: Optional[Union[str, DisableProtectionReason]] = ..., 
                replication_provider_input: Optional[DisableProtectionProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DisableProtectionProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DisableProtectionReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIGRATION_COMPLETE = "MigrationComplete"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.recoveryservicessiterecovery.models.DiscoverProtectableItemRequest(_Model):
        properties: Optional[DiscoverProtectableItemRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiscoverProtectableItemRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DiscoverProtectableItemRequestProperties(_Model):
        friendly_name: Optional[str]
        ip_address: Optional[str]
        os_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                os_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DiskAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.recoveryservicessiterecovery.models.DiskDetails(_Model):
        max_size_mb: Optional[int]
        vhd_id: Optional[str]
        vhd_name: Optional[str]
        vhd_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                max_size_mb: Optional[int] = ..., 
                vhd_id: Optional[str] = ..., 
                vhd_name: Optional[str] = ..., 
                vhd_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DiskEncryptionInfo(_Model):
        disk_encryption_key_info: Optional[DiskEncryptionKeyInfo]
        key_encryption_key_info: Optional[KeyEncryptionKeyInfo]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_key_info: Optional[DiskEncryptionKeyInfo] = ..., 
                key_encryption_key_info: Optional[KeyEncryptionKeyInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DiskEncryptionKeyInfo(_Model):
        key_vault_resource_arm_id: Optional[str]
        secret_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_resource_arm_id: Optional[str] = ..., 
                secret_identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.DiskNetworkAccessPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_ALL = "AllowAll"
        ALLOW_PRIVATE = "AllowPrivate"
        DENY_ALL = "DenyAll"


    class azure.mgmt.recoveryservicessiterecovery.models.DiskPublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservicessiterecovery.models.DiskReplicationProgressHealth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_PROGRESS = "InProgress"
        NONE = "None"
        NO_PROGRESS = "NoProgress"
        QUEUED = "Queued"
        SLOW_PROGRESS = "SlowProgress"


    class azure.mgmt.recoveryservicessiterecovery.models.DiskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIAL_REPLICATION_FAILED = "InitialReplicationFailed"
        INITIAL_REPLICATION_PENDING = "InitialReplicationPending"
        PROTECTED = "Protected"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.recoveryservicessiterecovery.models.DiskVolumeDetails(_Model):
        label: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                label: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.Display(_Model):
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


    class azure.mgmt.recoveryservicessiterecovery.models.DraDetails(_Model):
        bios_id: Optional[str]
        forward_protected_item_count: Optional[int]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        name: Optional[str]
        reverse_protected_item_count: Optional[int]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.EnableMigrationInput(_Model):
        properties: EnableMigrationInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: EnableMigrationInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EnableMigrationInputProperties(_Model):
        policy_id: str
        provider_specific_details: EnableMigrationProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                policy_id: str, 
                provider_specific_details: EnableMigrationProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EnableMigrationProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EnableProtectionInput(_Model):
        properties: Optional[EnableProtectionInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnableProtectionInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EnableProtectionInputProperties(_Model):
        policy_id: Optional[str]
        protectable_item_id: Optional[str]
        provider_specific_details: Optional[EnableProtectionProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: Optional[str] = ..., 
                protectable_item_id: Optional[str] = ..., 
                provider_specific_details: Optional[EnableProtectionProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EnableProtectionProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EncryptionDetails(_Model):
        kek_cert_expiry_date: Optional[datetime]
        kek_cert_thumbprint: Optional[str]
        kek_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kek_cert_expiry_date: Optional[datetime] = ..., 
                kek_cert_thumbprint: Optional[str] = ..., 
                kek_state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EthernetAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.recoveryservicessiterecovery.models.Event(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[EventProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[EventProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EventProperties(_Model):
        affected_object_correlation_id: Optional[str]
        affected_object_friendly_name: Optional[str]
        description: Optional[str]
        event_code: Optional[str]
        event_specific_details: Optional[EventSpecificDetails]
        event_type: Optional[str]
        fabric_id: Optional[str]
        health_errors: Optional[list[HealthError]]
        provider_specific_details: Optional[EventProviderSpecificDetails]
        severity: Optional[str]
        time_of_occurrence: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_correlation_id: Optional[str] = ..., 
                affected_object_friendly_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                event_code: Optional[str] = ..., 
                event_specific_details: Optional[EventSpecificDetails] = ..., 
                event_type: Optional[str] = ..., 
                fabric_id: Optional[str] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                provider_specific_details: Optional[EventProviderSpecificDetails] = ..., 
                severity: Optional[str] = ..., 
                time_of_occurrence: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EventProviderSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.EventSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExistingProtectionProfile(ProtectionProfileCustomDetails, discriminator='Existing'):
        protection_profile_id: str
        resource_type: Literal["Existing"]

        @overload
        def __init__(
                self, 
                *, 
                protection_profile_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExistingRecoveryAvailabilitySet(RecoveryAvailabilitySetCustomDetails, discriminator='Existing'):
        recovery_availability_set_id: Optional[str]
        resource_type: Literal["Existing"]

        @overload
        def __init__(
                self, 
                *, 
                recovery_availability_set_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExistingRecoveryProximityPlacementGroup(RecoveryProximityPlacementGroupCustomDetails, discriminator='Existing'):
        recovery_proximity_placement_group_id: Optional[str]
        resource_type: Literal["Existing"]

        @overload
        def __init__(
                self, 
                *, 
                recovery_proximity_placement_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExistingRecoveryResourceGroup(RecoveryResourceGroupCustomDetails, discriminator='Existing'):
        recovery_resource_group_id: Optional[str]
        resource_type: Literal["Existing"]

        @overload
        def __init__(
                self, 
                *, 
                recovery_resource_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExistingRecoveryVirtualNetwork(RecoveryVirtualNetworkCustomDetails, discriminator='Existing'):
        recovery_subnet_name: Optional[str]
        recovery_virtual_network_id: str
        resource_type: Literal["Existing"]

        @overload
        def __init__(
                self, 
                *, 
                recovery_subnet_name: Optional[str] = ..., 
                recovery_virtual_network_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExistingStorageAccount(StorageAccountCustomDetails, discriminator='Existing'):
        azure_storage_account_id: str
        resource_type: Literal["Existing"]

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExportJobDetails(JobDetails, discriminator='ExportJobDetails'):
        affected_object_details: dict[str, str]
        blob_uri: Optional[str]
        instance_type: Literal["ExportJobDetails"]
        sas_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                blob_uri: Optional[str] = ..., 
                sas_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExportJobOutputSerializationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCEL = "Excel"
        JSON = "Json"
        XML = "Xml"


    class azure.mgmt.recoveryservicessiterecovery.models.ExtendedLocation(_Model):
        name: str
        type: Union[str, ExtendedLocationType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ExtendedLocationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.recoveryservicessiterecovery.models.Fabric(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[FabricProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[FabricProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricCreationInput(_Model):
        properties: Optional[FabricCreationInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricCreationInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricCreationInputProperties(_Model):
        custom_details: Optional[FabricSpecificCreationInput]

        @overload
        def __init__(
                self, 
                *, 
                custom_details: Optional[FabricSpecificCreationInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricProperties(_Model):
        bcdr_state: Optional[str]
        custom_details: Optional[FabricSpecificDetails]
        encryption_details: Optional[EncryptionDetails]
        friendly_name: Optional[str]
        health: Optional[str]
        health_error_details: Optional[list[HealthError]]
        internal_identifier: Optional[str]
        rollover_encryption_details: Optional[EncryptionDetails]

        @overload
        def __init__(
                self, 
                *, 
                bcdr_state: Optional[str] = ..., 
                custom_details: Optional[FabricSpecificDetails] = ..., 
                encryption_details: Optional[EncryptionDetails] = ..., 
                friendly_name: Optional[str] = ..., 
                health: Optional[str] = ..., 
                health_error_details: Optional[list[HealthError]] = ..., 
                internal_identifier: Optional[str] = ..., 
                rollover_encryption_details: Optional[EncryptionDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricReplicationGroupTaskDetails(JobTaskDetails, discriminator='FabricReplicationGroupTaskDetails'):
        instance_type: Literal["FabricReplicationGroupTaskDetails"]
        job_task: JobEntity
        skipped_reason: Optional[str]
        skipped_reason_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                job_task: Optional[JobEntity] = ..., 
                skipped_reason: Optional[str] = ..., 
                skipped_reason_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricSpecificCreateNetworkMappingInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricSpecificCreationInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FabricSpecificUpdateNetworkMappingInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FailoverDeploymentModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIC = "Classic"
        NOT_APPLICABLE = "NotApplicable"
        RESOURCE_MANAGER = "ResourceManager"


    class azure.mgmt.recoveryservicessiterecovery.models.FailoverDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_TO_RECOVERY = "PrimaryToRecovery"
        RECOVERY_TO_PRIMARY = "RecoveryToPrimary"


    class azure.mgmt.recoveryservicessiterecovery.models.FailoverJobDetails(JobDetails, discriminator='FailoverJobDetails'):
        affected_object_details: dict[str, str]
        instance_type: Literal["FailoverJobDetails"]
        protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FailoverProcessServerRequest(_Model):
        properties: Optional[FailoverProcessServerRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FailoverProcessServerRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FailoverProcessServerRequestProperties(_Model):
        container_name: Optional[str]
        source_process_server_id: Optional[str]
        target_process_server_id: Optional[str]
        update_type: Optional[str]
        vms_to_migrate: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                source_process_server_id: Optional[str] = ..., 
                target_process_server_id: Optional[str] = ..., 
                update_type: Optional[str] = ..., 
                vms_to_migrate: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.FailoverReplicationProtectedItemDetails(_Model):
        friendly_name: Optional[str]
        name: Optional[str]
        network_connection_status: Optional[str]
        network_friendly_name: Optional[str]
        recovery_point_id: Optional[str]
        recovery_point_time: Optional[datetime]
        subnet: Optional[str]
        test_vm_friendly_name: Optional[str]
        test_vm_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                network_connection_status: Optional[str] = ..., 
                network_friendly_name: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                subnet: Optional[str] = ..., 
                test_vm_friendly_name: Optional[str] = ..., 
                test_vm_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.GatewayOperationDetails(_Model):
        data_stores: Optional[list[str]]
        host_name: Optional[str]
        progress_percentage: Optional[int]
        state: Optional[str]
        time_elapsed: Optional[int]
        time_remaining: Optional[int]
        upload_speed: Optional[int]
        vmware_read_throughput: Optional[int]


    class azure.mgmt.recoveryservicessiterecovery.models.GroupTaskDetails(_Model):
        child_tasks: Optional[list[ASRTask]]
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                child_tasks: Optional[list[ASRTask]] = ..., 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HealthError(_Model):
        creation_time_utc: Optional[datetime]
        customer_resolvability: Optional[Union[str, HealthErrorCustomerResolvability]]
        entity_id: Optional[str]
        error_category: Optional[str]
        error_code: Optional[str]
        error_id: Optional[str]
        error_level: Optional[str]
        error_message: Optional[str]
        error_source: Optional[str]
        error_type: Optional[str]
        inner_health_errors: Optional[list[InnerHealthError]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]
        recovery_provider_error_message: Optional[str]
        summary_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time_utc: Optional[datetime] = ..., 
                customer_resolvability: Optional[Union[str, HealthErrorCustomerResolvability]] = ..., 
                entity_id: Optional[str] = ..., 
                error_category: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_id: Optional[str] = ..., 
                error_level: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                error_source: Optional[str] = ..., 
                error_type: Optional[str] = ..., 
                inner_health_errors: Optional[list[InnerHealthError]] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ..., 
                recovery_provider_error_message: Optional[str] = ..., 
                summary_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HealthErrorCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_AUTO_UPDATE_ARTIFACT_DELETED = "AgentAutoUpdateArtifactDeleted"
        AGENT_AUTO_UPDATE_INFRA = "AgentAutoUpdateInfra"
        AGENT_AUTO_UPDATE_RUN_AS_ACCOUNT = "AgentAutoUpdateRunAsAccount"
        AGENT_AUTO_UPDATE_RUN_AS_ACCOUNT_EXPIRED = "AgentAutoUpdateRunAsAccountExpired"
        AGENT_AUTO_UPDATE_RUN_AS_ACCOUNT_EXPIRY = "AgentAutoUpdateRunAsAccountExpiry"
        CONFIGURATION = "Configuration"
        FABRIC_INFRASTRUCTURE = "FabricInfrastructure"
        NONE = "None"
        REPLICATION = "Replication"
        TEST_FAILOVER = "TestFailover"
        VERSION_EXPIRY = "VersionExpiry"


    class azure.mgmt.recoveryservicessiterecovery.models.HealthErrorCustomerResolvability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.recoveryservicessiterecovery.models.HealthErrorSummary(_Model):
        affected_resource_correlation_ids: Optional[list[str]]
        affected_resource_subtype: Optional[str]
        affected_resource_type: Optional[str]
        category: Optional[Union[str, HealthErrorCategory]]
        severity: Optional[Union[str, Severity]]
        summary_code: Optional[str]
        summary_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_resource_correlation_ids: Optional[list[str]] = ..., 
                affected_resource_subtype: Optional[str] = ..., 
                affected_resource_type: Optional[str] = ..., 
                category: Optional[Union[str, HealthErrorCategory]] = ..., 
                severity: Optional[Union[str, Severity]] = ..., 
                summary_code: Optional[str] = ..., 
                summary_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVHostDetails(_Model):
        id: Optional[str]
        mars_agent_version: Optional[str]
        name: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplica2012EventDetails(EventProviderSpecificDetails, discriminator='HyperVReplica2012'):
        container_name: Optional[str]
        fabric_name: Optional[str]
        instance_type: Literal["HyperVReplica2012"]
        remote_container_name: Optional[str]
        remote_fabric_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                remote_container_name: Optional[str] = ..., 
                remote_fabric_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplica2012R2EventDetails(EventProviderSpecificDetails, discriminator='HyperVReplica2012R2'):
        container_name: Optional[str]
        fabric_name: Optional[str]
        instance_type: Literal["HyperVReplica2012R2"]
        remote_container_name: Optional[str]
        remote_fabric_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                remote_container_name: Optional[str] = ..., 
                remote_fabric_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureApplyRecoveryPointInput(ApplyRecoveryPointProviderSpecificInput, discriminator='HyperVReplicaAzure'):
        instance_type: Literal["HyperVReplicaAzure"]
        primary_kek_certificate_pfx: Optional[str]
        secondary_kek_certificate_pfx: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_kek_certificate_pfx: Optional[str] = ..., 
                secondary_kek_certificate_pfx: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureDiskInputDetails(_Model):
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        disk_size_in_gb: Optional[int]
        disk_type: Optional[Union[str, DiskAccountType]]
        iops: Optional[int]
        log_storage_account_id: Optional[str]
        sector_size_in_bytes: Optional[int]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                disk_size_in_gb: Optional[int] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                iops: Optional[int] = ..., 
                log_storage_account_id: Optional[str] = ..., 
                sector_size_in_bytes: Optional[int] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureEnableProtectionInput(EnableProtectionProviderSpecificInput, discriminator='HyperVReplicaAzure'):
        disk_encryption_set_id: Optional[str]
        disk_type: Optional[Union[str, DiskAccountType]]
        disks_to_include: Optional[list[str]]
        disks_to_include_for_managed_disks: Optional[list[HyperVReplicaAzureDiskInputDetails]]
        enable_rdp_on_target_option: Optional[str]
        hv_host_vm_id: Optional[str]
        instance_type: Literal["HyperVReplicaAzure"]
        license_type: Optional[Union[str, LicenseType]]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        log_storage_account_id: Optional[str]
        os_type: Optional[str]
        seed_managed_disk_tags: Optional[dict[str, str]]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_azure_network_id: Optional[str]
        target_azure_subnet_id: Optional[str]
        target_azure_v1_resource_group_id: Optional[str]
        target_azure_v2_resource_group_id: Optional[str]
        target_azure_vm_name: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_managed_disk_tags: Optional[dict[str, str]]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_storage_account_id: Optional[str]
        target_vm_security_profile: Optional[SecurityProfileProperties]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        use_managed_disks: Optional[str]
        use_managed_disks_for_replication: Optional[str]
        user_selected_os_name: Optional[str]
        vhd_id: Optional[str]
        vm_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                disks_to_include: Optional[list[str]] = ..., 
                disks_to_include_for_managed_disks: Optional[list[HyperVReplicaAzureDiskInputDetails]] = ..., 
                enable_rdp_on_target_option: Optional[str] = ..., 
                hv_host_vm_id: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                log_storage_account_id: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                seed_managed_disk_tags: Optional[dict[str, str]] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_azure_network_id: Optional[str] = ..., 
                target_azure_subnet_id: Optional[str] = ..., 
                target_azure_v1_resource_group_id: Optional[str] = ..., 
                target_azure_v2_resource_group_id: Optional[str] = ..., 
                target_azure_vm_name: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_managed_disk_tags: Optional[dict[str, str]] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_storage_account_id: Optional[str] = ..., 
                target_vm_security_profile: Optional[SecurityProfileProperties] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                use_managed_disks: Optional[str] = ..., 
                use_managed_disks_for_replication: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ..., 
                vhd_id: Optional[str] = ..., 
                vm_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureEventDetails(EventProviderSpecificDetails, discriminator='HyperVReplicaAzure'):
        container_name: Optional[str]
        fabric_name: Optional[str]
        instance_type: Literal["HyperVReplicaAzure"]
        remote_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                remote_container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureFailbackProviderInput(PlannedFailoverProviderSpecificFailoverInput, discriminator='HyperVReplicaAzureFailback'):
        data_sync_option: Optional[str]
        instance_type: Literal["HyperVReplicaAzureFailback"]
        provider_id_for_alternate_recovery: Optional[str]
        recovery_vm_creation_option: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_sync_option: Optional[str] = ..., 
                provider_id_for_alternate_recovery: Optional[str] = ..., 
                recovery_vm_creation_option: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureManagedDiskDetails(_Model):
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        disk_size_in_gb: Optional[int]
        iops: Optional[int]
        replica_disk_type: Optional[str]
        sector_size_in_bytes: Optional[int]
        seed_managed_disk_id: Optional[str]
        target_disk_account_type: Optional[Union[str, DiskAccountType]]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                disk_size_in_gb: Optional[int] = ..., 
                iops: Optional[int] = ..., 
                replica_disk_type: Optional[str] = ..., 
                sector_size_in_bytes: Optional[int] = ..., 
                seed_managed_disk_id: Optional[str] = ..., 
                target_disk_account_type: Optional[Union[str, DiskAccountType]] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzurePlannedFailoverProviderInput(PlannedFailoverProviderSpecificFailoverInput, discriminator='HyperVReplicaAzure'):
        instance_type: Literal["HyperVReplicaAzure"]
        os_upgrade_version: Optional[str]
        primary_kek_certificate_pfx: Optional[str]
        recovery_point_id: Optional[str]
        secondary_kek_certificate_pfx: Optional[str]
        target_capacity_reservation_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_upgrade_version: Optional[str] = ..., 
                primary_kek_certificate_pfx: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                secondary_kek_certificate_pfx: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzurePolicyDetails(PolicyProviderSpecificDetails, discriminator='HyperVReplicaAzure'):
        active_storage_account_id: Optional[str]
        application_consistent_snapshot_frequency_in_hours: Optional[int]
        encryption: Optional[str]
        instance_type: Literal["HyperVReplicaAzure"]
        online_replication_start_time: Optional[str]
        recovery_point_history_duration_in_hours: Optional[int]
        replication_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                active_storage_account_id: Optional[str] = ..., 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                encryption: Optional[str] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_point_history_duration_in_hours: Optional[int] = ..., 
                replication_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzurePolicyInput(PolicyProviderSpecificInput, discriminator='HyperVReplicaAzure'):
        application_consistent_snapshot_frequency_in_hours: Optional[int]
        instance_type: Literal["HyperVReplicaAzure"]
        online_replication_start_time: Optional[str]
        recovery_point_history_duration: Optional[int]
        replication_interval: Optional[int]
        storage_accounts: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_point_history_duration: Optional[int] = ..., 
                replication_interval: Optional[int] = ..., 
                storage_accounts: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureReplicationDetails(ReplicationProviderSpecificSettings, discriminator='HyperVReplicaAzure'):
        all_available_os_upgrade_configurations: Optional[list[OSUpgradeSupportedVersions]]
        azure_vm_disk_details: Optional[list[AzureVmDiskDetails]]
        enable_rdp_on_target_option: Optional[str]
        encryption: Optional[str]
        initial_replication_details: Optional[InitialReplicationDetails]
        instance_type: Literal["HyperVReplicaAzure"]
        last_recovery_point_received: Optional[datetime]
        last_replicated_time: Optional[datetime]
        last_rpo_calculated_time: Optional[datetime]
        license_type: Optional[str]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        o_s_details: Optional[OSDetails]
        protected_managed_disks: Optional[list[HyperVReplicaAzureManagedDiskDetails]]
        recovery_availability_set_id: Optional[str]
        recovery_azure_log_storage_account_id: Optional[str]
        recovery_azure_resource_group_id: Optional[str]
        recovery_azure_storage_account: Optional[str]
        recovery_azure_vm_name: Optional[str]
        recovery_azure_vm_size: Optional[str]
        rpo_in_seconds: Optional[int]
        seed_managed_disk_tags: Optional[dict[str, str]]
        selected_recovery_azure_network_id: Optional[str]
        selected_source_nic_id: Optional[str]
        source_vm_cpu_count: Optional[int]
        source_vm_ram_size_in_mb: Optional[int]
        sql_server_license_type: Optional[str]
        target_availability_zone: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_managed_disk_tags: Optional[dict[str, str]]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_vm_security_profile: Optional[SecurityProfileProperties]
        target_vm_tags: Optional[dict[str, str]]
        use_managed_disks: Optional[str]
        vm_id: Optional[str]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                all_available_os_upgrade_configurations: Optional[list[OSUpgradeSupportedVersions]] = ..., 
                azure_vm_disk_details: Optional[list[AzureVmDiskDetails]] = ..., 
                enable_rdp_on_target_option: Optional[str] = ..., 
                encryption: Optional[str] = ..., 
                initial_replication_details: Optional[InitialReplicationDetails] = ..., 
                last_replicated_time: Optional[datetime] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                license_type: Optional[str] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                o_s_details: Optional[OSDetails] = ..., 
                protected_managed_disks: Optional[list[HyperVReplicaAzureManagedDiskDetails]] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_azure_log_storage_account_id: Optional[str] = ..., 
                recovery_azure_resource_group_id: Optional[str] = ..., 
                recovery_azure_storage_account: Optional[str] = ..., 
                recovery_azure_vm_name: Optional[str] = ..., 
                recovery_azure_vm_size: Optional[str] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                seed_managed_disk_tags: Optional[dict[str, str]] = ..., 
                selected_recovery_azure_network_id: Optional[str] = ..., 
                selected_source_nic_id: Optional[str] = ..., 
                source_vm_cpu_count: Optional[int] = ..., 
                source_vm_ram_size_in_mb: Optional[int] = ..., 
                sql_server_license_type: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_managed_disk_tags: Optional[dict[str, str]] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_vm_security_profile: Optional[SecurityProfileProperties] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                use_managed_disks: Optional[str] = ..., 
                vm_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureReprotectInput(ReverseReplicationProviderSpecificInput, discriminator='HyperVReplicaAzure'):
        hv_host_vm_id: Optional[str]
        instance_type: Literal["HyperVReplicaAzure"]
        log_storage_account_id: Optional[str]
        os_type: Optional[str]
        storage_account_id: Optional[str]
        v_hd_id: Optional[str]
        vm_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                hv_host_vm_id: Optional[str] = ..., 
                log_storage_account_id: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                v_hd_id: Optional[str] = ..., 
                vm_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureRpRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATEST = "Latest"
        LATEST_APPLICATION_CONSISTENT = "LatestApplicationConsistent"
        LATEST_PROCESSED = "LatestProcessed"


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureTestFailoverInput(TestFailoverProviderSpecificInput, discriminator='HyperVReplicaAzure'):
        instance_type: Literal["HyperVReplicaAzure"]
        os_upgrade_version: Optional[str]
        primary_kek_certificate_pfx: Optional[str]
        recovery_point_id: Optional[str]
        secondary_kek_certificate_pfx: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_upgrade_version: Optional[str] = ..., 
                primary_kek_certificate_pfx: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                secondary_kek_certificate_pfx: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureUnplannedFailoverInput(UnplannedFailoverProviderSpecificInput, discriminator='HyperVReplicaAzure'):
        instance_type: Literal["HyperVReplicaAzure"]
        primary_kek_certificate_pfx: Optional[str]
        recovery_point_id: Optional[str]
        secondary_kek_certificate_pfx: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_kek_certificate_pfx: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ..., 
                secondary_kek_certificate_pfx: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaAzureUpdateReplicationProtectedItemInput(UpdateReplicationProtectedItemProviderInput, discriminator='HyperVReplicaAzure'):
        disk_id_to_disk_encryption_map: Optional[dict[str, str]]
        instance_type: Literal["HyperVReplicaAzure"]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        recovery_azure_v1_resource_group_id: Optional[str]
        recovery_azure_v2_resource_group_id: Optional[str]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_zone: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_managed_disk_tags: Optional[dict[str, str]]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        use_managed_disks: Optional[str]
        user_selected_os_name: Optional[str]
        vm_disks: Optional[list[UpdateDiskInput]]

        @overload
        def __init__(
                self, 
                *, 
                disk_id_to_disk_encryption_map: Optional[dict[str, str]] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                recovery_azure_v1_resource_group_id: Optional[str] = ..., 
                recovery_azure_v2_resource_group_id: Optional[str] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_managed_disk_tags: Optional[dict[str, str]] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                use_managed_disks: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ..., 
                vm_disks: Optional[list[UpdateDiskInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaBaseEventDetails(EventProviderSpecificDetails, discriminator='HyperVReplicaBaseEventDetails'):
        container_name: Optional[str]
        fabric_name: Optional[str]
        instance_type: Literal["HyperVReplicaBaseEventDetails"]
        remote_container_name: Optional[str]
        remote_fabric_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                fabric_name: Optional[str] = ..., 
                remote_container_name: Optional[str] = ..., 
                remote_fabric_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaBasePolicyDetails(PolicyProviderSpecificDetails, discriminator='HyperVReplicaBasePolicyDetails'):
        allowed_authentication_type: Optional[int]
        application_consistent_snapshot_frequency_in_hours: Optional[int]
        compression: Optional[str]
        initial_replication_method: Optional[str]
        instance_type: Literal["HyperVReplicaBasePolicyDetails"]
        offline_replication_export_path: Optional[str]
        offline_replication_import_path: Optional[str]
        online_replication_start_time: Optional[str]
        recovery_points: Optional[int]
        replica_deletion_option: Optional[str]
        replication_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_type: Optional[int] = ..., 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                compression: Optional[str] = ..., 
                initial_replication_method: Optional[str] = ..., 
                offline_replication_export_path: Optional[str] = ..., 
                offline_replication_import_path: Optional[str] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_points: Optional[int] = ..., 
                replica_deletion_option: Optional[str] = ..., 
                replication_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaBaseReplicationDetails(ReplicationProviderSpecificSettings, discriminator='HyperVReplicaBaseReplicationDetails'):
        initial_replication_details: Optional[InitialReplicationDetails]
        instance_type: Literal["HyperVReplicaBaseReplicationDetails"]
        last_replicated_time: Optional[datetime]
        v_m_disk_details: Optional[list[DiskDetails]]
        vm_id: Optional[str]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initial_replication_details: Optional[InitialReplicationDetails] = ..., 
                last_replicated_time: Optional[datetime] = ..., 
                v_m_disk_details: Optional[list[DiskDetails]] = ..., 
                vm_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaBluePolicyDetails(PolicyProviderSpecificDetails, discriminator='HyperVReplica2012R2'):
        allowed_authentication_type: Optional[int]
        application_consistent_snapshot_frequency_in_hours: Optional[int]
        compression: Optional[str]
        initial_replication_method: Optional[str]
        instance_type: Literal["HyperVReplica2012R2"]
        offline_replication_export_path: Optional[str]
        offline_replication_import_path: Optional[str]
        online_replication_start_time: Optional[str]
        recovery_points: Optional[int]
        replica_deletion_option: Optional[str]
        replication_frequency_in_seconds: Optional[int]
        replication_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_type: Optional[int] = ..., 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                compression: Optional[str] = ..., 
                initial_replication_method: Optional[str] = ..., 
                offline_replication_export_path: Optional[str] = ..., 
                offline_replication_import_path: Optional[str] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_points: Optional[int] = ..., 
                replica_deletion_option: Optional[str] = ..., 
                replication_frequency_in_seconds: Optional[int] = ..., 
                replication_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaBluePolicyInput(HyperVReplicaPolicyInput, discriminator='HyperVReplica2012R2'):
        allowed_authentication_type: int
        application_consistent_snapshot_frequency_in_hours: int
        compression: str
        initial_replication_method: str
        instance_type: Literal["HyperVReplica2012R2"]
        offline_replication_export_path: str
        offline_replication_import_path: str
        online_replication_start_time: str
        recovery_points: int
        replica_deletion: str
        replication_frequency_in_seconds: Optional[int]
        replication_port: int

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_type: Optional[int] = ..., 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                compression: Optional[str] = ..., 
                initial_replication_method: Optional[str] = ..., 
                offline_replication_export_path: Optional[str] = ..., 
                offline_replication_import_path: Optional[str] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_points: Optional[int] = ..., 
                replica_deletion: Optional[str] = ..., 
                replication_frequency_in_seconds: Optional[int] = ..., 
                replication_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaBlueReplicationDetails(ReplicationProviderSpecificSettings, discriminator='HyperVReplica2012R2'):
        initial_replication_details: Optional[InitialReplicationDetails]
        instance_type: Literal["HyperVReplica2012R2"]
        last_replicated_time: Optional[datetime]
        v_m_disk_details: Optional[list[DiskDetails]]
        vm_id: Optional[str]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initial_replication_details: Optional[InitialReplicationDetails] = ..., 
                last_replicated_time: Optional[datetime] = ..., 
                v_m_disk_details: Optional[list[DiskDetails]] = ..., 
                vm_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaPolicyDetails(PolicyProviderSpecificDetails, discriminator='HyperVReplica2012'):
        allowed_authentication_type: Optional[int]
        application_consistent_snapshot_frequency_in_hours: Optional[int]
        compression: Optional[str]
        initial_replication_method: Optional[str]
        instance_type: Literal["HyperVReplica2012"]
        offline_replication_export_path: Optional[str]
        offline_replication_import_path: Optional[str]
        online_replication_start_time: Optional[str]
        recovery_points: Optional[int]
        replica_deletion_option: Optional[str]
        replication_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_type: Optional[int] = ..., 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                compression: Optional[str] = ..., 
                initial_replication_method: Optional[str] = ..., 
                offline_replication_export_path: Optional[str] = ..., 
                offline_replication_import_path: Optional[str] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_points: Optional[int] = ..., 
                replica_deletion_option: Optional[str] = ..., 
                replication_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaPolicyInput(PolicyProviderSpecificInput, discriminator='HyperVReplica2012'):
        allowed_authentication_type: Optional[int]
        application_consistent_snapshot_frequency_in_hours: Optional[int]
        compression: Optional[str]
        initial_replication_method: Optional[str]
        instance_type: Literal["HyperVReplica2012"]
        offline_replication_export_path: Optional[str]
        offline_replication_import_path: Optional[str]
        online_replication_start_time: Optional[str]
        recovery_points: Optional[int]
        replica_deletion: Optional[str]
        replication_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_type: Optional[int] = ..., 
                application_consistent_snapshot_frequency_in_hours: Optional[int] = ..., 
                compression: Optional[str] = ..., 
                initial_replication_method: Optional[str] = ..., 
                offline_replication_export_path: Optional[str] = ..., 
                offline_replication_import_path: Optional[str] = ..., 
                online_replication_start_time: Optional[str] = ..., 
                recovery_points: Optional[int] = ..., 
                replica_deletion: Optional[str] = ..., 
                replication_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVReplicaReplicationDetails(ReplicationProviderSpecificSettings, discriminator='HyperVReplica2012'):
        initial_replication_details: Optional[InitialReplicationDetails]
        instance_type: Literal["HyperVReplica2012"]
        last_replicated_time: Optional[datetime]
        v_m_disk_details: Optional[list[DiskDetails]]
        vm_id: Optional[str]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initial_replication_details: Optional[InitialReplicationDetails] = ..., 
                last_replicated_time: Optional[datetime] = ..., 
                v_m_disk_details: Optional[list[DiskDetails]] = ..., 
                vm_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVSiteDetails(FabricSpecificDetails, discriminator='HyperVSite'):
        hyper_v_hosts: Optional[list[HyperVHostDetails]]
        instance_type: Literal["HyperVSite"]

        @overload
        def __init__(
                self, 
                *, 
                hyper_v_hosts: Optional[list[HyperVHostDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.HyperVVirtualMachineDetails(ConfigurationSettings, discriminator='HyperVVirtualMachine'):
        disk_details: Optional[list[DiskDetails]]
        generation: Optional[str]
        has_fibre_channel_adapter: Optional[Union[str, PresenceStatus]]
        has_physical_disk: Optional[Union[str, PresenceStatus]]
        has_shared_vhd: Optional[Union[str, PresenceStatus]]
        hyper_v_host_id: Optional[str]
        instance_type: Literal["HyperVVirtualMachine"]
        os_details: Optional[OSDetails]
        source_item_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_details: Optional[list[DiskDetails]] = ..., 
                generation: Optional[str] = ..., 
                has_fibre_channel_adapter: Optional[Union[str, PresenceStatus]] = ..., 
                has_physical_disk: Optional[Union[str, PresenceStatus]] = ..., 
                has_shared_vhd: Optional[Union[str, PresenceStatus]] = ..., 
                hyper_v_host_id: Optional[str] = ..., 
                os_details: Optional[OSDetails] = ..., 
                source_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.IPConfigDetails(_Model):
        ip_address_type: Optional[str]
        ip_version: Optional[Union[str, IPVersion]]
        is_primary: Optional[bool]
        is_seleted_for_failover: Optional[bool]
        name: Optional[str]
        recovery_ip_address_type: Optional[str]
        recovery_lb_backend_address_pool_ids: Optional[list[str]]
        recovery_public_ip_address_id: Optional[str]
        recovery_static_ip_address: Optional[str]
        recovery_subnet_name: Optional[str]
        static_ip_address: Optional[str]
        subnet_name: Optional[str]
        tfo_lb_backend_address_pool_ids: Optional[list[str]]
        tfo_public_ip_address_id: Optional[str]
        tfo_static_ip_address: Optional[str]
        tfo_subnet_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_type: Optional[str] = ..., 
                is_primary: Optional[bool] = ..., 
                is_seleted_for_failover: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                recovery_ip_address_type: Optional[str] = ..., 
                recovery_lb_backend_address_pool_ids: Optional[list[str]] = ..., 
                recovery_public_ip_address_id: Optional[str] = ..., 
                recovery_static_ip_address: Optional[str] = ..., 
                recovery_subnet_name: Optional[str] = ..., 
                static_ip_address: Optional[str] = ..., 
                subnet_name: Optional[str] = ..., 
                tfo_lb_backend_address_pool_ids: Optional[list[str]] = ..., 
                tfo_public_ip_address_id: Optional[str] = ..., 
                tfo_static_ip_address: Optional[str] = ..., 
                tfo_subnet_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.IPConfigInputDetails(_Model):
        ip_config_name: Optional[str]
        is_primary: Optional[bool]
        is_seleted_for_failover: Optional[bool]
        recovery_lb_backend_address_pool_ids: Optional[list[str]]
        recovery_public_ip_address_id: Optional[str]
        recovery_static_ip_address: Optional[str]
        recovery_subnet_name: Optional[str]
        tfo_lb_backend_address_pool_ids: Optional[list[str]]
        tfo_public_ip_address_id: Optional[str]
        tfo_static_ip_address: Optional[str]
        tfo_subnet_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_config_name: Optional[str] = ..., 
                is_primary: Optional[bool] = ..., 
                is_seleted_for_failover: Optional[bool] = ..., 
                recovery_lb_backend_address_pool_ids: Optional[list[str]] = ..., 
                recovery_public_ip_address_id: Optional[str] = ..., 
                recovery_static_ip_address: Optional[str] = ..., 
                recovery_subnet_name: Optional[str] = ..., 
                tfo_lb_backend_address_pool_ids: Optional[list[str]] = ..., 
                tfo_public_ip_address_id: Optional[str] = ..., 
                tfo_static_ip_address: Optional[str] = ..., 
                tfo_subnet_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.IPVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.recoveryservicessiterecovery.models.IdentityProviderDetails(_Model):
        aad_authority: Optional[str]
        application_id: Optional[str]
        audience: Optional[str]
        object_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_authority: Optional[str] = ..., 
                application_id: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.IdentityProviderInput(_Model):
        aad_authority: str
        application_id: str
        audience: str
        object_id: str
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                aad_authority: str, 
                application_id: str, 
                audience: str, 
                object_id: str, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAgentDetails(_Model):
        agent_expiry_date: Optional[datetime]
        agent_update_status: Optional[str]
        agent_version: Optional[str]
        post_update_reboot_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_expiry_date: Optional[datetime] = ..., 
                agent_update_status: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                post_update_reboot_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2ApplyRecoveryPointInput(ApplyRecoveryPointProviderSpecificInput, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2DiskInputDetails(_Model):
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        disk_type: Optional[Union[str, DiskAccountType]]
        log_storage_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                log_storage_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2EnableProtectionInput(EnableProtectionProviderSpecificInput, discriminator='InMageAzureV2'):
        disk_encryption_set_id: Optional[str]
        disk_type: Optional[Union[str, DiskAccountType]]
        disks_to_include: Optional[list[InMageAzureV2DiskInputDetails]]
        enable_rdp_on_target_option: Optional[str]
        instance_type: Literal["InMageAzureV2"]
        license_type: Optional[Union[str, LicenseType]]
        log_storage_account_id: Optional[str]
        master_target_id: Optional[str]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        process_server_id: Optional[str]
        run_as_account_id: Optional[str]
        seed_managed_disk_tags: Optional[dict[str, str]]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        storage_account_id: Optional[str]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_azure_network_id: Optional[str]
        target_azure_subnet_id: Optional[str]
        target_azure_v1_resource_group_id: Optional[str]
        target_azure_v2_resource_group_id: Optional[str]
        target_azure_vm_name: Optional[str]
        target_managed_disk_tags: Optional[dict[str, str]]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                disks_to_include: Optional[list[InMageAzureV2DiskInputDetails]] = ..., 
                enable_rdp_on_target_option: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                log_storage_account_id: Optional[str] = ..., 
                master_target_id: Optional[str] = ..., 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                run_as_account_id: Optional[str] = ..., 
                seed_managed_disk_tags: Optional[dict[str, str]] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                storage_account_id: Optional[str] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_azure_network_id: Optional[str] = ..., 
                target_azure_subnet_id: Optional[str] = ..., 
                target_azure_v1_resource_group_id: Optional[str] = ..., 
                target_azure_v2_resource_group_id: Optional[str] = ..., 
                target_azure_vm_name: Optional[str] = ..., 
                target_managed_disk_tags: Optional[dict[str, str]] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2EventDetails(EventProviderSpecificDetails, discriminator='InMageAzureV2'):
        category: Optional[str]
        component: Optional[str]
        corrective_action: Optional[str]
        details: Optional[str]
        event_type: Optional[str]
        instance_type: Literal["InMageAzureV2"]
        site_name: Optional[str]
        summary: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                component: Optional[str] = ..., 
                corrective_action: Optional[str] = ..., 
                details: Optional[str] = ..., 
                event_type: Optional[str] = ..., 
                site_name: Optional[str] = ..., 
                summary: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2ManagedDiskDetails(_Model):
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        replica_disk_type: Optional[str]
        seed_managed_disk_id: Optional[str]
        target_disk_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                replica_disk_type: Optional[str] = ..., 
                seed_managed_disk_id: Optional[str] = ..., 
                target_disk_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2PolicyDetails(PolicyProviderSpecificDetails, discriminator='InMageAzureV2'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMageAzureV2"]
        multi_vm_sync_status: Optional[str]
        recovery_point_history: Optional[int]
        recovery_point_threshold_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Optional[str] = ..., 
                recovery_point_history: Optional[int] = ..., 
                recovery_point_threshold_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2PolicyInput(PolicyProviderSpecificInput, discriminator='InMageAzureV2'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMageAzureV2"]
        multi_vm_sync_status: Union[str, SetMultiVmSyncStatus]
        recovery_point_history: Optional[int]
        recovery_point_threshold_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Union[str, SetMultiVmSyncStatus], 
                recovery_point_history: Optional[int] = ..., 
                recovery_point_threshold_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2ProtectedDiskDetails(_Model):
        disk_capacity_in_bytes: Optional[int]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_resized: Optional[str]
        file_system_capacity_in_bytes: Optional[int]
        health_error_code: Optional[str]
        last_rpo_calculated_time: Optional[datetime]
        progress_health: Optional[str]
        progress_status: Optional[str]
        protection_stage: Optional[str]
        ps_data_in_mega_bytes: Optional[float]
        resync_duration_in_seconds: Optional[int]
        resync_last15_minutes_transferred_bytes: Optional[int]
        resync_last_data_transfer_time_utc: Optional[datetime]
        resync_processed_bytes: Optional[int]
        resync_progress_percentage: Optional[int]
        resync_required: Optional[str]
        resync_start_time: Optional[datetime]
        resync_total_transferred_bytes: Optional[int]
        rpo_in_seconds: Optional[int]
        seconds_to_take_switch_provider: Optional[int]
        source_data_in_mega_bytes: Optional[float]
        target_data_in_mega_bytes: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                disk_capacity_in_bytes: Optional[int] = ..., 
                disk_id: Optional[str] = ..., 
                disk_name: Optional[str] = ..., 
                disk_resized: Optional[str] = ..., 
                file_system_capacity_in_bytes: Optional[int] = ..., 
                health_error_code: Optional[str] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                progress_health: Optional[str] = ..., 
                progress_status: Optional[str] = ..., 
                protection_stage: Optional[str] = ..., 
                ps_data_in_mega_bytes: Optional[float] = ..., 
                resync_duration_in_seconds: Optional[int] = ..., 
                resync_last15_minutes_transferred_bytes: Optional[int] = ..., 
                resync_last_data_transfer_time_utc: Optional[datetime] = ..., 
                resync_processed_bytes: Optional[int] = ..., 
                resync_progress_percentage: Optional[int] = ..., 
                resync_required: Optional[str] = ..., 
                resync_start_time: Optional[datetime] = ..., 
                resync_total_transferred_bytes: Optional[int] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                seconds_to_take_switch_provider: Optional[int] = ..., 
                source_data_in_mega_bytes: Optional[float] = ..., 
                target_data_in_mega_bytes: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2RecoveryPointDetails(ProviderSpecificRecoveryPointDetails, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]
        is_multi_vm_sync_point: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_multi_vm_sync_point: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2ReplicationDetails(ReplicationProviderSpecificSettings, discriminator='InMageAzureV2'):
        agent_expiry_date: Optional[datetime]
        agent_version: Optional[str]
        all_available_os_upgrade_configurations: Optional[list[OSUpgradeSupportedVersions]]
        azure_vm_disk_details: Optional[list[AzureVmDiskDetails]]
        azure_vm_generation: Optional[str]
        compressed_data_rate_in_mb: Optional[float]
        datastores: Optional[list[str]]
        discovery_type: Optional[str]
        disk_resized: Optional[str]
        enable_rdp_on_target_option: Optional[str]
        firmware_type: Optional[str]
        infrastructure_vm_id: Optional[str]
        instance_type: Literal["InMageAzureV2"]
        ip_address: Optional[str]
        is_additional_stats_available: Optional[bool]
        is_agent_update_required: Optional[str]
        is_reboot_after_update_required: Optional[str]
        last_heartbeat: Optional[datetime]
        last_recovery_point_received: Optional[datetime]
        last_rpo_calculated_time: Optional[datetime]
        last_update_received_time: Optional[datetime]
        license_type: Optional[str]
        master_target_id: Optional[str]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        multi_vm_sync_status: Optional[str]
        os_disk_id: Optional[str]
        os_name: Optional[str]
        os_type: Optional[str]
        os_version: Optional[str]
        process_server_id: Optional[str]
        process_server_name: Optional[str]
        protected_disks: Optional[list[InMageAzureV2ProtectedDiskDetails]]
        protected_managed_disks: Optional[list[InMageAzureV2ManagedDiskDetails]]
        protection_stage: Optional[str]
        recovery_availability_set_id: Optional[str]
        recovery_azure_log_storage_account_id: Optional[str]
        recovery_azure_resource_group_id: Optional[str]
        recovery_azure_storage_account: Optional[str]
        recovery_azure_vm_name: Optional[str]
        recovery_azure_vm_size: Optional[str]
        replica_id: Optional[str]
        resync_progress_percentage: Optional[int]
        rpo_in_seconds: Optional[int]
        seed_managed_disk_tags: Optional[dict[str, str]]
        selected_recovery_azure_network_id: Optional[str]
        selected_source_nic_id: Optional[str]
        selected_tfo_azure_network_id: Optional[str]
        source_vm_cpu_count: Optional[int]
        source_vm_ram_size_in_mb: Optional[int]
        sql_server_license_type: Optional[str]
        supported_os_versions: Optional[list[str]]
        switch_provider_blocking_error_details: Optional[list[InMageAzureV2SwitchProviderBlockingErrorDetails]]
        switch_provider_details: Optional[InMageAzureV2SwitchProviderDetails]
        target_availability_zone: Optional[str]
        target_managed_disk_tags: Optional[dict[str, str]]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_vm_id: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        total_data_transferred: Optional[int]
        total_progress_health: Optional[str]
        uncompressed_data_rate_in_mb: Optional[float]
        use_managed_disks: Optional[str]
        v_center_infrastructure_id: Optional[str]
        validation_errors: Optional[list[HealthError]]
        vhd_name: Optional[str]
        vm_id: Optional[str]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_expiry_date: Optional[datetime] = ..., 
                agent_version: Optional[str] = ..., 
                all_available_os_upgrade_configurations: Optional[list[OSUpgradeSupportedVersions]] = ..., 
                azure_vm_disk_details: Optional[list[AzureVmDiskDetails]] = ..., 
                azure_vm_generation: Optional[str] = ..., 
                compressed_data_rate_in_mb: Optional[float] = ..., 
                datastores: Optional[list[str]] = ..., 
                discovery_type: Optional[str] = ..., 
                disk_resized: Optional[str] = ..., 
                enable_rdp_on_target_option: Optional[str] = ..., 
                firmware_type: Optional[str] = ..., 
                infrastructure_vm_id: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                is_additional_stats_available: Optional[bool] = ..., 
                is_agent_update_required: Optional[str] = ..., 
                is_reboot_after_update_required: Optional[str] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                last_update_received_time: Optional[datetime] = ..., 
                license_type: Optional[str] = ..., 
                master_target_id: Optional[str] = ..., 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                multi_vm_sync_status: Optional[str] = ..., 
                os_disk_id: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                process_server_name: Optional[str] = ..., 
                protected_disks: Optional[list[InMageAzureV2ProtectedDiskDetails]] = ..., 
                protected_managed_disks: Optional[list[InMageAzureV2ManagedDiskDetails]] = ..., 
                protection_stage: Optional[str] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_azure_log_storage_account_id: Optional[str] = ..., 
                recovery_azure_resource_group_id: Optional[str] = ..., 
                recovery_azure_storage_account: Optional[str] = ..., 
                recovery_azure_vm_name: Optional[str] = ..., 
                recovery_azure_vm_size: Optional[str] = ..., 
                replica_id: Optional[str] = ..., 
                resync_progress_percentage: Optional[int] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                seed_managed_disk_tags: Optional[dict[str, str]] = ..., 
                selected_recovery_azure_network_id: Optional[str] = ..., 
                selected_source_nic_id: Optional[str] = ..., 
                selected_tfo_azure_network_id: Optional[str] = ..., 
                source_vm_cpu_count: Optional[int] = ..., 
                source_vm_ram_size_in_mb: Optional[int] = ..., 
                sql_server_license_type: Optional[str] = ..., 
                supported_os_versions: Optional[list[str]] = ..., 
                switch_provider_blocking_error_details: Optional[list[InMageAzureV2SwitchProviderBlockingErrorDetails]] = ..., 
                switch_provider_details: Optional[InMageAzureV2SwitchProviderDetails] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_managed_disk_tags: Optional[dict[str, str]] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_vm_id: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                total_data_transferred: Optional[int] = ..., 
                total_progress_health: Optional[str] = ..., 
                uncompressed_data_rate_in_mb: Optional[float] = ..., 
                use_managed_disks: Optional[str] = ..., 
                v_center_infrastructure_id: Optional[str] = ..., 
                validation_errors: Optional[list[HealthError]] = ..., 
                vhd_name: Optional[str] = ..., 
                vm_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2ReprotectInput(ReverseReplicationProviderSpecificInput, discriminator='InMageAzureV2'):
        disks_to_include: Optional[list[str]]
        instance_type: Literal["InMageAzureV2"]
        log_storage_account_id: Optional[str]
        master_target_id: Optional[str]
        policy_id: Optional[str]
        process_server_id: Optional[str]
        run_as_account_id: Optional[str]
        storage_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disks_to_include: Optional[list[str]] = ..., 
                log_storage_account_id: Optional[str] = ..., 
                master_target_id: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                run_as_account_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2SwitchProviderBlockingErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2SwitchProviderDetails(_Model):
        target_appliance_id: Optional[str]
        target_fabric_id: Optional[str]
        target_resource_id: Optional[str]
        target_vault_id: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2SwitchProviderInput(SwitchProviderSpecificInput, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]
        target_appliance_id: str
        target_fabric_id: str
        target_vault_id: str

        @overload
        def __init__(
                self, 
                *, 
                target_appliance_id: str, 
                target_fabric_id: str, 
                target_vault_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2TestFailoverInput(TestFailoverProviderSpecificInput, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]
        os_upgrade_version: Optional[str]
        recovery_point_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_upgrade_version: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2UnplannedFailoverInput(UnplannedFailoverProviderSpecificInput, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]
        os_upgrade_version: Optional[str]
        recovery_point_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_upgrade_version: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageAzureV2UpdateReplicationProtectedItemInput(UpdateReplicationProtectedItemProviderInput, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]
        recovery_azure_v1_resource_group_id: Optional[str]
        recovery_azure_v2_resource_group_id: Optional[str]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_zone: Optional[str]
        target_managed_disk_tags: Optional[dict[str, str]]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        use_managed_disks: Optional[str]
        vm_disks: Optional[list[UpdateDiskInput]]

        @overload
        def __init__(
                self, 
                *, 
                recovery_azure_v1_resource_group_id: Optional[str] = ..., 
                recovery_azure_v2_resource_group_id: Optional[str] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_managed_disk_tags: Optional[dict[str, str]] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                use_managed_disks: Optional[str] = ..., 
                vm_disks: Optional[list[UpdateDiskInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageBasePolicyDetails(PolicyProviderSpecificDetails, discriminator='InMageBasePolicyDetails'):
        app_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMageBasePolicyDetails"]
        multi_vm_sync_status: Optional[str]
        recovery_point_history: Optional[int]
        recovery_point_threshold_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Optional[str] = ..., 
                recovery_point_history: Optional[int] = ..., 
                recovery_point_threshold_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageDisableProtectionProviderSpecificInput(DisableProtectionProviderSpecificInput, discriminator='InMage'):
        instance_type: Literal["InMage"]
        replica_vm_deletion_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                replica_vm_deletion_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageDiskDetails(_Model):
        disk_configuration: Optional[str]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_size_in_mb: Optional[str]
        disk_type: Optional[str]
        volume_list: Optional[list[DiskVolumeDetails]]

        @overload
        def __init__(
                self, 
                *, 
                disk_configuration: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                disk_name: Optional[str] = ..., 
                disk_size_in_mb: Optional[str] = ..., 
                disk_type: Optional[str] = ..., 
                volume_list: Optional[list[DiskVolumeDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageDiskExclusionInput(_Model):
        disk_signature_options: Optional[list[InMageDiskSignatureExclusionOptions]]
        volume_options: Optional[list[InMageVolumeExclusionOptions]]

        @overload
        def __init__(
                self, 
                *, 
                disk_signature_options: Optional[list[InMageDiskSignatureExclusionOptions]] = ..., 
                volume_options: Optional[list[InMageVolumeExclusionOptions]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageDiskSignatureExclusionOptions(_Model):
        disk_signature: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_signature: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageEnableProtectionInput(EnableProtectionProviderSpecificInput, discriminator='InMage'):
        datastore_name: Optional[str]
        disk_exclusion_input: Optional[InMageDiskExclusionInput]
        disks_to_include: Optional[list[str]]
        instance_type: Literal["InMage"]
        master_target_id: str
        multi_vm_group_id: str
        multi_vm_group_name: str
        process_server_id: str
        retention_drive: str
        run_as_account_id: Optional[str]
        vm_friendly_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                datastore_name: Optional[str] = ..., 
                disk_exclusion_input: Optional[InMageDiskExclusionInput] = ..., 
                disks_to_include: Optional[list[str]] = ..., 
                master_target_id: str, 
                multi_vm_group_id: str, 
                multi_vm_group_name: str, 
                process_server_id: str, 
                retention_drive: str, 
                run_as_account_id: Optional[str] = ..., 
                vm_friendly_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageFabricSwitchProviderBlockingErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMagePolicyDetails(PolicyProviderSpecificDetails, discriminator='InMage'):
        app_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMage"]
        multi_vm_sync_status: Optional[str]
        recovery_point_history: Optional[int]
        recovery_point_threshold_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Optional[str] = ..., 
                recovery_point_history: Optional[int] = ..., 
                recovery_point_threshold_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMagePolicyInput(PolicyProviderSpecificInput, discriminator='InMage'):
        app_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMage"]
        multi_vm_sync_status: Union[str, SetMultiVmSyncStatus]
        recovery_point_history: Optional[int]
        recovery_point_threshold_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Union[str, SetMultiVmSyncStatus], 
                recovery_point_history: Optional[int] = ..., 
                recovery_point_threshold_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageProtectedDiskDetails(_Model):
        disk_capacity_in_bytes: Optional[int]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_resized: Optional[str]
        file_system_capacity_in_bytes: Optional[int]
        health_error_code: Optional[str]
        last_rpo_calculated_time: Optional[datetime]
        progress_health: Optional[str]
        progress_status: Optional[str]
        protection_stage: Optional[str]
        ps_data_in_mb: Optional[float]
        resync_duration_in_seconds: Optional[int]
        resync_last15_minutes_transferred_bytes: Optional[int]
        resync_last_data_transfer_time_utc: Optional[datetime]
        resync_processed_bytes: Optional[int]
        resync_progress_percentage: Optional[int]
        resync_required: Optional[str]
        resync_start_time: Optional[datetime]
        resync_total_transferred_bytes: Optional[int]
        rpo_in_seconds: Optional[int]
        source_data_in_mb: Optional[float]
        target_data_in_mb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                disk_capacity_in_bytes: Optional[int] = ..., 
                disk_id: Optional[str] = ..., 
                disk_name: Optional[str] = ..., 
                disk_resized: Optional[str] = ..., 
                file_system_capacity_in_bytes: Optional[int] = ..., 
                health_error_code: Optional[str] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                progress_health: Optional[str] = ..., 
                progress_status: Optional[str] = ..., 
                protection_stage: Optional[str] = ..., 
                ps_data_in_mb: Optional[float] = ..., 
                resync_duration_in_seconds: Optional[int] = ..., 
                resync_last15_minutes_transferred_bytes: Optional[int] = ..., 
                resync_last_data_transfer_time_utc: Optional[datetime] = ..., 
                resync_processed_bytes: Optional[int] = ..., 
                resync_progress_percentage: Optional[int] = ..., 
                resync_required: Optional[str] = ..., 
                resync_start_time: Optional[datetime] = ..., 
                resync_total_transferred_bytes: Optional[int] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                source_data_in_mb: Optional[float] = ..., 
                target_data_in_mb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmAddDisksInput(AddDisksProviderSpecificInput, discriminator='InMageRcm'):
        disks: list[InMageRcmDiskInput]
        instance_type: Literal["InMageRcm"]

        @overload
        def __init__(
                self, 
                *, 
                disks: list[InMageRcmDiskInput]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmAgentReinstallBlockingErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                error_message_parameters: Optional[dict[str, str]] = ..., 
                error_tags: Optional[dict[str, str]] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmAgentUpgradeBlockingErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmApplianceDetails(_Model):
        dra: Optional[DraDetails]
        fabric_arm_id: Optional[str]
        id: Optional[str]
        mars_agent: Optional[MarsAgentDetails]
        name: Optional[str]
        process_server: Optional[ProcessServerDetails]
        push_installer: Optional[PushInstallerDetails]
        rcm_proxy: Optional[RcmProxyDetails]
        replication_agent: Optional[ReplicationAgentDetails]
        reprotect_agent: Optional[ReprotectAgentDetails]
        switch_provider_blocking_error_details: Optional[list[InMageRcmFabricSwitchProviderBlockingErrorDetails]]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmApplianceSpecificDetails(ApplianceSpecificDetails, discriminator='InMageRcm'):
        appliances: Optional[list[InMageRcmApplianceDetails]]
        instance_type: Literal["InMageRcm"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmApplyRecoveryPointInput(ApplyRecoveryPointProviderSpecificInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        recovery_point_id: str

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmDiscoveredProtectedVmDetails(_Model):
        created_timestamp: Optional[datetime]
        datastores: Optional[list[str]]
        ip_addresses: Optional[list[str]]
        is_deleted: Optional[bool]
        last_discovery_time_in_utc: Optional[datetime]
        os_name: Optional[str]
        power_status: Optional[str]
        updated_timestamp: Optional[datetime]
        v_center_fqdn: Optional[str]
        v_center_id: Optional[str]
        vm_fqdn: Optional[str]
        vmware_tools_status: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmDiskInput(_Model):
        confidential_disk_encryption_set_id: Optional[str]
        disk_encryption_set_id: Optional[str]
        disk_id: str
        disk_size_in_gb: Optional[int]
        disk_type: Union[str, DiskAccountType]
        iops: Optional[int]
        log_storage_account_id: str
        sector_size_in_bytes: Optional[int]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                confidential_disk_encryption_set_id: Optional[str] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: str, 
                disk_size_in_gb: Optional[int] = ..., 
                disk_type: Union[str, DiskAccountType], 
                iops: Optional[int] = ..., 
                log_storage_account_id: str, 
                sector_size_in_bytes: Optional[int] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmDisksDefaultInput(_Model):
        confidential_disk_encryption_set_id: Optional[str]
        disk_encryption_set_id: Optional[str]
        disk_size_in_gb: Optional[int]
        disk_type: Union[str, DiskAccountType]
        iops: Optional[int]
        log_storage_account_id: str
        sector_size_in_bytes: Optional[int]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                confidential_disk_encryption_set_id: Optional[str] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_size_in_gb: Optional[int] = ..., 
                disk_type: Union[str, DiskAccountType], 
                iops: Optional[int] = ..., 
                log_storage_account_id: str, 
                sector_size_in_bytes: Optional[int] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmEnableProtectionInput(EnableProtectionProviderSpecificInput, discriminator='InMageRcm'):
        disks_default: Optional[InMageRcmDisksDefaultInput]
        disks_to_include: Optional[list[InMageRcmDiskInput]]
        fabric_discovery_machine_id: str
        instance_type: Literal["InMageRcm"]
        license_type: Optional[Union[str, LicenseType]]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        multi_vm_group_name: Optional[str]
        process_server_id: str
        run_as_account_id: Optional[str]
        seed_managed_disk_tags: Optional[list[UserCreatedResourceTag]]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_boot_diagnostics_storage_account_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_extended_location: Optional[ExtendedLocation]
        target_managed_disk_tags: Optional[list[UserCreatedResourceTag]]
        target_network_id: Optional[str]
        target_nic_tags: Optional[list[UserCreatedResourceTag]]
        target_proximity_placement_group_id: Optional[str]
        target_resource_group_id: str
        target_subnet_name: Optional[str]
        target_vm_name: Optional[str]
        target_vm_security_profile: Optional[SecurityProfileProperties]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[list[UserCreatedResourceTag]]
        test_network_id: Optional[str]
        test_subnet_name: Optional[str]
        user_selected_os_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disks_default: Optional[InMageRcmDisksDefaultInput] = ..., 
                disks_to_include: Optional[list[InMageRcmDiskInput]] = ..., 
                fabric_discovery_machine_id: str, 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                process_server_id: str, 
                run_as_account_id: Optional[str] = ..., 
                seed_managed_disk_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_boot_diagnostics_storage_account_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_extended_location: Optional[ExtendedLocation] = ..., 
                target_managed_disk_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                target_network_id: Optional[str] = ..., 
                target_nic_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_resource_group_id: str, 
                target_subnet_name: Optional[str] = ..., 
                target_vm_name: Optional[str] = ..., 
                target_vm_security_profile: Optional[SecurityProfileProperties] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                test_network_id: Optional[str] = ..., 
                test_subnet_name: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmEventDetails(EventProviderSpecificDetails, discriminator='InMageRcm'):
        appliance_name: Optional[str]
        component_display_name: Optional[str]
        fabric_name: Optional[str]
        instance_type: Literal["InMageRcm"]
        job_id: Optional[str]
        latest_agent_version: Optional[str]
        protected_item_name: Optional[str]
        server_type: Optional[str]
        vm_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFabricCreationInput(FabricSpecificCreationInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        physical_site_id: str
        source_agent_identity: IdentityProviderInput
        vmware_site_id: str

        @overload
        def __init__(
                self, 
                *, 
                physical_site_id: str, 
                source_agent_identity: IdentityProviderInput, 
                vmware_site_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFabricSpecificDetails(FabricSpecificDetails, discriminator='InMageRcm'):
        agent_details: Optional[list[AgentDetails]]
        control_plane_uri: Optional[str]
        data_plane_uri: Optional[str]
        dras: Optional[list[DraDetails]]
        instance_type: Literal["InMageRcm"]
        mars_agents: Optional[list[MarsAgentDetails]]
        physical_site_id: Optional[str]
        process_servers: Optional[list[ProcessServerDetails]]
        push_installers: Optional[list[PushInstallerDetails]]
        rcm_proxies: Optional[list[RcmProxyDetails]]
        replication_agents: Optional[list[ReplicationAgentDetails]]
        reprotect_agents: Optional[list[ReprotectAgentDetails]]
        service_container_id: Optional[str]
        service_endpoint: Optional[str]
        service_resource_id: Optional[str]
        source_agent_identity_details: Optional[IdentityProviderDetails]
        vmware_site_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_agent_identity_details: Optional[IdentityProviderDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFabricSwitchProviderBlockingErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackDiscoveredProtectedVmDetails(_Model):
        created_timestamp: Optional[datetime]
        datastores: Optional[list[str]]
        ip_addresses: Optional[list[str]]
        is_deleted: Optional[bool]
        last_discovery_time_in_utc: Optional[datetime]
        os_name: Optional[str]
        power_status: Optional[str]
        updated_timestamp: Optional[datetime]
        v_center_fqdn: Optional[str]
        v_center_id: Optional[str]
        vm_fqdn: Optional[str]
        vmware_tools_status: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackEventDetails(EventProviderSpecificDetails, discriminator='InMageRcmFailback'):
        appliance_name: Optional[str]
        component_display_name: Optional[str]
        instance_type: Literal["InMageRcmFailback"]
        protected_item_name: Optional[str]
        server_type: Optional[str]
        vm_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackMobilityAgentDetails(_Model):
        agent_version_expiry_date: Optional[datetime]
        driver_version: Optional[str]
        driver_version_expiry_date: Optional[datetime]
        is_upgradeable: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        latest_upgradable_version_without_reboot: Optional[str]
        latest_version: Optional[str]
        reasons_blocking_upgrade: Optional[list[Union[str, AgentUpgradeBlockedReason]]]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackNicDetails(_Model):
        adapter_type: Optional[str]
        mac_address: Optional[str]
        network_name: Optional[str]
        source_ip_address: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackPlannedFailoverProviderInput(PlannedFailoverProviderSpecificFailoverInput, discriminator='InMageRcmFailback'):
        instance_type: Literal["InMageRcmFailback"]
        recovery_point_type: Union[str, InMageRcmFailbackRecoveryPointType]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_type: Union[str, InMageRcmFailbackRecoveryPointType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackPolicyCreationInput(PolicyProviderSpecificInput, discriminator='InMageRcmFailback'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMageRcmFailback"]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackPolicyDetails(PolicyProviderSpecificDetails, discriminator='InMageRcmFailback'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["InMageRcmFailback"]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackProtectedDiskDetails(_Model):
        capacity_in_bytes: Optional[int]
        data_pending_at_source_agent_in_mb: Optional[float]
        data_pending_in_log_data_store_in_mb: Optional[float]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_uuid: Optional[str]
        ir_details: Optional[InMageRcmFailbackSyncDetails]
        is_initial_replication_complete: Optional[str]
        is_os_disk: Optional[str]
        last_sync_time: Optional[datetime]
        resync_details: Optional[InMageRcmFailbackSyncDetails]

        @overload
        def __init__(
                self, 
                *, 
                ir_details: Optional[InMageRcmFailbackSyncDetails] = ..., 
                resync_details: Optional[InMageRcmFailbackSyncDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_CONSISTENT = "ApplicationConsistent"
        CRASH_CONSISTENT = "CrashConsistent"


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackReplicationDetails(ReplicationProviderSpecificSettings, discriminator='InMageRcmFailback'):
        azure_virtual_machine_id: Optional[str]
        discovered_vm_details: Optional[InMageRcmFailbackDiscoveredProtectedVmDetails]
        initial_replication_processed_bytes: Optional[int]
        initial_replication_progress_health: Optional[Union[str, VmReplicationProgressHealth]]
        initial_replication_progress_percentage: Optional[int]
        initial_replication_transferred_bytes: Optional[int]
        instance_type: Literal["InMageRcmFailback"]
        internal_identifier: Optional[str]
        is_agent_registration_successful_after_failover: Optional[bool]
        last_planned_failover_start_time: Optional[datetime]
        last_planned_failover_status: Optional[Union[str, PlannedFailoverStatus]]
        last_used_policy_friendly_name: Optional[str]
        last_used_policy_id: Optional[str]
        log_storage_account_id: Optional[str]
        mobility_agent_details: Optional[InMageRcmFailbackMobilityAgentDetails]
        multi_vm_group_name: Optional[str]
        os_type: Optional[str]
        protected_disks: Optional[list[InMageRcmFailbackProtectedDiskDetails]]
        reprotect_agent_id: Optional[str]
        reprotect_agent_name: Optional[str]
        resync_processed_bytes: Optional[int]
        resync_progress_health: Optional[Union[str, VmReplicationProgressHealth]]
        resync_progress_percentage: Optional[int]
        resync_required: Optional[str]
        resync_state: Optional[Union[str, ResyncState]]
        resync_transferred_bytes: Optional[int]
        target_data_store_name: Optional[str]
        target_vm_name: Optional[str]
        targetv_center_id: Optional[str]
        vm_nics: Optional[list[InMageRcmFailbackNicDetails]]

        @overload
        def __init__(
                self, 
                *, 
                discovered_vm_details: Optional[InMageRcmFailbackDiscoveredProtectedVmDetails] = ..., 
                mobility_agent_details: Optional[InMageRcmFailbackMobilityAgentDetails] = ..., 
                protected_disks: Optional[list[InMageRcmFailbackProtectedDiskDetails]] = ..., 
                vm_nics: Optional[list[InMageRcmFailbackNicDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackReprotectInput(ReverseReplicationProviderSpecificInput, discriminator='InMageRcmFailback'):
        instance_type: Literal["InMageRcmFailback"]
        policy_id: str
        process_server_id: str
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: str, 
                process_server_id: str, 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmFailbackSyncDetails(_Model):
        last15_minutes_transferred_bytes: Optional[int]
        last_data_transfer_time_utc: Optional[str]
        last_refresh_time: Optional[str]
        processed_bytes: Optional[int]
        progress_health: Optional[Union[str, DiskReplicationProgressHealth]]
        progress_percentage: Optional[int]
        start_time: Optional[str]
        transferred_bytes: Optional[int]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmLastAgentUpgradeErrorDetails(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        error_message_parameters: Optional[dict[str, str]]
        error_tags: Optional[dict[str, str]]
        possible_causes: Optional[str]
        recommended_action: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmMobilityAgentDetails(_Model):
        agent_reinstall_attempt_to_version: Optional[str]
        agent_reinstall_job_id: Optional[str]
        agent_reinstall_state: Optional[Union[str, MobilityAgentReinstallType]]
        agent_version_expiry_date: Optional[datetime]
        distro_name: Optional[str]
        distro_name_for_which_agent_is_installed: Optional[str]
        driver_version: Optional[str]
        driver_version_expiry_date: Optional[datetime]
        is_agent_reinstall_required: Optional[bool]
        is_agent_upgradeable: Optional[bool]
        is_last_reinstall_successful: Optional[bool]
        is_upgradeable: Optional[str]
        last_agent_reinstall_type: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        latest_agent_release_date: Optional[str]
        latest_upgradable_version_without_reboot: Optional[str]
        latest_version: Optional[str]
        os_family_name: Optional[str]
        reasons_blocking_reinstall: Optional[list[Union[str, AgentReinstallBlockedReason]]]
        reasons_blocking_reinstall_details: Optional[list[InMageRcmAgentReinstallBlockingErrorDetails]]
        reasons_blocking_upgrade: Optional[list[Union[str, AgentUpgradeBlockedReason]]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                distro_name: Optional[str] = ..., 
                distro_name_for_which_agent_is_installed: Optional[str] = ..., 
                is_agent_reinstall_required: Optional[bool] = ..., 
                is_agent_upgradeable: Optional[bool] = ..., 
                is_last_reinstall_successful: Optional[bool] = ..., 
                os_family_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmNicDetails(_Model):
        is_primary_nic: Optional[str]
        is_selected_for_failover: Optional[str]
        nic_id: Optional[str]
        source_ip_address: Optional[str]
        source_ip_address_type: Optional[Union[str, EthernetAddressType]]
        source_network_id: Optional[str]
        source_subnet_name: Optional[str]
        target_ip_address: Optional[str]
        target_ip_address_type: Optional[Union[str, EthernetAddressType]]
        target_nic_name: Optional[str]
        target_subnet_name: Optional[str]
        test_ip_address: Optional[str]
        test_ip_address_type: Optional[Union[str, EthernetAddressType]]
        test_subnet_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_primary_nic: Optional[str] = ..., 
                is_selected_for_failover: Optional[str] = ..., 
                target_ip_address: Optional[str] = ..., 
                target_ip_address_type: Optional[Union[str, EthernetAddressType]] = ..., 
                target_nic_name: Optional[str] = ..., 
                target_subnet_name: Optional[str] = ..., 
                test_ip_address: Optional[str] = ..., 
                test_ip_address_type: Optional[Union[str, EthernetAddressType]] = ..., 
                test_subnet_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmNicInput(_Model):
        is_primary_nic: str
        is_selected_for_failover: Optional[str]
        nic_id: str
        target_nic_name: Optional[str]
        target_static_ip_address: Optional[str]
        target_subnet_name: Optional[str]
        test_static_ip_address: Optional[str]
        test_subnet_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_primary_nic: str, 
                is_selected_for_failover: Optional[str] = ..., 
                nic_id: str, 
                target_nic_name: Optional[str] = ..., 
                target_static_ip_address: Optional[str] = ..., 
                target_subnet_name: Optional[str] = ..., 
                test_static_ip_address: Optional[str] = ..., 
                test_subnet_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmPolicyCreationInput(PolicyProviderSpecificInput, discriminator='InMageRcm'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        enable_multi_vm_sync: Optional[str]
        instance_type: Literal["InMageRcm"]
        recovery_point_history_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                enable_multi_vm_sync: Optional[str] = ..., 
                recovery_point_history_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmPolicyDetails(PolicyProviderSpecificDetails, discriminator='InMageRcm'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        enable_multi_vm_sync: Optional[str]
        instance_type: Literal["InMageRcm"]
        recovery_point_history_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                enable_multi_vm_sync: Optional[str] = ..., 
                recovery_point_history_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmProtectedDiskDetails(_Model):
        capacity_in_bytes: Optional[int]
        confidential_disk_encryption_set_id: Optional[str]
        custom_target_disk_name: Optional[str]
        data_pending_at_source_agent_in_mb: Optional[float]
        data_pending_in_log_data_store_in_mb: Optional[float]
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_size_in_gb: Optional[int]
        disk_state: Optional[Union[str, DiskState]]
        disk_type: Optional[Union[str, DiskAccountType]]
        iops: Optional[int]
        ir_details: Optional[InMageRcmSyncDetails]
        is_initial_replication_complete: Optional[str]
        is_os_disk: Optional[str]
        log_storage_account_id: Optional[str]
        resync_details: Optional[InMageRcmSyncDetails]
        sector_size_in_bytes: Optional[int]
        seed_blob_uri: Optional[str]
        seed_managed_disk_id: Optional[str]
        target_managed_disk_id: Optional[str]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                custom_target_disk_name: Optional[str] = ..., 
                disk_size_in_gb: Optional[int] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                iops: Optional[int] = ..., 
                ir_details: Optional[InMageRcmSyncDetails] = ..., 
                resync_details: Optional[InMageRcmSyncDetails] = ..., 
                sector_size_in_bytes: Optional[int] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmProtectionContainerMappingDetails(ProtectionContainerMappingProviderSpecificDetails, discriminator='InMageRcm'):
        enable_agent_auto_upgrade: Optional[str]
        instance_type: Literal["InMageRcm"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmRecoveryPointDetails(ProviderSpecificRecoveryPointDetails, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        is_multi_vm_sync_point: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmReplicationDetails(ReplicationProviderSpecificSettings, discriminator='InMageRcm'):
        agent_upgrade_attempt_to_version: Optional[str]
        agent_upgrade_blocking_error_details: Optional[list[InMageRcmAgentUpgradeBlockingErrorDetails]]
        agent_upgrade_job_id: Optional[str]
        agent_upgrade_state: Optional[Union[str, MobilityAgentUpgradeState]]
        allocated_memory_in_mb: Optional[float]
        discovered_vm_details: Optional[InMageRcmDiscoveredProtectedVmDetails]
        discovery_type: Optional[str]
        fabric_discovery_machine_id: Optional[str]
        failover_recovery_point_id: Optional[str]
        firmware_type: Optional[str]
        initial_replication_processed_bytes: Optional[int]
        initial_replication_progress_health: Optional[Union[str, VmReplicationProgressHealth]]
        initial_replication_progress_percentage: Optional[int]
        initial_replication_transferred_bytes: Optional[int]
        instance_type: Literal["InMageRcm"]
        internal_identifier: Optional[str]
        is_agent_registration_successful_after_failover: Optional[bool]
        is_last_upgrade_successful: Optional[str]
        last_agent_upgrade_error_details: Optional[list[InMageRcmLastAgentUpgradeErrorDetails]]
        last_agent_upgrade_type: Optional[str]
        last_recovery_point_id: Optional[str]
        last_recovery_point_received: Optional[datetime]
        last_rpo_calculated_time: Optional[datetime]
        last_rpo_in_seconds: Optional[int]
        license_type: Optional[str]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        mobility_agent_details: Optional[InMageRcmMobilityAgentDetails]
        multi_vm_group_name: Optional[str]
        os_name: Optional[str]
        os_type: Optional[str]
        primary_nic_ip_address: Optional[str]
        process_server_id: Optional[str]
        process_server_name: Optional[str]
        processor_core_count: Optional[int]
        protected_disks: Optional[list[InMageRcmProtectedDiskDetails]]
        resync_processed_bytes: Optional[int]
        resync_progress_health: Optional[Union[str, VmReplicationProgressHealth]]
        resync_progress_percentage: Optional[int]
        resync_required: Optional[str]
        resync_state: Optional[Union[str, ResyncState]]
        resync_transferred_bytes: Optional[int]
        run_as_account_id: Optional[str]
        seed_managed_disk_tags: Optional[list[UserCreatedResourceTag]]
        sql_server_license_type: Optional[str]
        storage_account_id: Optional[str]
        supported_os_versions: Optional[list[str]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_boot_diagnostics_storage_account_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_extended_location: Optional[ExtendedLocation]
        target_generation: Optional[str]
        target_location: Optional[str]
        target_managed_disk_tags: Optional[list[UserCreatedResourceTag]]
        target_network_id: Optional[str]
        target_nic_tags: Optional[list[UserCreatedResourceTag]]
        target_proximity_placement_group_id: Optional[str]
        target_resource_group_id: Optional[str]
        target_vm_name: Optional[str]
        target_vm_security_profile: Optional[SecurityProfileProperties]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[list[UserCreatedResourceTag]]
        test_network_id: Optional[str]
        unprotected_disks: Optional[list[InMageRcmUnProtectedDiskDetails]]
        vm_nics: Optional[list[InMageRcmNicDetails]]

        @overload
        def __init__(
                self, 
                *, 
                agent_upgrade_blocking_error_details: Optional[list[InMageRcmAgentUpgradeBlockingErrorDetails]] = ..., 
                discovered_vm_details: Optional[InMageRcmDiscoveredProtectedVmDetails] = ..., 
                last_agent_upgrade_error_details: Optional[list[InMageRcmLastAgentUpgradeErrorDetails]] = ..., 
                license_type: Optional[str] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                mobility_agent_details: Optional[InMageRcmMobilityAgentDetails] = ..., 
                os_name: Optional[str] = ..., 
                protected_disks: Optional[list[InMageRcmProtectedDiskDetails]] = ..., 
                seed_managed_disk_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                sql_server_license_type: Optional[str] = ..., 
                supported_os_versions: Optional[list[str]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_boot_diagnostics_storage_account_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_extended_location: Optional[ExtendedLocation] = ..., 
                target_location: Optional[str] = ..., 
                target_managed_disk_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                target_network_id: Optional[str] = ..., 
                target_nic_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_vm_name: Optional[str] = ..., 
                target_vm_security_profile: Optional[SecurityProfileProperties] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                test_network_id: Optional[str] = ..., 
                unprotected_disks: Optional[list[InMageRcmUnProtectedDiskDetails]] = ..., 
                vm_nics: Optional[list[InMageRcmNicDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmReprotectInput(ReverseReplicationProviderSpecificInput, discriminator='InMageRcm'):
        datastore_name: str
        instance_type: Literal["InMageRcm"]
        log_storage_account_id: str
        policy_id: Optional[str]
        reprotect_agent_id: str

        @overload
        def __init__(
                self, 
                *, 
                datastore_name: str, 
                log_storage_account_id: str, 
                policy_id: Optional[str] = ..., 
                reprotect_agent_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmSyncDetails(_Model):
        last15_minutes_transferred_bytes: Optional[int]
        last_data_transfer_time_utc: Optional[str]
        last_refresh_time: Optional[str]
        processed_bytes: Optional[int]
        progress_health: Optional[Union[str, DiskReplicationProgressHealth]]
        progress_percentage: Optional[int]
        start_time: Optional[str]
        transferred_bytes: Optional[int]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmTestFailoverInput(TestFailoverProviderSpecificInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        network_id: Optional[str]
        os_upgrade_version: Optional[str]
        recovery_point_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                network_id: Optional[str] = ..., 
                os_upgrade_version: Optional[str] = ..., 
                recovery_point_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmUnProtectedDiskDetails(_Model):
        capacity_in_bytes: Optional[int]
        disk_id: Optional[str]
        disk_name: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmUnplannedFailoverInput(UnplannedFailoverProviderSpecificInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        os_upgrade_version: Optional[str]
        perform_shutdown: str
        recovery_point_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_upgrade_version: Optional[str] = ..., 
                perform_shutdown: str, 
                recovery_point_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmUpdateApplianceForReplicationProtectedItemInput(UpdateApplianceForReplicationProtectedItemProviderSpecificInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmUpdateContainerMappingInput(ReplicationProviderSpecificUpdateContainerMappingInput, discriminator='InMageRcm'):
        enable_agent_auto_upgrade: str
        instance_type: Literal["InMageRcm"]

        @overload
        def __init__(
                self, 
                *, 
                enable_agent_auto_upgrade: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageRcmUpdateReplicationProtectedItemInput(UpdateReplicationProtectedItemProviderInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        license_type: Optional[Union[str, LicenseType]]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_boot_diagnostics_storage_account_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_managed_disk_tags: Optional[list[UserCreatedResourceTag]]
        target_network_id: Optional[str]
        target_nic_tags: Optional[list[UserCreatedResourceTag]]
        target_proximity_placement_group_id: Optional[str]
        target_resource_group_id: Optional[str]
        target_vm_name: Optional[str]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[list[UserCreatedResourceTag]]
        test_network_id: Optional[str]
        user_selected_os_name: Optional[str]
        vm_disks: Optional[list[UpdateDiskInput]]
        vm_nics: Optional[list[InMageRcmNicInput]]

        @overload
        def __init__(
                self, 
                *, 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_boot_diagnostics_storage_account_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_managed_disk_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                target_network_id: Optional[str] = ..., 
                target_nic_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_vm_name: Optional[str] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[list[UserCreatedResourceTag]] = ..., 
                test_network_id: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ..., 
                vm_disks: Optional[list[UpdateDiskInput]] = ..., 
                vm_nics: Optional[list[InMageRcmNicInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageReplicationDetails(ReplicationProviderSpecificSettings, discriminator='InMage'):
        active_site_type: Optional[str]
        agent_details: Optional[InMageAgentDetails]
        azure_storage_account_id: Optional[str]
        compressed_data_rate_in_mb: Optional[float]
        consistency_points: Optional[dict[str, datetime]]
        datastores: Optional[list[str]]
        discovery_type: Optional[str]
        disk_resized: Optional[str]
        infrastructure_vm_id: Optional[str]
        instance_type: Literal["InMage"]
        ip_address: Optional[str]
        is_additional_stats_available: Optional[bool]
        last_heartbeat: Optional[datetime]
        last_rpo_calculated_time: Optional[datetime]
        last_update_received_time: Optional[datetime]
        master_target_id: Optional[str]
        multi_vm_group_id: Optional[str]
        multi_vm_group_name: Optional[str]
        multi_vm_sync_status: Optional[str]
        os_details: Optional[OSDiskDetails]
        os_version: Optional[str]
        process_server_id: Optional[str]
        protected_disks: Optional[list[InMageProtectedDiskDetails]]
        protection_stage: Optional[str]
        reboot_after_update_status: Optional[str]
        replica_id: Optional[str]
        resync_details: Optional[InitialReplicationDetails]
        retention_window_end: Optional[datetime]
        retention_window_start: Optional[datetime]
        rpo_in_seconds: Optional[int]
        source_vm_cpu_count: Optional[int]
        source_vm_ram_size_in_mb: Optional[int]
        total_data_transferred: Optional[int]
        total_progress_health: Optional[str]
        uncompressed_data_rate_in_mb: Optional[float]
        v_center_infrastructure_id: Optional[str]
        validation_errors: Optional[list[HealthError]]
        vm_id: Optional[str]
        vm_nics: Optional[list[VMNicDetails]]
        vm_protection_state: Optional[str]
        vm_protection_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_site_type: Optional[str] = ..., 
                agent_details: Optional[InMageAgentDetails] = ..., 
                azure_storage_account_id: Optional[str] = ..., 
                compressed_data_rate_in_mb: Optional[float] = ..., 
                consistency_points: Optional[dict[str, datetime]] = ..., 
                datastores: Optional[list[str]] = ..., 
                discovery_type: Optional[str] = ..., 
                disk_resized: Optional[str] = ..., 
                infrastructure_vm_id: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                is_additional_stats_available: Optional[bool] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                last_rpo_calculated_time: Optional[datetime] = ..., 
                last_update_received_time: Optional[datetime] = ..., 
                master_target_id: Optional[str] = ..., 
                multi_vm_group_id: Optional[str] = ..., 
                multi_vm_group_name: Optional[str] = ..., 
                multi_vm_sync_status: Optional[str] = ..., 
                os_details: Optional[OSDiskDetails] = ..., 
                os_version: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                protected_disks: Optional[list[InMageProtectedDiskDetails]] = ..., 
                protection_stage: Optional[str] = ..., 
                reboot_after_update_status: Optional[str] = ..., 
                replica_id: Optional[str] = ..., 
                resync_details: Optional[InitialReplicationDetails] = ..., 
                retention_window_end: Optional[datetime] = ..., 
                retention_window_start: Optional[datetime] = ..., 
                rpo_in_seconds: Optional[int] = ..., 
                source_vm_cpu_count: Optional[int] = ..., 
                source_vm_ram_size_in_mb: Optional[int] = ..., 
                total_data_transferred: Optional[int] = ..., 
                total_progress_health: Optional[str] = ..., 
                uncompressed_data_rate_in_mb: Optional[float] = ..., 
                v_center_infrastructure_id: Optional[str] = ..., 
                validation_errors: Optional[list[HealthError]] = ..., 
                vm_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicDetails]] = ..., 
                vm_protection_state: Optional[str] = ..., 
                vm_protection_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageReprotectInput(ReverseReplicationProviderSpecificInput, discriminator='InMage'):
        datastore_name: Optional[str]
        disk_exclusion_input: Optional[InMageDiskExclusionInput]
        disks_to_include: Optional[list[str]]
        instance_type: Literal["InMage"]
        master_target_id: str
        process_server_id: str
        profile_id: str
        retention_drive: str
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                datastore_name: Optional[str] = ..., 
                disk_exclusion_input: Optional[InMageDiskExclusionInput] = ..., 
                disks_to_include: Optional[list[str]] = ..., 
                master_target_id: str, 
                process_server_id: str, 
                profile_id: str, 
                retention_drive: str, 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageTestFailoverInput(TestFailoverProviderSpecificInput, discriminator='InMage'):
        instance_type: Literal["InMage"]
        recovery_point_id: Optional[str]
        recovery_point_type: Optional[Union[str, RecoveryPointType]]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_type: Optional[Union[str, RecoveryPointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageUnplannedFailoverInput(UnplannedFailoverProviderSpecificInput, discriminator='InMage'):
        instance_type: Literal["InMage"]
        recovery_point_id: Optional[str]
        recovery_point_type: Optional[Union[str, RecoveryPointType]]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_id: Optional[str] = ..., 
                recovery_point_type: Optional[Union[str, RecoveryPointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InMageV2RpRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATEST = "Latest"
        LATEST_APPLICATION_CONSISTENT = "LatestApplicationConsistent"
        LATEST_CRASH_CONSISTENT = "LatestCrashConsistent"
        LATEST_PROCESSED = "LatestProcessed"


    class azure.mgmt.recoveryservicessiterecovery.models.InMageVolumeExclusionOptions(_Model):
        only_exclude_if_single_volume: Optional[str]
        volume_label: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                only_exclude_if_single_volume: Optional[str] = ..., 
                volume_label: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InconsistentVmDetails(_Model):
        cloud_name: Optional[str]
        details: Optional[list[str]]
        error_ids: Optional[list[str]]
        vm_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_name: Optional[str] = ..., 
                details: Optional[list[str]] = ..., 
                error_ids: Optional[list[str]] = ..., 
                vm_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InitialReplicationDetails(_Model):
        initial_replication_progress_percentage: Optional[str]
        initial_replication_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initial_replication_progress_percentage: Optional[str] = ..., 
                initial_replication_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InlineWorkflowTaskDetails(GroupTaskDetails, discriminator='InlineWorkflowTaskDetails'):
        child_tasks: list[ASRTask]
        instance_type: Literal["InlineWorkflowTaskDetails"]
        workflow_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                child_tasks: Optional[list[ASRTask]] = ..., 
                workflow_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InnerHealthError(_Model):
        creation_time_utc: Optional[datetime]
        customer_resolvability: Optional[Union[str, HealthErrorCustomerResolvability]]
        entity_id: Optional[str]
        error_category: Optional[str]
        error_code: Optional[str]
        error_id: Optional[str]
        error_level: Optional[str]
        error_message: Optional[str]
        error_source: Optional[str]
        error_type: Optional[str]
        possible_causes: Optional[str]
        recommended_action: Optional[str]
        recovery_provider_error_message: Optional[str]
        summary_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time_utc: Optional[datetime] = ..., 
                customer_resolvability: Optional[Union[str, HealthErrorCustomerResolvability]] = ..., 
                entity_id: Optional[str] = ..., 
                error_category: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_id: Optional[str] = ..., 
                error_level: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                error_source: Optional[str] = ..., 
                error_type: Optional[str] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ..., 
                recovery_provider_error_message: Optional[str] = ..., 
                summary_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.InputEndpoint(_Model):
        endpoint_name: Optional[str]
        private_port: Optional[int]
        protocol: Optional[str]
        public_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_name: Optional[str] = ..., 
                private_port: Optional[int] = ..., 
                protocol: Optional[str] = ..., 
                public_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.Job(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[JobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[JobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobDetails(_Model):
        affected_object_details: Optional[dict[str, str]]
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobEntity(_Model):
        job_friendly_name: Optional[str]
        job_id: Optional[str]
        job_scenario_name: Optional[str]
        target_instance_type: Optional[str]
        target_object_id: Optional[str]
        target_object_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                job_friendly_name: Optional[str] = ..., 
                job_id: Optional[str] = ..., 
                job_scenario_name: Optional[str] = ..., 
                target_instance_type: Optional[str] = ..., 
                target_object_id: Optional[str] = ..., 
                target_object_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobErrorDetails(_Model):
        creation_time: Optional[datetime]
        error_level: Optional[str]
        provider_error_details: Optional[ProviderError]
        service_error_details: Optional[ServiceError]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                error_level: Optional[str] = ..., 
                provider_error_details: Optional[ProviderError] = ..., 
                service_error_details: Optional[ServiceError] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobProperties(_Model):
        activity_id: Optional[str]
        allowed_actions: Optional[list[str]]
        custom_details: Optional[JobDetails]
        end_time: Optional[datetime]
        errors: Optional[list[JobErrorDetails]]
        friendly_name: Optional[str]
        scenario_name: Optional[str]
        start_time: Optional[datetime]
        state: Optional[str]
        state_description: Optional[str]
        target_instance_type: Optional[str]
        target_object_id: Optional[str]
        target_object_name: Optional[str]
        tasks: Optional[list[ASRTask]]

        @overload
        def __init__(
                self, 
                *, 
                activity_id: Optional[str] = ..., 
                allowed_actions: Optional[list[str]] = ..., 
                custom_details: Optional[JobDetails] = ..., 
                end_time: Optional[datetime] = ..., 
                errors: Optional[list[JobErrorDetails]] = ..., 
                friendly_name: Optional[str] = ..., 
                scenario_name: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                state: Optional[str] = ..., 
                state_description: Optional[str] = ..., 
                target_instance_type: Optional[str] = ..., 
                target_object_id: Optional[str] = ..., 
                target_object_name: Optional[str] = ..., 
                tasks: Optional[list[ASRTask]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobQueryParameter(_Model):
        affected_object_types: Optional[str]
        end_time: Optional[str]
        fabric_id: Optional[str]
        job_name: Optional[str]
        job_output_type: Optional[Union[str, ExportJobOutputSerializationType]]
        job_status: Optional[str]
        start_time: Optional[str]
        timezone_offset: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_types: Optional[str] = ..., 
                end_time: Optional[str] = ..., 
                fabric_id: Optional[str] = ..., 
                job_name: Optional[str] = ..., 
                job_output_type: Optional[Union[str, ExportJobOutputSerializationType]] = ..., 
                job_status: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                timezone_offset: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobStatusEventDetails(EventSpecificDetails, discriminator='JobStatus'):
        affected_object_type: Optional[str]
        instance_type: Literal["JobStatus"]
        job_friendly_name: Optional[str]
        job_id: Optional[str]
        job_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_type: Optional[str] = ..., 
                job_friendly_name: Optional[str] = ..., 
                job_id: Optional[str] = ..., 
                job_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.JobTaskDetails(TaskTypeDetails, discriminator='JobTaskDetails'):
        instance_type: Literal["JobTaskDetails"]
        job_task: Optional[JobEntity]

        @overload
        def __init__(
                self, 
                *, 
                job_task: Optional[JobEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.KeyEncryptionKeyInfo(_Model):
        key_identifier: Optional[str]
        key_vault_resource_arm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_identifier: Optional[str] = ..., 
                key_vault_resource_arm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.LicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        NO_LICENSE_TYPE = "NoLicenseType"
        WINDOWS_SERVER = "WindowsServer"


    class azure.mgmt.recoveryservicessiterecovery.models.LinuxLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX_SERVER = "LinuxServer"
        NOT_SPECIFIED = "NotSpecified"
        NO_LICENSE_TYPE = "NoLicenseType"


    class azure.mgmt.recoveryservicessiterecovery.models.LogicalNetwork(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[LogicalNetworkProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[LogicalNetworkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.LogicalNetworkProperties(_Model):
        friendly_name: Optional[str]
        logical_network_definitions_status: Optional[str]
        logical_network_usage: Optional[str]
        network_virtualization_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                logical_network_definitions_status: Optional[str] = ..., 
                logical_network_usage: Optional[str] = ..., 
                network_virtualization_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ManagedRunCommandScriptInput(_Model):
        script_parameters: str
        script_url: str
        step_name: str

        @overload
        def __init__(
                self, 
                *, 
                script_parameters: str, 
                script_url: str, 
                step_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ManualActionTaskDetails(TaskTypeDetails, discriminator='ManualActionTaskDetails'):
        instance_type: Literal["ManualActionTaskDetails"]
        instructions: Optional[str]
        name: Optional[str]
        observation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                name: Optional[str] = ..., 
                observation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MarsAgentDetails(_Model):
        bios_id: Optional[str]
        fabric_object_id: Optional[str]
        fqdn: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.MasterTargetServer(_Model):
        agent_expiry_date: Optional[datetime]
        agent_version: Optional[str]
        agent_version_details: Optional[VersionDetails]
        data_stores: Optional[list[DataStore]]
        disk_count: Optional[int]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        ip_address: Optional[str]
        last_heartbeat: Optional[datetime]
        mars_agent_expiry_date: Optional[datetime]
        mars_agent_version: Optional[str]
        mars_agent_version_details: Optional[VersionDetails]
        name: Optional[str]
        os_type: Optional[str]
        os_version: Optional[str]
        retention_volumes: Optional[list[RetentionVolume]]
        validation_errors: Optional[list[HealthError]]
        version_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_expiry_date: Optional[datetime] = ..., 
                agent_version: Optional[str] = ..., 
                agent_version_details: Optional[VersionDetails] = ..., 
                data_stores: Optional[list[DataStore]] = ..., 
                disk_count: Optional[int] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                id: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                mars_agent_expiry_date: Optional[datetime] = ..., 
                mars_agent_version: Optional[str] = ..., 
                mars_agent_version_details: Optional[VersionDetails] = ..., 
                name: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                retention_volumes: Optional[list[RetentionVolume]] = ..., 
                validation_errors: Optional[list[HealthError]] = ..., 
                version_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrateInput(_Model):
        properties: MigrateInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: MigrateInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrateInputProperties(_Model):
        provider_specific_details: MigrateProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: MigrateProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrateProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationItem(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[MigrationItemProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[MigrationItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationItemOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE_MIGRATION = "DisableMigration"
        MIGRATE = "Migrate"
        PAUSE_REPLICATION = "PauseReplication"
        RESUME_REPLICATION = "ResumeReplication"
        START_RESYNC = "StartResync"
        TEST_MIGRATE = "TestMigrate"
        TEST_MIGRATE_CLEANUP = "TestMigrateCleanup"


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationItemProperties(_Model):
        allowed_operations: Optional[list[Union[str, MigrationItemOperation]]]
        critical_job_history: Optional[list[CriticalJobHistoryDetails]]
        current_job: Optional[CurrentJobDetails]
        event_correlation_id: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        last_migration_status: Optional[str]
        last_migration_time: Optional[datetime]
        last_test_migration_status: Optional[str]
        last_test_migration_time: Optional[datetime]
        machine_name: Optional[str]
        migration_state: Optional[Union[str, MigrationState]]
        migration_state_description: Optional[str]
        policy_friendly_name: Optional[str]
        policy_id: Optional[str]
        provider_specific_details: Optional[MigrationProviderSpecificSettings]
        recovery_services_provider_id: Optional[str]
        replication_status: Optional[str]
        test_migrate_state: Optional[Union[str, TestMigrationState]]
        test_migrate_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[MigrationProviderSpecificSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationProviderSpecificSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationRecoveryPoint(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[MigrationRecoveryPointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[MigrationRecoveryPointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationRecoveryPointProperties(_Model):
        recovery_point_time: Optional[datetime]
        recovery_point_type: Optional[Union[str, MigrationRecoveryPointType]]


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_CONSISTENT = "ApplicationConsistent"
        CRASH_CONSISTENT = "CrashConsistent"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.recoveryservicessiterecovery.models.MigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE_MIGRATION_FAILED = "DisableMigrationFailed"
        DISABLE_MIGRATION_IN_PROGRESS = "DisableMigrationInProgress"
        ENABLE_MIGRATION_FAILED = "EnableMigrationFailed"
        ENABLE_MIGRATION_IN_PROGRESS = "EnableMigrationInProgress"
        INITIAL_SEEDING_FAILED = "InitialSeedingFailed"
        INITIAL_SEEDING_IN_PROGRESS = "InitialSeedingInProgress"
        MIGRATION_COMPLETED_WITH_INFORMATION = "MigrationCompletedWithInformation"
        MIGRATION_FAILED = "MigrationFailed"
        MIGRATION_IN_PROGRESS = "MigrationInProgress"
        MIGRATION_PARTIALLY_SUCCEEDED = "MigrationPartiallySucceeded"
        MIGRATION_SUCCEEDED = "MigrationSucceeded"
        NONE = "None"
        PROTECTION_SUSPENDED = "ProtectionSuspended"
        REPLICATING = "Replicating"
        RESUME_INITIATED = "ResumeInitiated"
        RESUME_IN_PROGRESS = "ResumeInProgress"
        SUSPENDING_PROTECTION = "SuspendingProtection"


    class azure.mgmt.recoveryservicessiterecovery.models.MobilityAgentReinstallType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_TRIGGERED = "AutoTriggered"
        USER_TRIGGERED = "UserTriggered"


    class azure.mgmt.recoveryservicessiterecovery.models.MobilityAgentUpgradeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMIT = "Commit"
        COMPLETED = "Completed"
        NONE = "None"
        STARTED = "Started"


    class azure.mgmt.recoveryservicessiterecovery.models.MobilityServiceUpdate(_Model):
        os_type: Optional[str]
        reboot_status: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_type: Optional[str] = ..., 
                reboot_status: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.MultiVmGroupCreateOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_CREATED = "AutoCreated"
        USER_SPECIFIED = "UserSpecified"


    class azure.mgmt.recoveryservicessiterecovery.models.MultiVmSyncPointOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USE_MULTI_VM_SYNC_RECOVERY_POINT = "UseMultiVmSyncRecoveryPoint"
        USE_PER_VM_RECOVERY_POINT = "UsePerVmRecoveryPoint"


    class azure.mgmt.recoveryservicessiterecovery.models.Network(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[NetworkProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[NetworkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.NetworkMapping(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[NetworkMappingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[NetworkMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.NetworkMappingFabricSpecificSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.NetworkMappingProperties(_Model):
        fabric_specific_settings: Optional[NetworkMappingFabricSpecificSettings]
        primary_fabric_friendly_name: Optional[str]
        primary_network_friendly_name: Optional[str]
        primary_network_id: Optional[str]
        recovery_fabric_arm_id: Optional[str]
        recovery_fabric_friendly_name: Optional[str]
        recovery_network_friendly_name: Optional[str]
        recovery_network_id: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_specific_settings: Optional[NetworkMappingFabricSpecificSettings] = ..., 
                primary_fabric_friendly_name: Optional[str] = ..., 
                primary_network_friendly_name: Optional[str] = ..., 
                primary_network_id: Optional[str] = ..., 
                recovery_fabric_arm_id: Optional[str] = ..., 
                recovery_fabric_friendly_name: Optional[str] = ..., 
                recovery_network_friendly_name: Optional[str] = ..., 
                recovery_network_id: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.NetworkProperties(_Model):
        fabric_type: Optional[str]
        friendly_name: Optional[str]
        network_type: Optional[str]
        subnets: Optional[list[Subnet]]

        @overload
        def __init__(
                self, 
                *, 
                fabric_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                network_type: Optional[str] = ..., 
                subnets: Optional[list[Subnet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.NewProtectionProfile(ProtectionProfileCustomDetails, discriminator='New'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        multi_vm_sync_status: Union[str, SetMultiVmSyncStatus]
        policy_name: str
        recovery_point_history: Optional[int]
        resource_type: Literal["New"]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                multi_vm_sync_status: Union[str, SetMultiVmSyncStatus], 
                policy_name: str, 
                recovery_point_history: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.NewRecoveryVirtualNetwork(RecoveryVirtualNetworkCustomDetails, discriminator='New'):
        recovery_virtual_network_name: Optional[str]
        recovery_virtual_network_resource_group_name: Optional[str]
        resource_type: Literal["New"]

        @overload
        def __init__(
                self, 
                *, 
                recovery_virtual_network_name: Optional[str] = ..., 
                recovery_virtual_network_resource_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.OSDetails(_Model):
        o_s_major_version: Optional[str]
        o_s_minor_version: Optional[str]
        o_s_version: Optional[str]
        os_edition: Optional[str]
        os_type: Optional[str]
        product_type: Optional[str]
        user_selected_os_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                o_s_major_version: Optional[str] = ..., 
                o_s_minor_version: Optional[str] = ..., 
                o_s_version: Optional[str] = ..., 
                os_edition: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                product_type: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.OSDiskDetails(_Model):
        os_type: Optional[str]
        os_vhd_id: Optional[str]
        vhd_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_type: Optional[str] = ..., 
                os_vhd_id: Optional[str] = ..., 
                vhd_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.OSUpgradeSupportedVersions(_Model):
        supported_source_os_version: Optional[str]
        supported_target_os_versions: Optional[list[str]]


    class azure.mgmt.recoveryservicessiterecovery.models.OSVersionWrapper(_Model):
        service_pack: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_pack: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.OperationsDiscovery(_Model):
        display: Optional[Display]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[Display] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PauseReplicationInput(_Model):
        properties: PauseReplicationInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: PauseReplicationInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PauseReplicationInputProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PlannedFailoverInput(_Model):
        properties: Optional[PlannedFailoverInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlannedFailoverInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PlannedFailoverInputProperties(_Model):
        failover_direction: Optional[str]
        provider_specific_details: Optional[PlannedFailoverProviderSpecificFailoverInput]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Optional[str] = ..., 
                provider_specific_details: Optional[PlannedFailoverProviderSpecificFailoverInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PlannedFailoverProviderSpecificFailoverInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PlannedFailoverStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.recoveryservicessiterecovery.models.Policy(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PolicyProperties(_Model):
        friendly_name: Optional[str]
        provider_specific_details: Optional[PolicyProviderSpecificDetails]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                provider_specific_details: Optional[PolicyProviderSpecificDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PolicyProviderSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PolicyProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.PossibleOperationsDirections(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_TO_RECOVERY = "PrimaryToRecovery"
        RECOVERY_TO_PRIMARY = "RecoveryToPrimary"


    class azure.mgmt.recoveryservicessiterecovery.models.PresenceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_PRESENT = "NotPresent"
        PRESENT = "Present"
        UNKNOWN = "Unknown"


    class azure.mgmt.recoveryservicessiterecovery.models.ProcessServer(_Model):
        agent_expiry_date: Optional[datetime]
        agent_version: Optional[str]
        agent_version_details: Optional[VersionDetails]
        available_memory_in_bytes: Optional[int]
        available_space_in_bytes: Optional[int]
        cpu_load: Optional[str]
        cpu_load_status: Optional[str]
        friendly_name: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        host_id: Optional[str]
        id: Optional[str]
        ip_address: Optional[str]
        last_heartbeat: Optional[datetime]
        machine_count: Optional[str]
        mars_communication_status: Optional[str]
        mars_registration_status: Optional[str]
        memory_usage_status: Optional[str]
        mobility_service_updates: Optional[list[MobilityServiceUpdate]]
        os_type: Optional[str]
        os_version: Optional[str]
        ps_service_status: Optional[str]
        ps_stats_refresh_time: Optional[datetime]
        replication_pair_count: Optional[str]
        space_usage_status: Optional[str]
        ssl_cert_expiry_date: Optional[datetime]
        ssl_cert_expiry_remaining_days: Optional[int]
        system_load: Optional[str]
        system_load_status: Optional[str]
        throughput_in_bytes: Optional[int]
        throughput_in_m_bps: Optional[int]
        throughput_status: Optional[str]
        throughput_upload_pending_data_in_bytes: Optional[int]
        total_memory_in_bytes: Optional[int]
        total_space_in_bytes: Optional[int]
        version_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_expiry_date: Optional[datetime] = ..., 
                agent_version: Optional[str] = ..., 
                agent_version_details: Optional[VersionDetails] = ..., 
                available_memory_in_bytes: Optional[int] = ..., 
                available_space_in_bytes: Optional[int] = ..., 
                cpu_load: Optional[str] = ..., 
                cpu_load_status: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                host_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                machine_count: Optional[str] = ..., 
                memory_usage_status: Optional[str] = ..., 
                mobility_service_updates: Optional[list[MobilityServiceUpdate]] = ..., 
                os_type: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                ps_service_status: Optional[str] = ..., 
                replication_pair_count: Optional[str] = ..., 
                space_usage_status: Optional[str] = ..., 
                ssl_cert_expiry_date: Optional[datetime] = ..., 
                ssl_cert_expiry_remaining_days: Optional[int] = ..., 
                system_load: Optional[str] = ..., 
                system_load_status: Optional[str] = ..., 
                total_memory_in_bytes: Optional[int] = ..., 
                total_space_in_bytes: Optional[int] = ..., 
                version_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProcessServerDetails(_Model):
        available_memory_in_bytes: Optional[int]
        available_space_in_bytes: Optional[int]
        bios_id: Optional[str]
        disk_usage_status: Optional[Union[str, RcmComponentStatus]]
        fabric_object_id: Optional[str]
        fqdn: Optional[str]
        free_space_percentage: Optional[float]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        historic_health: Optional[Union[str, ProtectionHealth]]
        id: Optional[str]
        ip_addresses: Optional[list[str]]
        last_heartbeat_utc: Optional[datetime]
        memory_usage_percentage: Optional[float]
        memory_usage_status: Optional[Union[str, RcmComponentStatus]]
        name: Optional[str]
        processor_usage_percentage: Optional[float]
        processor_usage_status: Optional[Union[str, RcmComponentStatus]]
        protected_item_count: Optional[int]
        system_load: Optional[int]
        system_load_status: Optional[Union[str, RcmComponentStatus]]
        throughput_in_bytes: Optional[int]
        throughput_status: Optional[Union[str, RcmComponentStatus]]
        throughput_upload_pending_data_in_bytes: Optional[int]
        total_memory_in_bytes: Optional[int]
        total_space_in_bytes: Optional[int]
        used_memory_in_bytes: Optional[int]
        used_space_in_bytes: Optional[int]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectableItem(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectableItemProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ProtectableItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectableItemProperties(_Model):
        custom_details: Optional[ConfigurationSettings]
        friendly_name: Optional[str]
        protection_readiness_errors: Optional[list[str]]
        protection_status: Optional[str]
        recovery_services_provider_id: Optional[str]
        replication_protected_item_id: Optional[str]
        supported_replication_providers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                custom_details: Optional[ConfigurationSettings] = ..., 
                friendly_name: Optional[str] = ..., 
                protection_readiness_errors: Optional[list[str]] = ..., 
                protection_status: Optional[str] = ..., 
                recovery_services_provider_id: Optional[str] = ..., 
                replication_protected_item_id: Optional[str] = ..., 
                supported_replication_providers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionContainer(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectionContainerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ProtectionContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionContainerFabricSpecificDetails(_Model):
        instance_type: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionContainerMapping(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ProtectionContainerMappingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ProtectionContainerMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionContainerMappingProperties(_Model):
        health: Optional[str]
        health_error_details: Optional[list[HealthError]]
        policy_friendly_name: Optional[str]
        policy_id: Optional[str]
        provider_specific_details: Optional[ProtectionContainerMappingProviderSpecificDetails]
        source_fabric_friendly_name: Optional[str]
        source_protection_container_friendly_name: Optional[str]
        state: Optional[str]
        target_fabric_friendly_name: Optional[str]
        target_protection_container_friendly_name: Optional[str]
        target_protection_container_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                health: Optional[str] = ..., 
                health_error_details: Optional[list[HealthError]] = ..., 
                policy_friendly_name: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                provider_specific_details: Optional[ProtectionContainerMappingProviderSpecificDetails] = ..., 
                source_fabric_friendly_name: Optional[str] = ..., 
                source_protection_container_friendly_name: Optional[str] = ..., 
                state: Optional[str] = ..., 
                target_fabric_friendly_name: Optional[str] = ..., 
                target_protection_container_friendly_name: Optional[str] = ..., 
                target_protection_container_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionContainerMappingProviderSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionContainerProperties(_Model):
        fabric_friendly_name: Optional[str]
        fabric_specific_details: Optional[ProtectionContainerFabricSpecificDetails]
        fabric_type: Optional[str]
        friendly_name: Optional[str]
        pairing_status: Optional[str]
        protected_item_count: Optional[int]
        role: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_friendly_name: Optional[str] = ..., 
                fabric_specific_details: Optional[ProtectionContainerFabricSpecificDetails] = ..., 
                fabric_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                pairing_status: Optional[str] = ..., 
                protected_item_count: Optional[int] = ..., 
                role: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionHealth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        NONE = "None"
        NORMAL = "Normal"
        WARNING = "Warning"


    class azure.mgmt.recoveryservicessiterecovery.models.ProtectionProfileCustomDetails(_Model):
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProviderError(_Model):
        error_code: Optional[int]
        error_id: Optional[str]
        error_message: Optional[str]
        possible_causes: Optional[str]
        recommended_action: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[int] = ..., 
                error_id: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProviderSpecificRecoveryPointDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservicessiterecovery.models.PushInstallerDetails(_Model):
        bios_id: Optional[str]
        fabric_object_id: Optional[str]
        fqdn: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.RcmComponentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HEALTHY = "Healthy"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.recoveryservicessiterecovery.models.RcmProxyDetails(_Model):
        bios_id: Optional[str]
        client_authentication_type: Optional[str]
        fabric_object_id: Optional[str]
        fqdn: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryAvailabilitySetCustomDetails(_Model):
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryNetworkConfigAutoSyncPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlan(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[RecoveryPlanProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[RecoveryPlanProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanA2ADetails(RecoveryPlanProviderSpecificDetails, discriminator='A2A'):
        instance_type: Literal["A2A"]
        primary_extended_location: Optional[ExtendedLocation]
        primary_zone: Optional[str]
        recovery_extended_location: Optional[ExtendedLocation]
        recovery_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_extended_location: Optional[ExtendedLocation] = ..., 
                primary_zone: Optional[str] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanA2AFailoverInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='A2A'):
        cloud_service_creation_option: Optional[str]
        instance_type: Literal["A2A"]
        multi_vm_sync_point_option: Optional[Union[str, MultiVmSyncPointOption]]
        recovery_point_type: Union[str, A2ARpRecoveryPointType]

        @overload
        def __init__(
                self, 
                *, 
                cloud_service_creation_option: Optional[str] = ..., 
                multi_vm_sync_point_option: Optional[Union[str, MultiVmSyncPointOption]] = ..., 
                recovery_point_type: Union[str, A2ARpRecoveryPointType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanA2AInput(RecoveryPlanProviderSpecificInput, discriminator='A2A'):
        instance_type: Literal["A2A"]
        primary_extended_location: Optional[ExtendedLocation]
        primary_zone: Optional[str]
        recovery_extended_location: Optional[ExtendedLocation]
        recovery_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_extended_location: Optional[ExtendedLocation] = ..., 
                primary_zone: Optional[str] = ..., 
                recovery_extended_location: Optional[ExtendedLocation] = ..., 
                recovery_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanAction(_Model):
        action_name: str
        custom_details: RecoveryPlanActionDetails
        failover_directions: list[Union[str, PossibleOperationsDirections]]
        failover_types: list[Union[str, ReplicationProtectedItemOperation]]

        @overload
        def __init__(
                self, 
                *, 
                action_name: str, 
                custom_details: RecoveryPlanActionDetails, 
                failover_directions: list[Union[str, PossibleOperationsDirections]], 
                failover_types: list[Union[str, ReplicationProtectedItemOperation]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanActionDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanActionLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        RECOVERY = "Recovery"


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanAutomationRunbookActionDetails(RecoveryPlanActionDetails, discriminator='AutomationRunbookActionDetails'):
        fabric_location: Union[str, RecoveryPlanActionLocation]
        instance_type: Literal["AutomationRunbookActionDetails"]
        runbook_id: Optional[str]
        timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_location: Union[str, RecoveryPlanActionLocation], 
                runbook_id: Optional[str] = ..., 
                timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanGroup(_Model):
        end_group_actions: Optional[list[RecoveryPlanAction]]
        group_type: Union[str, RecoveryPlanGroupType]
        replication_protected_items: Optional[list[RecoveryPlanProtectedItem]]
        start_group_actions: Optional[list[RecoveryPlanAction]]

        @overload
        def __init__(
                self, 
                *, 
                end_group_actions: Optional[list[RecoveryPlanAction]] = ..., 
                group_type: Union[str, RecoveryPlanGroupType], 
                replication_protected_items: Optional[list[RecoveryPlanProtectedItem]] = ..., 
                start_group_actions: Optional[list[RecoveryPlanAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanGroupTaskDetails(GroupTaskDetails, discriminator='RecoveryPlanGroupTaskDetails'):
        child_tasks: list[ASRTask]
        group_id: Optional[str]
        instance_type: Literal["RecoveryPlanGroupTaskDetails"]
        name: Optional[str]
        rp_group_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                child_tasks: Optional[list[ASRTask]] = ..., 
                group_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                rp_group_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanGroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOT = "Boot"
        FAILOVER = "Failover"
        SHUTDOWN = "Shutdown"


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanHyperVReplicaAzureFailbackInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='HyperVReplicaAzureFailback'):
        data_sync_option: Union[str, DataSyncStatus]
        instance_type: Literal["HyperVReplicaAzureFailback"]
        recovery_vm_creation_option: Union[str, AlternateLocationRecoveryOption]

        @overload
        def __init__(
                self, 
                *, 
                data_sync_option: Union[str, DataSyncStatus], 
                recovery_vm_creation_option: Union[str, AlternateLocationRecoveryOption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanHyperVReplicaAzureFailoverInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='HyperVReplicaAzure'):
        instance_type: Literal["HyperVReplicaAzure"]
        primary_kek_certificate_pfx: Optional[str]
        recovery_point_type: Optional[Union[str, HyperVReplicaAzureRpRecoveryPointType]]
        secondary_kek_certificate_pfx: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_kek_certificate_pfx: Optional[str] = ..., 
                recovery_point_type: Optional[Union[str, HyperVReplicaAzureRpRecoveryPointType]] = ..., 
                secondary_kek_certificate_pfx: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanInMageAzureV2FailoverInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='InMageAzureV2'):
        instance_type: Literal["InMageAzureV2"]
        recovery_point_type: Union[str, InMageV2RpRecoveryPointType]
        use_multi_vm_sync_point: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_type: Union[str, InMageV2RpRecoveryPointType], 
                use_multi_vm_sync_point: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanInMageFailoverInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='InMage'):
        instance_type: Literal["InMage"]
        recovery_point_type: Union[str, RpInMageRecoveryPointType]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_type: Union[str, RpInMageRecoveryPointType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanInMageRcmFailbackFailoverInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='InMageRcmFailback'):
        instance_type: Literal["InMageRcmFailback"]
        recovery_point_type: Union[str, InMageRcmFailbackRecoveryPointType]
        use_multi_vm_sync_point: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_type: Union[str, InMageRcmFailbackRecoveryPointType], 
                use_multi_vm_sync_point: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanInMageRcmFailoverInput(RecoveryPlanProviderSpecificFailoverInput, discriminator='InMageRcm'):
        instance_type: Literal["InMageRcm"]
        recovery_point_type: Union[str, RecoveryPlanPointType]
        use_multi_vm_sync_point: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recovery_point_type: Union[str, RecoveryPlanPointType], 
                use_multi_vm_sync_point: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanManualActionDetails(RecoveryPlanActionDetails, discriminator='ManualActionDetails'):
        description: Optional[str]
        instance_type: Literal["ManualActionDetails"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanPlannedFailoverInput(_Model):
        properties: RecoveryPlanPlannedFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: RecoveryPlanPlannedFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanPlannedFailoverInputProperties(_Model):
        failover_direction: Union[str, PossibleOperationsDirections]
        provider_specific_details: Optional[list[RecoveryPlanProviderSpecificFailoverInput]]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Union[str, PossibleOperationsDirections], 
                provider_specific_details: Optional[list[RecoveryPlanProviderSpecificFailoverInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATEST = "Latest"
        LATEST_APPLICATION_CONSISTENT = "LatestApplicationConsistent"
        LATEST_CRASH_CONSISTENT = "LatestCrashConsistent"
        LATEST_PROCESSED = "LatestProcessed"


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanProperties(_Model):
        allowed_operations: Optional[list[str]]
        current_scenario: Optional[CurrentScenarioDetails]
        current_scenario_status: Optional[str]
        current_scenario_status_description: Optional[str]
        failover_deployment_model: Optional[str]
        friendly_name: Optional[str]
        groups: Optional[list[RecoveryPlanGroup]]
        last_planned_failover_time: Optional[datetime]
        last_test_failover_time: Optional[datetime]
        last_unplanned_failover_time: Optional[datetime]
        primary_fabric_friendly_name: Optional[str]
        primary_fabric_id: Optional[str]
        provider_specific_details: Optional[list[RecoveryPlanProviderSpecificDetails]]
        recovery_fabric_friendly_name: Optional[str]
        recovery_fabric_id: Optional[str]
        replication_providers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_operations: Optional[list[str]] = ..., 
                current_scenario: Optional[CurrentScenarioDetails] = ..., 
                current_scenario_status: Optional[str] = ..., 
                current_scenario_status_description: Optional[str] = ..., 
                failover_deployment_model: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                groups: Optional[list[RecoveryPlanGroup]] = ..., 
                last_planned_failover_time: Optional[datetime] = ..., 
                last_test_failover_time: Optional[datetime] = ..., 
                last_unplanned_failover_time: Optional[datetime] = ..., 
                primary_fabric_friendly_name: Optional[str] = ..., 
                primary_fabric_id: Optional[str] = ..., 
                provider_specific_details: Optional[list[RecoveryPlanProviderSpecificDetails]] = ..., 
                recovery_fabric_friendly_name: Optional[str] = ..., 
                recovery_fabric_id: Optional[str] = ..., 
                replication_providers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanProtectedItem(_Model):
        id: Optional[str]
        virtual_machine_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanProviderSpecificDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanProviderSpecificFailoverInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanScriptActionDetails(RecoveryPlanActionDetails, discriminator='ScriptActionDetails'):
        fabric_location: Union[str, RecoveryPlanActionLocation]
        instance_type: Literal["ScriptActionDetails"]
        path: str
        timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_location: Union[str, RecoveryPlanActionLocation], 
                path: str, 
                timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanShutdownGroupTaskDetails(RecoveryPlanGroupTaskDetails, discriminator='RecoveryPlanShutdownGroupTaskDetails'):
        child_tasks: list[ASRTask]
        group_id: str
        instance_type: Literal["RecoveryPlanShutdownGroupTaskDetails"]
        name: str
        rp_group_type: str

        @overload
        def __init__(
                self, 
                *, 
                child_tasks: Optional[list[ASRTask]] = ..., 
                group_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                rp_group_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanTestFailoverCleanupInput(_Model):
        properties: RecoveryPlanTestFailoverCleanupInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: RecoveryPlanTestFailoverCleanupInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanTestFailoverCleanupInputProperties(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanTestFailoverInput(_Model):
        properties: RecoveryPlanTestFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: RecoveryPlanTestFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanTestFailoverInputProperties(_Model):
        failover_direction: Union[str, PossibleOperationsDirections]
        network_id: Optional[str]
        network_type: str
        provider_specific_details: Optional[list[RecoveryPlanProviderSpecificFailoverInput]]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Union[str, PossibleOperationsDirections], 
                network_id: Optional[str] = ..., 
                network_type: str, 
                provider_specific_details: Optional[list[RecoveryPlanProviderSpecificFailoverInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanUnplannedFailoverInput(_Model):
        properties: RecoveryPlanUnplannedFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: RecoveryPlanUnplannedFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPlanUnplannedFailoverInputProperties(_Model):
        failover_direction: Union[str, PossibleOperationsDirections]
        provider_specific_details: Optional[list[RecoveryPlanProviderSpecificFailoverInput]]
        source_site_operations: Union[str, SourceSiteOperations]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Union[str, PossibleOperationsDirections], 
                provider_specific_details: Optional[list[RecoveryPlanProviderSpecificFailoverInput]] = ..., 
                source_site_operations: Union[str, SourceSiteOperations]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPoint(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[RecoveryPointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[RecoveryPointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPointProperties(_Model):
        provider_specific_details: Optional[ProviderSpecificRecoveryPointDetails]
        recovery_point_time: Optional[datetime]
        recovery_point_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[ProviderSpecificRecoveryPointDetails] = ..., 
                recovery_point_time: Optional[datetime] = ..., 
                recovery_point_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPointSyncType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_VM_SYNC_RECOVERY_POINT = "MultiVmSyncRecoveryPoint"
        PER_VM_RECOVERY_POINT = "PerVmRecoveryPoint"


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        LATEST_TAG = "LatestTag"
        LATEST_TIME = "LatestTime"


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryProximityPlacementGroupCustomDetails(_Model):
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryResourceGroupCustomDetails(_Model):
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryServicesProvider(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[RecoveryServicesProviderProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[RecoveryServicesProviderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryServicesProviderProperties(_Model):
        allowed_scenarios: Optional[list[str]]
        authentication_identity_details: Optional[IdentityProviderDetails]
        bios_id: Optional[str]
        connection_status: Optional[str]
        data_plane_authentication_identity_details: Optional[IdentityProviderDetails]
        dra_identifier: Optional[str]
        fabric_friendly_name: Optional[str]
        fabric_type: Optional[str]
        friendly_name: Optional[str]
        health_error_details: Optional[list[HealthError]]
        last_heart_beat: Optional[datetime]
        machine_id: Optional[str]
        machine_name: Optional[str]
        protected_item_count: Optional[int]
        provider_version: Optional[str]
        provider_version_details: Optional[VersionDetails]
        provider_version_expiry_date: Optional[datetime]
        provider_version_state: Optional[str]
        resource_access_identity_details: Optional[IdentityProviderDetails]
        server_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_scenarios: Optional[list[str]] = ..., 
                authentication_identity_details: Optional[IdentityProviderDetails] = ..., 
                bios_id: Optional[str] = ..., 
                connection_status: Optional[str] = ..., 
                data_plane_authentication_identity_details: Optional[IdentityProviderDetails] = ..., 
                dra_identifier: Optional[str] = ..., 
                fabric_friendly_name: Optional[str] = ..., 
                fabric_type: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_error_details: Optional[list[HealthError]] = ..., 
                last_heart_beat: Optional[datetime] = ..., 
                machine_id: Optional[str] = ..., 
                machine_name: Optional[str] = ..., 
                protected_item_count: Optional[int] = ..., 
                provider_version: Optional[str] = ..., 
                provider_version_details: Optional[VersionDetails] = ..., 
                provider_version_expiry_date: Optional[datetime] = ..., 
                provider_version_state: Optional[str] = ..., 
                resource_access_identity_details: Optional[IdentityProviderDetails] = ..., 
                server_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RecoveryVirtualNetworkCustomDetails(_Model):
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RegisteredClusterNodes(_Model):
        bios_id: Optional[str]
        cluster_node_fqdn: Optional[str]
        is_shared_disk_virtual_node: Optional[bool]
        machine_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bios_id: Optional[str] = ..., 
                cluster_node_fqdn: Optional[str] = ..., 
                is_shared_disk_virtual_node: Optional[bool] = ..., 
                machine_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReinstallMobilityServiceRequest(_Model):
        properties: Optional[ReinstallMobilityServiceRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReinstallMobilityServiceRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReinstallMobilityServiceRequestProperties(_Model):
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RemoveDisksInput(_Model):
        properties: Optional[RemoveDisksInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RemoveDisksInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RemoveDisksInputProperties(_Model):
        provider_specific_details: Optional[RemoveDisksProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[RemoveDisksProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RemoveDisksProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RemoveProtectionContainerMappingInput(_Model):
        properties: Optional[RemoveProtectionContainerMappingInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RemoveProtectionContainerMappingInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RemoveProtectionContainerMappingInputProperties(_Model):
        provider_specific_input: Optional[ReplicationProviderContainerUnmappingInput]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_input: Optional[ReplicationProviderContainerUnmappingInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RenewCertificateInput(_Model):
        properties: Optional[RenewCertificateInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RenewCertificateInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RenewCertificateInputProperties(_Model):
        renew_certificate_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                renew_certificate_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationAgentDetails(_Model):
        bios_id: Optional[str]
        fabric_object_id: Optional[str]
        fqdn: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        last_heartbeat_utc: Optional[datetime]
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationAppliance(_Model):
        properties: Optional[ReplicationApplianceProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReplicationApplianceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationApplianceProperties(_Model):
        provider_specific_details: Optional[ApplianceSpecificDetails]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[ApplianceSpecificDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationClusterProviderSpecificSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationEligibilityResults(ProxyResource):
        id: str
        name: str
        properties: Optional[ReplicationEligibilityResultsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReplicationEligibilityResultsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationEligibilityResultsCollection(_Model):
        value: Optional[list[ReplicationEligibilityResults]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[ReplicationEligibilityResults]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationEligibilityResultsErrorInfo(_Model):
        code: Optional[str]
        message: Optional[str]
        possible_causes: Optional[str]
        recommended_action: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationEligibilityResultsProperties(_Model):
        client_request_id: Optional[str]
        errors: Optional[list[ReplicationEligibilityResultsErrorInfo]]

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[ReplicationEligibilityResultsErrorInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationGroupDetails(ConfigurationSettings, discriminator='ReplicationGroupDetails'):
        instance_type: Literal["ReplicationGroupDetails"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectedItem(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ReplicationProtectedItemProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReplicationProtectedItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectedItemOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL_FAILOVER = "CancelFailover"
        CHANGE_PIT = "ChangePit"
        COMMIT = "Commit"
        COMPLETE_MIGRATION = "CompleteMigration"
        DISABLE_PROTECTION = "DisableProtection"
        FAILBACK = "Failback"
        FINALIZE_FAILBACK = "FinalizeFailback"
        PLANNED_FAILOVER = "PlannedFailover"
        REPAIR_REPLICATION = "RepairReplication"
        REVERSE_REPLICATE = "ReverseReplicate"
        SWITCH_PROTECTION = "SwitchProtection"
        TEST_FAILOVER = "TestFailover"
        TEST_FAILOVER_CLEANUP = "TestFailoverCleanup"
        UNPLANNED_FAILOVER = "UnplannedFailover"


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectedItemProperties(_Model):
        active_location: Optional[str]
        allowed_operations: Optional[list[str]]
        current_scenario: Optional[CurrentScenarioDetails]
        event_correlation_id: Optional[str]
        failover_health: Optional[str]
        failover_recovery_point_id: Optional[str]
        friendly_name: Optional[str]
        health_errors: Optional[list[HealthError]]
        last_successful_failover_time: Optional[datetime]
        last_successful_test_failover_time: Optional[datetime]
        policy_friendly_name: Optional[str]
        policy_id: Optional[str]
        primary_fabric_friendly_name: Optional[str]
        primary_fabric_provider: Optional[str]
        primary_protection_container_friendly_name: Optional[str]
        protectable_item_id: Optional[str]
        protected_item_type: Optional[str]
        protection_state: Optional[str]
        protection_state_description: Optional[str]
        provider_specific_details: Optional[ReplicationProviderSpecificSettings]
        recovery_container_id: Optional[str]
        recovery_fabric_friendly_name: Optional[str]
        recovery_fabric_id: Optional[str]
        recovery_protection_container_friendly_name: Optional[str]
        recovery_services_provider_id: Optional[str]
        replication_health: Optional[str]
        switch_provider_state: Optional[str]
        switch_provider_state_description: Optional[str]
        test_failover_state: Optional[str]
        test_failover_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                allowed_operations: Optional[list[str]] = ..., 
                current_scenario: Optional[CurrentScenarioDetails] = ..., 
                event_correlation_id: Optional[str] = ..., 
                failover_health: Optional[str] = ..., 
                failover_recovery_point_id: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                last_successful_failover_time: Optional[datetime] = ..., 
                last_successful_test_failover_time: Optional[datetime] = ..., 
                policy_friendly_name: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                primary_fabric_friendly_name: Optional[str] = ..., 
                primary_fabric_provider: Optional[str] = ..., 
                primary_protection_container_friendly_name: Optional[str] = ..., 
                protectable_item_id: Optional[str] = ..., 
                protected_item_type: Optional[str] = ..., 
                protection_state: Optional[str] = ..., 
                protection_state_description: Optional[str] = ..., 
                provider_specific_details: Optional[ReplicationProviderSpecificSettings] = ..., 
                recovery_container_id: Optional[str] = ..., 
                recovery_fabric_friendly_name: Optional[str] = ..., 
                recovery_fabric_id: Optional[str] = ..., 
                recovery_protection_container_friendly_name: Optional[str] = ..., 
                recovery_services_provider_id: Optional[str] = ..., 
                replication_health: Optional[str] = ..., 
                switch_provider_state: Optional[str] = ..., 
                switch_provider_state_description: Optional[str] = ..., 
                test_failover_state: Optional[str] = ..., 
                test_failover_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectionCluster(ProxyResource):
        id: str
        name: str
        properties: Optional[ReplicationProtectionClusterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReplicationProtectionClusterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectionClusterProperties(_Model):
        active_location: Optional[str]
        agent_cluster_id: Optional[str]
        allowed_operations: Optional[list[str]]
        are_all_cluster_nodes_registered: Optional[bool]
        cluster_fqdn: Optional[str]
        cluster_node_fqdns: Optional[list[str]]
        cluster_protected_item_ids: Optional[list[str]]
        cluster_registered_nodes: Optional[list[RegisteredClusterNodes]]
        current_scenario: Optional[CurrentScenarioDetails]
        health_errors: Optional[list[HealthError]]
        last_successful_failover_time: Optional[datetime]
        last_successful_test_failover_time: Optional[datetime]
        policy_friendly_name: Optional[str]
        policy_id: Optional[str]
        primary_fabric_friendly_name: Optional[str]
        primary_fabric_provider: Optional[str]
        primary_protection_container_friendly_name: Optional[str]
        protection_cluster_type: Optional[str]
        protection_state: Optional[str]
        protection_state_description: Optional[str]
        provider_specific_details: Optional[ReplicationClusterProviderSpecificSettings]
        provisioning_state: Optional[str]
        recovery_container_id: Optional[str]
        recovery_fabric_friendly_name: Optional[str]
        recovery_fabric_id: Optional[str]
        recovery_protection_container_friendly_name: Optional[str]
        replication_health: Optional[str]
        shared_disk_properties: Optional[SharedDiskReplicationItemProperties]
        test_failover_state: Optional[str]
        test_failover_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                agent_cluster_id: Optional[str] = ..., 
                allowed_operations: Optional[list[str]] = ..., 
                are_all_cluster_nodes_registered: Optional[bool] = ..., 
                cluster_fqdn: Optional[str] = ..., 
                cluster_node_fqdns: Optional[list[str]] = ..., 
                cluster_protected_item_ids: Optional[list[str]] = ..., 
                cluster_registered_nodes: Optional[list[RegisteredClusterNodes]] = ..., 
                current_scenario: Optional[CurrentScenarioDetails] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                last_successful_failover_time: Optional[datetime] = ..., 
                last_successful_test_failover_time: Optional[datetime] = ..., 
                policy_friendly_name: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                primary_fabric_friendly_name: Optional[str] = ..., 
                primary_fabric_provider: Optional[str] = ..., 
                primary_protection_container_friendly_name: Optional[str] = ..., 
                protection_cluster_type: Optional[str] = ..., 
                protection_state: Optional[str] = ..., 
                protection_state_description: Optional[str] = ..., 
                provider_specific_details: Optional[ReplicationClusterProviderSpecificSettings] = ..., 
                recovery_container_id: Optional[str] = ..., 
                recovery_fabric_friendly_name: Optional[str] = ..., 
                recovery_fabric_id: Optional[str] = ..., 
                recovery_protection_container_friendly_name: Optional[str] = ..., 
                replication_health: Optional[str] = ..., 
                shared_disk_properties: Optional[SharedDiskReplicationItemProperties] = ..., 
                test_failover_state: Optional[str] = ..., 
                test_failover_state_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectionIntent(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ReplicationProtectionIntentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReplicationProtectionIntentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectionIntentProperties(_Model):
        creation_time_utc: Optional[str]
        friendly_name: Optional[str]
        is_active: Optional[bool]
        job_id: Optional[str]
        job_state: Optional[str]
        provider_specific_details: Optional[ReplicationProtectionIntentProviderSpecificSettings]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                provider_specific_details: Optional[ReplicationProtectionIntentProviderSpecificSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProtectionIntentProviderSpecificSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProviderContainerUnmappingInput(_Model):
        instance_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                instance_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProviderSpecificContainerCreationInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProviderSpecificContainerMappingInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProviderSpecificSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReplicationProviderSpecificUpdateContainerMappingInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReprotectAgentDetails(_Model):
        accessible_datastores: Optional[list[str]]
        bios_id: Optional[str]
        fabric_object_id: Optional[str]
        fqdn: Optional[str]
        health: Optional[Union[str, ProtectionHealth]]
        health_errors: Optional[list[HealthError]]
        id: Optional[str]
        last_discovery_in_utc: Optional[datetime]
        last_heartbeat_utc: Optional[datetime]
        name: Optional[str]
        protected_item_count: Optional[int]
        vcenter_id: Optional[str]
        version: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ResolveHealthError(_Model):
        health_error_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                health_error_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResolveHealthInput(_Model):
        properties: Optional[ResolveHealthInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResolveHealthInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResolveHealthInputProperties(_Model):
        health_errors: Optional[list[ResolveHealthError]]

        @overload
        def __init__(
                self, 
                *, 
                health_errors: Optional[list[ResolveHealthError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.recoveryservicessiterecovery.models.ResourceHealthSummary(_Model):
        categorized_resource_counts: Optional[dict[str, int]]
        issues: Optional[list[HealthErrorSummary]]
        resource_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                categorized_resource_counts: Optional[dict[str, int]] = ..., 
                issues: Optional[list[HealthErrorSummary]] = ..., 
                resource_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResumeJobParams(_Model):
        properties: Optional[ResumeJobParamsProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResumeJobParamsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResumeJobParamsProperties(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResumeReplicationInput(_Model):
        properties: ResumeReplicationInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ResumeReplicationInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResumeReplicationInputProperties(_Model):
        provider_specific_details: ResumeReplicationProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: ResumeReplicationProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResumeReplicationProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResyncInput(_Model):
        properties: ResyncInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ResyncInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResyncInputProperties(_Model):
        provider_specific_details: ResyncProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: ResyncProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResyncProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ResyncState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        PREPARED_FOR_RESYNCHRONIZATION = "PreparedForResynchronization"
        STARTED_RESYNCHRONIZATION = "StartedResynchronization"


    class azure.mgmt.recoveryservicessiterecovery.models.RetentionVolume(_Model):
        capacity_in_bytes: Optional[int]
        free_space_in_bytes: Optional[int]
        threshold_percentage: Optional[int]
        volume_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity_in_bytes: Optional[int] = ..., 
                free_space_in_bytes: Optional[int] = ..., 
                threshold_percentage: Optional[int] = ..., 
                volume_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReverseReplicationInput(_Model):
        properties: Optional[ReverseReplicationInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReverseReplicationInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReverseReplicationInputProperties(_Model):
        failover_direction: Optional[str]
        provider_specific_details: Optional[ReverseReplicationProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Optional[str] = ..., 
                provider_specific_details: Optional[ReverseReplicationProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ReverseReplicationProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.RpInMageRecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        LATEST_TAG = "LatestTag"
        LATEST_TIME = "LatestTime"


    class azure.mgmt.recoveryservicessiterecovery.models.RunAsAccount(_Model):
        account_id: Optional[str]
        account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.ScriptActionTaskDetails(TaskTypeDetails, discriminator='ScriptActionTaskDetails'):
        instance_type: Literal["ScriptActionTaskDetails"]
        is_primary_side_script: Optional[bool]
        name: Optional[str]
        output: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_primary_side_script: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                output: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SecurityConfiguration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservicessiterecovery.models.SecurityProfileProperties(_Model):
        target_vm_confidential_encryption: Optional[Union[str, SecurityConfiguration]]
        target_vm_monitoring: Optional[Union[str, SecurityConfiguration]]
        target_vm_secure_boot: Optional[Union[str, SecurityConfiguration]]
        target_vm_security_type: Optional[Union[str, SecurityType]]
        target_vm_tpm: Optional[Union[str, SecurityConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                target_vm_confidential_encryption: Optional[Union[str, SecurityConfiguration]] = ..., 
                target_vm_monitoring: Optional[Union[str, SecurityConfiguration]] = ..., 
                target_vm_secure_boot: Optional[Union[str, SecurityConfiguration]] = ..., 
                target_vm_security_type: Optional[Union[str, SecurityType]] = ..., 
                target_vm_tpm: Optional[Union[str, SecurityConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SecurityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        NONE = "None"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.recoveryservicessiterecovery.models.ServiceError(_Model):
        activity_id: Optional[str]
        code: Optional[str]
        message: Optional[str]
        possible_causes: Optional[str]
        recommended_action: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_id: Optional[str] = ..., 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                possible_causes: Optional[str] = ..., 
                recommended_action: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SetMultiVmSyncStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.recoveryservicessiterecovery.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        NONE = "NONE"
        WARNING = "Warning"


    class azure.mgmt.recoveryservicessiterecovery.models.SharedDiskReplicationItemProperties(_Model):
        active_location: Optional[str]
        allowed_operations: Optional[list[str]]
        current_scenario: Optional[CurrentScenarioDetails]
        health_errors: Optional[list[HealthError]]
        protection_state: Optional[str]
        replication_health: Optional[str]
        shared_disk_provider_specific_details: Optional[SharedDiskReplicationProviderSpecificSettings]
        test_failover_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                allowed_operations: Optional[list[str]] = ..., 
                current_scenario: Optional[CurrentScenarioDetails] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                protection_state: Optional[str] = ..., 
                replication_health: Optional[str] = ..., 
                shared_disk_provider_specific_details: Optional[SharedDiskReplicationProviderSpecificSettings] = ..., 
                test_failover_state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SharedDiskReplicationProviderSpecificSettings(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SourceSiteOperations(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REQUIRED = "NotRequired"
        REQUIRED = "Required"


    class azure.mgmt.recoveryservicessiterecovery.models.SqlServerLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AHUB = "AHUB"
        NOT_SPECIFIED = "NotSpecified"
        NO_LICENSE_TYPE = "NoLicenseType"
        PAYG = "PAYG"


    class azure.mgmt.recoveryservicessiterecovery.models.StorageAccountCustomDetails(_Model):
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.StorageClassification(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[StorageClassificationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[StorageClassificationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.StorageClassificationMapping(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[StorageClassificationMappingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[StorageClassificationMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.StorageClassificationMappingInput(_Model):
        properties: Optional[StorageMappingInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageMappingInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.StorageClassificationMappingProperties(_Model):
        target_storage_classification_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_storage_classification_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.StorageClassificationProperties(_Model):
        friendly_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.StorageMappingInputProperties(_Model):
        target_storage_classification_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_storage_classification_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.Subnet(_Model):
        address_list: Optional[list[str]]
        friendly_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_list: Optional[list[str]] = ..., 
                friendly_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SupportedOSDetails(_Model):
        os_name: Optional[str]
        os_type: Optional[str]
        os_versions: Optional[list[OSVersionWrapper]]

        @overload
        def __init__(
                self, 
                *, 
                os_name: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                os_versions: Optional[list[OSVersionWrapper]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SupportedOSProperties(_Model):
        supported_os_list: Optional[list[SupportedOSProperty]]

        @overload
        def __init__(
                self, 
                *, 
                supported_os_list: Optional[list[SupportedOSProperty]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SupportedOSProperty(_Model):
        instance_type: Optional[str]
        supported_os: Optional[list[SupportedOSDetails]]

        @overload
        def __init__(
                self, 
                *, 
                instance_type: Optional[str] = ..., 
                supported_os: Optional[list[SupportedOSDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SupportedOperatingSystems(Resource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SupportedOSProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[SupportedOSProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchClusterProtectionInput(_Model):
        properties: Optional[SwitchClusterProtectionInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SwitchClusterProtectionInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchClusterProtectionInputProperties(_Model):
        provider_specific_details: Optional[SwitchClusterProtectionProviderSpecificInput]
        replication_protection_cluster_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[SwitchClusterProtectionProviderSpecificInput] = ..., 
                replication_protection_cluster_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchClusterProtectionProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProtectionInput(_Model):
        properties: Optional[SwitchProtectionInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SwitchProtectionInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProtectionInputProperties(_Model):
        provider_specific_details: Optional[SwitchProtectionProviderSpecificInput]
        replication_protected_item_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[SwitchProtectionProviderSpecificInput] = ..., 
                replication_protected_item_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProtectionJobDetails(JobDetails, discriminator='SwitchProtectionJobDetails'):
        affected_object_details: dict[str, str]
        instance_type: Literal["SwitchProtectionJobDetails"]
        new_replication_protected_item_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                new_replication_protected_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProtectionProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProviderInput(_Model):
        properties: Optional[SwitchProviderInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SwitchProviderInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProviderInputProperties(_Model):
        provider_specific_details: Optional[SwitchProviderSpecificInput]
        target_instance_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: Optional[SwitchProviderSpecificInput] = ..., 
                target_instance_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SwitchProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.SystemData(_Model):
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


    class azure.mgmt.recoveryservicessiterecovery.models.TargetComputeSize(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[TargetComputeSizeProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[TargetComputeSizeProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TargetComputeSizeProperties(_Model):
        cpu_cores_count: Optional[int]
        errors: Optional[list[ComputeSizeErrorDetails]]
        friendly_name: Optional[str]
        high_iops_supported: Optional[str]
        hyper_v_generations: Optional[list[str]]
        max_data_disk_count: Optional[int]
        max_nics_count: Optional[int]
        memory_in_gb: Optional[float]
        name: Optional[str]
        v_cpus_available: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu_cores_count: Optional[int] = ..., 
                errors: Optional[list[ComputeSizeErrorDetails]] = ..., 
                friendly_name: Optional[str] = ..., 
                high_iops_supported: Optional[str] = ..., 
                hyper_v_generations: Optional[list[str]] = ..., 
                max_data_disk_count: Optional[int] = ..., 
                max_nics_count: Optional[int] = ..., 
                memory_in_gb: Optional[float] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TaskTypeDetails(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestFailoverCleanupInput(_Model):
        properties: TestFailoverCleanupInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: TestFailoverCleanupInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestFailoverCleanupInputProperties(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestFailoverInput(_Model):
        properties: TestFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: TestFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestFailoverInputProperties(_Model):
        failover_direction: Optional[str]
        network_id: Optional[str]
        network_type: Optional[str]
        provider_specific_details: Optional[TestFailoverProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Optional[str] = ..., 
                network_id: Optional[str] = ..., 
                network_type: Optional[str] = ..., 
                provider_specific_details: Optional[TestFailoverProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestFailoverJobDetails(JobDetails, discriminator='TestFailoverJobDetails'):
        affected_object_details: dict[str, str]
        comments: Optional[str]
        instance_type: Literal["TestFailoverJobDetails"]
        network_friendly_name: Optional[str]
        network_name: Optional[str]
        network_type: Optional[str]
        protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]]
        test_failover_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_object_details: Optional[dict[str, str]] = ..., 
                comments: Optional[str] = ..., 
                network_friendly_name: Optional[str] = ..., 
                network_name: Optional[str] = ..., 
                network_type: Optional[str] = ..., 
                protected_item_details: Optional[list[FailoverReplicationProtectedItemDetails]] = ..., 
                test_failover_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestFailoverProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestMigrateCleanupInput(_Model):
        properties: TestMigrateCleanupInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: TestMigrateCleanupInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestMigrateCleanupInputProperties(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestMigrateInput(_Model):
        properties: TestMigrateInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: TestMigrateInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestMigrateInputProperties(_Model):
        provider_specific_details: TestMigrateProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: TestMigrateProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestMigrateProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.TestMigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TEST_MIGRATION_CLEANUP_IN_PROGRESS = "TestMigrationCleanupInProgress"
        TEST_MIGRATION_COMPLETED_WITH_INFORMATION = "TestMigrationCompletedWithInformation"
        TEST_MIGRATION_FAILED = "TestMigrationFailed"
        TEST_MIGRATION_IN_PROGRESS = "TestMigrationInProgress"
        TEST_MIGRATION_PARTIALLY_SUCCEEDED = "TestMigrationPartiallySucceeded"
        TEST_MIGRATION_SUCCEEDED = "TestMigrationSucceeded"


    class azure.mgmt.recoveryservicessiterecovery.models.UnplannedFailoverInput(_Model):
        properties: UnplannedFailoverInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: UnplannedFailoverInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UnplannedFailoverInputProperties(_Model):
        failover_direction: Optional[str]
        provider_specific_details: Optional[UnplannedFailoverProviderSpecificInput]
        source_site_operations: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Optional[str] = ..., 
                provider_specific_details: Optional[UnplannedFailoverProviderSpecificInput] = ..., 
                source_site_operations: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UnplannedFailoverProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateApplianceForReplicationProtectedItemInput(_Model):
        properties: UpdateApplianceForReplicationProtectedItemInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: UpdateApplianceForReplicationProtectedItemInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateApplianceForReplicationProtectedItemInputProperties(_Model):
        provider_specific_details: UpdateApplianceForReplicationProtectedItemProviderSpecificInput
        target_appliance_id: str

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: UpdateApplianceForReplicationProtectedItemProviderSpecificInput, 
                target_appliance_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateApplianceForReplicationProtectedItemProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateConfidentialDiskEncryptionInfo(_Model):
        recovery_target_confidential_disk_encryption_set_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recovery_target_confidential_disk_encryption_set_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateDiskInput(_Model):
        disk_id: str
        disk_size_in_gb: Optional[int]
        iops: Optional[int]
        target_disk_name: Optional[str]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_id: str, 
                disk_size_in_gb: Optional[int] = ..., 
                iops: Optional[int] = ..., 
                target_disk_name: Optional[str] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateMigrationItemInput(_Model):
        properties: Optional[UpdateMigrationItemInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateMigrationItemInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateMigrationItemInputProperties(_Model):
        provider_specific_details: UpdateMigrationItemProviderSpecificInput

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_details: UpdateMigrationItemProviderSpecificInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateMigrationItemProviderSpecificInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateMobilityServiceRequest(_Model):
        properties: Optional[UpdateMobilityServiceRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateMobilityServiceRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateMobilityServiceRequestProperties(_Model):
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateNetworkMappingInput(_Model):
        properties: Optional[UpdateNetworkMappingInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateNetworkMappingInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateNetworkMappingInputProperties(_Model):
        fabric_specific_details: Optional[FabricSpecificUpdateNetworkMappingInput]
        recovery_fabric_name: Optional[str]
        recovery_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fabric_specific_details: Optional[FabricSpecificUpdateNetworkMappingInput] = ..., 
                recovery_fabric_name: Optional[str] = ..., 
                recovery_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdatePolicyInput(_Model):
        properties: Optional[UpdatePolicyInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdatePolicyInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdatePolicyInputProperties(_Model):
        replication_provider_settings: Optional[PolicyProviderSpecificInput]

        @overload
        def __init__(
                self, 
                *, 
                replication_provider_settings: Optional[PolicyProviderSpecificInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateProtectionContainerMappingInput(_Model):
        properties: Optional[UpdateProtectionContainerMappingInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateProtectionContainerMappingInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateProtectionContainerMappingInputProperties(_Model):
        provider_specific_input: Optional[ReplicationProviderSpecificUpdateContainerMappingInput]

        @overload
        def __init__(
                self, 
                *, 
                provider_specific_input: Optional[ReplicationProviderSpecificUpdateContainerMappingInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateRecoveryPlanInput(_Model):
        properties: Optional[UpdateRecoveryPlanInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateRecoveryPlanInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateRecoveryPlanInputProperties(_Model):
        groups: Optional[list[RecoveryPlanGroup]]

        @overload
        def __init__(
                self, 
                *, 
                groups: Optional[list[RecoveryPlanGroup]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateReplicationProtectedItemInput(_Model):
        properties: Optional[UpdateReplicationProtectedItemInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateReplicationProtectedItemInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateReplicationProtectedItemInputProperties(_Model):
        enable_rdp_on_target_option: Optional[str]
        license_type: Optional[Union[str, LicenseType]]
        provider_specific_details: Optional[UpdateReplicationProtectedItemProviderInput]
        recovery_availability_set_id: Optional[str]
        recovery_azure_vm_name: Optional[str]
        recovery_azure_vm_size: Optional[str]
        selected_recovery_azure_network_id: Optional[str]
        selected_source_nic_id: Optional[str]
        selected_tfo_azure_network_id: Optional[str]
        vm_nics: Optional[list[VMNicInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                enable_rdp_on_target_option: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                provider_specific_details: Optional[UpdateReplicationProtectedItemProviderInput] = ..., 
                recovery_availability_set_id: Optional[str] = ..., 
                recovery_azure_vm_name: Optional[str] = ..., 
                recovery_azure_vm_size: Optional[str] = ..., 
                selected_recovery_azure_network_id: Optional[str] = ..., 
                selected_source_nic_id: Optional[str] = ..., 
                selected_tfo_azure_network_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMNicInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateReplicationProtectedItemProviderInput(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateVCenterRequest(_Model):
        properties: Optional[UpdateVCenterRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateVCenterRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UpdateVCenterRequestProperties(_Model):
        friendly_name: Optional[str]
        ip_address: Optional[str]
        port: Optional[str]
        process_server_id: Optional[str]
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                port: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.UserCreatedResourceTag(_Model):
        tag_name: Optional[str]
        tag_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                tag_name: Optional[str] = ..., 
                tag_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VCenter(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[VCenterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VCenterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VCenterProperties(_Model):
        discovery_status: Optional[str]
        fabric_arm_resource_name: Optional[str]
        friendly_name: Optional[str]
        health_errors: Optional[list[HealthError]]
        infrastructure_id: Optional[str]
        internal_id: Optional[str]
        ip_address: Optional[str]
        last_heartbeat: Optional[datetime]
        port: Optional[str]
        process_server_id: Optional[str]
        run_as_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                discovery_status: Optional[str] = ..., 
                fabric_arm_resource_name: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                health_errors: Optional[list[HealthError]] = ..., 
                infrastructure_id: Optional[str] = ..., 
                internal_id: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                port: Optional[str] = ..., 
                process_server_id: Optional[str] = ..., 
                run_as_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMNicDetails(_Model):
        enable_accelerated_networking_on_recovery: Optional[bool]
        enable_accelerated_networking_on_tfo: Optional[bool]
        ip_configs: Optional[list[IPConfigDetails]]
        nic_id: Optional[str]
        recovery_network_security_group_id: Optional[str]
        recovery_nic_name: Optional[str]
        recovery_nic_resource_group_name: Optional[str]
        recovery_vm_network_id: Optional[str]
        replica_nic_id: Optional[str]
        reuse_existing_nic: Optional[bool]
        selection_type: Optional[str]
        source_nic_arm_id: Optional[str]
        target_nic_name: Optional[str]
        tfo_network_security_group_id: Optional[str]
        tfo_recovery_nic_name: Optional[str]
        tfo_recovery_nic_resource_group_name: Optional[str]
        tfo_reuse_existing_nic: Optional[bool]
        tfo_vm_network_id: Optional[str]
        v_m_network_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_accelerated_networking_on_recovery: Optional[bool] = ..., 
                enable_accelerated_networking_on_tfo: Optional[bool] = ..., 
                ip_configs: Optional[list[IPConfigDetails]] = ..., 
                nic_id: Optional[str] = ..., 
                recovery_network_security_group_id: Optional[str] = ..., 
                recovery_nic_name: Optional[str] = ..., 
                recovery_nic_resource_group_name: Optional[str] = ..., 
                recovery_vm_network_id: Optional[str] = ..., 
                replica_nic_id: Optional[str] = ..., 
                reuse_existing_nic: Optional[bool] = ..., 
                selection_type: Optional[str] = ..., 
                source_nic_arm_id: Optional[str] = ..., 
                target_nic_name: Optional[str] = ..., 
                tfo_network_security_group_id: Optional[str] = ..., 
                tfo_recovery_nic_name: Optional[str] = ..., 
                tfo_recovery_nic_resource_group_name: Optional[str] = ..., 
                tfo_reuse_existing_nic: Optional[bool] = ..., 
                tfo_vm_network_id: Optional[str] = ..., 
                v_m_network_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMNicInputDetails(_Model):
        enable_accelerated_networking_on_recovery: Optional[bool]
        enable_accelerated_networking_on_tfo: Optional[bool]
        ip_configs: Optional[list[IPConfigInputDetails]]
        nic_id: Optional[str]
        recovery_network_security_group_id: Optional[str]
        recovery_nic_name: Optional[str]
        recovery_nic_resource_group_name: Optional[str]
        reuse_existing_nic: Optional[bool]
        selection_type: Optional[str]
        target_nic_name: Optional[str]
        tfo_network_security_group_id: Optional[str]
        tfo_nic_name: Optional[str]
        tfo_nic_resource_group_name: Optional[str]
        tfo_reuse_existing_nic: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_accelerated_networking_on_recovery: Optional[bool] = ..., 
                enable_accelerated_networking_on_tfo: Optional[bool] = ..., 
                ip_configs: Optional[list[IPConfigInputDetails]] = ..., 
                nic_id: Optional[str] = ..., 
                recovery_network_security_group_id: Optional[str] = ..., 
                recovery_nic_name: Optional[str] = ..., 
                recovery_nic_resource_group_name: Optional[str] = ..., 
                reuse_existing_nic: Optional[bool] = ..., 
                selection_type: Optional[str] = ..., 
                target_nic_name: Optional[str] = ..., 
                tfo_network_security_group_id: Optional[str] = ..., 
                tfo_nic_name: Optional[str] = ..., 
                tfo_nic_resource_group_name: Optional[str] = ..., 
                tfo_reuse_existing_nic: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtContainerCreationInput(ReplicationProviderSpecificContainerCreationInput, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtContainerMappingInput(ReplicationProviderSpecificContainerMappingInput, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]
        key_vault_id: Optional[str]
        key_vault_uri: Optional[str]
        service_bus_connection_string_secret_name: Optional[str]
        storage_account_id: str
        storage_account_sas_secret_name: Optional[str]
        target_location: str

        @overload
        def __init__(
                self, 
                *, 
                key_vault_id: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                service_bus_connection_string_secret_name: Optional[str] = ..., 
                storage_account_id: str, 
                storage_account_sas_secret_name: Optional[str] = ..., 
                target_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtDiskInput(_Model):
        confidential_disk_encryption_set_id: Optional[str]
        disk_encryption_set_id: Optional[str]
        disk_id: str
        disk_size_in_gb: Optional[int]
        disk_type: Optional[Union[str, DiskAccountType]]
        iops: Optional[int]
        is_os_disk: str
        log_storage_account_id: str
        log_storage_account_sas_secret_name: str
        sector_size_in_bytes: Optional[int]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                confidential_disk_encryption_set_id: Optional[str] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_id: str, 
                disk_size_in_gb: Optional[int] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                iops: Optional[int] = ..., 
                is_os_disk: str, 
                log_storage_account_id: str, 
                log_storage_account_sas_secret_name: str, 
                sector_size_in_bytes: Optional[int] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtEnableMigrationInput(EnableMigrationProviderSpecificInput, discriminator='VMwareCbt'):
        confidential_vm_key_vault_id: Optional[str]
        data_mover_run_as_account_id: str
        disks_to_include: list[VMwareCbtDiskInput]
        instance_type: Literal["VMwareCbt"]
        license_type: Optional[Union[str, LicenseType]]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        perform_auto_resync: Optional[str]
        perform_sql_bulk_registration: Optional[str]
        seed_disk_tags: Optional[dict[str, str]]
        snapshot_run_as_account_id: str
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_boot_diagnostics_storage_account_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_disk_tags: Optional[dict[str, str]]
        target_network_id: str
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_resource_group_id: str
        target_subnet_name: Optional[str]
        target_vm_name: Optional[str]
        target_vm_security_profile: Optional[VMwareCbtSecurityProfileProperties]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        test_network_id: Optional[str]
        test_subnet_name: Optional[str]
        user_selected_os_name: Optional[str]
        vmware_machine_id: str

        @overload
        def __init__(
                self, 
                *, 
                confidential_vm_key_vault_id: Optional[str] = ..., 
                data_mover_run_as_account_id: str, 
                disks_to_include: list[VMwareCbtDiskInput], 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                perform_auto_resync: Optional[str] = ..., 
                perform_sql_bulk_registration: Optional[str] = ..., 
                seed_disk_tags: Optional[dict[str, str]] = ..., 
                snapshot_run_as_account_id: str, 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_boot_diagnostics_storage_account_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_disk_tags: Optional[dict[str, str]] = ..., 
                target_network_id: str, 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_resource_group_id: str, 
                target_subnet_name: Optional[str] = ..., 
                target_vm_name: Optional[str] = ..., 
                target_vm_security_profile: Optional[VMwareCbtSecurityProfileProperties] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                test_network_id: Optional[str] = ..., 
                test_subnet_name: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ..., 
                vmware_machine_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtEventDetails(EventProviderSpecificDetails, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]
        migration_item_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtMigrateInput(MigrateProviderSpecificInput, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]
        os_upgrade_version: Optional[str]
        perform_shutdown: str
        post_migration_steps: Optional[list[ManagedRunCommandScriptInput]]
        target_capacity_reservation_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_upgrade_version: Optional[str] = ..., 
                perform_shutdown: str, 
                post_migration_steps: Optional[list[ManagedRunCommandScriptInput]] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtMigrationDetails(MigrationProviderSpecificSettings, discriminator='VMwareCbt'):
        appliance_monitoring_details: Optional[ApplianceMonitoringDetails]
        confidential_vm_key_vault_id: Optional[str]
        data_mover_run_as_account_id: Optional[str]
        delta_sync_progress_percentage: Optional[int]
        delta_sync_retry_count: Optional[int]
        firmware_type: Optional[str]
        gateway_operation_details: Optional[GatewayOperationDetails]
        initial_seeding_progress_percentage: Optional[int]
        initial_seeding_retry_count: Optional[int]
        instance_type: Literal["VMwareCbt"]
        is_check_sum_resync_cycle: Optional[str]
        last_recovery_point_id: Optional[str]
        last_recovery_point_received: Optional[datetime]
        license_type: Optional[str]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        migration_progress_percentage: Optional[int]
        migration_recovery_point_id: Optional[str]
        operation_name: Optional[str]
        os_name: Optional[str]
        os_type: Optional[str]
        perform_auto_resync: Optional[str]
        protected_disks: Optional[list[VMwareCbtProtectedDiskDetails]]
        resume_progress_percentage: Optional[int]
        resume_retry_count: Optional[int]
        resync_progress_percentage: Optional[int]
        resync_required: Optional[str]
        resync_retry_count: Optional[int]
        resync_state: Optional[Union[str, ResyncState]]
        seed_disk_tags: Optional[dict[str, str]]
        snapshot_run_as_account_id: Optional[str]
        sql_server_license_type: Optional[str]
        storage_account_id: Optional[str]
        supported_os_versions: Optional[list[str]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_boot_diagnostics_storage_account_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_disk_tags: Optional[dict[str, str]]
        target_generation: Optional[str]
        target_location: Optional[str]
        target_network_id: Optional[str]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_resource_group_id: Optional[str]
        target_vm_name: Optional[str]
        target_vm_security_profile: Optional[VMwareCbtSecurityProfileProperties]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        test_network_id: Optional[str]
        vm_nics: Optional[list[VMwareCbtNicDetails]]
        vmware_machine_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidential_vm_key_vault_id: Optional[str] = ..., 
                license_type: Optional[str] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                perform_auto_resync: Optional[str] = ..., 
                protected_disks: Optional[list[VMwareCbtProtectedDiskDetails]] = ..., 
                seed_disk_tags: Optional[dict[str, str]] = ..., 
                sql_server_license_type: Optional[str] = ..., 
                supported_os_versions: Optional[list[str]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_boot_diagnostics_storage_account_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_disk_tags: Optional[dict[str, str]] = ..., 
                target_network_id: Optional[str] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_vm_name: Optional[str] = ..., 
                target_vm_security_profile: Optional[VMwareCbtSecurityProfileProperties] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                test_network_id: Optional[str] = ..., 
                vm_nics: Optional[list[VMwareCbtNicDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtNicDetails(_Model):
        is_primary_nic: Optional[str]
        is_selected_for_migration: Optional[str]
        nic_id: Optional[str]
        source_ip_address: Optional[str]
        source_ip_address_type: Optional[Union[str, EthernetAddressType]]
        source_network_id: Optional[str]
        target_ip_address: Optional[str]
        target_ip_address_type: Optional[Union[str, EthernetAddressType]]
        target_nic_name: Optional[str]
        target_subnet_name: Optional[str]
        test_ip_address: Optional[str]
        test_ip_address_type: Optional[Union[str, EthernetAddressType]]
        test_network_id: Optional[str]
        test_subnet_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_primary_nic: Optional[str] = ..., 
                is_selected_for_migration: Optional[str] = ..., 
                target_ip_address: Optional[str] = ..., 
                target_ip_address_type: Optional[Union[str, EthernetAddressType]] = ..., 
                target_nic_name: Optional[str] = ..., 
                target_subnet_name: Optional[str] = ..., 
                test_ip_address: Optional[str] = ..., 
                test_ip_address_type: Optional[Union[str, EthernetAddressType]] = ..., 
                test_network_id: Optional[str] = ..., 
                test_subnet_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtNicInput(_Model):
        is_primary_nic: str
        is_selected_for_migration: Optional[str]
        nic_id: str
        target_nic_name: Optional[str]
        target_static_ip_address: Optional[str]
        target_subnet_name: Optional[str]
        test_static_ip_address: Optional[str]
        test_subnet_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_primary_nic: str, 
                is_selected_for_migration: Optional[str] = ..., 
                nic_id: str, 
                target_nic_name: Optional[str] = ..., 
                target_static_ip_address: Optional[str] = ..., 
                target_subnet_name: Optional[str] = ..., 
                test_static_ip_address: Optional[str] = ..., 
                test_subnet_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtPolicyCreationInput(PolicyProviderSpecificInput, discriminator='VMwareCbt'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["VMwareCbt"]
        recovery_point_history_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                recovery_point_history_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtProtectedDiskDetails(_Model):
        capacity_in_bytes: Optional[int]
        confidential_disk_encryption_set_id: Optional[str]
        disk_encryption_set_id: Optional[str]
        disk_id: Optional[str]
        disk_name: Optional[str]
        disk_path: Optional[str]
        disk_size_in_gb: Optional[int]
        disk_type: Optional[Union[str, DiskAccountType]]
        gateway_operation_details: Optional[GatewayOperationDetails]
        iops: Optional[int]
        is_os_disk: Optional[str]
        log_storage_account_id: Optional[str]
        log_storage_account_sas_secret_name: Optional[str]
        sector_size_in_bytes: Optional[int]
        seed_blob_uri: Optional[str]
        seed_managed_disk_id: Optional[str]
        target_blob_uri: Optional[str]
        target_disk_name: Optional[str]
        target_managed_disk_id: Optional[str]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_size_in_gb: Optional[int] = ..., 
                disk_type: Optional[Union[str, DiskAccountType]] = ..., 
                iops: Optional[int] = ..., 
                sector_size_in_bytes: Optional[int] = ..., 
                target_disk_name: Optional[str] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtProtectionContainerMappingDetails(ProtectionContainerMappingProviderSpecificDetails, discriminator='VMwareCbt'):
        excluded_skus: Optional[list[str]]
        instance_type: Literal["VMwareCbt"]
        key_vault_id: Optional[str]
        key_vault_uri: Optional[str]
        role_size_to_nic_count_map: Optional[dict[str, int]]
        service_bus_connection_string_secret_name: Optional[str]
        storage_account_id: Optional[str]
        storage_account_sas_secret_name: Optional[str]
        target_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                excluded_skus: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtResumeReplicationInput(ResumeReplicationProviderSpecificInput, discriminator='VMwareCbt'):
        delete_migration_resources: Optional[str]
        instance_type: Literal["VMwareCbt"]

        @overload
        def __init__(
                self, 
                *, 
                delete_migration_resources: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtResyncInput(ResyncProviderSpecificInput, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]
        skip_cbt_reset: str

        @overload
        def __init__(
                self, 
                *, 
                skip_cbt_reset: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtSecurityProfileProperties(_Model):
        is_target_vm_confidential_encryption_enabled: Optional[str]
        is_target_vm_integrity_monitoring_enabled: Optional[str]
        is_target_vm_secure_boot_enabled: Optional[str]
        is_target_vm_tpm_enabled: Optional[str]
        target_vm_security_type: Optional[Union[str, SecurityType]]

        @overload
        def __init__(
                self, 
                *, 
                is_target_vm_confidential_encryption_enabled: Optional[str] = ..., 
                is_target_vm_integrity_monitoring_enabled: Optional[str] = ..., 
                is_target_vm_secure_boot_enabled: Optional[str] = ..., 
                is_target_vm_tpm_enabled: Optional[str] = ..., 
                target_vm_security_type: Optional[Union[str, SecurityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtTestMigrateInput(TestMigrateProviderSpecificInput, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]
        network_id: str
        os_upgrade_version: Optional[str]
        post_migration_steps: Optional[list[ManagedRunCommandScriptInput]]
        recovery_point_id: str
        vm_nics: Optional[list[VMwareCbtNicInput]]

        @overload
        def __init__(
                self, 
                *, 
                network_id: str, 
                os_upgrade_version: Optional[str] = ..., 
                post_migration_steps: Optional[list[ManagedRunCommandScriptInput]] = ..., 
                recovery_point_id: str, 
                vm_nics: Optional[list[VMwareCbtNicInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtUpdateDiskInput(_Model):
        disk_id: str
        disk_size_in_gb: Optional[int]
        iops: Optional[int]
        is_os_disk: Optional[str]
        target_disk_name: Optional[str]
        throughput_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_id: str, 
                disk_size_in_gb: Optional[int] = ..., 
                iops: Optional[int] = ..., 
                is_os_disk: Optional[str] = ..., 
                target_disk_name: Optional[str] = ..., 
                throughput_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareCbtUpdateMigrationItemInput(UpdateMigrationItemProviderSpecificInput, discriminator='VMwareCbt'):
        instance_type: Literal["VMwareCbt"]
        license_type: Optional[Union[str, LicenseType]]
        linux_license_type: Optional[Union[str, LinuxLicenseType]]
        perform_auto_resync: Optional[str]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        target_availability_set_id: Optional[str]
        target_availability_zone: Optional[str]
        target_boot_diagnostics_storage_account_id: Optional[str]
        target_capacity_reservation_group_id: Optional[str]
        target_disk_tags: Optional[dict[str, str]]
        target_network_id: Optional[str]
        target_nic_tags: Optional[dict[str, str]]
        target_proximity_placement_group_id: Optional[str]
        target_resource_group_id: Optional[str]
        target_vm_name: Optional[str]
        target_vm_size: Optional[str]
        target_vm_tags: Optional[dict[str, str]]
        test_network_id: Optional[str]
        user_selected_os_name: Optional[str]
        vm_disks: Optional[list[VMwareCbtUpdateDiskInput]]
        vm_nics: Optional[list[VMwareCbtNicInput]]

        @overload
        def __init__(
                self, 
                *, 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                linux_license_type: Optional[Union[str, LinuxLicenseType]] = ..., 
                perform_auto_resync: Optional[str] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[str] = ..., 
                target_boot_diagnostics_storage_account_id: Optional[str] = ..., 
                target_capacity_reservation_group_id: Optional[str] = ..., 
                target_disk_tags: Optional[dict[str, str]] = ..., 
                target_network_id: Optional[str] = ..., 
                target_nic_tags: Optional[dict[str, str]] = ..., 
                target_proximity_placement_group_id: Optional[str] = ..., 
                target_resource_group_id: Optional[str] = ..., 
                target_vm_name: Optional[str] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_vm_tags: Optional[dict[str, str]] = ..., 
                test_network_id: Optional[str] = ..., 
                user_selected_os_name: Optional[str] = ..., 
                vm_disks: Optional[list[VMwareCbtUpdateDiskInput]] = ..., 
                vm_nics: Optional[list[VMwareCbtNicInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareDetails(FabricSpecificDetails, discriminator='VMware'):
        agent_count: Optional[str]
        agent_expiry_date: Optional[datetime]
        agent_version: Optional[str]
        agent_version_details: Optional[VersionDetails]
        available_memory_in_bytes: Optional[int]
        available_space_in_bytes: Optional[int]
        cpu_load: Optional[str]
        cpu_load_status: Optional[str]
        cs_service_status: Optional[str]
        database_server_load: Optional[str]
        database_server_load_status: Optional[str]
        host_name: Optional[str]
        instance_type: Literal["VMware"]
        ip_address: Optional[str]
        last_heartbeat: Optional[datetime]
        master_target_servers: Optional[list[MasterTargetServer]]
        memory_usage_status: Optional[str]
        process_server_count: Optional[str]
        process_servers: Optional[list[ProcessServer]]
        protected_servers: Optional[str]
        ps_template_version: Optional[str]
        replication_pair_count: Optional[str]
        run_as_accounts: Optional[list[RunAsAccount]]
        space_usage_status: Optional[str]
        ssl_cert_expiry_date: Optional[datetime]
        ssl_cert_expiry_remaining_days: Optional[int]
        switch_provider_blocking_error_details: Optional[list[InMageFabricSwitchProviderBlockingErrorDetails]]
        system_load: Optional[str]
        system_load_status: Optional[str]
        total_memory_in_bytes: Optional[int]
        total_space_in_bytes: Optional[int]
        version_status: Optional[str]
        web_load: Optional[str]
        web_load_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_count: Optional[str] = ..., 
                agent_expiry_date: Optional[datetime] = ..., 
                agent_version: Optional[str] = ..., 
                agent_version_details: Optional[VersionDetails] = ..., 
                available_memory_in_bytes: Optional[int] = ..., 
                available_space_in_bytes: Optional[int] = ..., 
                cpu_load: Optional[str] = ..., 
                cpu_load_status: Optional[str] = ..., 
                cs_service_status: Optional[str] = ..., 
                database_server_load: Optional[str] = ..., 
                database_server_load_status: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                last_heartbeat: Optional[datetime] = ..., 
                master_target_servers: Optional[list[MasterTargetServer]] = ..., 
                memory_usage_status: Optional[str] = ..., 
                process_server_count: Optional[str] = ..., 
                process_servers: Optional[list[ProcessServer]] = ..., 
                protected_servers: Optional[str] = ..., 
                ps_template_version: Optional[str] = ..., 
                replication_pair_count: Optional[str] = ..., 
                run_as_accounts: Optional[list[RunAsAccount]] = ..., 
                space_usage_status: Optional[str] = ..., 
                ssl_cert_expiry_date: Optional[datetime] = ..., 
                ssl_cert_expiry_remaining_days: Optional[int] = ..., 
                switch_provider_blocking_error_details: Optional[list[InMageFabricSwitchProviderBlockingErrorDetails]] = ..., 
                system_load: Optional[str] = ..., 
                system_load_status: Optional[str] = ..., 
                total_memory_in_bytes: Optional[int] = ..., 
                total_space_in_bytes: Optional[int] = ..., 
                version_status: Optional[str] = ..., 
                web_load: Optional[str] = ..., 
                web_load_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareV2FabricCreationInput(FabricSpecificCreationInput, discriminator='VMwareV2'):
        instance_type: Literal["VMwareV2"]
        migration_solution_id: str
        physical_site_id: Optional[str]
        vmware_site_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                migration_solution_id: str, 
                physical_site_id: Optional[str] = ..., 
                vmware_site_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareV2FabricSpecificDetails(FabricSpecificDetails, discriminator='VMwareV2'):
        instance_type: Literal["VMwareV2"]
        migration_solution_id: Optional[str]
        physical_site_id: Optional[str]
        process_servers: Optional[list[ProcessServerDetails]]
        service_container_id: Optional[str]
        service_endpoint: Optional[str]
        service_resource_id: Optional[str]
        vmware_site_id: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VMwareVirtualMachineDetails(ConfigurationSettings, discriminator='VMwareVirtualMachine'):
        agent_generated_id: Optional[str]
        agent_installed: Optional[str]
        agent_version: Optional[str]
        discovery_type: Optional[str]
        disk_details: Optional[list[InMageDiskDetails]]
        instance_type: Literal["VMwareVirtualMachine"]
        ip_address: Optional[str]
        os_type: Optional[str]
        powered_on: Optional[str]
        v_center_infrastructure_id: Optional[str]
        validation_errors: Optional[list[HealthError]]

        @overload
        def __init__(
                self, 
                *, 
                agent_generated_id: Optional[str] = ..., 
                agent_installed: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                discovery_type: Optional[str] = ..., 
                disk_details: Optional[list[InMageDiskDetails]] = ..., 
                ip_address: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                powered_on: Optional[str] = ..., 
                v_center_infrastructure_id: Optional[str] = ..., 
                validation_errors: Optional[list[HealthError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VaultHealthDetails(Resource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[VaultHealthProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VaultHealthProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VaultHealthProperties(_Model):
        containers_health: Optional[ResourceHealthSummary]
        fabrics_health: Optional[ResourceHealthSummary]
        protected_items_health: Optional[ResourceHealthSummary]
        vault_errors: Optional[list[HealthError]]

        @overload
        def __init__(
                self, 
                *, 
                containers_health: Optional[ResourceHealthSummary] = ..., 
                fabrics_health: Optional[ResourceHealthSummary] = ..., 
                protected_items_health: Optional[ResourceHealthSummary] = ..., 
                vault_errors: Optional[list[HealthError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VaultSetting(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[VaultSettingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VaultSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VaultSettingCreationInput(_Model):
        properties: VaultSettingCreationInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: VaultSettingCreationInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VaultSettingCreationInputProperties(_Model):
        migration_solution_id: Optional[str]
        recovery_network_config_auto_sync: Optional[Union[str, RecoveryNetworkConfigAutoSyncPolicy]]
        vmware_to_azure_provider_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                migration_solution_id: Optional[str] = ..., 
                recovery_network_config_auto_sync: Optional[Union[str, RecoveryNetworkConfigAutoSyncPolicy]] = ..., 
                vmware_to_azure_provider_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VaultSettingProperties(_Model):
        migration_solution_id: Optional[str]
        recovery_network_config_auto_sync: Optional[Union[str, RecoveryNetworkConfigAutoSyncPolicy]]
        vmware_to_azure_provider_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                migration_solution_id: Optional[str] = ..., 
                recovery_network_config_auto_sync: Optional[Union[str, RecoveryNetworkConfigAutoSyncPolicy]] = ..., 
                vmware_to_azure_provider_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VersionDetails(_Model):
        expiry_date: Optional[datetime]
        status: Optional[Union[str, AgentVersionStatus]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_date: Optional[datetime] = ..., 
                status: Optional[Union[str, AgentVersionStatus]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VirtualMachineTaskDetails(JobTaskDetails, discriminator='VirtualMachineTaskDetails'):
        instance_type: Literal["VirtualMachineTaskDetails"]
        job_task: JobEntity
        skipped_reason: Optional[str]
        skipped_reason_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                job_task: Optional[JobEntity] = ..., 
                skipped_reason: Optional[str] = ..., 
                skipped_reason_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_ENCRYPTED = "NotEncrypted"
        ONE_PASS_ENCRYPTED = "OnePassEncrypted"
        TWO_PASS_ENCRYPTED = "TwoPassEncrypted"


    class azure.mgmt.recoveryservicessiterecovery.models.VmNicUpdatesTaskDetails(TaskTypeDetails, discriminator='VmNicUpdatesTaskDetails'):
        instance_type: Literal["VmNicUpdatesTaskDetails"]
        name: Optional[str]
        nic_id: Optional[str]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                nic_id: Optional[str] = ..., 
                vm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmReplicationProgressHealth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_PROGRESS = "InProgress"
        NONE = "None"
        NO_PROGRESS = "NoProgress"
        SLOW_PROGRESS = "SlowProgress"


    class azure.mgmt.recoveryservicessiterecovery.models.VmmDetails(FabricSpecificDetails, discriminator='VMM'):
        instance_type: Literal["VMM"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmToAzureCreateNetworkMappingInput(FabricSpecificCreateNetworkMappingInput, discriminator='VmmToAzure'):
        instance_type: Literal["VmmToAzure"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmToAzureNetworkMappingSettings(NetworkMappingFabricSpecificSettings, discriminator='VmmToAzure'):
        instance_type: Literal["VmmToAzure"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmToAzureUpdateNetworkMappingInput(FabricSpecificUpdateNetworkMappingInput, discriminator='VmmToAzure'):
        instance_type: Literal["VmmToAzure"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmToVmmCreateNetworkMappingInput(FabricSpecificCreateNetworkMappingInput, discriminator='VmmToVmm'):
        instance_type: Literal["VmmToVmm"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmToVmmNetworkMappingSettings(NetworkMappingFabricSpecificSettings, discriminator='VmmToVmm'):
        instance_type: Literal["VmmToVmm"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmToVmmUpdateNetworkMappingInput(FabricSpecificUpdateNetworkMappingInput, discriminator='VmmToVmm'):
        instance_type: Literal["VmmToVmm"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmmVirtualMachineDetails(HyperVVirtualMachineDetails, discriminator='VmmVirtualMachine'):
        disk_details: list[DiskDetails]
        generation: str
        has_fibre_channel_adapter: Union[str, PresenceStatus]
        has_physical_disk: Union[str, PresenceStatus]
        has_shared_vhd: Union[str, PresenceStatus]
        hyper_v_host_id: str
        instance_type: Literal["VmmVirtualMachine"]
        os_details: OSDetails
        source_item_id: str

        @overload
        def __init__(
                self, 
                *, 
                disk_details: Optional[list[DiskDetails]] = ..., 
                generation: Optional[str] = ..., 
                has_fibre_channel_adapter: Optional[Union[str, PresenceStatus]] = ..., 
                has_physical_disk: Optional[Union[str, PresenceStatus]] = ..., 
                has_shared_vhd: Optional[Union[str, PresenceStatus]] = ..., 
                hyper_v_host_id: Optional[str] = ..., 
                os_details: Optional[OSDetails] = ..., 
                source_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicessiterecovery.models.VmwareCbtPolicyDetails(PolicyProviderSpecificDetails, discriminator='VMwareCbt'):
        app_consistent_frequency_in_minutes: Optional[int]
        crash_consistent_frequency_in_minutes: Optional[int]
        instance_type: Literal["VMwareCbt"]
        recovery_point_history_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: Optional[int] = ..., 
                crash_consistent_frequency_in_minutes: Optional[int] = ..., 
                recovery_point_history_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.recoveryservicessiterecovery.operations

    class azure.mgmt.recoveryservicessiterecovery.operations.ClusterRecoveryPointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                recovery_point_name: str, 
                **kwargs: Any
            ) -> ClusterRecoveryPoint: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ClusterRecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_replication_protection_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClusterRecoveryPoint]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.MigrationRecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migration_recovery_point_name: str, 
                **kwargs: Any
            ) -> MigrationRecoveryPoint: ...

        @distributed_trace
        def list_by_replication_migration_items(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MigrationRecoveryPoint]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OperationsDiscovery]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.RecoveryPointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                recovery_point_name: str, 
                **kwargs: Any
            ) -> RecoveryPoint: ...

        @distributed_trace
        def list_by_replication_protected_items(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPoint]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationAlertSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                request: ConfigureAlertRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                request: ConfigureAlertRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                alert_setting_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Alert]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationAppliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReplicationAppliance]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationEligibilityResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> ReplicationEligibilityResults: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> ReplicationEligibilityResultsCollection: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_name: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Event]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_check_consistency(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                input: FabricCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                input: FabricCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_migrate_to_aad(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reassociate_gateway(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                failover_process_server_request: FailoverProcessServerRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_reassociate_gateway(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                failover_process_server_request: FailoverProcessServerRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_reassociate_gateway(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                failover_process_server_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @distributed_trace
        def begin_remove_infra(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_renew_certificate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                renew_certificate: RenewCertificateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_renew_certificate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                renew_certificate: RenewCertificateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_renew_certificate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                renew_certificate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Fabric: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Fabric]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_export(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_query_parameter: JobQueryParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_export(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_query_parameter: JobQueryParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_export(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_query_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_resume(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                resume_job_params: ResumeJobParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_resume(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                resume_job_params: ResumeJobParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_resume(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                resume_job_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Job]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationLogicalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                logical_network_name: str, 
                **kwargs: Any
            ) -> LogicalNetwork: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LogicalNetwork]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationMigrationItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: EnableMigrationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: EnableMigrationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                *, 
                delete_option: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migrate_input: MigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migrate_input: MigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                migrate_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_pause_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                pause_replication_input: PauseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_pause_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                pause_replication_input: PauseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_pause_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                pause_replication_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_resume_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                resume_replication_input: ResumeReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_resume_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                resume_replication_input: ResumeReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_resume_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                resume_replication_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_resync(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: ResyncInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_resync(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: ResyncInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_resync(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_test_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_input: TestMigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_test_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_input: TestMigrateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_test_migrate(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_test_migrate_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_cleanup_input: TestMigrateCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_test_migrate_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_cleanup_input: TestMigrateCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_test_migrate_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                test_migrate_cleanup_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: UpdateMigrationItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: UpdateMigrationItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationItem]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                migration_item_name: str, 
                **kwargs: Any
            ) -> MigrationItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                take_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MigrationItem]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                take_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MigrationItem]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationNetworkMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: CreateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMapping]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: CreateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMapping]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMapping]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: UpdateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMapping]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: UpdateNetworkMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMapping]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMapping]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                network_mapping_name: str, 
                **kwargs: Any
            ) -> NetworkMapping: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkMapping]: ...

        @distributed_trace
        def list_by_replication_networks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkMapping]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                network_name: str, 
                **kwargs: Any
            ) -> Network: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Network]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Network]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: CreatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: CreatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: UpdatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: UpdatePolicyInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Policy]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationProtectableItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                protectable_item_name: str, 
                **kwargs: Any
            ) -> ProtectableItem: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                take: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectableItem]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationProtectedItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_add_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                add_disks_input: AddDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_add_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                add_disks_input: AddDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_add_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                add_disks_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                apply_recovery_point_input: ApplyRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                apply_recovery_point_input: ApplyRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                apply_recovery_point_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                input: EnableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                input: EnableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                disable_protection_input: DisableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                disable_protection_input: DisableProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                disable_protection_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_failover_cancel(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @distributed_trace
        def begin_failover_commit(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: PlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: PlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @distributed_trace
        def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reinstall_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: ReinstallMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_reinstall_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: ReinstallMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_reinstall_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_remove_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                remove_disks_input: RemoveDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_remove_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                remove_disks_input: RemoveDisksInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_remove_disks(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                remove_disks_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @distributed_trace
        def begin_repair_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                reprotect_input: ReverseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                reprotect_input: ReverseReplicationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                reprotect_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_resolve_health_errors(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                resolve_health_input: ResolveHealthInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_resolve_health_errors(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                resolve_health_input: ResolveHealthInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_resolve_health_errors(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                resolve_health_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_switch_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                switch_provider_input: SwitchProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_switch_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                switch_provider_input: SwitchProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_switch_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                switch_provider_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                testfailover_input: TestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                testfailover_input: TestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                testfailover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                cleanup_input: TestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                cleanup_input: TestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                cleanup_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: UnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: UnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_protection_input: UpdateReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_protection_input: UpdateReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_protection_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update_appliance(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                appliance_update_input: UpdateApplianceForReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update_appliance(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                appliance_update_input: UpdateApplianceForReplicationProtectedItemInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update_appliance(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                appliance_update_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: UpdateMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: UpdateMobilityServiceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @overload
        def begin_update_mobility_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                update_mobility_service_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectedItem]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> ReplicationProtectedItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReplicationProtectedItem]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ReplicationProtectedItem]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationProtectionClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                apply_cluster_recovery_point_input: ApplyClusterRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                apply_cluster_recovery_point_input: ApplyClusterRecoveryPointInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_apply_recovery_point(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                apply_cluster_recovery_point_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                replication_protection_cluster: ReplicationProtectionCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                replication_protection_cluster: ReplicationProtectionCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                replication_protection_cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @distributed_trace
        def begin_failover_commit(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @distributed_trace
        def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_repair_replication(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                cleanup_input: ClusterTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                cleanup_input: ClusterTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                cleanup_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: ClusterUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationProtectionCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                **kwargs: Any
            ) -> ReplicationProtectionCluster: ...

        @distributed_trace
        def get_operation_results(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replication_protection_cluster_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> ReplicationProtectionCluster: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReplicationProtectionCluster]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ReplicationProtectionCluster]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationProtectionContainerMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                creation_input: CreateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerMapping]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                creation_input: CreateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerMapping]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                creation_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerMapping]: ...

        @overload
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                removal_input: RemoveProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                removal_input: RemoveProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                removal_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                update_input: UpdateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerMapping]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                update_input: UpdateProtectionContainerMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerMapping]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                update_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainerMapping]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                mapping_name: str, 
                **kwargs: Any
            ) -> ProtectionContainerMapping: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProtectionContainerMapping]: ...

        @distributed_trace
        def list_by_replication_protection_containers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProtectionContainerMapping]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationProtectionContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                creation_input: CreateProtectionContainerInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                creation_input: CreateProtectionContainerInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                creation_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_discover_protectable_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                discover_protectable_item_request: DiscoverProtectableItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_discover_protectable_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                discover_protectable_item_request: DiscoverProtectableItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_discover_protectable_item(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                discover_protectable_item_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_switch_cluster_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchClusterProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_switch_cluster_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchClusterProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_switch_cluster_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_switch_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_switch_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: SwitchProtectionInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @overload
        def begin_switch_protection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                switch_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionContainer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                **kwargs: Any
            ) -> ProtectionContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProtectionContainer]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProtectionContainer]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationProtectionIntentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                input: CreateProtectionIntentInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                input: CreateProtectionIntentInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                intent_object_name: str, 
                **kwargs: Any
            ) -> ReplicationProtectionIntent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                take_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReplicationProtectionIntent]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationRecoveryPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: CreateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: CreateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_failover_cancel(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @distributed_trace
        def begin_failover_commit(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanPlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanPlannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @distributed_trace
        def begin_reprotect(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_test_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanTestFailoverCleanupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: RecoveryPlanUnplannedFailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_unplanned_failover(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: UpdateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: UpdateRecoveryPlanInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> RecoveryPlan: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPlan]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationRecoveryServicesProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                add_provider_input: AddRecoveryServicesProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryServicesProvider]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                add_provider_input: AddRecoveryServicesProviderInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryServicesProvider]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                add_provider_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryServicesProvider]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_purge(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh_provider(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryServicesProvider]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> RecoveryServicesProvider: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryServicesProvider]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryServicesProvider]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationStorageClassificationMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                pairing_input: StorageClassificationMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassificationMapping]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                pairing_input: StorageClassificationMappingInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassificationMapping]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                pairing_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageClassificationMapping]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                storage_classification_mapping_name: str, 
                **kwargs: Any
            ) -> StorageClassificationMapping: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageClassificationMapping]: ...

        @distributed_trace
        def list_by_replication_storage_classifications(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageClassificationMapping]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationStorageClassificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                storage_classification_name: str, 
                **kwargs: Any
            ) -> StorageClassification: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageClassification]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageClassification]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationVaultHealthOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_refresh(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[VaultHealthDetails]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> VaultHealthDetails: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationVaultSettingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                input: VaultSettingCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultSetting]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                input: VaultSettingCreationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultSetting]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultSetting]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                vault_setting_name: str, 
                **kwargs: Any
            ) -> VaultSetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VaultSetting]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.ReplicationvCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                add_v_center_request: AddVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                add_v_center_request: AddVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                add_v_center_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                update_v_center_request: UpdateVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                update_v_center_request: UpdateVCenterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                update_v_center_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                vcenter_name: str, 
                **kwargs: Any
            ) -> VCenter: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VCenter]: ...

        @distributed_trace
        def list_by_replication_fabrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VCenter]: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.SupportedOperatingSystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                instance_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> SupportedOperatingSystems: ...


    class azure.mgmt.recoveryservicessiterecovery.operations.TargetComputeSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_replication_protected_items(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                fabric_name: str, 
                protection_container_name: str, 
                replicated_protected_item_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TargetComputeSize]: ...


namespace azure.mgmt.recoveryservicessiterecovery.types

    class azure.mgmt.recoveryservicessiterecovery.types.A2AAddDisksInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]
        vmDisks: list[A2AVmDiskInputDetails]
        vmManagedDisks: list[A2AVmManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AApplyClusterRecoveryPointInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AApplyRecoveryPointInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AClusterTestFailoverInput(TypedDict, total=False):
        key "clusterRecoveryPointId": str
        key "instanceType": Required[Literal["A2A"]]
        clusterRecoveryPointId: str
        individualNodeRecoveryPoints: list[str]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AClusterUnplannedFailoverInput(TypedDict, total=False):
        key "clusterRecoveryPointId": str
        key "instanceType": Required[Literal["A2A"]]
        clusterRecoveryPointId: str
        individualNodeRecoveryPoints: list[str]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AClusterVmManagedDiskInputDetails(TypedDict, total=False):
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "diskId": Required[str]
        key "primaryStagingAzureStorageAccountId": Required[str]
        key "recoveryDiskAccessId": str
        key "recoveryDiskEncryptionSetId": str
        key "recoveryNetworkAccessPolicy": Union[str, DiskNetworkAccessPolicy]
        key "recoveryPublicNetworkAccess": Union[str, DiskPublicNetworkAccess]
        key "recoveryReplicaDiskAccountType": str
        key "recoveryResourceGroupId": Required[str]
        key "recoveryTargetDiskAccountType": str
        diskEncryptionInfo: DiskEncryptionInfo
        diskId: str
        primaryStagingAzureStorageAccountId: str
        recoveryDiskAccessId: str
        recoveryDiskEncryptionSetId: str
        recoveryNetworkAccessPolicy: Union[str, DiskNetworkAccessPolicy]
        recoveryPublicNetworkAccess: Union[str, DiskPublicNetworkAccess]
        recoveryReplicaDiskAccountType: str
        recoveryResourceGroupId: str
        recoveryTargetDiskAccountType: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AContainerCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AContainerMappingInput(TypedDict, total=False):
        key "agentAutoUpdateStatus": Union[str, AgentAutoUpdateStatus]
        key "automationAccountArmId": str
        key "automationAccountAuthenticationType": Union[str, AutomationAccountAuthenticationType]
        key "instanceType": Required[Literal["A2A"]]
        agentAutoUpdateStatus: Union[str, AgentAutoUpdateStatus]
        automationAccountArmId: str
        automationAccountAuthenticationType: Union[str, AutomationAccountAuthenticationType]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ACreateProtectionIntentInput(TypedDict, total=False):
        key "agentAutoUpdateStatus": Union[str, AgentAutoUpdateStatus]
        key "autoProtectionOfDataDisk": Union[str, AutoProtectionOfDataDisk]
        key "automationAccountArmId": str
        key "automationAccountAuthenticationType": Union[str, AutomationAccountAuthenticationType]
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "fabricObjectId": Required[str]
        key "instanceType": Required[Literal["A2A"]]
        key "multiVmGroupId": str
        key "multiVmGroupName": str
        key "primaryLocation": Required[str]
        key "primaryStagingStorageAccountCustomInput": ForwardRef('StorageAccountCustomDetails', module='types')
        key "protectionProfileCustomInput": ForwardRef('ProtectionProfileCustomDetails', module='types')
        key "recoveryAvailabilitySetCustomInput": ForwardRef('RecoveryAvailabilitySetCustomDetails', module='types')
        key "recoveryAvailabilityType": Required[Union[str, A2ARecoveryAvailabilityType]]
        key "recoveryAvailabilityZone": str
        key "recoveryBootDiagStorageAccount": ForwardRef('StorageAccountCustomDetails', module='types')
        key "recoveryLocation": Required[str]
        key "recoveryProximityPlacementGroupCustomInput": ForwardRef('RecoveryProximityPlacementGroupCustomDetails', module='types')
        key "recoveryResourceGroupId": Required[str]
        key "recoverySubscriptionId": Required[str]
        key "recoveryVirtualNetworkCustomInput": ForwardRef('RecoveryVirtualNetworkCustomDetails', module='types')
        agentAutoUpdateStatus: Union[str, AgentAutoUpdateStatus]
        autoProtectionOfDataDisk: Union[str, AutoProtectionOfDataDisk]
        automationAccountArmId: str
        automationAccountAuthenticationType: Union[str, AutomationAccountAuthenticationType]
        diskEncryptionInfo: DiskEncryptionInfo
        fabricObjectId: str
        instanceType: Literal[A2A]
        multiVmGroupId: str
        multiVmGroupName: str
        primaryLocation: str
        primaryStagingStorageAccountCustomInput: StorageAccountCustomDetails
        protectionProfileCustomInput: ProtectionProfileCustomDetails
        recoveryAvailabilitySetCustomInput: RecoveryAvailabilitySetCustomDetails
        recoveryAvailabilityType: Union[str, A2ARecoveryAvailabilityType]
        recoveryAvailabilityZone: str
        recoveryBootDiagStorageAccount: StorageAccountCustomDetails
        recoveryLocation: str
        recoveryProximityPlacementGroupCustomInput: RecoveryProximityPlacementGroupCustomDetails
        recoveryResourceGroupId: str
        recoverySubscriptionId: str
        recoveryVirtualNetworkCustomInput: RecoveryVirtualNetworkCustomDetails
        vmDisks: list[A2AProtectionIntentDiskInputDetails]
        vmManagedDisks: list[A2AProtectionIntentManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ACrossClusterMigrationApplyRecoveryPointInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2ACrossClusterMigration"]]
        instanceType: Literal[A2ACrossClusterMigration]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ACrossClusterMigrationContainerCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2ACrossClusterMigration"]]
        instanceType: Literal[A2ACrossClusterMigration]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ACrossClusterMigrationEnableProtectionInput(TypedDict, total=False):
        key "fabricObjectId": str
        key "instanceType": Required[Literal["A2ACrossClusterMigration"]]
        key "recoveryContainerId": str
        fabricObjectId: str
        instanceType: Literal[A2ACrossClusterMigration]
        recoveryContainerId: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2ACrossClusterMigrationPolicyCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2ACrossClusterMigration"]]
        instanceType: Literal[A2ACrossClusterMigration]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AEnableProtectionInput(TypedDict, total=False):
        key "autoProtectionOfDataDisk": Union[str, AutoProtectionOfDataDisk]
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "fabricObjectId": Required[str]
        key "instanceType": Required[Literal["A2A"]]
        key "multiVmGroupId": str
        key "multiVmGroupName": str
        key "platformFaultDomain": int
        key "protectionClusterId": str
        key "recoveryAvailabilitySetId": str
        key "recoveryAvailabilityZone": str
        key "recoveryAzureNetworkId": str
        key "recoveryBootDiagStorageAccountId": str
        key "recoveryCapacityReservationGroupId": str
        key "recoveryCloudServiceId": str
        key "recoveryConfidentialDataDiskEncryptionIdentity": str
        key "recoveryContainerId": str
        key "recoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "recoveryProximityPlacementGroupId": str
        key "recoveryResourceGroupId": str
        key "recoverySubnetName": str
        key "recoveryVirtualMachineScaleSetId": str
        autoProtectionOfDataDisk: Union[str, AutoProtectionOfDataDisk]
        diskEncryptionInfo: DiskEncryptionInfo
        fabricObjectId: str
        instanceType: Literal[A2A]
        multiVmGroupId: str
        multiVmGroupName: str
        platformFaultDomain: int
        protectionClusterId: str
        recoveryAvailabilitySetId: str
        recoveryAvailabilityZone: str
        recoveryAzureNetworkId: str
        recoveryBootDiagStorageAccountId: str
        recoveryCapacityReservationGroupId: str
        recoveryCloudServiceId: str
        recoveryConfidentialDataDiskEncryptionIdentity: str
        recoveryContainerId: str
        recoveryExtendedLocation: ExtendedLocation
        recoveryProximityPlacementGroupId: str
        recoveryResourceGroupId: str
        recoverySubnetName: str
        recoveryVirtualMachineScaleSetId: str
        vmDisks: list[A2AVmDiskInputDetails]
        vmManagedDisks: list[A2AVmManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2APolicyCreationInput(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "crashConsistentFrequencyInMinutes": int
        key "instanceType": Required[Literal["A2A"]]
        key "multiVmSyncStatus": Required[Union[str, SetMultiVmSyncStatus]]
        key "recoveryPointHistory": int
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        instanceType: Literal[A2A]
        multiVmSyncStatus: Union[str, SetMultiVmSyncStatus]
        recoveryPointHistory: int


    class azure.mgmt.recoveryservicessiterecovery.types.A2AProtectedItemDetail(TypedDict, total=False):
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "recoveryAvailabilitySetId": str
        key "recoveryAvailabilityZone": str
        key "recoveryBootDiagStorageAccountId": str
        key "recoveryCapacityReservationGroupId": str
        key "recoveryProximityPlacementGroupId": str
        key "recoveryResourceGroupId": str
        key "recoveryVirtualMachineScaleSetId": str
        key "replicationProtectedItemName": str
        diskEncryptionInfo: DiskEncryptionInfo
        recoveryAvailabilitySetId: str
        recoveryAvailabilityZone: str
        recoveryBootDiagStorageAccountId: str
        recoveryCapacityReservationGroupId: str
        recoveryProximityPlacementGroupId: str
        recoveryResourceGroupId: str
        recoveryVirtualMachineScaleSetId: str
        replicationProtectedItemName: str
        vmManagedDisks: list[A2AClusterVmManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AProtectedManagedDiskDetails(TypedDict, total=False):
        key "confidentialDiskEncryptionInfo": ForwardRef('ConfidentialDiskEncryptionInfo', module='types')
        key "dataPendingAtSourceAgentInMB": float
        key "dataPendingInStagingStorageAccountInMB": float
        key "dekKeyVaultArmId": str
        key "diskCapacityInBytes": int
        key "diskId": str
        key "diskName": str
        key "diskState": str
        key "diskType": str
        key "failoverDiskName": str
        key "isDiskEncrypted": bool
        key "isDiskKeyEncrypted": bool
        key "kekKeyVaultArmId": str
        key "keyIdentifier": str
        key "monitoringJobType": str
        key "monitoringPercentageCompletion": int
        key "primaryDiskEncryptionSetId": str
        key "primaryStagingAzureStorageAccountId": str
        key "recoveryDiskAccessId": str
        key "recoveryDiskEncryptionSetId": str
        key "recoveryNetworkAccessPolicy": Union[str, DiskNetworkAccessPolicy]
        key "recoveryOrignalTargetDiskId": str
        key "recoveryPublicNetworkAccess": Union[str, DiskPublicNetworkAccess]
        key "recoveryReplicaDiskAccountType": str
        key "recoveryReplicaDiskId": str
        key "recoveryResourceGroupId": str
        key "recoveryTargetDiskAccountType": str
        key "recoveryTargetDiskId": str
        key "resyncRequired": bool
        key "secretIdentifier": str
        key "tfoDiskName": str
        allowedDiskLevelOperation: list[str]
        confidentialDiskEncryptionInfo: ConfidentialDiskEncryptionInfo
        dataPendingAtSourceAgentInMB: float
        dataPendingInStagingStorageAccountInMB: float
        dekKeyVaultArmId: str
        diskCapacityInBytes: int
        diskId: str
        diskName: str
        diskState: str
        diskType: str
        failoverDiskName: str
        isDiskEncrypted: bool
        isDiskKeyEncrypted: bool
        kekKeyVaultArmId: str
        keyIdentifier: str
        monitoringJobType: str
        monitoringPercentageCompletion: int
        primaryDiskEncryptionSetId: str
        primaryStagingAzureStorageAccountId: str
        recoveryDiskAccessId: str
        recoveryDiskEncryptionSetId: str
        recoveryNetworkAccessPolicy: Union[str, DiskNetworkAccessPolicy]
        recoveryOrignalTargetDiskId: str
        recoveryPublicNetworkAccess: Union[str, DiskPublicNetworkAccess]
        recoveryReplicaDiskAccountType: str
        recoveryReplicaDiskId: str
        recoveryResourceGroupId: str
        recoveryTargetDiskAccountType: str
        recoveryTargetDiskId: str
        resyncRequired: bool
        secretIdentifier: str
        tfoDiskName: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AProtectionIntentDiskInputDetails(TypedDict, total=False):
        key "diskUri": Required[str]
        key "primaryStagingStorageAccountCustomInput": ForwardRef('StorageAccountCustomDetails', module='types')
        key "recoveryAzureStorageAccountCustomInput": ForwardRef('StorageAccountCustomDetails', module='types')
        diskUri: str
        primaryStagingStorageAccountCustomInput: StorageAccountCustomDetails
        recoveryAzureStorageAccountCustomInput: StorageAccountCustomDetails


    class azure.mgmt.recoveryservicessiterecovery.types.A2AProtectionIntentManagedDiskInputDetails(TypedDict, total=False):
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "diskId": Required[str]
        key "primaryStagingStorageAccountCustomInput": ForwardRef('StorageAccountCustomDetails', module='types')
        key "recoveryDiskEncryptionSetId": str
        key "recoveryReplicaDiskAccountType": str
        key "recoveryResourceGroupCustomInput": ForwardRef('RecoveryResourceGroupCustomDetails', module='types')
        key "recoveryTargetDiskAccountType": str
        diskEncryptionInfo: DiskEncryptionInfo
        diskId: str
        primaryStagingStorageAccountCustomInput: StorageAccountCustomDetails
        recoveryDiskEncryptionSetId: str
        recoveryReplicaDiskAccountType: str
        recoveryResourceGroupCustomInput: RecoveryResourceGroupCustomDetails
        recoveryTargetDiskAccountType: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2ARemoveDisksInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]
        vmDisksUris: list[str]
        vmManagedDisksIds: list[str]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AReplicationProtectionClusterDetails(TypedDict, total=False):
        key "clusterManagementId": str
        key "failoverRecoveryPointId": str
        key "initialPrimaryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "initialPrimaryFabricLocation": str
        key "initialPrimaryZone": str
        key "initialRecoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "initialRecoveryFabricLocation": str
        key "initialRecoveryZone": str
        key "instanceType": Required[Literal["A2A"]]
        key "lastRpoCalculatedTime": str
        key "lifecycleId": str
        key "multiVmGroupCreateOption": Union[str, MultiVmGroupCreateOption]
        key "multiVmGroupId": str
        key "multiVmGroupName": str
        key "primaryAvailabilityZone": str
        key "primaryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "primaryFabricLocation": str
        key "recoveryAvailabilityZone": str
        key "recoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "recoveryFabricLocation": str
        key "rpoInSeconds": int
        clusterManagementId: str
        failoverRecoveryPointId: str
        initialPrimaryExtendedLocation: ExtendedLocation
        initialPrimaryFabricLocation: str
        initialPrimaryZone: str
        initialRecoveryExtendedLocation: ExtendedLocation
        initialRecoveryFabricLocation: str
        initialRecoveryZone: str
        instanceType: Literal[A2A]
        lastRpoCalculatedTime: str
        lifecycleId: str
        multiVmGroupCreateOption: Union[str, MultiVmGroupCreateOption]
        multiVmGroupId: str
        multiVmGroupName: str
        primaryAvailabilityZone: str
        primaryExtendedLocation: ExtendedLocation
        primaryFabricLocation: str
        recoveryAvailabilityZone: str
        recoveryExtendedLocation: ExtendedLocation
        recoveryFabricLocation: str
        rpoInSeconds: int


    class azure.mgmt.recoveryservicessiterecovery.types.A2AReprotectInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        key "policyId": str
        key "recoveryAvailabilitySetId": str
        key "recoveryCloudServiceId": str
        key "recoveryContainerId": str
        key "recoveryResourceGroupId": str
        instanceType: Literal[A2A]
        policyId: str
        recoveryAvailabilitySetId: str
        recoveryCloudServiceId: str
        recoveryContainerId: str
        recoveryResourceGroupId: str
        vmDisks: list[A2AVmDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ASharedDiskIRErrorDetails(TypedDict, total=False):
        key "errorCode": str
        key "errorCodeEnum": str
        key "errorMessage": str
        key "possibleCauses": str
        key "recommendedAction": str
        errorCode: str
        errorCodeEnum: str
        errorMessage: str
        possibleCauses: str
        recommendedAction: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2ASharedDiskReplicationDetails(TypedDict, total=False):
        key "failoverRecoveryPointId": str
        key "instanceType": Required[Literal["A2A"]]
        key "lastRpoCalculatedTime": str
        key "managementId": str
        key "monitoringJobType": str
        key "monitoringPercentageCompletion": int
        key "primaryFabricLocation": str
        key "recoveryFabricLocation": str
        key "rpoInSeconds": int
        failoverRecoveryPointId: str
        instanceType: Literal[A2A]
        lastRpoCalculatedTime: str
        managementId: str
        monitoringJobType: str
        monitoringPercentageCompletion: int
        primaryFabricLocation: str
        protectedManagedDisks: list[A2AProtectedManagedDiskDetails]
        recoveryFabricLocation: str
        rpoInSeconds: int
        sharedDiskIRErrors: list[A2ASharedDiskIRErrorDetails]
        unprotectedDisks: list[A2AUnprotectedDiskDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ASwitchClusterProtectionInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        key "policyId": str
        key "recoveryContainerId": str
        instanceType: Literal[A2A]
        policyId: str
        protectedItemsDetail: list[A2AProtectedItemDetail]
        recoveryContainerId: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2ASwitchProtectionInput(TypedDict, total=False):
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "instanceType": Required[Literal["A2A"]]
        key "platformFaultDomain": int
        key "policyId": str
        key "recoveryAvailabilitySetId": str
        key "recoveryAvailabilityZone": str
        key "recoveryBootDiagStorageAccountId": str
        key "recoveryCapacityReservationGroupId": str
        key "recoveryCloudServiceId": str
        key "recoveryConfidentialDataDiskEncryptionIdentity": str
        key "recoveryContainerId": str
        key "recoveryProximityPlacementGroupId": str
        key "recoveryResourceGroupId": str
        key "recoveryVirtualMachineScaleSetId": str
        diskEncryptionInfo: DiskEncryptionInfo
        instanceType: Literal[A2A]
        platformFaultDomain: int
        policyId: str
        recoveryAvailabilitySetId: str
        recoveryAvailabilityZone: str
        recoveryBootDiagStorageAccountId: str
        recoveryCapacityReservationGroupId: str
        recoveryCloudServiceId: str
        recoveryConfidentialDataDiskEncryptionIdentity: str
        recoveryContainerId: str
        recoveryProximityPlacementGroupId: str
        recoveryResourceGroupId: str
        recoveryVirtualMachineScaleSetId: str
        vmDisks: list[A2AVmDiskInputDetails]
        vmManagedDisks: list[A2AVmManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.A2ATestFailoverInput(TypedDict, total=False):
        key "cloudServiceCreationOption": str
        key "instanceType": Required[Literal["A2A"]]
        key "recoveryPointId": str
        cloudServiceCreationOption: str
        instanceType: Literal[A2A]
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AUnplannedFailoverInput(TypedDict, total=False):
        key "cloudServiceCreationOption": str
        key "instanceType": Required[Literal["A2A"]]
        key "recoveryPointId": str
        cloudServiceCreationOption: str
        instanceType: Literal[A2A]
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AUnprotectedDiskDetails(TypedDict, total=False):
        key "diskAutoProtectionStatus": Union[str, AutoProtectionOfDataDisk]
        key "diskLunId": int
        diskAutoProtectionStatus: Union[str, AutoProtectionOfDataDisk]
        diskLunId: int


    class azure.mgmt.recoveryservicessiterecovery.types.A2AUpdateContainerMappingInput(TypedDict, total=False):
        key "agentAutoUpdateStatus": Union[str, AgentAutoUpdateStatus]
        key "automationAccountArmId": str
        key "automationAccountAuthenticationType": Union[str, AutomationAccountAuthenticationType]
        key "instanceType": Required[Literal["A2A"]]
        agentAutoUpdateStatus: Union[str, AgentAutoUpdateStatus]
        automationAccountArmId: str
        automationAccountAuthenticationType: Union[str, AutomationAccountAuthenticationType]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.A2AUpdateReplicationProtectedItemInput(TypedDict, total=False):
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "instanceType": Required[Literal["A2A"]]
        key "platformFaultDomain": int
        key "recoveryAvailabilityZone": str
        key "recoveryBootDiagStorageAccountId": str
        key "recoveryCapacityReservationGroupId": str
        key "recoveryCloudServiceId": str
        key "recoveryConfidentialDataDiskEncryptionIdentity": str
        key "recoveryProximityPlacementGroupId": str
        key "recoveryResourceGroupId": str
        key "recoveryVirtualMachineScaleSetId": str
        key "tfoAzureVMName": str
        diskEncryptionInfo: DiskEncryptionInfo
        instanceType: Literal[A2A]
        managedDiskUpdateDetails: list[A2AVmManagedDiskUpdateDetails]
        platformFaultDomain: int
        recoveryAvailabilityZone: str
        recoveryBootDiagStorageAccountId: str
        recoveryCapacityReservationGroupId: str
        recoveryCloudServiceId: str
        recoveryConfidentialDataDiskEncryptionIdentity: str
        recoveryProximityPlacementGroupId: str
        recoveryResourceGroupId: str
        recoveryVirtualMachineScaleSetId: str
        tfoAzureVMName: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AVmDiskInputDetails(TypedDict, total=False):
        key "diskUri": Required[str]
        key "primaryStagingAzureStorageAccountId": Required[str]
        key "recoveryAzureStorageAccountId": Required[str]
        diskUri: str
        primaryStagingAzureStorageAccountId: str
        recoveryAzureStorageAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AVmManagedDiskInputDetails(TypedDict, total=False):
        key "confidentialDiskEncryptionInfo": ForwardRef('ConfidentialDiskEncryptionInfo', module='types')
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "diskId": Required[str]
        key "primaryStagingAzureStorageAccountId": Required[str]
        key "recoveryDiskAccessId": str
        key "recoveryDiskEncryptionSetId": str
        key "recoveryNetworkAccessPolicy": Union[str, DiskNetworkAccessPolicy]
        key "recoveryPublicNetworkAccess": Union[str, DiskPublicNetworkAccess]
        key "recoveryReplicaDiskAccountType": str
        key "recoveryResourceGroupId": Required[str]
        key "recoveryTargetDiskAccountType": str
        confidentialDiskEncryptionInfo: ConfidentialDiskEncryptionInfo
        diskEncryptionInfo: DiskEncryptionInfo
        diskId: str
        primaryStagingAzureStorageAccountId: str
        recoveryDiskAccessId: str
        recoveryDiskEncryptionSetId: str
        recoveryNetworkAccessPolicy: Union[str, DiskNetworkAccessPolicy]
        recoveryPublicNetworkAccess: Union[str, DiskPublicNetworkAccess]
        recoveryReplicaDiskAccountType: str
        recoveryResourceGroupId: str
        recoveryTargetDiskAccountType: str


    class azure.mgmt.recoveryservicessiterecovery.types.A2AVmManagedDiskUpdateDetails(TypedDict, total=False):
        key "confidentialDiskEncryptionInfo": ForwardRef('UpdateConfidentialDiskEncryptionInfo', module='types')
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "diskId": str
        key "failoverDiskName": str
        key "recoveryReplicaDiskAccountType": str
        key "recoveryTargetDiskAccountType": str
        key "tfoDiskName": str
        confidentialDiskEncryptionInfo: UpdateConfidentialDiskEncryptionInfo
        diskEncryptionInfo: DiskEncryptionInfo
        diskId: str
        failoverDiskName: str
        recoveryReplicaDiskAccountType: str
        recoveryTargetDiskAccountType: str
        tfoDiskName: str


    class azure.mgmt.recoveryservicessiterecovery.types.AddDisksInput(TypedDict, total=False):
        key "properties": ForwardRef('AddDisksInputProperties', module='types')
        properties: AddDisksInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.AddDisksInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[AddDisksProviderSpecificInput]
        providerSpecificDetails: AddDisksProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.AddRecoveryServicesProviderInput(TypedDict, total=False):
        key "properties": Required[AddRecoveryServicesProviderInputProperties]
        properties: AddRecoveryServicesProviderInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.AddRecoveryServicesProviderInputProperties(TypedDict, total=False):
        key "authenticationIdentityInput": Required[IdentityProviderInput]
        key "biosId": str
        key "dataPlaneAuthenticationIdentityInput": ForwardRef('IdentityProviderInput', module='types')
        key "machineId": str
        key "machineName": Required[str]
        key "resourceAccessIdentityInput": Required[IdentityProviderInput]
        authenticationIdentityInput: IdentityProviderInput
        biosId: str
        dataPlaneAuthenticationIdentityInput: IdentityProviderInput
        machineId: str
        machineName: str
        resourceAccessIdentityInput: IdentityProviderInput


    class azure.mgmt.recoveryservicessiterecovery.types.AddVCenterRequest(TypedDict, total=False):
        key "properties": ForwardRef('AddVCenterRequestProperties', module='types')
        properties: AddVCenterRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.AddVCenterRequestProperties(TypedDict, total=False):
        key "friendlyName": str
        key "ipAddress": str
        key "port": str
        key "processServerId": str
        key "runAsAccountId": str
        friendlyName: str
        ipAddress: str
        port: str
        processServerId: str
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.ApplyClusterRecoveryPointInput(TypedDict, total=False):
        key "properties": Required[ApplyClusterRecoveryPointInputProperties]
        properties: ApplyClusterRecoveryPointInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ApplyClusterRecoveryPointInputProperties(TypedDict, total=False):
        key "clusterRecoveryPointId": str
        key "providerSpecificDetails": Required[ApplyClusterRecoveryPointProviderSpecificInput]
        clusterRecoveryPointId: str
        individualNodeRecoveryPoints: list[str]
        providerSpecificDetails: ApplyClusterRecoveryPointProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.ApplyClusterRecoveryPointProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.ApplyRecoveryPointInput(TypedDict, total=False):
        key "properties": Required[ApplyRecoveryPointInputProperties]
        properties: ApplyRecoveryPointInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ApplyRecoveryPointInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[ApplyRecoveryPointProviderSpecificInput]
        key "recoveryPointId": str
        providerSpecificDetails: ApplyRecoveryPointProviderSpecificInput
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.AzureFabricCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["Azure"]]
        key "location": str
        instanceType: Literal[Azure]
        location: str


    class azure.mgmt.recoveryservicessiterecovery.types.AzureToAzureCreateNetworkMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["AzureToAzure"]]
        key "primaryNetworkId": Required[str]
        instanceType: Literal[AzureToAzure]
        primaryNetworkId: str


    class azure.mgmt.recoveryservicessiterecovery.types.AzureToAzureUpdateNetworkMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["AzureToAzure"]]
        key "primaryNetworkId": str
        instanceType: Literal[AzureToAzure]
        primaryNetworkId: str


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterTestFailoverCleanupInput(TypedDict, total=False):
        key "properties": Required[ClusterTestFailoverCleanupInputProperties]
        properties: ClusterTestFailoverCleanupInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterTestFailoverCleanupInputProperties(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterTestFailoverInput(TypedDict, total=False):
        key "properties": Required[ClusterTestFailoverInputProperties]
        properties: ClusterTestFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterTestFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": Union[str, FailoverDirection]
        key "networkId": str
        key "networkType": str
        key "providerSpecificDetails": ForwardRef('ClusterTestFailoverProviderSpecificInput', module='types')
        failoverDirection: Union[str, FailoverDirection]
        networkId: str
        networkType: str
        providerSpecificDetails: ClusterTestFailoverProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterTestFailoverProviderSpecificInput(TypedDict, total=False):
        key "clusterRecoveryPointId": str
        key "instanceType": Required[Literal["A2A"]]
        clusterRecoveryPointId: str
        individualNodeRecoveryPoints: list[str]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterUnplannedFailoverInput(TypedDict, total=False):
        key "properties": Required[ClusterUnplannedFailoverInputProperties]
        properties: ClusterUnplannedFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterUnplannedFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": str
        key "providerSpecificDetails": ForwardRef('ClusterUnplannedFailoverProviderSpecificInput', module='types')
        key "sourceSiteOperations": str
        failoverDirection: str
        providerSpecificDetails: ClusterUnplannedFailoverProviderSpecificInput
        sourceSiteOperations: str


    class azure.mgmt.recoveryservicessiterecovery.types.ClusterUnplannedFailoverProviderSpecificInput(TypedDict, total=False):
        key "clusterRecoveryPointId": str
        key "instanceType": Required[Literal["A2A"]]
        clusterRecoveryPointId: str
        individualNodeRecoveryPoints: list[str]
        instanceType: Literal[A2A]


    class azure.mgmt.recoveryservicessiterecovery.types.ConfidentialDiskEncryptionInfo(TypedDict, total=False):
        key "recoveryReplicaConfidentialDiskEncryptionSetId": str
        key "recoveryTargetConfidentialDiskEncryptionSetId": str
        recoveryReplicaConfidentialDiskEncryptionSetId: str
        recoveryTargetConfidentialDiskEncryptionSetId: str


    class azure.mgmt.recoveryservicessiterecovery.types.ConfigureAlertRequest(TypedDict, total=False):
        key "properties": ForwardRef('ConfigureAlertRequestProperties', module='types')
        properties: ConfigureAlertRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ConfigureAlertRequestProperties(TypedDict, total=False):
        key "locale": str
        key "sendToOwners": str
        customEmailAddresses: list[str]
        locale: str
        sendToOwners: str


    class azure.mgmt.recoveryservicessiterecovery.types.CreateNetworkMappingInput(TypedDict, total=False):
        key "properties": Required[CreateNetworkMappingInputProperties]
        properties: CreateNetworkMappingInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.CreateNetworkMappingInputProperties(TypedDict, total=False):
        key "fabricSpecificDetails": ForwardRef('FabricSpecificCreateNetworkMappingInput', module='types')
        key "recoveryFabricName": str
        key "recoveryNetworkId": Required[str]
        fabricSpecificDetails: FabricSpecificCreateNetworkMappingInput
        recoveryFabricName: str
        recoveryNetworkId: str


    class azure.mgmt.recoveryservicessiterecovery.types.CreatePolicyInput(TypedDict, total=False):
        key "properties": ForwardRef('CreatePolicyInputProperties', module='types')
        properties: CreatePolicyInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.CreatePolicyInputProperties(TypedDict, total=False):
        key "providerSpecificInput": ForwardRef('PolicyProviderSpecificInput', module='types')
        providerSpecificInput: PolicyProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionContainerInput(TypedDict, total=False):
        key "properties": ForwardRef('CreateProtectionContainerInputProperties', module='types')
        properties: CreateProtectionContainerInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionContainerInputProperties(TypedDict, total=False):
        providerSpecificInput: list[ReplicationProviderSpecificContainerCreationInput]


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionContainerMappingInput(TypedDict, total=False):
        key "properties": ForwardRef('CreateProtectionContainerMappingInputProperties', module='types')
        properties: CreateProtectionContainerMappingInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionContainerMappingInputProperties(TypedDict, total=False):
        key "policyId": str
        key "providerSpecificInput": ForwardRef('ReplicationProviderSpecificContainerMappingInput', module='types')
        key "targetProtectionContainerId": str
        policyId: str
        providerSpecificInput: ReplicationProviderSpecificContainerMappingInput
        targetProtectionContainerId: str


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionIntentInput(TypedDict, total=False):
        key "properties": ForwardRef('CreateProtectionIntentProperties', module='types')
        properties: CreateProtectionIntentProperties


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionIntentProperties(TypedDict, total=False):
        key "providerSpecificDetails": ForwardRef('CreateProtectionIntentProviderSpecificDetails', module='types')
        providerSpecificDetails: CreateProtectionIntentProviderSpecificDetails


    class azure.mgmt.recoveryservicessiterecovery.types.CreateProtectionIntentProviderSpecificDetails(TypedDict, total=False):
        key "agentAutoUpdateStatus": Union[str, AgentAutoUpdateStatus]
        key "autoProtectionOfDataDisk": Union[str, AutoProtectionOfDataDisk]
        key "automationAccountArmId": str
        key "automationAccountAuthenticationType": Union[str, AutomationAccountAuthenticationType]
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "fabricObjectId": Required[str]
        key "instanceType": Required[Literal["A2A"]]
        key "multiVmGroupId": str
        key "multiVmGroupName": str
        key "primaryLocation": Required[str]
        key "primaryStagingStorageAccountCustomInput": ForwardRef('StorageAccountCustomDetails', module='types')
        key "protectionProfileCustomInput": ForwardRef('ProtectionProfileCustomDetails', module='types')
        key "recoveryAvailabilitySetCustomInput": ForwardRef('RecoveryAvailabilitySetCustomDetails', module='types')
        key "recoveryAvailabilityType": Required[Union[str, A2ARecoveryAvailabilityType]]
        key "recoveryAvailabilityZone": str
        key "recoveryBootDiagStorageAccount": ForwardRef('StorageAccountCustomDetails', module='types')
        key "recoveryLocation": Required[str]
        key "recoveryProximityPlacementGroupCustomInput": ForwardRef('RecoveryProximityPlacementGroupCustomDetails', module='types')
        key "recoveryResourceGroupId": Required[str]
        key "recoverySubscriptionId": Required[str]
        key "recoveryVirtualNetworkCustomInput": ForwardRef('RecoveryVirtualNetworkCustomDetails', module='types')
        agentAutoUpdateStatus: Union[str, AgentAutoUpdateStatus]
        autoProtectionOfDataDisk: Union[str, AutoProtectionOfDataDisk]
        automationAccountArmId: str
        automationAccountAuthenticationType: Union[str, AutomationAccountAuthenticationType]
        diskEncryptionInfo: DiskEncryptionInfo
        fabricObjectId: str
        instanceType: Literal[A2A]
        multiVmGroupId: str
        multiVmGroupName: str
        primaryLocation: str
        primaryStagingStorageAccountCustomInput: StorageAccountCustomDetails
        protectionProfileCustomInput: ProtectionProfileCustomDetails
        recoveryAvailabilitySetCustomInput: RecoveryAvailabilitySetCustomDetails
        recoveryAvailabilityType: Union[str, A2ARecoveryAvailabilityType]
        recoveryAvailabilityZone: str
        recoveryBootDiagStorageAccount: StorageAccountCustomDetails
        recoveryLocation: str
        recoveryProximityPlacementGroupCustomInput: RecoveryProximityPlacementGroupCustomDetails
        recoveryResourceGroupId: str
        recoverySubscriptionId: str
        recoveryVirtualNetworkCustomInput: RecoveryVirtualNetworkCustomDetails
        vmDisks: list[A2AProtectionIntentDiskInputDetails]
        vmManagedDisks: list[A2AProtectionIntentManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.CreateRecoveryPlanInput(TypedDict, total=False):
        key "properties": Required[CreateRecoveryPlanInputProperties]
        properties: CreateRecoveryPlanInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.CreateRecoveryPlanInputProperties(TypedDict, total=False):
        key "failoverDeploymentModel": Union[str, FailoverDeploymentModel]
        key "groups": Required[list[RecoveryPlanGroup]]
        key "primaryFabricId": Required[str]
        key "recoveryFabricId": Required[str]
        failoverDeploymentModel: Union[str, FailoverDeploymentModel]
        groups: list[RecoveryPlanGroup]
        primaryFabricId: str
        providerSpecificInput: list[RecoveryPlanProviderSpecificInput]
        recoveryFabricId: str


    class azure.mgmt.recoveryservicessiterecovery.types.CurrentScenarioDetails(TypedDict, total=False):
        key "jobId": str
        key "scenarioName": str
        key "startTime": str
        jobId: str
        scenarioName: str
        startTime: str


    class azure.mgmt.recoveryservicessiterecovery.types.DisableProtectionInput(TypedDict, total=False):
        key "properties": Required[DisableProtectionInputProperties]
        properties: DisableProtectionInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.DisableProtectionInputProperties(TypedDict, total=False):
        key "disableProtectionReason": Union[str, DisableProtectionReason]
        key "replicationProviderInput": ForwardRef('DisableProtectionProviderSpecificInput', module='types')
        disableProtectionReason: Union[str, DisableProtectionReason]
        replicationProviderInput: DisableProtectionProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.DisableProtectionProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMage"]]
        key "replicaVmDeletionStatus": str
        instanceType: Literal[InMage]
        replicaVmDeletionStatus: str


    class azure.mgmt.recoveryservicessiterecovery.types.DiscoverProtectableItemRequest(TypedDict, total=False):
        key "properties": ForwardRef('DiscoverProtectableItemRequestProperties', module='types')
        properties: DiscoverProtectableItemRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.DiscoverProtectableItemRequestProperties(TypedDict, total=False):
        key "friendlyName": str
        key "ipAddress": str
        key "osType": str
        friendlyName: str
        ipAddress: str
        osType: str


    class azure.mgmt.recoveryservicessiterecovery.types.DiskEncryptionInfo(TypedDict, total=False):
        key "diskEncryptionKeyInfo": ForwardRef('DiskEncryptionKeyInfo', module='types')
        key "keyEncryptionKeyInfo": ForwardRef('KeyEncryptionKeyInfo', module='types')
        diskEncryptionKeyInfo: DiskEncryptionKeyInfo
        keyEncryptionKeyInfo: KeyEncryptionKeyInfo


    class azure.mgmt.recoveryservicessiterecovery.types.DiskEncryptionKeyInfo(TypedDict, total=False):
        key "keyVaultResourceArmId": str
        key "secretIdentifier": str
        keyVaultResourceArmId: str
        secretIdentifier: str


    class azure.mgmt.recoveryservicessiterecovery.types.EnableMigrationInput(TypedDict, total=False):
        key "properties": Required[EnableMigrationInputProperties]
        properties: EnableMigrationInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.EnableMigrationInputProperties(TypedDict, total=False):
        key "policyId": Required[str]
        key "providerSpecificDetails": Required[EnableMigrationProviderSpecificInput]
        policyId: str
        providerSpecificDetails: EnableMigrationProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.EnableMigrationProviderSpecificInput(TypedDict, total=False):
        key "confidentialVmKeyVaultId": str
        key "dataMoverRunAsAccountId": Required[str]
        key "disksToInclude": Required[list[VMwareCbtDiskInput]]
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "performAutoResync": str
        key "performSqlBulkRegistration": str
        key "snapshotRunAsAccountId": Required[str]
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetBootDiagnosticsStorageAccountId": str
        key "targetCapacityReservationGroupId": str
        key "targetNetworkId": Required[str]
        key "targetProximityPlacementGroupId": str
        key "targetResourceGroupId": Required[str]
        key "targetSubnetName": str
        key "targetVmName": str
        key "targetVmSecurityProfile": ForwardRef('VMwareCbtSecurityProfileProperties', module='types')
        key "targetVmSize": str
        key "testNetworkId": str
        key "testSubnetName": str
        key "userSelectedOSName": str
        key "vmwareMachineId": Required[str]
        confidentialVmKeyVaultId: str
        dataMoverRunAsAccountId: str
        disksToInclude: list[VMwareCbtDiskInput]
        instanceType: Literal[VMwareCbt]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        performAutoResync: str
        performSqlBulkRegistration: str
        seedDiskTags: dict[str, str]
        snapshotRunAsAccountId: str
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetBootDiagnosticsStorageAccountId: str
        targetCapacityReservationGroupId: str
        targetDiskTags: dict[str, str]
        targetNetworkId: str
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetResourceGroupId: str
        targetSubnetName: str
        targetVmName: str
        targetVmSecurityProfile: VMwareCbtSecurityProfileProperties
        targetVmSize: str
        targetVmTags: dict[str, str]
        testNetworkId: str
        testSubnetName: str
        userSelectedOSName: str
        vmwareMachineId: str


    class azure.mgmt.recoveryservicessiterecovery.types.EnableProtectionInput(TypedDict, total=False):
        key "properties": ForwardRef('EnableProtectionInputProperties', module='types')
        properties: EnableProtectionInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.EnableProtectionInputProperties(TypedDict, total=False):
        key "policyId": str
        key "protectableItemId": str
        key "providerSpecificDetails": ForwardRef('EnableProtectionProviderSpecificInput', module='types')
        policyId: str
        protectableItemId: str
        providerSpecificDetails: EnableProtectionProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.ExistingProtectionProfile(TypedDict, total=False):
        key "protectionProfileId": Required[str]
        key "resourceType": Required[Literal["Existing"]]
        protectionProfileId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.ExistingRecoveryAvailabilitySet(TypedDict, total=False):
        key "recoveryAvailabilitySetId": str
        key "resourceType": Required[Literal["Existing"]]
        recoveryAvailabilitySetId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.ExistingRecoveryProximityPlacementGroup(TypedDict, total=False):
        key "recoveryProximityPlacementGroupId": str
        key "resourceType": Required[Literal["Existing"]]
        recoveryProximityPlacementGroupId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.ExistingRecoveryResourceGroup(TypedDict, total=False):
        key "recoveryResourceGroupId": str
        key "resourceType": Required[Literal["Existing"]]
        recoveryResourceGroupId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.ExistingRecoveryVirtualNetwork(TypedDict, total=False):
        key "recoverySubnetName": str
        key "recoveryVirtualNetworkId": Required[str]
        key "resourceType": Required[Literal["Existing"]]
        recoverySubnetName: str
        recoveryVirtualNetworkId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.ExistingStorageAccount(TypedDict, total=False):
        key "azureStorageAccountId": Required[str]
        key "resourceType": Required[Literal["Existing"]]
        azureStorageAccountId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.ExtendedLocation(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ExtendedLocationType]]
        name: str
        type: Union[str, ExtendedLocationType]


    class azure.mgmt.recoveryservicessiterecovery.types.FabricCreationInput(TypedDict, total=False):
        key "properties": ForwardRef('FabricCreationInputProperties', module='types')
        properties: FabricCreationInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.FabricCreationInputProperties(TypedDict, total=False):
        key "customDetails": ForwardRef('FabricSpecificCreationInput', module='types')
        customDetails: FabricSpecificCreationInput


    class azure.mgmt.recoveryservicessiterecovery.types.FailoverProcessServerRequest(TypedDict, total=False):
        key "properties": ForwardRef('FailoverProcessServerRequestProperties', module='types')
        properties: FailoverProcessServerRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.FailoverProcessServerRequestProperties(TypedDict, total=False):
        key "containerName": str
        key "sourceProcessServerId": str
        key "targetProcessServerId": str
        key "updateType": str
        containerName: str
        sourceProcessServerId: str
        targetProcessServerId: str
        updateType: str
        vmsToMigrate: list[str]


    class azure.mgmt.recoveryservicessiterecovery.types.HealthError(TypedDict, total=False):
        key "creationTimeUtc": str
        key "customerResolvability": Union[str, HealthErrorCustomerResolvability]
        key "entityId": str
        key "errorCategory": str
        key "errorCode": str
        key "errorId": str
        key "errorLevel": str
        key "errorMessage": str
        key "errorSource": str
        key "errorType": str
        key "possibleCauses": str
        key "recommendedAction": str
        key "recoveryProviderErrorMessage": str
        key "summaryMessage": str
        creationTimeUtc: str
        customerResolvability: Union[str, HealthErrorCustomerResolvability]
        entityId: str
        errorCategory: str
        errorCode: str
        errorId: str
        errorLevel: str
        errorMessage: str
        errorSource: str
        errorType: str
        innerHealthErrors: list[InnerHealthError]
        possibleCauses: str
        recommendedAction: str
        recoveryProviderErrorMessage: str
        summaryMessage: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureApplyRecoveryPointInput(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "primaryKekCertificatePfx": str
        key "secondaryKekCertificatePfx": str
        instanceType: Literal[HyperVReplicaAzure]
        primaryKekCertificatePfx: str
        secondaryKekCertificatePfx: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureDiskInputDetails(TypedDict, total=False):
        key "diskEncryptionSetId": str
        key "diskId": str
        key "diskSizeInGB": int
        key "diskType": Union[str, DiskAccountType]
        key "iops": int
        key "logStorageAccountId": str
        key "sectorSizeInBytes": int
        key "throughputInMbps": int
        diskEncryptionSetId: str
        diskId: str
        diskSizeInGB: int
        diskType: Union[str, DiskAccountType]
        iops: int
        logStorageAccountId: str
        sectorSizeInBytes: int
        throughputInMbps: int


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureEnableProtectionInput(TypedDict, total=False):
        key "diskEncryptionSetId": str
        key "diskType": Union[str, DiskAccountType]
        key "enableRdpOnTargetOption": str
        key "hvHostVmId": str
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "logStorageAccountId": str
        key "osType": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetAzureNetworkId": str
        key "targetAzureSubnetId": str
        key "targetAzureV1ResourceGroupId": str
        key "targetAzureV2ResourceGroupId": str
        key "targetAzureVmName": str
        key "targetCapacityReservationGroupId": str
        key "targetProximityPlacementGroupId": str
        key "targetStorageAccountId": str
        key "targetVmSecurityProfile": ForwardRef('SecurityProfileProperties', module='types')
        key "targetVmSize": str
        key "useManagedDisks": str
        key "useManagedDisksForReplication": str
        key "userSelectedOSName": str
        key "vhdId": str
        key "vmName": str
        diskEncryptionSetId: str
        diskType: Union[str, DiskAccountType]
        disksToInclude: list[str]
        disksToIncludeForManagedDisks: list[HyperVReplicaAzureDiskInputDetails]
        enableRdpOnTargetOption: str
        hvHostVmId: str
        instanceType: Literal[HyperVReplicaAzure]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        logStorageAccountId: str
        osType: str
        seedManagedDiskTags: dict[str, str]
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetAzureNetworkId: str
        targetAzureSubnetId: str
        targetAzureV1ResourceGroupId: str
        targetAzureV2ResourceGroupId: str
        targetAzureVmName: str
        targetCapacityReservationGroupId: str
        targetManagedDiskTags: dict[str, str]
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetStorageAccountId: str
        targetVmSecurityProfile: SecurityProfileProperties
        targetVmSize: str
        targetVmTags: dict[str, str]
        useManagedDisks: str
        useManagedDisksForReplication: str
        userSelectedOSName: str
        vhdId: str
        vmName: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureFailbackProviderInput(TypedDict, total=False):
        key "dataSyncOption": str
        key "instanceType": Required[Literal["HyperVReplicaAzureFailback"]]
        key "providerIdForAlternateRecovery": str
        key "recoveryVmCreationOption": str
        dataSyncOption: str
        instanceType: Literal[HyperVReplicaAzureFailback]
        providerIdForAlternateRecovery: str
        recoveryVmCreationOption: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzurePlannedFailoverProviderInput(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "osUpgradeVersion": str
        key "primaryKekCertificatePfx": str
        key "recoveryPointId": str
        key "secondaryKekCertificatePfx": str
        key "targetCapacityReservationGroupId": str
        instanceType: Literal[HyperVReplicaAzure]
        osUpgradeVersion: str
        primaryKekCertificatePfx: str
        recoveryPointId: str
        secondaryKekCertificatePfx: str
        targetCapacityReservationGroupId: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzurePolicyInput(TypedDict, total=False):
        key "applicationConsistentSnapshotFrequencyInHours": int
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "onlineReplicationStartTime": str
        key "recoveryPointHistoryDuration": int
        key "replicationInterval": int
        applicationConsistentSnapshotFrequencyInHours: int
        instanceType: Literal[HyperVReplicaAzure]
        onlineReplicationStartTime: str
        recoveryPointHistoryDuration: int
        replicationInterval: int
        storageAccounts: list[str]


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureReprotectInput(TypedDict, total=False):
        key "hvHostVmId": str
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "logStorageAccountId": str
        key "osType": str
        key "storageAccountId": str
        key "vHDId": str
        key "vmName": str
        hvHostVmId: str
        instanceType: Literal[HyperVReplicaAzure]
        logStorageAccountId: str
        osType: str
        storageAccountId: str
        vHDId: str
        vmName: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureTestFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "osUpgradeVersion": str
        key "primaryKekCertificatePfx": str
        key "recoveryPointId": str
        key "secondaryKekCertificatePfx": str
        instanceType: Literal[HyperVReplicaAzure]
        osUpgradeVersion: str
        primaryKekCertificatePfx: str
        recoveryPointId: str
        secondaryKekCertificatePfx: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureUnplannedFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "primaryKekCertificatePfx": str
        key "recoveryPointId": str
        key "secondaryKekCertificatePfx": str
        instanceType: Literal[HyperVReplicaAzure]
        primaryKekCertificatePfx: str
        recoveryPointId: str
        secondaryKekCertificatePfx: str


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaAzureUpdateReplicationProtectedItemInput(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "recoveryAzureV1ResourceGroupId": str
        key "recoveryAzureV2ResourceGroupId": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilityZone": str
        key "targetCapacityReservationGroupId": str
        key "targetProximityPlacementGroupId": str
        key "useManagedDisks": str
        key "userSelectedOSName": str
        diskIdToDiskEncryptionMap: dict[str, str]
        instanceType: Literal[HyperVReplicaAzure]
        linuxLicenseType: Union[str, LinuxLicenseType]
        recoveryAzureV1ResourceGroupId: str
        recoveryAzureV2ResourceGroupId: str
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilityZone: str
        targetCapacityReservationGroupId: str
        targetManagedDiskTags: dict[str, str]
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetVmTags: dict[str, str]
        useManagedDisks: str
        userSelectedOSName: str
        vmDisks: list[UpdateDiskInput]


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaBluePolicyInput(TypedDict, total=False):
        key "allowedAuthenticationType": int
        key "applicationConsistentSnapshotFrequencyInHours": int
        key "compression": str
        key "initialReplicationMethod": str
        key "instanceType": Required[Literal["HyperVReplica2012R2"]]
        key "offlineReplicationExportPath": str
        key "offlineReplicationImportPath": str
        key "onlineReplicationStartTime": str
        key "recoveryPoints": int
        key "replicaDeletion": str
        key "replicationFrequencyInSeconds": int
        key "replicationPort": int
        allowedAuthenticationType: int
        applicationConsistentSnapshotFrequencyInHours: int
        compression: str
        initialReplicationMethod: str
        instanceType: Literal[HyperVReplica2012R2]
        offlineReplicationExportPath: str
        offlineReplicationImportPath: str
        onlineReplicationStartTime: str
        recoveryPoints: int
        replicaDeletion: str
        replicationFrequencyInSeconds: int
        replicationPort: int


    class azure.mgmt.recoveryservicessiterecovery.types.HyperVReplicaPolicyInput(TypedDict, total=False):
        key "allowedAuthenticationType": int
        key "applicationConsistentSnapshotFrequencyInHours": int
        key "compression": str
        key "initialReplicationMethod": str
        key "instanceType": Required[Literal["HyperVReplica2012R2"]]
        key "offlineReplicationExportPath": str
        key "offlineReplicationImportPath": str
        key "onlineReplicationStartTime": str
        key "recoveryPoints": int
        key "replicaDeletion": str
        key "replicationFrequencyInSeconds": int
        key "replicationPort": int
        allowedAuthenticationType: int
        applicationConsistentSnapshotFrequencyInHours: int
        compression: str
        initialReplicationMethod: str
        instanceType: Literal[HyperVReplica2012R2]
        offlineReplicationExportPath: str
        offlineReplicationImportPath: str
        onlineReplicationStartTime: str
        recoveryPoints: int
        replicaDeletion: str
        replicationFrequencyInSeconds: int
        replicationPort: int


    class azure.mgmt.recoveryservicessiterecovery.types.IPConfigInputDetails(TypedDict, total=False):
        key "ipConfigName": str
        key "isPrimary": bool
        key "isSeletedForFailover": bool
        key "recoveryPublicIPAddressId": str
        key "recoveryStaticIPAddress": str
        key "recoverySubnetName": str
        key "tfoPublicIPAddressId": str
        key "tfoStaticIPAddress": str
        key "tfoSubnetName": str
        ipConfigName: str
        isPrimary: bool
        isSeletedForFailover: bool
        recoveryLBBackendAddressPoolIds: list[str]
        recoveryPublicIPAddressId: str
        recoveryStaticIPAddress: str
        recoverySubnetName: str
        tfoLBBackendAddressPoolIds: list[str]
        tfoPublicIPAddressId: str
        tfoStaticIPAddress: str
        tfoSubnetName: str


    class azure.mgmt.recoveryservicessiterecovery.types.IdentityProviderInput(TypedDict, total=False):
        key "aadAuthority": Required[str]
        key "applicationId": Required[str]
        key "audience": Required[str]
        key "objectId": Required[str]
        key "tenantId": Required[str]
        aadAuthority: str
        applicationId: str
        audience: str
        objectId: str
        tenantId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2ApplyRecoveryPointInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        instanceType: Literal[InMageAzureV2]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2DiskInputDetails(TypedDict, total=False):
        key "diskEncryptionSetId": str
        key "diskId": str
        key "diskType": Union[str, DiskAccountType]
        key "logStorageAccountId": str
        diskEncryptionSetId: str
        diskId: str
        diskType: Union[str, DiskAccountType]
        logStorageAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2EnableProtectionInput(TypedDict, total=False):
        key "diskEncryptionSetId": str
        key "diskType": Union[str, DiskAccountType]
        key "enableRdpOnTargetOption": str
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "licenseType": Union[str, LicenseType]
        key "logStorageAccountId": str
        key "masterTargetId": str
        key "multiVmGroupId": str
        key "multiVmGroupName": str
        key "processServerId": str
        key "runAsAccountId": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "storageAccountId": str
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetAzureNetworkId": str
        key "targetAzureSubnetId": str
        key "targetAzureV1ResourceGroupId": str
        key "targetAzureV2ResourceGroupId": str
        key "targetAzureVmName": str
        key "targetProximityPlacementGroupId": str
        key "targetVmSize": str
        diskEncryptionSetId: str
        diskType: Union[str, DiskAccountType]
        disksToInclude: list[InMageAzureV2DiskInputDetails]
        enableRdpOnTargetOption: str
        instanceType: Literal[InMageAzureV2]
        licenseType: Union[str, LicenseType]
        logStorageAccountId: str
        masterTargetId: str
        multiVmGroupId: str
        multiVmGroupName: str
        processServerId: str
        runAsAccountId: str
        seedManagedDiskTags: dict[str, str]
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        storageAccountId: str
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetAzureNetworkId: str
        targetAzureSubnetId: str
        targetAzureV1ResourceGroupId: str
        targetAzureV2ResourceGroupId: str
        targetAzureVmName: str
        targetManagedDiskTags: dict[str, str]
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetVmSize: str
        targetVmTags: dict[str, str]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2PolicyInput(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "crashConsistentFrequencyInMinutes": int
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "multiVmSyncStatus": Required[Union[str, SetMultiVmSyncStatus]]
        key "recoveryPointHistory": int
        key "recoveryPointThresholdInMinutes": int
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        instanceType: Literal[InMageAzureV2]
        multiVmSyncStatus: Union[str, SetMultiVmSyncStatus]
        recoveryPointHistory: int
        recoveryPointThresholdInMinutes: int


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2ReprotectInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "logStorageAccountId": str
        key "masterTargetId": str
        key "policyId": str
        key "processServerId": str
        key "runAsAccountId": str
        key "storageAccountId": str
        disksToInclude: list[str]
        instanceType: Literal[InMageAzureV2]
        logStorageAccountId: str
        masterTargetId: str
        policyId: str
        processServerId: str
        runAsAccountId: str
        storageAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2SwitchProviderInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "targetApplianceID": Required[str]
        key "targetFabricID": Required[str]
        key "targetVaultID": Required[str]
        instanceType: Literal[InMageAzureV2]
        targetApplianceID: str
        targetFabricID: str
        targetVaultID: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2TestFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "osUpgradeVersion": str
        key "recoveryPointId": str
        instanceType: Literal[InMageAzureV2]
        osUpgradeVersion: str
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2UnplannedFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "osUpgradeVersion": str
        key "recoveryPointId": str
        instanceType: Literal[InMageAzureV2]
        osUpgradeVersion: str
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageAzureV2UpdateReplicationProtectedItemInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "recoveryAzureV1ResourceGroupId": str
        key "recoveryAzureV2ResourceGroupId": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilityZone": str
        key "targetProximityPlacementGroupId": str
        key "useManagedDisks": str
        instanceType: Literal[InMageAzureV2]
        recoveryAzureV1ResourceGroupId: str
        recoveryAzureV2ResourceGroupId: str
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilityZone: str
        targetManagedDiskTags: dict[str, str]
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetVmTags: dict[str, str]
        useManagedDisks: str
        vmDisks: list[UpdateDiskInput]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageDisableProtectionProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMage"]]
        key "replicaVmDeletionStatus": str
        instanceType: Literal[InMage]
        replicaVmDeletionStatus: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageDiskExclusionInput(TypedDict, total=False):
        diskSignatureOptions: list[InMageDiskSignatureExclusionOptions]
        volumeOptions: list[InMageVolumeExclusionOptions]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageDiskSignatureExclusionOptions(TypedDict, total=False):
        key "diskSignature": str
        diskSignature: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageEnableProtectionInput(TypedDict, total=False):
        key "datastoreName": str
        key "diskExclusionInput": ForwardRef('InMageDiskExclusionInput', module='types')
        key "instanceType": Required[Literal["InMage"]]
        key "masterTargetId": Required[str]
        key "multiVmGroupId": Required[str]
        key "multiVmGroupName": Required[str]
        key "processServerId": Required[str]
        key "retentionDrive": Required[str]
        key "runAsAccountId": str
        key "vmFriendlyName": str
        datastoreName: str
        diskExclusionInput: InMageDiskExclusionInput
        disksToInclude: list[str]
        instanceType: Literal[InMage]
        masterTargetId: str
        multiVmGroupId: str
        multiVmGroupName: str
        processServerId: str
        retentionDrive: str
        runAsAccountId: str
        vmFriendlyName: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMagePolicyInput(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "instanceType": Required[Literal["InMage"]]
        key "multiVmSyncStatus": Required[Union[str, SetMultiVmSyncStatus]]
        key "recoveryPointHistory": int
        key "recoveryPointThresholdInMinutes": int
        appConsistentFrequencyInMinutes: int
        instanceType: Literal[InMage]
        multiVmSyncStatus: Union[str, SetMultiVmSyncStatus]
        recoveryPointHistory: int
        recoveryPointThresholdInMinutes: int


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmAddDisksInput(TypedDict, total=False):
        key "disks": Required[list[InMageRcmDiskInput]]
        key "instanceType": Required[Literal["InMageRcm"]]
        disks: list[InMageRcmDiskInput]
        instanceType: Literal[InMageRcm]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmApplyRecoveryPointInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "recoveryPointId": Required[str]
        instanceType: Literal[InMageRcm]
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmDiskInput(TypedDict, total=False):
        key "confidentialDiskEncryptionSetId": str
        key "diskEncryptionSetId": str
        key "diskId": Required[str]
        key "diskSizeInGB": int
        key "diskType": Required[Union[str, DiskAccountType]]
        key "iops": int
        key "logStorageAccountId": Required[str]
        key "sectorSizeInBytes": int
        key "throughputInMbps": int
        confidentialDiskEncryptionSetId: str
        diskEncryptionSetId: str
        diskId: str
        diskSizeInGB: int
        diskType: Union[str, DiskAccountType]
        iops: int
        logStorageAccountId: str
        sectorSizeInBytes: int
        throughputInMbps: int


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmDisksDefaultInput(TypedDict, total=False):
        key "confidentialDiskEncryptionSetId": str
        key "diskEncryptionSetId": str
        key "diskSizeInGB": int
        key "diskType": Required[Union[str, DiskAccountType]]
        key "iops": int
        key "logStorageAccountId": Required[str]
        key "sectorSizeInBytes": int
        key "throughputInMbps": int
        confidentialDiskEncryptionSetId: str
        diskEncryptionSetId: str
        diskSizeInGB: int
        diskType: Union[str, DiskAccountType]
        iops: int
        logStorageAccountId: str
        sectorSizeInBytes: int
        throughputInMbps: int


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmEnableProtectionInput(TypedDict, total=False):
        key "disksDefault": ForwardRef('InMageRcmDisksDefaultInput', module='types')
        key "fabricDiscoveryMachineId": Required[str]
        key "instanceType": Required[Literal["InMageRcm"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "multiVmGroupName": str
        key "processServerId": Required[str]
        key "runAsAccountId": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetBootDiagnosticsStorageAccountId": str
        key "targetCapacityReservationGroupId": str
        key "targetExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "targetNetworkId": str
        key "targetProximityPlacementGroupId": str
        key "targetResourceGroupId": Required[str]
        key "targetSubnetName": str
        key "targetVmName": str
        key "targetVmSecurityProfile": ForwardRef('SecurityProfileProperties', module='types')
        key "targetVmSize": str
        key "testNetworkId": str
        key "testSubnetName": str
        key "userSelectedOSName": str
        disksDefault: InMageRcmDisksDefaultInput
        disksToInclude: list[InMageRcmDiskInput]
        fabricDiscoveryMachineId: str
        instanceType: Literal[InMageRcm]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        multiVmGroupName: str
        processServerId: str
        runAsAccountId: str
        seedManagedDiskTags: list[UserCreatedResourceTag]
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetBootDiagnosticsStorageAccountId: str
        targetCapacityReservationGroupId: str
        targetExtendedLocation: ExtendedLocation
        targetManagedDiskTags: list[UserCreatedResourceTag]
        targetNetworkId: str
        targetNicTags: list[UserCreatedResourceTag]
        targetProximityPlacementGroupId: str
        targetResourceGroupId: str
        targetSubnetName: str
        targetVmName: str
        targetVmSecurityProfile: SecurityProfileProperties
        targetVmSize: str
        targetVmTags: list[UserCreatedResourceTag]
        testNetworkId: str
        testSubnetName: str
        userSelectedOSName: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmFabricCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "physicalSiteId": Required[str]
        key "sourceAgentIdentity": Required[IdentityProviderInput]
        key "vmwareSiteId": Required[str]
        instanceType: Literal[InMageRcm]
        physicalSiteId: str
        sourceAgentIdentity: IdentityProviderInput
        vmwareSiteId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmFailbackPlannedFailoverProviderInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcmFailback"]]
        key "recoveryPointType": Required[Union[str, InMageRcmFailbackRecoveryPointType]]
        instanceType: Literal[InMageRcmFailback]
        recoveryPointType: Union[str, InMageRcmFailbackRecoveryPointType]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmFailbackPolicyCreationInput(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "crashConsistentFrequencyInMinutes": int
        key "instanceType": Required[Literal["InMageRcmFailback"]]
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        instanceType: Literal[InMageRcmFailback]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmFailbackReprotectInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcmFailback"]]
        key "policyId": Required[str]
        key "processServerId": Required[str]
        key "runAsAccountId": str
        instanceType: Literal[InMageRcmFailback]
        policyId: str
        processServerId: str
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmNicInput(TypedDict, total=False):
        key "isPrimaryNic": Required[str]
        key "isSelectedForFailover": str
        key "nicId": Required[str]
        key "targetNicName": str
        key "targetStaticIPAddress": str
        key "targetSubnetName": str
        key "testStaticIPAddress": str
        key "testSubnetName": str
        isPrimaryNic: str
        isSelectedForFailover: str
        nicId: str
        targetNicName: str
        targetStaticIPAddress: str
        targetSubnetName: str
        testStaticIPAddress: str
        testSubnetName: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmPolicyCreationInput(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "crashConsistentFrequencyInMinutes": int
        key "enableMultiVmSync": str
        key "instanceType": Required[Literal["InMageRcm"]]
        key "recoveryPointHistoryInMinutes": int
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        enableMultiVmSync: str
        instanceType: Literal[InMageRcm]
        recoveryPointHistoryInMinutes: int


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmReprotectInput(TypedDict, total=False):
        key "datastoreName": Required[str]
        key "instanceType": Required[Literal["InMageRcm"]]
        key "logStorageAccountId": Required[str]
        key "policyId": str
        key "reprotectAgentId": Required[str]
        datastoreName: str
        instanceType: Literal[InMageRcm]
        logStorageAccountId: str
        policyId: str
        reprotectAgentId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmTestFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "networkId": str
        key "osUpgradeVersion": str
        key "recoveryPointId": str
        instanceType: Literal[InMageRcm]
        networkId: str
        osUpgradeVersion: str
        recoveryPointId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmUnplannedFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "osUpgradeVersion": str
        key "performShutdown": Required[str]
        key "recoveryPointId": str
        key "targetCapacityReservationGroupId": str
        instanceType: Literal[InMageRcm]
        osUpgradeVersion: str
        performShutdown: str
        recoveryPointId: str
        targetCapacityReservationGroupId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmUpdateApplianceForReplicationProtectedItemInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "runAsAccountId": str
        instanceType: Literal[InMageRcm]
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmUpdateContainerMappingInput(TypedDict, total=False):
        key "enableAgentAutoUpgrade": Required[str]
        key "instanceType": Required[Literal["InMageRcm"]]
        enableAgentAutoUpgrade: str
        instanceType: Literal[InMageRcm]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageRcmUpdateReplicationProtectedItemInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetBootDiagnosticsStorageAccountId": str
        key "targetCapacityReservationGroupId": str
        key "targetNetworkId": str
        key "targetProximityPlacementGroupId": str
        key "targetResourceGroupId": str
        key "targetVmName": str
        key "targetVmSize": str
        key "testNetworkId": str
        key "userSelectedOSName": str
        instanceType: Literal[InMageRcm]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetBootDiagnosticsStorageAccountId: str
        targetCapacityReservationGroupId: str
        targetManagedDiskTags: list[UserCreatedResourceTag]
        targetNetworkId: str
        targetNicTags: list[UserCreatedResourceTag]
        targetProximityPlacementGroupId: str
        targetResourceGroupId: str
        targetVmName: str
        targetVmSize: str
        targetVmTags: list[UserCreatedResourceTag]
        testNetworkId: str
        userSelectedOSName: str
        vmDisks: list[UpdateDiskInput]
        vmNics: list[InMageRcmNicInput]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageReprotectInput(TypedDict, total=False):
        key "datastoreName": str
        key "diskExclusionInput": ForwardRef('InMageDiskExclusionInput', module='types')
        key "instanceType": Required[Literal["InMage"]]
        key "masterTargetId": Required[str]
        key "processServerId": Required[str]
        key "profileId": Required[str]
        key "retentionDrive": Required[str]
        key "runAsAccountId": str
        datastoreName: str
        diskExclusionInput: InMageDiskExclusionInput
        disksToInclude: list[str]
        instanceType: Literal[InMage]
        masterTargetId: str
        processServerId: str
        profileId: str
        retentionDrive: str
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.InMageTestFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMage"]]
        key "recoveryPointId": str
        key "recoveryPointType": Union[str, RecoveryPointType]
        instanceType: Literal[InMage]
        recoveryPointId: str
        recoveryPointType: Union[str, RecoveryPointType]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageUnplannedFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMage"]]
        key "recoveryPointId": str
        key "recoveryPointType": Union[str, RecoveryPointType]
        instanceType: Literal[InMage]
        recoveryPointId: str
        recoveryPointType: Union[str, RecoveryPointType]


    class azure.mgmt.recoveryservicessiterecovery.types.InMageVolumeExclusionOptions(TypedDict, total=False):
        key "onlyExcludeIfSingleVolume": str
        key "volumeLabel": str
        onlyExcludeIfSingleVolume: str
        volumeLabel: str


    class azure.mgmt.recoveryservicessiterecovery.types.InnerHealthError(TypedDict, total=False):
        key "creationTimeUtc": str
        key "customerResolvability": Union[str, HealthErrorCustomerResolvability]
        key "entityId": str
        key "errorCategory": str
        key "errorCode": str
        key "errorId": str
        key "errorLevel": str
        key "errorMessage": str
        key "errorSource": str
        key "errorType": str
        key "possibleCauses": str
        key "recommendedAction": str
        key "recoveryProviderErrorMessage": str
        key "summaryMessage": str
        creationTimeUtc: str
        customerResolvability: Union[str, HealthErrorCustomerResolvability]
        entityId: str
        errorCategory: str
        errorCode: str
        errorId: str
        errorLevel: str
        errorMessage: str
        errorSource: str
        errorType: str
        possibleCauses: str
        recommendedAction: str
        recoveryProviderErrorMessage: str
        summaryMessage: str


    class azure.mgmt.recoveryservicessiterecovery.types.JobQueryParameter(TypedDict, total=False):
        key "affectedObjectTypes": str
        key "endTime": str
        key "fabricId": str
        key "jobName": str
        key "jobOutputType": Union[str, ExportJobOutputSerializationType]
        key "jobStatus": str
        key "startTime": str
        key "timezoneOffset": float
        affectedObjectTypes: str
        endTime: str
        fabricId: str
        jobName: str
        jobOutputType: Union[str, ExportJobOutputSerializationType]
        jobStatus: str
        startTime: str
        timezoneOffset: float


    class azure.mgmt.recoveryservicessiterecovery.types.KeyEncryptionKeyInfo(TypedDict, total=False):
        key "keyIdentifier": str
        key "keyVaultResourceArmId": str
        keyIdentifier: str
        keyVaultResourceArmId: str


    class azure.mgmt.recoveryservicessiterecovery.types.ManagedRunCommandScriptInput(TypedDict, total=False):
        key "scriptParameters": Required[str]
        key "scriptUrl": Required[str]
        key "stepName": Required[str]
        scriptParameters: str
        scriptUrl: str
        stepName: str


    class azure.mgmt.recoveryservicessiterecovery.types.MigrateInput(TypedDict, total=False):
        key "properties": Required[MigrateInputProperties]
        properties: MigrateInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.MigrateInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[MigrateProviderSpecificInput]
        providerSpecificDetails: MigrateProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.MigrateProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "osUpgradeVersion": str
        key "performShutdown": Required[str]
        key "targetCapacityReservationGroupId": str
        instanceType: Literal[VMwareCbt]
        osUpgradeVersion: str
        performShutdown: str
        postMigrationSteps: list[ManagedRunCommandScriptInput]
        targetCapacityReservationGroupId: str


    class azure.mgmt.recoveryservicessiterecovery.types.NewProtectionProfile(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "crashConsistentFrequencyInMinutes": int
        key "multiVmSyncStatus": Required[Union[str, SetMultiVmSyncStatus]]
        key "policyName": Required[str]
        key "recoveryPointHistory": int
        key "resourceType": Required[Literal["New"]]
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        multiVmSyncStatus: Union[str, SetMultiVmSyncStatus]
        policyName: str
        recoveryPointHistory: int
        resourceType: Literal[New]


    class azure.mgmt.recoveryservicessiterecovery.types.NewRecoveryVirtualNetwork(TypedDict, total=False):
        key "recoveryVirtualNetworkName": str
        key "recoveryVirtualNetworkResourceGroupName": str
        key "resourceType": Required[Literal["New"]]
        recoveryVirtualNetworkName: str
        recoveryVirtualNetworkResourceGroupName: str
        resourceType: Literal[New]


    class azure.mgmt.recoveryservicessiterecovery.types.PauseReplicationInput(TypedDict, total=False):
        key "properties": Required[PauseReplicationInputProperties]
        properties: PauseReplicationInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.PauseReplicationInputProperties(TypedDict, total=False):
        key "instanceType": Required[str]
        instanceType: str


    class azure.mgmt.recoveryservicessiterecovery.types.PlannedFailoverInput(TypedDict, total=False):
        key "properties": ForwardRef('PlannedFailoverInputProperties', module='types')
        properties: PlannedFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.PlannedFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": str
        key "providerSpecificDetails": ForwardRef('PlannedFailoverProviderSpecificFailoverInput', module='types')
        failoverDirection: str
        providerSpecificDetails: PlannedFailoverProviderSpecificFailoverInput


    class azure.mgmt.recoveryservicessiterecovery.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryAvailabilitySetCustomDetails(TypedDict, total=False):
        key "recoveryAvailabilitySetId": str
        key "resourceType": Required[Literal["Existing"]]
        recoveryAvailabilitySetId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanA2AFailoverInput(TypedDict, total=False):
        key "cloudServiceCreationOption": str
        key "instanceType": Required[Literal["A2A"]]
        key "multiVmSyncPointOption": Union[str, MultiVmSyncPointOption]
        key "recoveryPointType": Required[Union[str, A2ARpRecoveryPointType]]
        cloudServiceCreationOption: str
        instanceType: Literal[A2A]
        multiVmSyncPointOption: Union[str, MultiVmSyncPointOption]
        recoveryPointType: Union[str, A2ARpRecoveryPointType]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanA2AInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        key "primaryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "primaryZone": str
        key "recoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "recoveryZone": str
        instanceType: Literal[A2A]
        primaryExtendedLocation: ExtendedLocation
        primaryZone: str
        recoveryExtendedLocation: ExtendedLocation
        recoveryZone: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanAction(TypedDict, total=False):
        key "actionName": Required[str]
        key "customDetails": Required[RecoveryPlanActionDetails]
        key "failoverDirections": Required[list[Union[str, PossibleOperationsDirections]]]
        key "failoverTypes": Required[list[Union[str, ReplicationProtectedItemOperation]]]
        actionName: str
        customDetails: RecoveryPlanActionDetails
        failoverDirections: list[Union[str, PossibleOperationsDirections]]
        failoverTypes: list[Union[str, ReplicationProtectedItemOperation]]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanAutomationRunbookActionDetails(TypedDict, total=False):
        key "fabricLocation": Required[Union[str, RecoveryPlanActionLocation]]
        key "instanceType": Required[Literal["AutomationRunbookActionDetails"]]
        key "runbookId": str
        key "timeout": str
        fabricLocation: Union[str, RecoveryPlanActionLocation]
        instanceType: Literal[AutomationRunbookActionDetails]
        runbookId: str
        timeout: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanGroup(TypedDict, total=False):
        key "groupType": Required[Union[str, RecoveryPlanGroupType]]
        endGroupActions: list[RecoveryPlanAction]
        groupType: Union[str, RecoveryPlanGroupType]
        replicationProtectedItems: list[RecoveryPlanProtectedItem]
        startGroupActions: list[RecoveryPlanAction]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanHyperVReplicaAzureFailbackInput(TypedDict, total=False):
        key "dataSyncOption": Required[Union[str, DataSyncStatus]]
        key "instanceType": Required[Literal["HyperVReplicaAzureFailback"]]
        key "recoveryVmCreationOption": Required[Union[str, AlternateLocationRecoveryOption]]
        dataSyncOption: Union[str, DataSyncStatus]
        instanceType: Literal[HyperVReplicaAzureFailback]
        recoveryVmCreationOption: Union[str, AlternateLocationRecoveryOption]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanHyperVReplicaAzureFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVReplicaAzure"]]
        key "primaryKekCertificatePfx": str
        key "recoveryPointType": Union[str, HyperVReplicaAzureRpRecoveryPointType]
        key "secondaryKekCertificatePfx": str
        instanceType: Literal[HyperVReplicaAzure]
        primaryKekCertificatePfx: str
        recoveryPointType: Union[str, HyperVReplicaAzureRpRecoveryPointType]
        secondaryKekCertificatePfx: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanInMageAzureV2FailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "recoveryPointType": Required[Union[str, InMageV2RpRecoveryPointType]]
        key "useMultiVmSyncPoint": str
        instanceType: Literal[InMageAzureV2]
        recoveryPointType: Union[str, InMageV2RpRecoveryPointType]
        useMultiVmSyncPoint: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanInMageFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMage"]]
        key "recoveryPointType": Required[Union[str, RpInMageRecoveryPointType]]
        instanceType: Literal[InMage]
        recoveryPointType: Union[str, RpInMageRecoveryPointType]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanInMageRcmFailbackFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcmFailback"]]
        key "recoveryPointType": Required[Union[str, InMageRcmFailbackRecoveryPointType]]
        key "useMultiVmSyncPoint": str
        instanceType: Literal[InMageRcmFailback]
        recoveryPointType: Union[str, InMageRcmFailbackRecoveryPointType]
        useMultiVmSyncPoint: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanInMageRcmFailoverInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "recoveryPointType": Required[Union[str, RecoveryPlanPointType]]
        key "useMultiVmSyncPoint": str
        instanceType: Literal[InMageRcm]
        recoveryPointType: Union[str, RecoveryPlanPointType]
        useMultiVmSyncPoint: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanManualActionDetails(TypedDict, total=False):
        key "description": str
        key "instanceType": Required[Literal["ManualActionDetails"]]
        description: str
        instanceType: Literal[ManualActionDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanPlannedFailoverInput(TypedDict, total=False):
        key "properties": Required[RecoveryPlanPlannedFailoverInputProperties]
        properties: RecoveryPlanPlannedFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanPlannedFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": Required[Union[str, PossibleOperationsDirections]]
        failoverDirection: Union[str, PossibleOperationsDirections]
        providerSpecificDetails: list[RecoveryPlanProviderSpecificFailoverInput]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanProtectedItem(TypedDict, total=False):
        key "id": str
        key "virtualMachineId": str
        id: str
        virtualMachineId: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        key "primaryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "primaryZone": str
        key "recoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "recoveryZone": str
        instanceType: Literal[A2A]
        primaryExtendedLocation: ExtendedLocation
        primaryZone: str
        recoveryExtendedLocation: ExtendedLocation
        recoveryZone: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanScriptActionDetails(TypedDict, total=False):
        key "fabricLocation": Required[Union[str, RecoveryPlanActionLocation]]
        key "instanceType": Required[Literal["ScriptActionDetails"]]
        key "path": Required[str]
        key "timeout": str
        fabricLocation: Union[str, RecoveryPlanActionLocation]
        instanceType: Literal[ScriptActionDetails]
        path: str
        timeout: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanTestFailoverCleanupInput(TypedDict, total=False):
        key "properties": Required[RecoveryPlanTestFailoverCleanupInputProperties]
        properties: RecoveryPlanTestFailoverCleanupInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanTestFailoverCleanupInputProperties(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanTestFailoverInput(TypedDict, total=False):
        key "properties": Required[RecoveryPlanTestFailoverInputProperties]
        properties: RecoveryPlanTestFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanTestFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": Required[Union[str, PossibleOperationsDirections]]
        key "networkId": str
        key "networkType": Required[str]
        failoverDirection: Union[str, PossibleOperationsDirections]
        networkId: str
        networkType: str
        providerSpecificDetails: list[RecoveryPlanProviderSpecificFailoverInput]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanUnplannedFailoverInput(TypedDict, total=False):
        key "properties": Required[RecoveryPlanUnplannedFailoverInputProperties]
        properties: RecoveryPlanUnplannedFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryPlanUnplannedFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": Required[Union[str, PossibleOperationsDirections]]
        key "sourceSiteOperations": Required[Union[str, SourceSiteOperations]]
        failoverDirection: Union[str, PossibleOperationsDirections]
        providerSpecificDetails: list[RecoveryPlanProviderSpecificFailoverInput]
        sourceSiteOperations: Union[str, SourceSiteOperations]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryProximityPlacementGroupCustomDetails(TypedDict, total=False):
        key "recoveryProximityPlacementGroupId": str
        key "resourceType": Required[Literal["Existing"]]
        recoveryProximityPlacementGroupId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.RecoveryResourceGroupCustomDetails(TypedDict, total=False):
        key "recoveryResourceGroupId": str
        key "resourceType": Required[Literal["Existing"]]
        recoveryResourceGroupId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.RegisteredClusterNodes(TypedDict, total=False):
        key "biosId": str
        key "clusterNodeFqdn": str
        key "isSharedDiskVirtualNode": bool
        key "machineId": str
        biosId: str
        clusterNodeFqdn: str
        isSharedDiskVirtualNode: bool
        machineId: str


    class azure.mgmt.recoveryservicessiterecovery.types.ReinstallMobilityServiceRequest(TypedDict, total=False):
        key "properties": ForwardRef('ReinstallMobilityServiceRequestProperties', module='types')
        properties: ReinstallMobilityServiceRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ReinstallMobilityServiceRequestProperties(TypedDict, total=False):
        key "runAsAccountId": str
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.RemoveDisksInput(TypedDict, total=False):
        key "properties": ForwardRef('RemoveDisksInputProperties', module='types')
        properties: RemoveDisksInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RemoveDisksInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": ForwardRef('RemoveDisksProviderSpecificInput', module='types')
        providerSpecificDetails: RemoveDisksProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.RemoveDisksProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        instanceType: Literal[A2A]
        vmDisksUris: list[str]
        vmManagedDisksIds: list[str]


    class azure.mgmt.recoveryservicessiterecovery.types.RemoveProtectionContainerMappingInput(TypedDict, total=False):
        key "properties": ForwardRef('RemoveProtectionContainerMappingInputProperties', module='types')
        properties: RemoveProtectionContainerMappingInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RemoveProtectionContainerMappingInputProperties(TypedDict, total=False):
        key "providerSpecificInput": ForwardRef('ReplicationProviderContainerUnmappingInput', module='types')
        providerSpecificInput: ReplicationProviderContainerUnmappingInput


    class azure.mgmt.recoveryservicessiterecovery.types.RenewCertificateInput(TypedDict, total=False):
        key "properties": ForwardRef('RenewCertificateInputProperties', module='types')
        properties: RenewCertificateInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.RenewCertificateInputProperties(TypedDict, total=False):
        key "renewCertificateType": str
        renewCertificateType: str


    class azure.mgmt.recoveryservicessiterecovery.types.ReplicationClusterProviderSpecificSettings(TypedDict, total=False):
        key "clusterManagementId": str
        key "failoverRecoveryPointId": str
        key "initialPrimaryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "initialPrimaryFabricLocation": str
        key "initialPrimaryZone": str
        key "initialRecoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "initialRecoveryFabricLocation": str
        key "initialRecoveryZone": str
        key "instanceType": Required[Literal["A2A"]]
        key "lastRpoCalculatedTime": str
        key "lifecycleId": str
        key "multiVmGroupCreateOption": Union[str, MultiVmGroupCreateOption]
        key "multiVmGroupId": str
        key "multiVmGroupName": str
        key "primaryAvailabilityZone": str
        key "primaryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "primaryFabricLocation": str
        key "recoveryAvailabilityZone": str
        key "recoveryExtendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "recoveryFabricLocation": str
        key "rpoInSeconds": int
        clusterManagementId: str
        failoverRecoveryPointId: str
        initialPrimaryExtendedLocation: ExtendedLocation
        initialPrimaryFabricLocation: str
        initialPrimaryZone: str
        initialRecoveryExtendedLocation: ExtendedLocation
        initialRecoveryFabricLocation: str
        initialRecoveryZone: str
        instanceType: Literal[A2A]
        lastRpoCalculatedTime: str
        lifecycleId: str
        multiVmGroupCreateOption: Union[str, MultiVmGroupCreateOption]
        multiVmGroupId: str
        multiVmGroupName: str
        primaryAvailabilityZone: str
        primaryExtendedLocation: ExtendedLocation
        primaryFabricLocation: str
        recoveryAvailabilityZone: str
        recoveryExtendedLocation: ExtendedLocation
        recoveryFabricLocation: str
        rpoInSeconds: int


    class azure.mgmt.recoveryservicessiterecovery.types.ReplicationProtectionCluster(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ReplicationProtectionClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ReplicationProtectionClusterProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicessiterecovery.types.ReplicationProtectionClusterProperties(TypedDict, total=False):
        key "activeLocation": str
        key "agentClusterId": str
        key "areAllClusterNodesRegistered": bool
        key "clusterFqdn": str
        key "currentScenario": ForwardRef('CurrentScenarioDetails', module='types')
        key "lastSuccessfulFailoverTime": str
        key "lastSuccessfulTestFailoverTime": str
        key "policyFriendlyName": str
        key "policyId": str
        key "primaryFabricFriendlyName": str
        key "primaryFabricProvider": str
        key "primaryProtectionContainerFriendlyName": str
        key "protectionClusterType": str
        key "protectionState": str
        key "protectionStateDescription": str
        key "providerSpecificDetails": ForwardRef('ReplicationClusterProviderSpecificSettings', module='types')
        key "provisioningState": str
        key "recoveryContainerId": str
        key "recoveryFabricFriendlyName": str
        key "recoveryFabricId": str
        key "recoveryProtectionContainerFriendlyName": str
        key "replicationHealth": str
        key "sharedDiskProperties": ForwardRef('SharedDiskReplicationItemProperties', module='types')
        key "testFailoverState": str
        key "testFailoverStateDescription": str
        activeLocation: str
        agentClusterId: str
        allowedOperations: list[str]
        areAllClusterNodesRegistered: bool
        clusterFqdn: str
        clusterNodeFqdns: list[str]
        clusterProtectedItemIds: list[str]
        clusterRegisteredNodes: list[RegisteredClusterNodes]
        currentScenario: CurrentScenarioDetails
        healthErrors: list[HealthError]
        lastSuccessfulFailoverTime: str
        lastSuccessfulTestFailoverTime: str
        policyFriendlyName: str
        policyId: str
        primaryFabricFriendlyName: str
        primaryFabricProvider: str
        primaryProtectionContainerFriendlyName: str
        protectionClusterType: str
        protectionState: str
        protectionStateDescription: str
        providerSpecificDetails: ReplicationClusterProviderSpecificSettings
        provisioningState: str
        recoveryContainerId: str
        recoveryFabricFriendlyName: str
        recoveryFabricId: str
        recoveryProtectionContainerFriendlyName: str
        replicationHealth: str
        sharedDiskProperties: SharedDiskReplicationItemProperties
        testFailoverState: str
        testFailoverStateDescription: str


    class azure.mgmt.recoveryservicessiterecovery.types.ReplicationProviderContainerUnmappingInput(TypedDict, total=False):
        key "instanceType": str
        instanceType: str


    class azure.mgmt.recoveryservicessiterecovery.types.ResolveHealthError(TypedDict, total=False):
        key "healthErrorId": str
        healthErrorId: str


    class azure.mgmt.recoveryservicessiterecovery.types.ResolveHealthInput(TypedDict, total=False):
        key "properties": ForwardRef('ResolveHealthInputProperties', module='types')
        properties: ResolveHealthInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ResolveHealthInputProperties(TypedDict, total=False):
        healthErrors: list[ResolveHealthError]


    class azure.mgmt.recoveryservicessiterecovery.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicessiterecovery.types.ResumeJobParams(TypedDict, total=False):
        key "properties": ForwardRef('ResumeJobParamsProperties', module='types')
        properties: ResumeJobParamsProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ResumeJobParamsProperties(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.recoveryservicessiterecovery.types.ResumeReplicationInput(TypedDict, total=False):
        key "properties": Required[ResumeReplicationInputProperties]
        properties: ResumeReplicationInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ResumeReplicationInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[ResumeReplicationProviderSpecificInput]
        providerSpecificDetails: ResumeReplicationProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.ResumeReplicationProviderSpecificInput(TypedDict, total=False):
        key "deleteMigrationResources": str
        key "instanceType": Required[Literal["VMwareCbt"]]
        deleteMigrationResources: str
        instanceType: Literal[VMwareCbt]


    class azure.mgmt.recoveryservicessiterecovery.types.ResyncInput(TypedDict, total=False):
        key "properties": Required[ResyncInputProperties]
        properties: ResyncInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ResyncInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[ResyncProviderSpecificInput]
        providerSpecificDetails: ResyncProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.ResyncProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "skipCbtReset": Required[str]
        instanceType: Literal[VMwareCbt]
        skipCbtReset: str


    class azure.mgmt.recoveryservicessiterecovery.types.ReverseReplicationInput(TypedDict, total=False):
        key "properties": ForwardRef('ReverseReplicationInputProperties', module='types')
        properties: ReverseReplicationInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.ReverseReplicationInputProperties(TypedDict, total=False):
        key "failoverDirection": str
        key "providerSpecificDetails": ForwardRef('ReverseReplicationProviderSpecificInput', module='types')
        failoverDirection: str
        providerSpecificDetails: ReverseReplicationProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.SecurityProfileProperties(TypedDict, total=False):
        key "targetVmConfidentialEncryption": Union[str, SecurityConfiguration]
        key "targetVmMonitoring": Union[str, SecurityConfiguration]
        key "targetVmSecureBoot": Union[str, SecurityConfiguration]
        key "targetVmSecurityType": Union[str, SecurityType]
        key "targetVmTpm": Union[str, SecurityConfiguration]
        targetVmConfidentialEncryption: Union[str, SecurityConfiguration]
        targetVmMonitoring: Union[str, SecurityConfiguration]
        targetVmSecureBoot: Union[str, SecurityConfiguration]
        targetVmSecurityType: Union[str, SecurityType]
        targetVmTpm: Union[str, SecurityConfiguration]


    class azure.mgmt.recoveryservicessiterecovery.types.SharedDiskReplicationItemProperties(TypedDict, total=False):
        key "activeLocation": str
        key "currentScenario": ForwardRef('CurrentScenarioDetails', module='types')
        key "protectionState": str
        key "replicationHealth": str
        key "sharedDiskProviderSpecificDetails": ForwardRef('SharedDiskReplicationProviderSpecificSettings', module='types')
        key "testFailoverState": str
        activeLocation: str
        allowedOperations: list[str]
        currentScenario: CurrentScenarioDetails
        healthErrors: list[HealthError]
        protectionState: str
        replicationHealth: str
        sharedDiskProviderSpecificDetails: SharedDiskReplicationProviderSpecificSettings
        testFailoverState: str


    class azure.mgmt.recoveryservicessiterecovery.types.SharedDiskReplicationProviderSpecificSettings(TypedDict, total=False):
        key "failoverRecoveryPointId": str
        key "instanceType": Required[Literal["A2A"]]
        key "lastRpoCalculatedTime": str
        key "managementId": str
        key "monitoringJobType": str
        key "monitoringPercentageCompletion": int
        key "primaryFabricLocation": str
        key "recoveryFabricLocation": str
        key "rpoInSeconds": int
        failoverRecoveryPointId: str
        instanceType: Literal[A2A]
        lastRpoCalculatedTime: str
        managementId: str
        monitoringJobType: str
        monitoringPercentageCompletion: int
        primaryFabricLocation: str
        protectedManagedDisks: list[A2AProtectedManagedDiskDetails]
        recoveryFabricLocation: str
        rpoInSeconds: int
        sharedDiskIRErrors: list[A2ASharedDiskIRErrorDetails]
        unprotectedDisks: list[A2AUnprotectedDiskDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.StorageAccountCustomDetails(TypedDict, total=False):
        key "azureStorageAccountId": Required[str]
        key "resourceType": Required[Literal["Existing"]]
        azureStorageAccountId: str
        resourceType: Literal[Existing]


    class azure.mgmt.recoveryservicessiterecovery.types.StorageClassificationMappingInput(TypedDict, total=False):
        key "properties": ForwardRef('StorageMappingInputProperties', module='types')
        properties: StorageMappingInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.StorageMappingInputProperties(TypedDict, total=False):
        key "targetStorageClassificationId": str
        targetStorageClassificationId: str


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchClusterProtectionInput(TypedDict, total=False):
        key "properties": ForwardRef('SwitchClusterProtectionInputProperties', module='types')
        properties: SwitchClusterProtectionInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchClusterProtectionInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": ForwardRef('SwitchClusterProtectionProviderSpecificInput', module='types')
        key "replicationProtectionClusterName": str
        providerSpecificDetails: SwitchClusterProtectionProviderSpecificInput
        replicationProtectionClusterName: str


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchClusterProtectionProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["A2A"]]
        key "policyId": str
        key "recoveryContainerId": str
        instanceType: Literal[A2A]
        policyId: str
        protectedItemsDetail: list[A2AProtectedItemDetail]
        recoveryContainerId: str


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchProtectionInput(TypedDict, total=False):
        key "properties": ForwardRef('SwitchProtectionInputProperties', module='types')
        properties: SwitchProtectionInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchProtectionInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": ForwardRef('SwitchProtectionProviderSpecificInput', module='types')
        key "replicationProtectedItemName": str
        providerSpecificDetails: SwitchProtectionProviderSpecificInput
        replicationProtectedItemName: str


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchProtectionProviderSpecificInput(TypedDict, total=False):
        key "diskEncryptionInfo": ForwardRef('DiskEncryptionInfo', module='types')
        key "instanceType": Required[Literal["A2A"]]
        key "platformFaultDomain": int
        key "policyId": str
        key "recoveryAvailabilitySetId": str
        key "recoveryAvailabilityZone": str
        key "recoveryBootDiagStorageAccountId": str
        key "recoveryCapacityReservationGroupId": str
        key "recoveryCloudServiceId": str
        key "recoveryConfidentialDataDiskEncryptionIdentity": str
        key "recoveryContainerId": str
        key "recoveryProximityPlacementGroupId": str
        key "recoveryResourceGroupId": str
        key "recoveryVirtualMachineScaleSetId": str
        diskEncryptionInfo: DiskEncryptionInfo
        instanceType: Literal[A2A]
        platformFaultDomain: int
        policyId: str
        recoveryAvailabilitySetId: str
        recoveryAvailabilityZone: str
        recoveryBootDiagStorageAccountId: str
        recoveryCapacityReservationGroupId: str
        recoveryCloudServiceId: str
        recoveryConfidentialDataDiskEncryptionIdentity: str
        recoveryContainerId: str
        recoveryProximityPlacementGroupId: str
        recoveryResourceGroupId: str
        recoveryVirtualMachineScaleSetId: str
        vmDisks: list[A2AVmDiskInputDetails]
        vmManagedDisks: list[A2AVmManagedDiskInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchProviderInput(TypedDict, total=False):
        key "properties": ForwardRef('SwitchProviderInputProperties', module='types')
        properties: SwitchProviderInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchProviderInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": ForwardRef('SwitchProviderSpecificInput', module='types')
        key "targetInstanceType": str
        providerSpecificDetails: SwitchProviderSpecificInput
        targetInstanceType: str


    class azure.mgmt.recoveryservicessiterecovery.types.SwitchProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageAzureV2"]]
        key "targetApplianceID": Required[str]
        key "targetFabricID": Required[str]
        key "targetVaultID": Required[str]
        instanceType: Literal[InMageAzureV2]
        targetApplianceID: str
        targetFabricID: str
        targetVaultID: str


    class azure.mgmt.recoveryservicessiterecovery.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.recoveryservicessiterecovery.types.TestFailoverCleanupInput(TypedDict, total=False):
        key "properties": Required[TestFailoverCleanupInputProperties]
        properties: TestFailoverCleanupInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.TestFailoverCleanupInputProperties(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.recoveryservicessiterecovery.types.TestFailoverInput(TypedDict, total=False):
        key "properties": Required[TestFailoverInputProperties]
        properties: TestFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.TestFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": str
        key "networkId": str
        key "networkType": str
        key "providerSpecificDetails": ForwardRef('TestFailoverProviderSpecificInput', module='types')
        failoverDirection: str
        networkId: str
        networkType: str
        providerSpecificDetails: TestFailoverProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.TestMigrateCleanupInput(TypedDict, total=False):
        key "properties": Required[TestMigrateCleanupInputProperties]
        properties: TestMigrateCleanupInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.TestMigrateCleanupInputProperties(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.recoveryservicessiterecovery.types.TestMigrateInput(TypedDict, total=False):
        key "properties": Required[TestMigrateInputProperties]
        properties: TestMigrateInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.TestMigrateInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[TestMigrateProviderSpecificInput]
        providerSpecificDetails: TestMigrateProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.TestMigrateProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "networkId": Required[str]
        key "osUpgradeVersion": str
        key "recoveryPointId": Required[str]
        instanceType: Literal[VMwareCbt]
        networkId: str
        osUpgradeVersion: str
        postMigrationSteps: list[ManagedRunCommandScriptInput]
        recoveryPointId: str
        vmNics: list[VMwareCbtNicInput]


    class azure.mgmt.recoveryservicessiterecovery.types.UnplannedFailoverInput(TypedDict, total=False):
        key "properties": Required[UnplannedFailoverInputProperties]
        properties: UnplannedFailoverInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UnplannedFailoverInputProperties(TypedDict, total=False):
        key "failoverDirection": str
        key "providerSpecificDetails": ForwardRef('UnplannedFailoverProviderSpecificInput', module='types')
        key "sourceSiteOperations": str
        failoverDirection: str
        providerSpecificDetails: UnplannedFailoverProviderSpecificInput
        sourceSiteOperations: str


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateApplianceForReplicationProtectedItemInput(TypedDict, total=False):
        key "properties": Required[UpdateApplianceForReplicationProtectedItemInputProperties]
        properties: UpdateApplianceForReplicationProtectedItemInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateApplianceForReplicationProtectedItemInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[UpdateApplianceForReplicationProtectedItemProviderSpecificInput]
        key "targetApplianceId": Required[str]
        providerSpecificDetails: UpdateApplianceForReplicationProtectedItemProviderSpecificInput
        targetApplianceId: str


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateApplianceForReplicationProtectedItemProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["InMageRcm"]]
        key "runAsAccountId": str
        instanceType: Literal[InMageRcm]
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateConfidentialDiskEncryptionInfo(TypedDict, total=False):
        key "recoveryTargetConfidentialDiskEncryptionSetId": str
        recoveryTargetConfidentialDiskEncryptionSetId: str


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateDiskInput(TypedDict, total=False):
        key "diskId": Required[str]
        key "diskSizeInGB": int
        key "iops": int
        key "targetDiskName": str
        key "throughputInMbps": int
        diskId: str
        diskSizeInGB: int
        iops: int
        targetDiskName: str
        throughputInMbps: int


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateMigrationItemInput(TypedDict, total=False):
        key "properties": ForwardRef('UpdateMigrationItemInputProperties', module='types')
        properties: UpdateMigrationItemInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateMigrationItemInputProperties(TypedDict, total=False):
        key "providerSpecificDetails": Required[UpdateMigrationItemProviderSpecificInput]
        providerSpecificDetails: UpdateMigrationItemProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateMigrationItemProviderSpecificInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "performAutoResync": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetBootDiagnosticsStorageAccountId": str
        key "targetCapacityReservationGroupId": str
        key "targetNetworkId": str
        key "targetProximityPlacementGroupId": str
        key "targetResourceGroupId": str
        key "targetVmName": str
        key "targetVmSize": str
        key "testNetworkId": str
        key "userSelectedOSName": str
        instanceType: Literal[VMwareCbt]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        performAutoResync: str
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetBootDiagnosticsStorageAccountId: str
        targetCapacityReservationGroupId: str
        targetDiskTags: dict[str, str]
        targetNetworkId: str
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetResourceGroupId: str
        targetVmName: str
        targetVmSize: str
        targetVmTags: dict[str, str]
        testNetworkId: str
        userSelectedOSName: str
        vmDisks: list[VMwareCbtUpdateDiskInput]
        vmNics: list[VMwareCbtNicInput]


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateMobilityServiceRequest(TypedDict, total=False):
        key "properties": ForwardRef('UpdateMobilityServiceRequestProperties', module='types')
        properties: UpdateMobilityServiceRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateMobilityServiceRequestProperties(TypedDict, total=False):
        key "runAsAccountId": str
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateNetworkMappingInput(TypedDict, total=False):
        key "properties": ForwardRef('UpdateNetworkMappingInputProperties', module='types')
        properties: UpdateNetworkMappingInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateNetworkMappingInputProperties(TypedDict, total=False):
        key "fabricSpecificDetails": ForwardRef('FabricSpecificUpdateNetworkMappingInput', module='types')
        key "recoveryFabricName": str
        key "recoveryNetworkId": str
        fabricSpecificDetails: FabricSpecificUpdateNetworkMappingInput
        recoveryFabricName: str
        recoveryNetworkId: str


    class azure.mgmt.recoveryservicessiterecovery.types.UpdatePolicyInput(TypedDict, total=False):
        key "properties": ForwardRef('UpdatePolicyInputProperties', module='types')
        properties: UpdatePolicyInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdatePolicyInputProperties(TypedDict, total=False):
        key "replicationProviderSettings": ForwardRef('PolicyProviderSpecificInput', module='types')
        replicationProviderSettings: PolicyProviderSpecificInput


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateProtectionContainerMappingInput(TypedDict, total=False):
        key "properties": ForwardRef('UpdateProtectionContainerMappingInputProperties', module='types')
        properties: UpdateProtectionContainerMappingInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateProtectionContainerMappingInputProperties(TypedDict, total=False):
        key "providerSpecificInput": ForwardRef('ReplicationProviderSpecificUpdateContainerMappingInput', module='types')
        providerSpecificInput: ReplicationProviderSpecificUpdateContainerMappingInput


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateRecoveryPlanInput(TypedDict, total=False):
        key "properties": ForwardRef('UpdateRecoveryPlanInputProperties', module='types')
        properties: UpdateRecoveryPlanInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateRecoveryPlanInputProperties(TypedDict, total=False):
        groups: list[RecoveryPlanGroup]


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateReplicationProtectedItemInput(TypedDict, total=False):
        key "properties": ForwardRef('UpdateReplicationProtectedItemInputProperties', module='types')
        properties: UpdateReplicationProtectedItemInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateReplicationProtectedItemInputProperties(TypedDict, total=False):
        key "enableRdpOnTargetOption": str
        key "licenseType": Union[str, LicenseType]
        key "providerSpecificDetails": ForwardRef('UpdateReplicationProtectedItemProviderInput', module='types')
        key "recoveryAvailabilitySetId": str
        key "recoveryAzureVMName": str
        key "recoveryAzureVMSize": str
        key "selectedRecoveryAzureNetworkId": str
        key "selectedSourceNicId": str
        key "selectedTfoAzureNetworkId": str
        enableRdpOnTargetOption: str
        licenseType: Union[str, LicenseType]
        providerSpecificDetails: UpdateReplicationProtectedItemProviderInput
        recoveryAvailabilitySetId: str
        recoveryAzureVMName: str
        recoveryAzureVMSize: str
        selectedRecoveryAzureNetworkId: str
        selectedSourceNicId: str
        selectedTfoAzureNetworkId: str
        vmNics: list[VMNicInputDetails]


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateVCenterRequest(TypedDict, total=False):
        key "properties": ForwardRef('UpdateVCenterRequestProperties', module='types')
        properties: UpdateVCenterRequestProperties


    class azure.mgmt.recoveryservicessiterecovery.types.UpdateVCenterRequestProperties(TypedDict, total=False):
        key "friendlyName": str
        key "ipAddress": str
        key "port": str
        key "processServerId": str
        key "runAsAccountId": str
        friendlyName: str
        ipAddress: str
        port: str
        processServerId: str
        runAsAccountId: str


    class azure.mgmt.recoveryservicessiterecovery.types.UserCreatedResourceTag(TypedDict, total=False):
        key "tagName": str
        key "tagValue": str
        tagName: str
        tagValue: str


    class azure.mgmt.recoveryservicessiterecovery.types.VMNicInputDetails(TypedDict, total=False):
        key "enableAcceleratedNetworkingOnRecovery": bool
        key "enableAcceleratedNetworkingOnTfo": bool
        key "nicId": str
        key "recoveryNetworkSecurityGroupId": str
        key "recoveryNicName": str
        key "recoveryNicResourceGroupName": str
        key "reuseExistingNic": bool
        key "selectionType": str
        key "targetNicName": str
        key "tfoNetworkSecurityGroupId": str
        key "tfoNicName": str
        key "tfoNicResourceGroupName": str
        key "tfoReuseExistingNic": bool
        enableAcceleratedNetworkingOnRecovery: bool
        enableAcceleratedNetworkingOnTfo: bool
        ipConfigs: list[IPConfigInputDetails]
        nicId: str
        recoveryNetworkSecurityGroupId: str
        recoveryNicName: str
        recoveryNicResourceGroupName: str
        reuseExistingNic: bool
        selectionType: str
        targetNicName: str
        tfoNetworkSecurityGroupId: str
        tfoNicName: str
        tfoNicResourceGroupName: str
        tfoReuseExistingNic: bool


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtContainerCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        instanceType: Literal[VMwareCbt]


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtContainerMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "keyVaultId": str
        key "keyVaultUri": str
        key "serviceBusConnectionStringSecretName": str
        key "storageAccountId": Required[str]
        key "storageAccountSasSecretName": str
        key "targetLocation": Required[str]
        instanceType: Literal[VMwareCbt]
        keyVaultId: str
        keyVaultUri: str
        serviceBusConnectionStringSecretName: str
        storageAccountId: str
        storageAccountSasSecretName: str
        targetLocation: str


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtDiskInput(TypedDict, total=False):
        key "confidentialDiskEncryptionSetId": str
        key "diskEncryptionSetId": str
        key "diskId": Required[str]
        key "diskSizeInGB": int
        key "diskType": Union[str, DiskAccountType]
        key "iops": int
        key "isOSDisk": Required[str]
        key "logStorageAccountId": Required[str]
        key "logStorageAccountSasSecretName": Required[str]
        key "sectorSizeInBytes": int
        key "throughputInMbps": int
        confidentialDiskEncryptionSetId: str
        diskEncryptionSetId: str
        diskId: str
        diskSizeInGB: int
        diskType: Union[str, DiskAccountType]
        iops: int
        isOSDisk: str
        logStorageAccountId: str
        logStorageAccountSasSecretName: str
        sectorSizeInBytes: int
        throughputInMbps: int


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtEnableMigrationInput(TypedDict, total=False):
        key "confidentialVmKeyVaultId": str
        key "dataMoverRunAsAccountId": Required[str]
        key "disksToInclude": Required[list[VMwareCbtDiskInput]]
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "performAutoResync": str
        key "performSqlBulkRegistration": str
        key "snapshotRunAsAccountId": Required[str]
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetBootDiagnosticsStorageAccountId": str
        key "targetCapacityReservationGroupId": str
        key "targetNetworkId": Required[str]
        key "targetProximityPlacementGroupId": str
        key "targetResourceGroupId": Required[str]
        key "targetSubnetName": str
        key "targetVmName": str
        key "targetVmSecurityProfile": ForwardRef('VMwareCbtSecurityProfileProperties', module='types')
        key "targetVmSize": str
        key "testNetworkId": str
        key "testSubnetName": str
        key "userSelectedOSName": str
        key "vmwareMachineId": Required[str]
        confidentialVmKeyVaultId: str
        dataMoverRunAsAccountId: str
        disksToInclude: list[VMwareCbtDiskInput]
        instanceType: Literal[VMwareCbt]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        performAutoResync: str
        performSqlBulkRegistration: str
        seedDiskTags: dict[str, str]
        snapshotRunAsAccountId: str
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetBootDiagnosticsStorageAccountId: str
        targetCapacityReservationGroupId: str
        targetDiskTags: dict[str, str]
        targetNetworkId: str
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetResourceGroupId: str
        targetSubnetName: str
        targetVmName: str
        targetVmSecurityProfile: VMwareCbtSecurityProfileProperties
        targetVmSize: str
        targetVmTags: dict[str, str]
        testNetworkId: str
        testSubnetName: str
        userSelectedOSName: str
        vmwareMachineId: str


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtMigrateInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "osUpgradeVersion": str
        key "performShutdown": Required[str]
        key "targetCapacityReservationGroupId": str
        instanceType: Literal[VMwareCbt]
        osUpgradeVersion: str
        performShutdown: str
        postMigrationSteps: list[ManagedRunCommandScriptInput]
        targetCapacityReservationGroupId: str


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtNicInput(TypedDict, total=False):
        key "isPrimaryNic": Required[str]
        key "isSelectedForMigration": str
        key "nicId": Required[str]
        key "targetNicName": str
        key "targetStaticIPAddress": str
        key "targetSubnetName": str
        key "testStaticIPAddress": str
        key "testSubnetName": str
        isPrimaryNic: str
        isSelectedForMigration: str
        nicId: str
        targetNicName: str
        targetStaticIPAddress: str
        targetSubnetName: str
        testStaticIPAddress: str
        testSubnetName: str


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtPolicyCreationInput(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": int
        key "crashConsistentFrequencyInMinutes": int
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "recoveryPointHistoryInMinutes": int
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        instanceType: Literal[VMwareCbt]
        recoveryPointHistoryInMinutes: int


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtResumeReplicationInput(TypedDict, total=False):
        key "deleteMigrationResources": str
        key "instanceType": Required[Literal["VMwareCbt"]]
        deleteMigrationResources: str
        instanceType: Literal[VMwareCbt]


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtResyncInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "skipCbtReset": Required[str]
        instanceType: Literal[VMwareCbt]
        skipCbtReset: str


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtSecurityProfileProperties(TypedDict, total=False):
        key "isTargetVmConfidentialEncryptionEnabled": str
        key "isTargetVmIntegrityMonitoringEnabled": str
        key "isTargetVmSecureBootEnabled": str
        key "isTargetVmTpmEnabled": str
        key "targetVmSecurityType": Union[str, SecurityType]
        isTargetVmConfidentialEncryptionEnabled: str
        isTargetVmIntegrityMonitoringEnabled: str
        isTargetVmSecureBootEnabled: str
        isTargetVmTpmEnabled: str
        targetVmSecurityType: Union[str, SecurityType]


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtTestMigrateInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "networkId": Required[str]
        key "osUpgradeVersion": str
        key "recoveryPointId": Required[str]
        instanceType: Literal[VMwareCbt]
        networkId: str
        osUpgradeVersion: str
        postMigrationSteps: list[ManagedRunCommandScriptInput]
        recoveryPointId: str
        vmNics: list[VMwareCbtNicInput]


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtUpdateDiskInput(TypedDict, total=False):
        key "diskId": Required[str]
        key "diskSizeInGB": int
        key "iops": int
        key "isOSDisk": str
        key "targetDiskName": str
        key "throughputInMbps": int
        diskId: str
        diskSizeInGB: int
        iops: int
        isOSDisk: str
        targetDiskName: str
        throughputInMbps: int


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareCbtUpdateMigrationItemInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareCbt"]]
        key "licenseType": Union[str, LicenseType]
        key "linuxLicenseType": Union[str, LinuxLicenseType]
        key "performAutoResync": str
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "targetAvailabilitySetId": str
        key "targetAvailabilityZone": str
        key "targetBootDiagnosticsStorageAccountId": str
        key "targetCapacityReservationGroupId": str
        key "targetNetworkId": str
        key "targetProximityPlacementGroupId": str
        key "targetResourceGroupId": str
        key "targetVmName": str
        key "targetVmSize": str
        key "testNetworkId": str
        key "userSelectedOSName": str
        instanceType: Literal[VMwareCbt]
        licenseType: Union[str, LicenseType]
        linuxLicenseType: Union[str, LinuxLicenseType]
        performAutoResync: str
        sqlServerLicenseType: Union[str, SqlServerLicenseType]
        targetAvailabilitySetId: str
        targetAvailabilityZone: str
        targetBootDiagnosticsStorageAccountId: str
        targetCapacityReservationGroupId: str
        targetDiskTags: dict[str, str]
        targetNetworkId: str
        targetNicTags: dict[str, str]
        targetProximityPlacementGroupId: str
        targetResourceGroupId: str
        targetVmName: str
        targetVmSize: str
        targetVmTags: dict[str, str]
        testNetworkId: str
        userSelectedOSName: str
        vmDisks: list[VMwareCbtUpdateDiskInput]
        vmNics: list[VMwareCbtNicInput]


    class azure.mgmt.recoveryservicessiterecovery.types.VMwareV2FabricCreationInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareV2"]]
        key "migrationSolutionId": Required[str]
        key "physicalSiteId": str
        key "vmwareSiteId": str
        instanceType: Literal[VMwareV2]
        migrationSolutionId: str
        physicalSiteId: str
        vmwareSiteId: str


    class azure.mgmt.recoveryservicessiterecovery.types.VaultSettingCreationInput(TypedDict, total=False):
        key "properties": Required[VaultSettingCreationInputProperties]
        properties: VaultSettingCreationInputProperties


    class azure.mgmt.recoveryservicessiterecovery.types.VaultSettingCreationInputProperties(TypedDict, total=False):
        key "migrationSolutionId": str
        key "recoveryNetworkConfigAutoSync": Union[str, RecoveryNetworkConfigAutoSyncPolicy]
        key "vmwareToAzureProviderType": str
        migrationSolutionId: str
        recoveryNetworkConfigAutoSync: Union[str, RecoveryNetworkConfigAutoSyncPolicy]
        vmwareToAzureProviderType: str


    class azure.mgmt.recoveryservicessiterecovery.types.VmmToAzureCreateNetworkMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VmmToAzure"]]
        instanceType: Literal[VmmToAzure]


    class azure.mgmt.recoveryservicessiterecovery.types.VmmToAzureUpdateNetworkMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VmmToAzure"]]
        instanceType: Literal[VmmToAzure]


    class azure.mgmt.recoveryservicessiterecovery.types.VmmToVmmCreateNetworkMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VmmToVmm"]]
        instanceType: Literal[VmmToVmm]


    class azure.mgmt.recoveryservicessiterecovery.types.VmmToVmmUpdateNetworkMappingInput(TypedDict, total=False):
        key "instanceType": Required[Literal["VmmToVmm"]]
        instanceType: Literal[VmmToVmm]


```