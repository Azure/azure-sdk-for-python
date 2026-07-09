```py
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
        fabric_mirroring_settings: FabricMirroringSettingsOperations
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


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
        fabric_mirroring_settings: FabricMirroringSettingsOperations
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


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
                *, 
                keyword: Optional[str] = ..., 
                page: Optional[int] = ..., 
                page_size: Optional[int] = ..., 
                tags: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.aio.operations.FabricMirroringSettingsOperations:

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
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                resource: FabricMirroringSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricMirroringSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                resource: FabricMirroringSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricMirroringSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricMirroringSetting]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'fabric_mirroring_settings_name', 'accept']}, api_versions_list=['2025-12-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                **kwargs: Any
            ) -> FabricMirroringSetting: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'accept']}, api_versions_list=['2025-12-01-preview'])
        async def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> FabricMirroringSettingListResult: ...


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
                capability_set_name: str, 
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
        @api_version_validation(method_added_on='2025-06-01-preview', params_added_on={'2025-06-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'backup_name']}, api_versions_list=['2025-06-01-preview', '2025-12-01-preview'])
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

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


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

    class azure.mgmt.mysqlflexibleservers.models.AdministratorName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"


    class azure.mgmt.mysqlflexibleservers.models.AdministratorProperties(_Model):
        administrator_type: Optional[Union[str, AdministratorType]]
        identity_resource_id: Optional[str]
        login: Optional[str]
        sid: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrator_type: Optional[Union[str, AdministratorType]] = ..., 
                identity_resource_id: Optional[str] = ..., 
                login: Optional[str] = ..., 
                sid: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.AdministratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtection(ProxyResource):
        id: str
        name: str
        properties: Optional[AdvancedThreatProtectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdvancedThreatProtectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionForUpdate(_Model):
        properties: Optional[AdvancedThreatProtectionUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdvancedThreatProtectionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionProperties(_Model):
        creation_time: Optional[datetime]
        provisioning_state: Optional[Union[str, AdvancedThreatProtectionProvisioningState]]
        state: Optional[Union[str, AdvancedThreatProtectionState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, AdvancedThreatProtectionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mysqlflexibleservers.models.AdvancedThreatProtectionUpdateProperties(_Model):
        state: Union[str, AdvancedThreatProtectionState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, AdvancedThreatProtectionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.AzureADAdministrator(ProxyResource):
        id: str
        name: str
        properties: Optional[AdministratorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdministratorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.Backup(_Model):
        backup_interval_hours: Optional[int]
        backup_retention_days: Optional[int]
        earliest_restore_date: Optional[datetime]
        geo_redundant_backup: Optional[Union[str, EnableStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                backup_interval_hours: Optional[int] = ..., 
                backup_retention_days: Optional[int] = ..., 
                geo_redundant_backup: Optional[Union[str, EnableStatusEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportRequest(BackupRequestBase):
        backup_settings: BackupSettings
        target_details: BackupStoreDetails

        @overload
        def __init__(
                self, 
                *, 
                backup_settings: BackupSettings, 
                target_details: BackupStoreDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportResponse(ProxyResource):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: str
        name: str
        percent_complete: Optional[float]
        properties: Optional[BackupAndExportResponseProperties]
        start_time: Optional[datetime]
        status: Optional[Union[str, OperationStatus]]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[BackupAndExportResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, OperationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportResponseProperties(_Model):
        backup_metadata: Optional[str]
        data_transferred_in_bytes: Optional[int]
        datasource_size_in_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                backup_metadata: Optional[str] = ..., 
                data_transferred_in_bytes: Optional[int] = ..., 
                datasource_size_in_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupAndExportResponseType(OperationProgressResponseType, discriminator='BackupAndExportResponse'):
        backup_metadata: Optional[str]
        data_transferred_in_bytes: Optional[int]
        datasource_size_in_bytes: Optional[int]
        object_type: Literal[ObjectType.BACKUP_AND_EXPORT_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                backup_metadata: Optional[str] = ..., 
                data_transferred_in_bytes: Optional[int] = ..., 
                datasource_size_in_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLATED_FORMAT = "CollatedFormat"
        RAW = "Raw"


    class azure.mgmt.mysqlflexibleservers.models.BackupRequestBase(_Model):
        backup_settings: BackupSettings

        @overload
        def __init__(
                self, 
                *, 
                backup_settings: BackupSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupSettings(_Model):
        backup_format: Optional[Union[str, BackupFormat]]
        backup_name: str

        @overload
        def __init__(
                self, 
                *, 
                backup_format: Optional[Union[str, BackupFormat]] = ..., 
                backup_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupStoreDetails(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.BackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "FULL"


    class azure.mgmt.mysqlflexibleservers.models.BatchOfMaintenance(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH1 = "Batch1"
        BATCH2 = "Batch2"
        DEFAULT = "Default"


    class azure.mgmt.mysqlflexibleservers.models.Capability(ProxyResource):
        id: str
        name: str
        properties: Optional[CapabilityPropertiesV2]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilityPropertiesV2] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.CapabilityProperties(_Model):
        supported_flexible_server_editions: Optional[list[ServerEditionCapability]]
        supported_geo_backup_regions: Optional[list[str]]
        supported_ha_mode: Optional[list[str]]
        zone: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.CapabilityPropertiesV2(_Model):
        supported_features: Optional[list[FeatureProperty]]
        supported_flexible_server_editions: Optional[list[ServerEditionCapabilityV2]]
        supported_geo_backup_regions: Optional[list[str]]
        supported_server_versions: Optional[list[ServerVersionCapabilityV2]]


    class azure.mgmt.mysqlflexibleservers.models.Configuration(ProxyResource):
        id: str
        name: str
        properties: Optional[ConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationForBatchUpdate(_Model):
        name: Optional[str]
        properties: Optional[ConfigurationForBatchUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[ConfigurationForBatchUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationForBatchUpdateProperties(_Model):
        source: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationListForBatchUpdate(_Model):
        reset_all_to_default: Optional[Union[str, ResetAllToDefault]]
        value: Optional[list[ConfigurationForBatchUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                reset_all_to_default: Optional[Union[str, ResetAllToDefault]] = ..., 
                value: Optional[list[ConfigurationForBatchUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[Configuration]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Configuration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationProperties(_Model):
        allowed_values: Optional[str]
        current_value: Optional[str]
        data_type: Optional[str]
        default_value: Optional[str]
        description: Optional[str]
        documentation_link: Optional[str]
        is_config_pending_restart: Optional[Union[str, IsConfigPendingRestart]]
        is_dynamic_config: Optional[Union[str, IsDynamicConfig]]
        is_read_only: Optional[Union[str, IsReadOnly]]
        source: Optional[Union[str, ConfigurationSource]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[str] = ..., 
                source: Optional[Union[str, ConfigurationSource]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ConfigurationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_DEFAULT = "system-default"
        USER_OVERRIDE = "user-override"


    class azure.mgmt.mysqlflexibleservers.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        GEO_RESTORE = "GeoRestore"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"
        RENAME = "Rename"
        REPLICA = "Replica"


    class azure.mgmt.mysqlflexibleservers.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.mysqlflexibleservers.models.DataEncryption(_Model):
        geo_backup_key_uri: Optional[str]
        geo_backup_user_assigned_identity_id: Optional[str]
        primary_key_uri: Optional[str]
        primary_user_assigned_identity_id: Optional[str]
        type: Optional[Union[str, DataEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                geo_backup_key_uri: Optional[str] = ..., 
                geo_backup_user_assigned_identity_id: Optional[str] = ..., 
                primary_key_uri: Optional[str] = ..., 
                primary_user_assigned_identity_id: Optional[str] = ..., 
                type: Optional[Union[str, DataEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.DataEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        SYSTEM_MANAGED = "SystemManaged"


    class azure.mgmt.mysqlflexibleservers.models.Database(ProxyResource):
        id: str
        name: str
        properties: Optional[DatabaseProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.DatabaseProperties(_Model):
        charset: Optional[str]
        collation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                charset: Optional[str] = ..., 
                collation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.DelegatedSubnetUsage(_Model):
        subnet_name: Optional[str]
        usage: Optional[int]


    class azure.mgmt.mysqlflexibleservers.models.EnableStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mysqlflexibleservers.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.FabricMirroringProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.mysqlflexibleservers.models.FabricMirroringSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[FabricMirroringSettingsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricMirroringSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.FabricMirroringSettingListResult(_Model):
        next_link: Optional[str]
        value: list[FabricMirroringSetting]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[FabricMirroringSetting]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.FabricMirroringSettingsName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.mysqlflexibleservers.models.FabricMirroringSettingsProperties(_Model):
        identity_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, FabricMirroringProvisioningState]]
        state: Optional[Union[str, FabricMirroringState]]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ..., 
                state: Optional[Union[str, FabricMirroringState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.FabricMirroringState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mysqlflexibleservers.models.FeatureProperty(_Model):
        feature_name: Optional[str]
        feature_value: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.FirewallRule(ProxyResource):
        id: str
        name: str
        properties: FirewallRuleProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: FirewallRuleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.FirewallRuleProperties(_Model):
        end_ip_address: str
        start_ip_address: str

        @overload
        def __init__(
                self, 
                *, 
                end_ip_address: str, 
                start_ip_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.FullBackupStoreDetails(BackupStoreDetails, discriminator='FullBackupStoreDetails'):
        object_type: Literal["FullBackupStoreDetails"]
        sas_uri_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                sas_uri_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.GetPrivateDnsZoneSuffixResponse(_Model):
        private_dns_zone_suffix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_dns_zone_suffix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.HighAvailability(_Model):
        mode: Optional[Union[str, HighAvailabilityMode]]
        replication_mode: Optional[Union[str, ReplicationMode]]
        standby_availability_zone: Optional[str]
        state: Optional[Union[str, HighAvailabilityState]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, HighAvailabilityMode]] = ..., 
                replication_mode: Optional[Union[str, ReplicationMode]] = ..., 
                standby_availability_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.mysqlflexibleservers.models.HighAvailabilityValidationEstimation(_Model):
        estimated_downtime: Optional[int]
        expected_standby_availability_zone: Optional[str]
        scheduled_standby_availability_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expected_standby_availability_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ImportFromStorageResponseType(OperationProgressResponseType, discriminator='ImportFromStorageResponse'):
        estimated_completion_time: Optional[datetime]
        object_type: Literal[ObjectType.IMPORT_FROM_STORAGE_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                estimated_completion_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ImportSourceProperties(_Model):
        data_dir_path: Optional[str]
        sas_token: Optional[str]
        storage_type: Optional[Union[str, ImportSourceStorageType]]
        storage_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_dir_path: Optional[str] = ..., 
                sas_token: Optional[str] = ..., 
                storage_type: Optional[Union[str, ImportSourceStorageType]] = ..., 
                storage_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        id: str
        name: str
        properties: Optional[LogFileProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogFileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.LogFileProperties(_Model):
        created_time: Optional[datetime]
        last_modified_time: Optional[datetime]
        size_in_kb: Optional[int]
        type: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_time: Optional[datetime] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                size_in_kb: Optional[int] = ..., 
                type: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.Maintenance(ProxyResource):
        id: str
        name: str
        properties: MaintenanceProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: MaintenanceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.MaintenancePolicy(_Model):
        patch_strategy: Optional[Union[str, PatchStrategy]]

        @overload
        def __init__(
                self, 
                *, 
                patch_strategy: Optional[Union[str, PatchStrategy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceProperties(_Model):
        maintenance_available_schedule_max_time: Optional[datetime]
        maintenance_available_schedule_min_time: Optional[datetime]
        maintenance_description: Optional[str]
        maintenance_end_time: Optional[datetime]
        maintenance_execution_end_time: Optional[datetime]
        maintenance_execution_start_time: Optional[datetime]
        maintenance_start_time: Optional[datetime]
        maintenance_state: Optional[Union[str, MaintenanceState]]
        maintenance_title: Optional[str]
        maintenance_type: Optional[Union[str, MaintenanceType]]
        provisioning_state: Optional[Union[str, MaintenanceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                maintenance_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.MaintenancePropertiesForUpdate(_Model):
        maintenance_start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                maintenance_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceUpdate(_Model):
        properties: Optional[MaintenancePropertiesForUpdate]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaintenancePropertiesForUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.MaintenanceWindow(_Model):
        batch_of_maintenance: Optional[Union[str, BatchOfMaintenance]]
        custom_window: Optional[str]
        day_of_week: Optional[int]
        start_hour: Optional[int]
        start_minute: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                batch_of_maintenance: Optional[Union[str, BatchOfMaintenance]] = ..., 
                custom_window: Optional[str] = ..., 
                day_of_week: Optional[int] = ..., 
                start_hour: Optional[int] = ..., 
                start_minute: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.mysqlflexibleservers.models.MySQLServerIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.MySQLServerSku(_Model):
        name: str
        tier: Union[str, ServerSkuTier]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tier: Union[str, ServerSkuTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.NameAvailability(_Model):
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


    class azure.mgmt.mysqlflexibleservers.models.NameAvailabilityRequest(_Model):
        name: str
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.Network(_Model):
        delegated_subnet_resource_id: Optional[str]
        private_dns_zone_resource_id: Optional[str]
        public_network_access: Optional[Union[str, EnableStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                delegated_subnet_resource_id: Optional[str] = ..., 
                private_dns_zone_resource_id: Optional[str] = ..., 
                public_network_access: Optional[Union[str, EnableStatusEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_AND_EXPORT_RESPONSE = "BackupAndExportResponse"
        IMPORT_FROM_STORAGE_RESPONSE = "ImportFromStorageResponse"


    class azure.mgmt.mysqlflexibleservers.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]
        properties: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                properties: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.OperationProgressResponseType(_Model):
        object_type: str

        @overload
        def __init__(
                self, 
                *, 
                object_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.OperationProgressResult(OperationStatusResult):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        properties: Optional[OperationProgressResponseType]
        resource_id: str
        start_time: datetime
        status: str

        @overload
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
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        properties: Optional[dict[str, Any]]
        resource_id: str
        start_time: datetime
        status: str

        @overload
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
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
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
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.mysqlflexibleservers.models.PatchStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        VIRTUAL_CANARY = "VirtualCanary"


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointConnectionListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateEndpointConnection]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateEndpointConnection]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.mysqlflexibleservers.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.Server(TrackedResource):
        id: str
        identity: Optional[MySQLServerIdentity]
        location: str
        name: str
        properties: Optional[ServerProperties]
        sku: Optional[MySQLServerSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[MySQLServerIdentity] = ..., 
                location: str, 
                properties: Optional[ServerProperties] = ..., 
                sku: Optional[MySQLServerSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerBackup(ProxyResource):
        id: str
        name: str
        properties: Optional[ServerBackupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerBackupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerBackupProperties(_Model):
        backup_type: Optional[str]
        completed_time: Optional[datetime]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_type: Optional[str] = ..., 
                completed_time: Optional[datetime] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerBackupPropertiesV2(_Model):
        backup_name_v2: Optional[str]
        backup_type: Optional[Union[str, BackupType]]
        completed_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_name_v2: Optional[str] = ..., 
                backup_type: Optional[Union[str, BackupType]] = ..., 
                completed_time: Optional[datetime] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerBackupV2(ProxyResource):
        id: str
        name: str
        properties: Optional[ServerBackupPropertiesV2]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerBackupPropertiesV2] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerDetachVNetParameter(_Model):
        public_network_access: Optional[Union[str, EnableStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, EnableStatusEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerEditionCapability(_Model):
        name: Optional[str]
        supported_server_versions: Optional[list[ServerVersionCapability]]
        supported_storage_editions: Optional[list[StorageEditionCapability]]


    class azure.mgmt.mysqlflexibleservers.models.ServerEditionCapabilityV2(_Model):
        default_sku: Optional[str]
        default_storage_size: Optional[int]
        name: Optional[str]
        supported_skus: Optional[list[SkuCapabilityV2]]
        supported_storage_editions: Optional[list[StorageEditionCapability]]


    class azure.mgmt.mysqlflexibleservers.models.ServerForUpdate(_Model):
        identity: Optional[MySQLServerIdentity]
        properties: Optional[ServerPropertiesForUpdate]
        sku: Optional[MySQLServerSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[MySQLServerIdentity] = ..., 
                properties: Optional[ServerPropertiesForUpdate] = ..., 
                sku: Optional[MySQLServerSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerGtidSetParameter(_Model):
        gtid_set: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                gtid_set: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerProperties(_Model):
        administrator_login: Optional[str]
        administrator_login_password: Optional[str]
        availability_zone: Optional[str]
        backup: Optional[Backup]
        create_mode: Optional[Union[str, CreateMode]]
        data_encryption: Optional[DataEncryption]
        database_port: Optional[int]
        full_version: Optional[str]
        fully_qualified_domain_name: Optional[str]
        high_availability: Optional[HighAvailability]
        import_source_properties: Optional[ImportSourceProperties]
        lower_case_table_names: Optional[int]
        maintenance_policy: Optional[MaintenancePolicy]
        maintenance_window: Optional[MaintenanceWindow]
        network: Optional[Network]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        replica_capacity: Optional[int]
        replication_role: Optional[Union[str, ReplicationRole]]
        restore_point_in_time: Optional[datetime]
        source_server_resource_id: Optional[str]
        state: Optional[Union[str, ServerState]]
        storage: Optional[Storage]
        version: Optional[Union[str, ServerVersion]]

        @overload
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
                import_source_properties: Optional[ImportSourceProperties] = ..., 
                lower_case_table_names: Optional[int] = ..., 
                maintenance_policy: Optional[MaintenancePolicy] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                network: Optional[Network] = ..., 
                replication_role: Optional[Union[str, ReplicationRole]] = ..., 
                restore_point_in_time: Optional[datetime] = ..., 
                source_server_resource_id: Optional[str] = ..., 
                storage: Optional[Storage] = ..., 
                version: Optional[Union[str, ServerVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerPropertiesForUpdate(_Model):
        administrator_login_password: Optional[str]
        backup: Optional[Backup]
        data_encryption: Optional[DataEncryption]
        high_availability: Optional[HighAvailability]
        maintenance_policy: Optional[MaintenancePolicy]
        maintenance_window: Optional[MaintenanceWindow]
        network: Optional[Network]
        replication_role: Optional[Union[str, ReplicationRole]]
        storage: Optional[Storage]
        version: Optional[Union[str, ServerVersion]]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                backup: Optional[Backup] = ..., 
                data_encryption: Optional[DataEncryption] = ..., 
                high_availability: Optional[HighAvailability] = ..., 
                maintenance_policy: Optional[MaintenancePolicy] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                network: Optional[Network] = ..., 
                replication_role: Optional[Union[str, ReplicationRole]] = ..., 
                storage: Optional[Storage] = ..., 
                version: Optional[Union[str, ServerVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ServerRestartParameter(_Model):
        max_failover_seconds: Optional[int]
        restart_with_failover: Optional[Union[str, EnableStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                max_failover_seconds: Optional[int] = ..., 
                restart_with_failover: Optional[Union[str, EnableStatusEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.mysqlflexibleservers.models.ServerVersionCapability(_Model):
        name: Optional[str]
        supported_skus: Optional[list[SkuCapability]]


    class azure.mgmt.mysqlflexibleservers.models.ServerVersionCapabilityV2(_Model):
        name: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.SkuCapability(_Model):
        name: Optional[str]
        supported_iops: Optional[int]
        supported_memory_per_v_core_mb: Optional[int]
        v_cores: Optional[int]


    class azure.mgmt.mysqlflexibleservers.models.SkuCapabilityV2(_Model):
        name: Optional[str]
        supported_ha_mode: Optional[list[str]]
        supported_iops: Optional[int]
        supported_memory_per_v_core_mb: Optional[int]
        supported_zones: Optional[list[str]]
        v_cores: Optional[int]


    class azure.mgmt.mysqlflexibleservers.models.Storage(_Model):
        auto_grow: Optional[Union[str, EnableStatusEnum]]
        auto_io_scaling: Optional[Union[str, EnableStatusEnum]]
        iops: Optional[int]
        log_on_disk: Optional[Union[str, EnableStatusEnum]]
        storage_redundancy: Optional[Union[str, StorageRedundancyEnum]]
        storage_size_gb: Optional[int]
        storage_sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_grow: Optional[Union[str, EnableStatusEnum]] = ..., 
                auto_io_scaling: Optional[Union[str, EnableStatusEnum]] = ..., 
                iops: Optional[int] = ..., 
                log_on_disk: Optional[Union[str, EnableStatusEnum]] = ..., 
                storage_redundancy: Optional[Union[str, StorageRedundancyEnum]] = ..., 
                storage_size_gb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.StorageEditionCapability(_Model):
        max_backup_interval_hours: Optional[int]
        max_backup_retention_days: Optional[int]
        max_storage_size: Optional[int]
        min_backup_interval_hours: Optional[int]
        min_backup_retention_days: Optional[int]
        min_storage_size: Optional[int]
        name: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.StorageRedundancyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL_REDUNDANCY = "LocalRedundancy"
        ZONE_REDUNDANCY = "ZoneRedundancy"


    class azure.mgmt.mysqlflexibleservers.models.SystemData(_Model):
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


    class azure.mgmt.mysqlflexibleservers.models.TrackedResource(Resource):
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


    class azure.mgmt.mysqlflexibleservers.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.mysqlflexibleservers.models.ValidateBackupResponse(_Model):
        properties: Optional[ValidateBackupResponseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidateBackupResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.ValidateBackupResponseProperties(_Model):
        number_of_containers: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                number_of_containers: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.VirtualNetworkSubnetUsageParameter(_Model):
        virtual_network_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                virtual_network_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mysqlflexibleservers.models.VirtualNetworkSubnetUsageResult(_Model):
        delegated_subnets_usage: Optional[list[DelegatedSubnetUsage]]
        location: Optional[str]
        subscription_id: Optional[str]


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
                *, 
                keyword: Optional[str] = ..., 
                page: Optional[int] = ..., 
                page_size: Optional[int] = ..., 
                tags: Optional[str] = ..., 
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


    class azure.mgmt.mysqlflexibleservers.operations.FabricMirroringSettingsOperations:

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
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                resource: FabricMirroringSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricMirroringSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                resource: FabricMirroringSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricMirroringSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricMirroringSetting]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'fabric_mirroring_settings_name', 'accept']}, api_versions_list=['2025-12-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                fabric_mirroring_settings_name: Union[str, FabricMirroringSettingsName], 
                **kwargs: Any
            ) -> FabricMirroringSetting: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'accept']}, api_versions_list=['2025-12-01-preview'])
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> FabricMirroringSettingListResult: ...


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
                capability_set_name: str, 
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
        @api_version_validation(method_added_on='2025-06-01-preview', params_added_on={'2025-06-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'backup_name']}, api_versions_list=['2025-06-01-preview', '2025-12-01-preview'])
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
            ) -> ItemPaged[PrivateLinkResource]: ...


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


namespace azure.mgmt.mysqlflexibleservers.types

    class azure.mgmt.mysqlflexibleservers.types.AdministratorProperties(TypedDict, total=False):
        key "administratorType": Union[str, AdministratorType]
        key "identityResourceId": str
        key "login": str
        key "sid": str
        key "tenantId": str
        administrator_type: Union[str, AdministratorType]
        identity_resource_id: str
        login: str
        sid: str
        tenant_id: str


    class azure.mgmt.mysqlflexibleservers.types.AdvancedThreatProtection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AdvancedThreatProtectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AdvancedThreatProtectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.AdvancedThreatProtectionForUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AdvancedThreatProtectionUpdateProperties', module='types')
        properties: AdvancedThreatProtectionUpdateProperties


    class azure.mgmt.mysqlflexibleservers.types.AdvancedThreatProtectionProperties(TypedDict, total=False):
        key "creationTime": str
        key "provisioningState": Union[str, AdvancedThreatProtectionProvisioningState]
        key "state": Union[str, AdvancedThreatProtectionState]
        creation_time: str
        provisioning_state: Union[str, AdvancedThreatProtectionProvisioningState]
        state: Union[str, AdvancedThreatProtectionState]


    class azure.mgmt.mysqlflexibleservers.types.AdvancedThreatProtectionUpdateProperties(TypedDict, total=False):
        key "state": Required[Union[str, AdvancedThreatProtectionState]]
        state: Union[str, AdvancedThreatProtectionState]


    class azure.mgmt.mysqlflexibleservers.types.AzureADAdministrator(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AdministratorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AdministratorProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.Backup(TypedDict, total=False):
        key "backupIntervalHours": int
        key "backupRetentionDays": int
        key "earliestRestoreDate": str
        key "geoRedundantBackup": Union[str, EnableStatusEnum]
        backup_interval_hours: int
        backup_retention_days: int
        earliest_restore_date: str
        geo_redundant_backup: Union[str, EnableStatusEnum]


    class azure.mgmt.mysqlflexibleservers.types.BackupAndExportRequest(BackupRequestBase):
        key "backupSettings": Required[BackupSettings]
        key "targetDetails": Required[BackupStoreDetails]
        backup_settings: BackupSettings
        target_details: BackupStoreDetails


    class azure.mgmt.mysqlflexibleservers.types.BackupRequestBase(TypedDict, total=False):
        key "backupSettings": Required[BackupSettings]
        backup_settings: BackupSettings


    class azure.mgmt.mysqlflexibleservers.types.BackupSettings(TypedDict, total=False):
        key "backupFormat": Union[str, BackupFormat]
        key "backupName": Required[str]
        backup_format: Union[str, BackupFormat]
        backup_name: str


    class azure.mgmt.mysqlflexibleservers.types.BackupStoreDetails(TypedDict, total=False):
        key "objectType": Required[Literal["FullBackupStoreDetails"]]
        key "sasUriList": Required[list[str]]
        object_type: Literal[FullBackupStoreDetails]
        sas_uri_list: list[str]


    class azure.mgmt.mysqlflexibleservers.types.Configuration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.ConfigurationForBatchUpdate(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ConfigurationForBatchUpdateProperties', module='types')
        name: str
        properties: ConfigurationForBatchUpdateProperties


    class azure.mgmt.mysqlflexibleservers.types.ConfigurationForBatchUpdateProperties(TypedDict, total=False):
        key "source": str
        key "value": str
        source: str
        value: str


    class azure.mgmt.mysqlflexibleservers.types.ConfigurationListForBatchUpdate(TypedDict, total=False):
        key "resetAllToDefault": Union[str, ResetAllToDefault]
        reset_all_to_default: Union[str, ResetAllToDefault]
        value: list[ConfigurationForBatchUpdate]


    class azure.mgmt.mysqlflexibleservers.types.ConfigurationProperties(TypedDict, total=False):
        key "allowedValues": str
        key "currentValue": str
        key "dataType": str
        key "defaultValue": str
        key "description": str
        key "documentationLink": str
        key "isConfigPendingRestart": Union[str, IsConfigPendingRestart]
        key "isDynamicConfig": Union[str, IsDynamicConfig]
        key "isReadOnly": Union[str, IsReadOnly]
        key "source": Union[str, ConfigurationSource]
        key "value": str
        allowed_values: str
        current_value: str
        data_type: str
        default_value: str
        description: str
        documentation_link: str
        is_config_pending_restart: Union[str, IsConfigPendingRestart]
        is_dynamic_config: Union[str, IsDynamicConfig]
        is_read_only: Union[str, IsReadOnly]
        source: Union[str, ConfigurationSource]
        value: str


    class azure.mgmt.mysqlflexibleservers.types.DataEncryption(TypedDict, total=False):
        key "geoBackupKeyURI": str
        key "geoBackupUserAssignedIdentityId": str
        key "primaryKeyURI": str
        key "primaryUserAssignedIdentityId": str
        key "type": Union[str, DataEncryptionType]
        geo_backup_key_uri: str
        geo_backup_user_assigned_identity_id: str
        primary_key_uri: str
        primary_user_assigned_identity_id: str
        type: Union[str, DataEncryptionType]


    class azure.mgmt.mysqlflexibleservers.types.Database(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DatabaseProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DatabaseProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.DatabaseProperties(TypedDict, total=False):
        key "charset": str
        key "collation": str
        charset: str
        collation: str


    class azure.mgmt.mysqlflexibleservers.types.FabricMirroringSetting(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FabricMirroringSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FabricMirroringSettingsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.FabricMirroringSettingsProperties(TypedDict, total=False):
        key "identityResourceId": str
        key "provisioningState": Union[str, FabricMirroringProvisioningState]
        key "state": Union[str, FabricMirroringState]
        identity_resource_id: str
        provisioning_state: Union[str, FabricMirroringProvisioningState]
        state: Union[str, FabricMirroringState]


    class azure.mgmt.mysqlflexibleservers.types.FirewallRule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[FirewallRuleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FirewallRuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.FirewallRuleProperties(TypedDict, total=False):
        key "endIpAddress": Required[str]
        key "startIpAddress": Required[str]
        end_ip_address: str
        start_ip_address: str


    class azure.mgmt.mysqlflexibleservers.types.FullBackupStoreDetails(TypedDict, total=False):
        key "objectType": Required[Literal["FullBackupStoreDetails"]]
        key "sasUriList": Required[list[str]]
        object_type: Literal[FullBackupStoreDetails]
        sas_uri_list: list[str]


    class azure.mgmt.mysqlflexibleservers.types.HighAvailability(TypedDict, total=False):
        key "mode": Union[str, HighAvailabilityMode]
        key "replicationMode": Union[str, ReplicationMode]
        key "standbyAvailabilityZone": str
        key "state": Union[str, HighAvailabilityState]
        mode: Union[str, HighAvailabilityMode]
        replication_mode: Union[str, ReplicationMode]
        standby_availability_zone: str
        state: Union[str, HighAvailabilityState]


    class azure.mgmt.mysqlflexibleservers.types.HighAvailabilityValidationEstimation(TypedDict, total=False):
        key "estimatedDowntime": int
        key "expectedStandbyAvailabilityZone": str
        key "scheduledStandbyAvailabilityZone": str
        estimated_downtime: int
        expected_standby_availability_zone: str
        scheduled_standby_availability_zone: str


    class azure.mgmt.mysqlflexibleservers.types.ImportSourceProperties(TypedDict, total=False):
        key "dataDirPath": str
        key "sasToken": str
        key "storageType": Union[str, ImportSourceStorageType]
        key "storageUrl": str
        data_dir_path: str
        sas_token: str
        storage_type: Union[str, ImportSourceStorageType]
        storage_url: str


    class azure.mgmt.mysqlflexibleservers.types.MaintenancePolicy(TypedDict, total=False):
        key "patchStrategy": Union[str, PatchStrategy]
        patch_strategy: Union[str, PatchStrategy]


    class azure.mgmt.mysqlflexibleservers.types.MaintenancePropertiesForUpdate(TypedDict, total=False):
        key "maintenanceStartTime": str
        maintenance_start_time: str


    class azure.mgmt.mysqlflexibleservers.types.MaintenanceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('MaintenancePropertiesForUpdate', module='types')
        properties: MaintenancePropertiesForUpdate


    class azure.mgmt.mysqlflexibleservers.types.MaintenanceWindow(TypedDict, total=False):
        key "batchOfMaintenance": Union[str, BatchOfMaintenance]
        key "customWindow": str
        key "dayOfWeek": int
        key "startHour": int
        key "startMinute": int
        batch_of_maintenance: Union[str, BatchOfMaintenance]
        custom_window: str
        day_of_week: int
        start_hour: int
        start_minute: int


    class azure.mgmt.mysqlflexibleservers.types.MySQLServerIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedServiceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.mysqlflexibleservers.types.MySQLServerSku(TypedDict, total=False):
        key "name": Required[str]
        key "tier": Required[Union[str, ServerSkuTier]]
        name: str
        tier: Union[str, ServerSkuTier]


    class azure.mgmt.mysqlflexibleservers.types.NameAvailabilityRequest(TypedDict, total=False):
        key "name": Required[str]
        key "type": str
        name: str
        type: str


    class azure.mgmt.mysqlflexibleservers.types.Network(TypedDict, total=False):
        key "delegatedSubnetResourceId": str
        key "privateDnsZoneResourceId": str
        key "publicNetworkAccess": Union[str, EnableStatusEnum]
        delegated_subnet_resource_id: str
        private_dns_zone_resource_id: str
        public_network_access: Union[str, EnableStatusEnum]


    class azure.mgmt.mysqlflexibleservers.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.mysqlflexibleservers.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.mysqlflexibleservers.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.mysqlflexibleservers.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.Server(TrackedResource):
        key "id": str
        key "identity": ForwardRef('MySQLServerIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ServerProperties', module='types')
        key "sku": ForwardRef('MySQLServerSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: MySQLServerIdentity
        location: str
        name: str
        properties: ServerProperties
        sku: MySQLServerSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.mysqlflexibleservers.types.ServerBackupPropertiesV2(TypedDict, total=False):
        key "backupNameV2": str
        key "backupType": Union[str, BackupType]
        key "completedTime": str
        key "provisioningState": Union[str, ProvisioningState]
        key "source": str
        backup_name_v2: str
        backup_type: Union[str, BackupType]
        completed_time: str
        provisioning_state: Union[str, ProvisioningState]
        source: str


    class azure.mgmt.mysqlflexibleservers.types.ServerBackupV2(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServerBackupPropertiesV2', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServerBackupPropertiesV2
        system_data: SystemData
        type: str


    class azure.mgmt.mysqlflexibleservers.types.ServerDetachVNetParameter(TypedDict, total=False):
        key "publicNetworkAccess": Union[str, EnableStatusEnum]
        public_network_access: Union[str, EnableStatusEnum]


    class azure.mgmt.mysqlflexibleservers.types.ServerForUpdate(TypedDict, total=False):
        key "identity": ForwardRef('MySQLServerIdentity', module='types')
        key "properties": ForwardRef('ServerPropertiesForUpdate', module='types')
        key "sku": ForwardRef('MySQLServerSku', module='types')
        identity: MySQLServerIdentity
        properties: ServerPropertiesForUpdate
        sku: MySQLServerSku
        tags: dict[str, str]


    class azure.mgmt.mysqlflexibleservers.types.ServerGtidSetParameter(TypedDict, total=False):
        key "gtidSet": str
        gtid_set: str


    class azure.mgmt.mysqlflexibleservers.types.ServerProperties(TypedDict, total=False):
        key "administratorLogin": str
        key "administratorLoginPassword": str
        key "availabilityZone": str
        key "backup": ForwardRef('Backup', module='types')
        key "createMode": Union[str, CreateMode]
        key "dataEncryption": ForwardRef('DataEncryption', module='types')
        key "databasePort": int
        key "fullVersion": str
        key "fullyQualifiedDomainName": str
        key "highAvailability": ForwardRef('HighAvailability', module='types')
        key "importSourceProperties": ForwardRef('ImportSourceProperties', module='types')
        key "lowerCaseTableNames": int
        key "maintenancePolicy": ForwardRef('MaintenancePolicy', module='types')
        key "maintenanceWindow": ForwardRef('MaintenanceWindow', module='types')
        key "network": ForwardRef('Network', module='types')
        key "replicaCapacity": int
        key "replicationRole": Union[str, ReplicationRole]
        key "restorePointInTime": str
        key "sourceServerResourceId": str
        key "state": Union[str, ServerState]
        key "storage": ForwardRef('Storage', module='types')
        key "version": Union[str, ServerVersion]
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
        import_source_properties: ImportSourceProperties
        lower_case_table_names: int
        maintenance_policy: MaintenancePolicy
        maintenance_window: MaintenanceWindow
        network: Network
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        replica_capacity: int
        replication_role: Union[str, ReplicationRole]
        restore_point_in_time: str
        source_server_resource_id: str
        state: Union[str, ServerState]
        storage: Storage
        version: Union[str, ServerVersion]


    class azure.mgmt.mysqlflexibleservers.types.ServerPropertiesForUpdate(TypedDict, total=False):
        key "administratorLoginPassword": str
        key "backup": ForwardRef('Backup', module='types')
        key "dataEncryption": ForwardRef('DataEncryption', module='types')
        key "highAvailability": ForwardRef('HighAvailability', module='types')
        key "maintenancePolicy": ForwardRef('MaintenancePolicy', module='types')
        key "maintenanceWindow": ForwardRef('MaintenanceWindow', module='types')
        key "network": ForwardRef('Network', module='types')
        key "replicationRole": Union[str, ReplicationRole]
        key "storage": ForwardRef('Storage', module='types')
        key "version": Union[str, ServerVersion]
        administrator_login_password: str
        backup: Backup
        data_encryption: DataEncryption
        high_availability: HighAvailability
        maintenance_policy: MaintenancePolicy
        maintenance_window: MaintenanceWindow
        network: Network
        replication_role: Union[str, ReplicationRole]
        storage: Storage
        version: Union[str, ServerVersion]


    class azure.mgmt.mysqlflexibleservers.types.ServerRestartParameter(TypedDict, total=False):
        key "maxFailoverSeconds": int
        key "restartWithFailover": Union[str, EnableStatusEnum]
        max_failover_seconds: int
        restart_with_failover: Union[str, EnableStatusEnum]


    class azure.mgmt.mysqlflexibleservers.types.Storage(TypedDict, total=False):
        key "autoGrow": Union[str, EnableStatusEnum]
        key "autoIoScaling": Union[str, EnableStatusEnum]
        key "iops": int
        key "logOnDisk": Union[str, EnableStatusEnum]
        key "storageRedundancy": Union[str, StorageRedundancyEnum]
        key "storageSizeGB": int
        key "storageSku": str
        auto_grow: Union[str, EnableStatusEnum]
        auto_io_scaling: Union[str, EnableStatusEnum]
        iops: int
        log_on_disk: Union[str, EnableStatusEnum]
        storage_redundancy: Union[str, StorageRedundancyEnum]
        storage_size_gb: int
        storage_sku: str


    class azure.mgmt.mysqlflexibleservers.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.mysqlflexibleservers.types.TrackedResource(Resource):
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


    class azure.mgmt.mysqlflexibleservers.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.mysqlflexibleservers.types.VirtualNetworkSubnetUsageParameter(TypedDict, total=False):
        key "virtualNetworkResourceId": str
        virtual_network_resource_id: str


```