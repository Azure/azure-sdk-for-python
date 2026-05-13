```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.mysqlflexibleservers

    class azure.mgmt.mysqlflexibleservers.MySQLManagementClient: implements ContextManager 
        advanced_threat_protection_settings: AdvancedThreatProtectionSettingsOperations
        azure_ad_administrators: AzureADAdministratorsOperations
        backup_and_export: BackupAndExportOperations
        backups: BackupsOperations
        check_name_availability: CheckNameAvailabilityOperations
        check_name_availability_without_location: CheckNameAvailabilityWithoutLocationOperations
        check_virtual_network_subnet_usage: CheckVirtualNetworkSubnetUsageOperations
        configurations: ConfigurationsOperations
        databases: DatabasesOperations
        firewall_rules: FirewallRulesOperations
        get_private_dns_zone_suffix: GetPrivateDnsZoneSuffixOperations
        location_based_capabilities: LocationBasedCapabilitiesOperations
        location_based_capability_set: LocationBasedCapabilitySetOperations
        log_files: LogFilesOperations
        long_running_backup: LongRunningBackupOperations
        long_running_backups: LongRunningBackupsOperations
        maintenances: MaintenancesOperations
        operation_progress: OperationProgressOperations
        operation_results: OperationResultsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        replicas: ReplicasOperations
        servers: ServersOperations
        servers_migration: ServersMigrationOperations

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


namespace azure.mgmt.mysqlflexibleservers.aio

    class azure.mgmt.mysqlflexibleservers.aio.MySQLManagementClient: implements AsyncContextManager 
        advanced_threat_protection_settings: AdvancedThreatProtectionSettingsOperations
        azure_ad_administrators: AzureADAdministratorsOperations
        backup_and_export: BackupAndExportOperations
        backups: BackupsOperations
        check_name_availability: CheckNameAvailabilityOperations
        check_name_availability_without_location: CheckNameAvailabilityWithoutLocationOperations
        check_virtual_network_subnet_usage: CheckVirtualNetworkSubnetUsageOperations
        configurations: ConfigurationsOperations
        databases: DatabasesOperations
        firewall_rules: FirewallRulesOperations
        get_private_dns_zone_suffix: GetPrivateDnsZoneSuffixOperations
        location_based_capabilities: LocationBasedCapabilitiesOperations
        location_based_capability_set: LocationBasedCapabilitySetOperations
        log_files: LogFilesOperations
        long_running_backup: LongRunningBackupOperations
        long_running_backups: LongRunningBackupsOperations
        maintenances: MaintenancesOperations
        operation_progress: OperationProgressOperations
        operation_results: OperationResultsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        replicas: ReplicasOperations
        servers: ServersOperations
        servers_migration: ServersMigrationOperations

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


namespace azure.mgmt.mysqlflexibleservers.aio.operations

    class azure.mgmt.mysqlflexibleservers.aio.operations.AdvancedThreatProtectionSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: AdvancedThreatProtectionForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtection]: ...

        @overload
        async def begin_update_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: AdvancedThreatProtection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtection]: ...

        @overload
        async def begin_update_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                **kwargs: Any
            ) -> AdvancedThreatProtection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AdvancedThreatProtection]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.AzureADAdministratorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                parameters: AzureADAdministrator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureADAdministrator]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureADAdministrator]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                **kwargs: Any
            ) -> AzureADAdministrator: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureADAdministrator]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.BackupAndExportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: BackupAndExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupAndExportResponse]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupAndExportResponse]: ...

        @distributed_trace_async
        async def validate_backup(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ValidateBackupResponse: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.BackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> ServerBackup: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ServerBackup]: ...

        @distributed_trace_async
        async def put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> ServerBackup: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def execute(
                self, 
                location_name: str, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        async def execute(
                self, 
                location_name: str, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.CheckNameAvailabilityWithoutLocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def execute(
                self, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        async def execute(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.CheckVirtualNetworkSubnetUsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def execute(
                self, 
                location_name: str, 
                parameters: VirtualNetworkSubnetUsageParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageResult: ...

        @overload
        async def execute(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageResult: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_batch_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ConfigurationListForBatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationListResult]: ...

        @overload
        async def begin_batch_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationListResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: Configuration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Configuration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Configuration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: Configuration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Configuration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Configuration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> Configuration: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                tags: Optional[str] = None, 
                keyword: Optional[str] = None, 
                page: Optional[int] = None, 
                page_size: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Configuration]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.DatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Database]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                parameters: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FirewallRule]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.GetPrivateDnsZoneSuffixOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def execute(self, **kwargs: Any) -> GetPrivateDnsZoneSuffixResponse: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.LocationBasedCapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CapabilityProperties]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.LocationBasedCapabilitySetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location_name: str, 
                capability_set_name: str = "default", 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Capability]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.LogFilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LogFile]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.LongRunningBackupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                parameters: Optional[ServerBackupV2] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerBackupV2]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerBackupV2]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.LongRunningBackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> ServerBackupV2: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ServerBackupV2]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.MaintenancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                maintenance_name: str, 
                parameters: Optional[MaintenanceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Maintenance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                maintenance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Maintenance]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Maintenance]: ...

        @distributed_trace_async
        async def read(
                self, 
                resource_group_name: str, 
                server_name: str, 
                maintenance_name: str, 
                **kwargs: Any
            ) -> Maintenance: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.OperationProgressOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationProgressResult: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusExtendedResult: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace_async
        async def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.ReplicasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Server]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.ServersMigrationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cutover_migration(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...


    class azure.mgmt.mysqlflexibleservers.aio.operations.ServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Server, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_detach_v_net(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerDetachVNetParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @overload
        async def begin_detach_v_net(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @distributed_trace_async
        async def begin_failover(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_gtid(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerGtidSetParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_gtid(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerRestartParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> Server: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Server]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Server]: ...

        @overload
        async def validate_estimate_high_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: HighAvailabilityValidationEstimation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HighAvailabilityValidationEstimation: ...

        @overload
        async def validate_estimate_high_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HighAvailabilityValidationEstimation: ...


namespace azure.mgmt.mysqlflexibleservers.models

    class azure.mgmt.mysqlflexibleservers.models.AdministratorListResult(Model):
        next_link: str
        value: list[AzureADAdministrator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[AzureADAdministrator]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.AdministratorName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"


    class azure.mgmt.mysqlflexibleservers.models.AdministratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtection(ProxyResource):
        creation_time: datetime
        id: str
        name: str
        provisioning_state: Union[str, AdvancedThreatProtectionProvisioningState]
        state: Union[str, AdvancedThreatProtectionState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, AdvancedThreatProtectionState]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionForUpdate(Model):
        state: Union[str, AdvancedThreatProtectionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, AdvancedThreatProtectionState]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionListResult(Model):
        next_link: str
        value: list[AdvancedThreatProtection]

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


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mysqlflexibleservers.models.AzureADAdministrator(ProxyResource):
        administrator_type: Union[str, AdministratorType]
        id: str
        identity_resource_id: str
        login: str
        name: str
        sid: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrator_type: Optional[Union[str, AdministratorType]] = ..., 
                identity_resource_id: Optional[str] = ..., 
                login: Optional[str] = ..., 
                sid: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.Backup(Model):
        backup_interval_hours: int
        backup_retention_days: int
        earliest_restore_date: datetime
        geo_redundant_backup: Union[str, EnableStatusEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_interval_hours: Optional[int] = ..., 
                backup_retention_days: Optional[int] = ..., 
                geo_redundant_backup: Optional[Union[str, EnableStatusEnum]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportRequest(BackupRequestBase):
        backup_settings: BackupSettings
        target_details: BackupStoreDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_settings: BackupSettings, 
                target_details: BackupStoreDetails, 
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


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportResponse(ProxyResource):
        backup_metadata: str
        data_transferred_in_bytes: int
        datasource_size_in_bytes: int
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        percent_complete: float
        start_time: datetime
        status: Union[str, OperationStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_metadata: Optional[str] = ..., 
                data_transferred_in_bytes: Optional[int] = ..., 
                datasource_size_in_bytes: Optional[int] = ..., 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportResponseType(OperationProgressResponseType):
        backup_metadata: str
        data_transferred_in_bytes: int
        datasource_size_in_bytes: int
        object_type: Union[str, ObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_metadata: Optional[str] = ..., 
                data_transferred_in_bytes: Optional[int] = ..., 
                datasource_size_in_bytes: Optional[int] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.BackupFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLATED_FORMAT = "CollatedFormat"
        RAW = "Raw"


    class azure.mgmt.mysqlflexibleservers.models.BackupRequestBase(Model):
        backup_settings: BackupSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_settings: BackupSettings, 
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


    class azure.mgmt.mysqlflexibleservers.models.BackupSettings(Model):
        backup_format: Union[str, BackupFormat]
        backup_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_format: Optional[Union[str, BackupFormat]] = ..., 
                backup_name: str, 
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


    class azure.mgmt.mysqlflexibleservers.models.BackupStoreDetails(Model):
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


    class azure.mgmt.mysqlflexibleservers.models.BackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "FULL"


    class azure.mgmt.mysqlflexibleservers.models.BatchOfMaintenance(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH1 = "Batch1"
        BATCH2 = "Batch2"
        DEFAULT = "Default"


    class azure.mgmt.mysqlflexibleservers.models.CapabilitiesListResult(Model):
        next_link: str
        value: list[CapabilityProperties]

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


    class azure.mgmt.mysqlflexibleservers.models.Capability(ProxyResource):
        id: str
        name: str
        supported_features: list[FeatureProperty]
        supported_flexible_server_editions: list[ServerEditionCapabilityV2]
        supported_geo_backup_regions: list[str]
        supported_server_versions: list[ServerVersionCapabilityV2]
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


    class azure.mgmt.mysqlflexibleservers.models.CapabilityProperties(Model):
        supported_flexible_server_editions: list[ServerEditionCapability]
        supported_geo_backup_regions: list[str]
        supported_ha_mode: list[str]
        zone: str

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


    class azure.mgmt.mysqlflexibleservers.models.CapabilitySetsList(Model):
        next_link: str
        value: list[Capability]

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


    class azure.mgmt.mysqlflexibleservers.models.Configuration(ProxyResource):
        allowed_values: str
        current_value: str
        data_type: str
        default_value: str
        description: str
        documentation_link: str
        id: str
        is_config_pending_restart: Union[str, IsConfigPendingRestart]
        is_dynamic_config: Union[str, IsDynamicConfig]
        is_read_only: Union[str, IsReadOnly]
        name: str
        source: Union[str, ConfigurationSource]
        system_data: SystemData
        type: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_value: Optional[str] = ..., 
                source: Optional[Union[str, ConfigurationSource]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationForBatchUpdate(Model):
        name: str
        source: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                source: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationListForBatchUpdate(Model):
        reset_all_to_default: Union[str, ResetAllToDefault]
        value: list[ConfigurationForBatchUpdate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reset_all_to_default: Optional[Union[str, ResetAllToDefault]] = ..., 
                value: Optional[list[ConfigurationForBatchUpdate]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationListResult(Model):
        next_link: str
        value: list[Configuration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Configuration]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_DEFAULT = "system-default"
        USER_OVERRIDE = "user-override"


    class azure.mgmt.mysqlflexibleservers.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        GEO_RESTORE = "GeoRestore"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"
        REPLICA = "Replica"


    class azure.mgmt.mysqlflexibleservers.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.mysqlflexibleservers.models.DataEncryption(Model):
        geo_backup_key_uri: str
        geo_backup_user_assigned_identity_id: str
        primary_key_uri: str
        primary_user_assigned_identity_id: str
        type: Union[str, DataEncryptionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                geo_backup_key_uri: Optional[str] = ..., 
                geo_backup_user_assigned_identity_id: Optional[str] = ..., 
                primary_key_uri: Optional[str] = ..., 
                primary_user_assigned_identity_id: Optional[str] = ..., 
                type: Optional[Union[str, DataEncryptionType]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.DataEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        SYSTEM_MANAGED = "SystemManaged"


    class azure.mgmt.mysqlflexibleservers.models.Database(ProxyResource):
        charset: str
        collation: str
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                charset: Optional[str] = ..., 
                collation: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.DatabaseListResult(Model):
        next_link: str
        value: list[Database]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Database]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.DelegatedSubnetUsage(Model):
        subnet_name: str
        usage: int

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


    class azure.mgmt.mysqlflexibleservers.models.EnableStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mysqlflexibleservers.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.mysqlflexibleservers.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
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


    class azure.mgmt.mysqlflexibleservers.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.FeatureProperty(Model):
        feature_name: str
        feature_value: str

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


    class azure.mgmt.mysqlflexibleservers.models.FirewallRule(ProxyResource):
        end_ip_address: str
        id: str
        name: str
        start_ip_address: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_ip_address: str, 
                start_ip_address: str, 
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


    class azure.mgmt.mysqlflexibleservers.models.FirewallRuleListResult(Model):
        next_link: str
        value: list[FirewallRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[FirewallRule]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.FullBackupStoreDetails(BackupStoreDetails):
        object_type: str
        sas_uri_list: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sas_uri_list: list[str], 
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


    class azure.mgmt.mysqlflexibleservers.models.GetPrivateDnsZoneSuffixResponse(Model):
        private_dns_zone_suffix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_dns_zone_suffix: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.HighAvailability(Model):
        mode: Union[str, HighAvailabilityMode]
        replication_mode: Union[str, ReplicationMode]
        standby_availability_zone: str
        state: Union[str, HighAvailabilityState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, HighAvailabilityMode]] = ..., 
                replication_mode: Optional[Union[str, ReplicationMode]] = ..., 
                standby_availability_zone: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.HighAvailabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        SAME_ZONE = "SameZone"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.mysqlflexibleservers.models.HighAvailabilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING_STANDBY = "CreatingStandby"
        FAILING_OVER = "FailingOver"
        HEALTHY = "Healthy"
        NOT_ENABLED = "NotEnabled"
        REMOVING_STANDBY = "RemovingStandby"


    class azure.mgmt.mysqlflexibleservers.models.HighAvailabilityValidationEstimation(Model):
        estimated_downtime: int
        expected_standby_availability_zone: str
        scheduled_standby_availability_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expected_standby_availability_zone: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ImportFromStorageResponseType(OperationProgressResponseType):
        estimated_completion_time: datetime
        object_type: Union[str, ObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                estimated_completion_time: Optional[datetime] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ImportSourceProperties(Model):
        data_dir_path: str
        sas_token: str
        storage_type: Union[str, ImportSourceStorageType]
        storage_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_dir_path: Optional[str] = ..., 
                sas_token: Optional[str] = ..., 
                storage_type: Optional[Union[str, ImportSourceStorageType]] = ..., 
                storage_url: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ImportSourceStorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"


    class azure.mgmt.mysqlflexibleservers.models.IsConfigPendingRestart(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.mysqlflexibleservers.models.IsDynamicConfig(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.mysqlflexibleservers.models.IsReadOnly(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.mysqlflexibleservers.models.LogFile(ProxyResource):
        created_time: datetime
        id: str
        last_modified_time: datetime
        name: str
        size_in_kb: int
        system_data: SystemData
        type: str
        type_properties_type: str
        url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_time: Optional[datetime] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                size_in_kb: Optional[int] = ..., 
                type_properties_type: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.LogFileListResult(Model):
        next_link: str
        value: list[LogFile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[LogFile]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.Maintenance(ProxyResource):
        id: str
        maintenance_available_schedule_max_time: datetime
        maintenance_available_schedule_min_time: datetime
        maintenance_description: str
        maintenance_end_time: datetime
        maintenance_execution_end_time: datetime
        maintenance_execution_start_time: datetime
        maintenance_start_time: datetime
        maintenance_state: Union[str, MaintenanceState]
        maintenance_title: str
        maintenance_type: Union[str, MaintenanceType]
        name: str
        provisioning_state: Union[str, MaintenanceProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                maintenance_start_time: Optional[datetime] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceListResult(Model):
        next_link: str
        value: list[Maintenance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Maintenance]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.MaintenancePolicy(Model):
        patch_strategy: Union[str, PatchStrategy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                patch_strategy: Optional[Union[str, PatchStrategy]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        IN_PREPARATION = "InPreparation"
        PROCESSING = "Processing"
        RE_SCHEDULED = "ReScheduled"
        SCHEDULED = "Scheduled"


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOT_FIXES = "HotFixes"
        MINOR_VERSION_UPGRADE = "MinorVersionUpgrade"
        ROUTINE_MAINTENANCE = "RoutineMaintenance"
        SECURITY_PATCHES = "SecurityPatches"


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceUpdate(Model):
        maintenance_start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                maintenance_start_time: Optional[datetime] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceWindow(Model):
        batch_of_maintenance: Union[str, BatchOfMaintenance]
        custom_window: str
        day_of_week: int
        start_hour: int
        start_minute: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                batch_of_maintenance: Optional[Union[str, BatchOfMaintenance]] = ..., 
                custom_window: Optional[str] = ..., 
                day_of_week: Optional[int] = ..., 
                start_hour: Optional[int] = ..., 
                start_minute: Optional[int] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.mysqlflexibleservers.models.MySQLServerIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.MySQLServerSku(Model):
        name: str
        tier: Union[str, ServerSkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                tier: Union[str, ServerSkuTier], 
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


    class azure.mgmt.mysqlflexibleservers.models.NameAvailability(Model):
        message: str
        name_available: bool
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.NameAvailabilityRequest(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.Network(Model):
        delegated_subnet_resource_id: str
        private_dns_zone_resource_id: str
        public_network_access: Union[str, EnableStatusEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delegated_subnet_resource_id: Optional[str] = ..., 
                private_dns_zone_resource_id: Optional[str] = ..., 
                public_network_access: Optional[Union[str, EnableStatusEnum]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_AND_EXPORT_RESPONSE = "BackupAndExportResponse"
        IMPORT_FROM_STORAGE_RESPONSE = "ImportFromStorageResponse"


    class azure.mgmt.mysqlflexibleservers.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: Union[str, Origin]
        properties: dict[str, any]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                properties: Optional[dict[str, Any]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.mysqlflexibleservers.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Operation]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.OperationProgressResponseType(Model):
        object_type: Union[str, ObjectType]

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


    class azure.mgmt.mysqlflexibleservers.models.OperationProgressResult(OperationStatusResult):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        properties: OperationProgressResponseType
        resource_id: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[OperationProgressResponseType] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str, 
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


    class azure.mgmt.mysqlflexibleservers.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCEL_IN_PROGRESS = "CancelInProgress"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.mysqlflexibleservers.models.OperationStatusExtendedResult(OperationStatusResult):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        properties: dict[str, any]
        resource_id: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[dict[str, Any]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str, 
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


    class azure.mgmt.mysqlflexibleservers.models.OperationStatusResult(Model):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        resource_id: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str, 
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


    class azure.mgmt.mysqlflexibleservers.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.mysqlflexibleservers.models.PatchStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        VIRTUAL_CANARY = "VirtualCanary"


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpoint(Model):
        id: str

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


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointConnection(Resource):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointConnectionListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateEndpointConnection], 
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


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.mysqlflexibleservers.models.PrivateLinkResource(Resource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.mysqlflexibleservers.models.ProxyResource(Resource):
        id: str
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


    class azure.mgmt.mysqlflexibleservers.models.ReplicationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY_LOG = "BinaryLog"
        REDO_LOG = "RedoLog"


    class azure.mgmt.mysqlflexibleservers.models.ReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REPLICA = "Replica"
        SOURCE = "Source"


    class azure.mgmt.mysqlflexibleservers.models.ResetAllToDefault(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.mysqlflexibleservers.models.Resource(Model):
        id: str
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


    class azure.mgmt.mysqlflexibleservers.models.Server(TrackedResource):
        administrator_login: str
        administrator_login_password: str
        availability_zone: str
        backup: Backup
        create_mode: Union[str, CreateMode]
        data_encryption: DataEncryption
        database_port: int
        full_version: str
        fully_qualified_domain_name: str
        high_availability: HighAvailability
        id: str
        identity: MySQLServerIdentity
        import_source_properties: ImportSourceProperties
        location: str
        lower_case_table_names: int
        maintenance_policy: MaintenancePolicy
        maintenance_window: MaintenanceWindow
        name: str
        network: Network
        private_endpoint_connections: list[PrivateEndpointConnection]
        replica_capacity: int
        replication_role: Union[str, ReplicationRole]
        restore_point_in_time: datetime
        sku: MySQLServerSku
        source_server_resource_id: str
        state: Union[str, ServerState]
        storage: Storage
        system_data: SystemData
        tags: dict[str, str]
        type: str
        version: Union[str, ServerVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrator_login: Optional[str] = ..., 
                administrator_login_password: Optional[str] = ..., 
                availability_zone: Optional[str] = ..., 
                backup: Optional[Backup] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                data_encryption: Optional[DataEncryption] = ..., 
                database_port: Optional[int] = ..., 
                high_availability: Optional[HighAvailability] = ..., 
                identity: Optional[MySQLServerIdentity] = ..., 
                import_source_properties: Optional[ImportSourceProperties] = ..., 
                location: str, 
                lower_case_table_names: Optional[int] = ..., 
                maintenance_policy: Optional[MaintenancePolicy] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                network: Optional[Network] = ..., 
                replication_role: Optional[Union[str, ReplicationRole]] = ..., 
                restore_point_in_time: Optional[datetime] = ..., 
                sku: Optional[MySQLServerSku] = ..., 
                source_server_resource_id: Optional[str] = ..., 
                storage: Optional[Storage] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                version: Optional[Union[str, ServerVersion]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerBackup(ProxyResource):
        backup_type: str
        completed_time: datetime
        id: str
        name: str
        source: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_type: Optional[str] = ..., 
                completed_time: Optional[datetime] = ..., 
                source: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerBackupListResult(Model):
        next_link: str
        value: list[ServerBackup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[ServerBackup]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerBackupV2(ProxyResource):
        backup_name_v2: str
        backup_type: Union[str, BackupType]
        completed_time: datetime
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        source: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_name_v2: Optional[str] = ..., 
                backup_type: Optional[Union[str, BackupType]] = ..., 
                completed_time: Optional[datetime] = ..., 
                source: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerBackupV2ListResult(Model):
        next_link: str
        value: list[ServerBackupV2]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[ServerBackupV2]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerDetachVNetParameter(Model):
        public_network_access: Union[str, EnableStatusEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, EnableStatusEnum]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerEditionCapability(Model):
        name: str
        supported_server_versions: list[ServerVersionCapability]
        supported_storage_editions: list[StorageEditionCapability]

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


    class azure.mgmt.mysqlflexibleservers.models.ServerEditionCapabilityV2(Model):
        default_sku: str
        default_storage_size: int
        name: str
        supported_skus: list[SkuCapabilityV2]
        supported_storage_editions: list[StorageEditionCapability]

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


    class azure.mgmt.mysqlflexibleservers.models.ServerForUpdate(Model):
        administrator_login_password: str
        backup: Backup
        data_encryption: DataEncryption
        high_availability: HighAvailability
        identity: MySQLServerIdentity
        maintenance_policy: MaintenancePolicy
        maintenance_window: MaintenanceWindow
        network: Network
        replication_role: Union[str, ReplicationRole]
        sku: MySQLServerSku
        storage: Storage
        tags: dict[str, str]
        version: Union[str, ServerVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                backup: Optional[Backup] = ..., 
                data_encryption: Optional[DataEncryption] = ..., 
                high_availability: Optional[HighAvailability] = ..., 
                identity: Optional[MySQLServerIdentity] = ..., 
                maintenance_policy: Optional[MaintenancePolicy] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                network: Optional[Network] = ..., 
                replication_role: Optional[Union[str, ReplicationRole]] = ..., 
                sku: Optional[MySQLServerSku] = ..., 
                storage: Optional[Storage] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                version: Optional[Union[str, ServerVersion]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerGtidSetParameter(Model):
        gtid_set: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                gtid_set: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerListResult(Model):
        next_link: str
        value: list[Server]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Server]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerRestartParameter(Model):
        max_failover_seconds: int
        restart_with_failover: Union[str, EnableStatusEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_failover_seconds: Optional[int] = ..., 
                restart_with_failover: Optional[Union[str, EnableStatusEnum]] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.ServerSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BURSTABLE = "Burstable"
        GENERAL_PURPOSE = "GeneralPurpose"
        MEMORY_OPTIMIZED = "MemoryOptimized"


    class azure.mgmt.mysqlflexibleservers.models.ServerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DROPPING = "Dropping"
        READY = "Ready"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UPDATING = "Updating"


    class azure.mgmt.mysqlflexibleservers.models.ServerVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EIGHT0_21 = "8.0.21"
        EIGHT4 = "8.4"
        FIVE7 = "5.7"


    class azure.mgmt.mysqlflexibleservers.models.ServerVersionCapability(Model):
        name: str
        supported_skus: list[SkuCapability]

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


    class azure.mgmt.mysqlflexibleservers.models.ServerVersionCapabilityV2(Model):
        name: str

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


    class azure.mgmt.mysqlflexibleservers.models.SkuCapability(Model):
        name: str
        supported_iops: int
        supported_memory_per_v_core_mb: int
        v_cores: int

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


    class azure.mgmt.mysqlflexibleservers.models.SkuCapabilityV2(Model):
        name: str
        supported_ha_mode: list[str]
        supported_iops: int
        supported_memory_per_v_core_mb: int
        supported_zones: list[str]
        v_cores: int

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


    class azure.mgmt.mysqlflexibleservers.models.Storage(Model):
        auto_grow: Union[str, EnableStatusEnum]
        auto_io_scaling: Union[str, EnableStatusEnum]
        iops: int
        log_on_disk: Union[str, EnableStatusEnum]
        storage_redundancy: Union[str, StorageRedundancyEnum]
        storage_size_gb: int
        storage_sku: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_grow: Optional[Union[str, EnableStatusEnum]] = ..., 
                auto_io_scaling: Optional[Union[str, EnableStatusEnum]] = ..., 
                iops: Optional[int] = ..., 
                log_on_disk: Optional[Union[str, EnableStatusEnum]] = ..., 
                storage_redundancy: Union[str, StorageRedundancyEnum] = "LocalRedundancy", 
                storage_size_gb: Optional[int] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.StorageEditionCapability(Model):
        max_backup_interval_hours: int
        max_backup_retention_days: int
        max_storage_size: int
        min_backup_interval_hours: int
        min_backup_retention_days: int
        min_storage_size: int
        name: str

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


    class azure.mgmt.mysqlflexibleservers.models.StorageRedundancyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL_REDUNDANCY = "LocalRedundancy"
        ZONE_REDUNDANCY = "ZoneRedundancy"


    class azure.mgmt.mysqlflexibleservers.models.SystemData(Model):
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


    class azure.mgmt.mysqlflexibleservers.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
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


    class azure.mgmt.mysqlflexibleservers.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

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


    class azure.mgmt.mysqlflexibleservers.models.ValidateBackupResponse(Model):
        number_of_containers: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                number_of_containers: Optional[int] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.VirtualNetworkSubnetUsageParameter(Model):
        virtual_network_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                virtual_network_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.models.VirtualNetworkSubnetUsageResult(Model):
        delegated_subnets_usage: list[DelegatedSubnetUsage]
        location: str
        subscription_id: str

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


namespace azure.mgmt.mysqlflexibleservers.operations

    class azure.mgmt.mysqlflexibleservers.operations.AdvancedThreatProtectionSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: AdvancedThreatProtectionForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtection]: ...

        @overload
        def begin_update_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: AdvancedThreatProtection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtection]: ...

        @overload
        def begin_update_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                advanced_threat_protection_name: Union[str, AdvancedThreatProtectionName], 
                **kwargs: Any
            ) -> AdvancedThreatProtection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AdvancedThreatProtection]: ...


    class azure.mgmt.mysqlflexibleservers.operations.AzureADAdministratorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                parameters: AzureADAdministrator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureADAdministrator]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureADAdministrator]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                administrator_name: Union[str, AdministratorName], 
                **kwargs: Any
            ) -> AzureADAdministrator: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureADAdministrator]: ...


    class azure.mgmt.mysqlflexibleservers.operations.BackupAndExportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: BackupAndExportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupAndExportResponse]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupAndExportResponse]: ...

        @distributed_trace
        def validate_backup(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ValidateBackupResponse: ...


    class azure.mgmt.mysqlflexibleservers.operations.BackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> ServerBackup: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ServerBackup]: ...

        @distributed_trace
        def put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> ServerBackup: ...


    class azure.mgmt.mysqlflexibleservers.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def execute(
                self, 
                location_name: str, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        def execute(
                self, 
                location_name: str, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...


    class azure.mgmt.mysqlflexibleservers.operations.CheckNameAvailabilityWithoutLocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def execute(
                self, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        def execute(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...


    class azure.mgmt.mysqlflexibleservers.operations.CheckVirtualNetworkSubnetUsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def execute(
                self, 
                location_name: str, 
                parameters: VirtualNetworkSubnetUsageParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageResult: ...

        @overload
        def execute(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageResult: ...


    class azure.mgmt.mysqlflexibleservers.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_batch_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ConfigurationListForBatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationListResult]: ...

        @overload
        def begin_batch_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationListResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: Configuration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Configuration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Configuration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: Configuration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Configuration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Configuration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> Configuration: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                tags: Optional[str] = None, 
                keyword: Optional[str] = None, 
                page: Optional[int] = None, 
                page_size: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Configuration]: ...


    class azure.mgmt.mysqlflexibleservers.operations.DatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Database]: ...


    class azure.mgmt.mysqlflexibleservers.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                parameters: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FirewallRule]: ...


    class azure.mgmt.mysqlflexibleservers.operations.GetPrivateDnsZoneSuffixOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def execute(self, **kwargs: Any) -> GetPrivateDnsZoneSuffixResponse: ...


    class azure.mgmt.mysqlflexibleservers.operations.LocationBasedCapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CapabilityProperties]: ...


    class azure.mgmt.mysqlflexibleservers.operations.LocationBasedCapabilitySetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location_name: str, 
                capability_set_name: str = "default", 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Capability]: ...


    class azure.mgmt.mysqlflexibleservers.operations.LogFilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LogFile]: ...


    class azure.mgmt.mysqlflexibleservers.operations.LongRunningBackupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                parameters: Optional[ServerBackupV2] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerBackupV2]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerBackupV2]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.mysqlflexibleservers.operations.LongRunningBackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> ServerBackupV2: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ServerBackupV2]: ...


    class azure.mgmt.mysqlflexibleservers.operations.MaintenancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                maintenance_name: str, 
                parameters: Optional[MaintenanceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Maintenance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                maintenance_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Maintenance]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Maintenance]: ...

        @distributed_trace
        def read(
                self, 
                resource_group_name: str, 
                server_name: str, 
                maintenance_name: str, 
                **kwargs: Any
            ) -> Maintenance: ...


    class azure.mgmt.mysqlflexibleservers.operations.OperationProgressOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationProgressResult: ...


    class azure.mgmt.mysqlflexibleservers.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusExtendedResult: ...


    class azure.mgmt.mysqlflexibleservers.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.mysqlflexibleservers.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.mysqlflexibleservers.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.mysqlflexibleservers.operations.ReplicasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Server]: ...


    class azure.mgmt.mysqlflexibleservers.operations.ServersMigrationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cutover_migration(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> LROPoller[Server]: ...


    class azure.mgmt.mysqlflexibleservers.operations.ServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Server, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_detach_v_net(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerDetachVNetParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @overload
        def begin_detach_v_net(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @distributed_trace
        def begin_failover(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_gtid(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerGtidSetParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_gtid(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerRestartParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: ServerForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> Server: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Server]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Server]: ...

        @overload
        def validate_estimate_high_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: HighAvailabilityValidationEstimation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HighAvailabilityValidationEstimation: ...

        @overload
        def validate_estimate_high_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HighAvailabilityValidationEstimation: ...


```