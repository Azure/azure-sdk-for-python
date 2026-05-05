```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.postgresqlflexibleservers

    class azure.mgmt.postgresqlflexibleservers.PostgreSQLManagementClient: implements ContextManager 
        administrators_microsoft_entra: AdministratorsMicrosoftEntraOperations
        advanced_threat_protection_settings: AdvancedThreatProtectionSettingsOperations
        backups_automatic_and_on_demand: BackupsAutomaticAndOnDemandOperations
        backups_long_term_retention: BackupsLongTermRetentionOperations
        capabilities_by_location: CapabilitiesByLocationOperations
        capabilities_by_server: CapabilitiesByServerOperations
        captured_logs: CapturedLogsOperations
        configurations: ConfigurationsOperations
        databases: DatabasesOperations
        firewall_rules: FirewallRulesOperations
        migrations: MigrationsOperations
        name_availability: NameAvailabilityOperations
        operations: Operations
        private_dns_zone_suffix: PrivateDnsZoneSuffixOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        quota_usages: QuotaUsagesOperations
        replicas: ReplicasOperations
        server_threat_protection_settings: ServerThreatProtectionSettingsOperations
        servers: ServersOperations
        tuning_options: TuningOptionsOperations
        virtual_endpoints: VirtualEndpointsOperations
        virtual_network_subnet_usage: VirtualNetworkSubnetUsageOperations

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


namespace azure.mgmt.postgresqlflexibleservers.aio

    class azure.mgmt.postgresqlflexibleservers.aio.PostgreSQLManagementClient: implements AsyncContextManager 
        administrators_microsoft_entra: AdministratorsMicrosoftEntraOperations
        advanced_threat_protection_settings: AdvancedThreatProtectionSettingsOperations
        backups_automatic_and_on_demand: BackupsAutomaticAndOnDemandOperations
        backups_long_term_retention: BackupsLongTermRetentionOperations
        capabilities_by_location: CapabilitiesByLocationOperations
        capabilities_by_server: CapabilitiesByServerOperations
        captured_logs: CapturedLogsOperations
        configurations: ConfigurationsOperations
        databases: DatabasesOperations
        firewall_rules: FirewallRulesOperations
        migrations: MigrationsOperations
        name_availability: NameAvailabilityOperations
        operations: Operations
        private_dns_zone_suffix: PrivateDnsZoneSuffixOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        quota_usages: QuotaUsagesOperations
        replicas: ReplicasOperations
        server_threat_protection_settings: ServerThreatProtectionSettingsOperations
        servers: ServersOperations
        tuning_options: TuningOptionsOperations
        virtual_endpoints: VirtualEndpointsOperations
        virtual_network_subnet_usage: VirtualNetworkSubnetUsageOperations

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


namespace azure.mgmt.postgresqlflexibleservers.aio.operations

    class azure.mgmt.postgresqlflexibleservers.aio.operations.AdministratorsMicrosoftEntraOperations:

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
                object_id: str, 
                parameters: AdministratorMicrosoftEntraAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdministratorMicrosoftEntra]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdministratorMicrosoftEntra]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdministratorMicrosoftEntra]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> AdministratorMicrosoftEntra: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AdministratorMicrosoftEntra]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.AdvancedThreatProtectionSettingsOperations:

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
                threat_protection_name: Union[str, ThreatProtectionName], 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSettingsModel: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AdvancedThreatProtectionSettingsModel]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.BackupsAutomaticAndOnDemandOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupAutomaticAndOnDemand]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> BackupAutomaticAndOnDemand: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupAutomaticAndOnDemand]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.BackupsLongTermRetentionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: BackupsLongTermRetentionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupsLongTermRetentionResponse]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupsLongTermRetentionResponse]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupsLongTermRetentionResponse]: ...

        @overload
        async def check_prerequisites(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: LtrPreBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LtrPreBackupResponse: ...

        @overload
        async def check_prerequisites(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LtrPreBackupResponse: ...

        @overload
        async def check_prerequisites(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LtrPreBackupResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> BackupsLongTermRetentionOperation: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupsLongTermRetentionOperation]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.CapabilitiesByLocationOperations:

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
            ) -> AsyncItemPaged[Capability]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.CapabilitiesByServerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Capability]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.CapturedLogsOperations:

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
            ) -> AsyncItemPaged[CapturedLog]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: ConfigurationForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Configuration]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Configuration]: ...

        @overload
        async def begin_put(
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
                parameters: ConfigurationForUpdate, 
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
                parameters: JSON, 
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
                **kwargs: Any
            ) -> AsyncItemPaged[Configuration]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.DatabasesOperations:

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
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_create(
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


    class azure.mgmt.postgresqlflexibleservers.aio.operations.FirewallRulesOperations:

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
                parameters: JSON, 
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


    class azure.mgmt.postgresqlflexibleservers.aio.operations.MigrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> Optional[Migration]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: MigrationNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationNameAvailability: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationNameAvailability: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationNameAvailability: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: Migration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> Migration: ...

        @distributed_trace
        def list_by_target_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                *, 
                migration_list_filter: Optional[Union[str, MigrationListFilter]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Migration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: MigrationResourceForPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.NameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_globally(
                self, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        async def check_globally(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        async def check_globally(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        async def check_with_location(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        async def check_with_location(
                self, 
                location_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        async def check_with_location(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.PrivateDnsZoneSuffixOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> str: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
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
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
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
        async def get(
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
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.PrivateLinkResourcesOperations:

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


    class azure.mgmt.postgresqlflexibleservers.aio.operations.QuotaUsagesOperations:

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
            ) -> AsyncItemPaged[QuotaUsage]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.ReplicasOperations:

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


    class azure.mgmt.postgresqlflexibleservers.aio.operations.ServerThreatProtectionSettingsOperations:

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
                threat_protection_name: Union[str, ThreatProtectionName], 
                parameters: AdvancedThreatProtectionSettingsModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtectionSettingsModel]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                threat_protection_name: Union[str, ThreatProtectionName], 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtectionSettingsModel]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                threat_protection_name: Union[str, ThreatProtectionName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AdvancedThreatProtectionSettingsModel]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.ServersOperations:

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
                parameters: Server, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @overload
        async def begin_create_or_update(
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

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'accept']}, api_versions_list=['2026-01-01-preview'])
        async def begin_migrate_network_mode(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrateNetworkStatus]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Optional[RestartParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Optional[IO[bytes]] = None, 
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
                parameters: ServerForPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Server]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
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
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Server]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Server]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.TuningOptionsOperations:

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
                tuning_option: Union[str, TuningOptionParameterEnum], 
                **kwargs: Any
            ) -> TuningOptions: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TuningOptions]: ...

        @distributed_trace
        def list_recommendations(
                self, 
                resource_group_name: str, 
                server_name: str, 
                tuning_option: Union[str, TuningOptionParameterEnum], 
                *, 
                recommendation_type: Optional[Union[str, RecommendationTypeParameterEnum]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ObjectRecommendation]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.VirtualEndpointsOperations:

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
                virtual_endpoint_name: str, 
                parameters: VirtualEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: VirtualEndpointResourceForPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                **kwargs: Any
            ) -> VirtualEndpoint: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualEndpoint]: ...


    class azure.mgmt.postgresqlflexibleservers.aio.operations.VirtualNetworkSubnetUsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def list(
                self, 
                location_name: str, 
                parameters: VirtualNetworkSubnetUsageParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageModel: ...

        @overload
        async def list(
                self, 
                location_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageModel: ...

        @overload
        async def list(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageModel: ...


namespace azure.mgmt.postgresqlflexibleservers.models

    class azure.mgmt.postgresqlflexibleservers.models.AdminCredentials(_Model):
        source_server_password: str
        target_server_password: str

        @overload
        def __init__(
                self, 
                *, 
                source_server_password: str, 
                target_server_password: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdminCredentialsForPatch(_Model):
        source_server_password: Optional[str]
        target_server_password: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_server_password: Optional[str] = ..., 
                target_server_password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdministratorMicrosoftEntra(ProxyResource):
        id: str
        name: str
        properties: AdministratorMicrosoftEntraProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: AdministratorMicrosoftEntraProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdministratorMicrosoftEntraAdd(_Model):
        properties: Optional[AdministratorMicrosoftEntraPropertiesForAdd]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdministratorMicrosoftEntraPropertiesForAdd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdministratorMicrosoftEntraProperties(_Model):
        object_id: Optional[str]
        principal_name: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                principal_name: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdministratorMicrosoftEntraPropertiesForAdd(_Model):
        principal_name: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_name: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdvancedThreatProtectionSettingsModel(ProxyResource):
        id: str
        name: str
        properties: Optional[AdvancedThreatProtectionSettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdvancedThreatProtectionSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AdvancedThreatProtectionSettingsProperties(_Model):
        creation_time: Optional[datetime]
        state: Union[str, ThreatProtectionState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, ThreatProtectionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AuthConfig(_Model):
        active_directory_auth: Optional[Union[str, MicrosoftEntraAuth]]
        password_auth: Optional[Union[str, PasswordBasedAuth]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_directory_auth: Optional[Union[str, MicrosoftEntraAuth]] = ..., 
                password_auth: Optional[Union[str, PasswordBasedAuth]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AuthConfigForPatch(_Model):
        active_directory_auth: Optional[Union[str, MicrosoftEntraAuth]]
        password_auth: Optional[Union[str, PasswordBasedAuth]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_directory_auth: Optional[Union[str, MicrosoftEntraAuth]] = ..., 
                password_auth: Optional[Union[str, PasswordBasedAuth]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.AzureManagedDiskPerformanceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1 = "P1"
        P10 = "P10"
        P15 = "P15"
        P2 = "P2"
        P20 = "P20"
        P3 = "P3"
        P30 = "P30"
        P4 = "P4"
        P40 = "P40"
        P50 = "P50"
        P6 = "P6"
        P60 = "P60"
        P70 = "P70"
        P80 = "P80"


    class azure.mgmt.postgresqlflexibleservers.models.Backup(_Model):
        backup_retention_days: Optional[int]
        earliest_restore_date: Optional[datetime]
        geo_redundant_backup: Optional[Union[str, GeographicallyRedundantBackup]]

        @overload
        def __init__(
                self, 
                *, 
                backup_retention_days: Optional[int] = ..., 
                geo_redundant_backup: Optional[Union[str, GeographicallyRedundantBackup]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupAutomaticAndOnDemand(ProxyResource):
        id: str
        name: str
        properties: Optional[BackupAutomaticAndOnDemandProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BackupAutomaticAndOnDemandProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupAutomaticAndOnDemandProperties(_Model):
        backup_type: Optional[Union[str, BackupType]]
        completed_time: Optional[datetime]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_type: Optional[Union[str, BackupType]] = ..., 
                completed_time: Optional[datetime] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupForPatch(_Model):
        backup_retention_days: Optional[int]
        earliest_restore_date: Optional[datetime]
        geo_redundant_backup: Optional[Union[str, GeographicallyRedundantBackup]]

        @overload
        def __init__(
                self, 
                *, 
                backup_retention_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupRequestBase(_Model):
        backup_settings: BackupSettings

        @overload
        def __init__(
                self, 
                *, 
                backup_settings: BackupSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupSettings(_Model):
        backup_name: str

        @overload
        def __init__(
                self, 
                *, 
                backup_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupStoreDetails(_Model):
        sas_uri_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                sas_uri_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_ON_DEMAND = "Customer On-Demand"
        FULL = "Full"


    class azure.mgmt.postgresqlflexibleservers.models.BackupsLongTermRetentionOperation(ProxyResource):
        id: str
        name: str
        properties: Optional[LtrBackupOperationResponseProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LtrBackupOperationResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupsLongTermRetentionRequest(BackupRequestBase):
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


    class azure.mgmt.postgresqlflexibleservers.models.BackupsLongTermRetentionResponse(_Model):
        properties: Optional[LtrBackupOperationResponseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LtrBackupOperationResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.BackupsLongTermRetentionResponseProperties(_Model):
        number_of_containers: int

        @overload
        def __init__(
                self, 
                *, 
                number_of_containers: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.Cancel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.postgresqlflexibleservers.models.Capability(CapabilityBase):
        fast_provisioning_supported: Optional[Union[str, FastProvisioningSupport]]
        geo_backup_supported: Optional[Union[str, GeographicallyRedundantBackupSupport]]
        name: Optional[str]
        online_resize_supported: Optional[Union[str, OnlineStorageResizeSupport]]
        reason: str
        restricted: Optional[Union[str, LocationRestricted]]
        status: Union[str, CapabilityStatus]
        storage_auto_growth_supported: Optional[Union[str, StorageAutoGrowthSupport]]
        supported_fast_provisioning_editions: Optional[list[FastProvisioningEditionCapability]]
        supported_features: Optional[list[SupportedFeature]]
        supported_server_editions: Optional[list[ServerEditionCapability]]
        supported_server_versions: Optional[list[ServerVersionCapability]]
        zone_redundant_ha_and_geo_backup_supported: Optional[Union[str, ZoneRedundantHighAvailabilityAndGeographicallyRedundantBackupSupport]]
        zone_redundant_ha_supported: Optional[Union[str, ZoneRedundantHighAvailabilitySupport]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.CapabilityBase(_Model):
        reason: Optional[str]
        status: Optional[Union[str, CapabilityStatus]]


    class azure.mgmt.postgresqlflexibleservers.models.CapabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEFAULT = "Default"
        DISABLED = "Disabled"
        VISIBLE = "Visible"


    class azure.mgmt.postgresqlflexibleservers.models.CapturedLog(ProxyResource):
        id: str
        name: str
        properties: Optional[CapturedLogProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapturedLogProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.CapturedLogProperties(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.postgresqlflexibleservers.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.Cluster(_Model):
        cluster_size: Optional[int]
        default_database_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_size: Optional[int] = ..., 
                default_database_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.Configuration(ProxyResource):
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


    class azure.mgmt.postgresqlflexibleservers.models.ConfigurationDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Boolean"
        ENUMERATION = "Enumeration"
        INTEGER = "Integer"
        NUMERIC = "Numeric"
        SET = "Set"
        STRING = "String"


    class azure.mgmt.postgresqlflexibleservers.models.ConfigurationForUpdate(_Model):
        properties: Optional[ConfigurationProperties]

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


    class azure.mgmt.postgresqlflexibleservers.models.ConfigurationProperties(_Model):
        allowed_values: Optional[str]
        data_type: Optional[Union[str, ConfigurationDataType]]
        default_value: Optional[str]
        description: Optional[str]
        documentation_link: Optional[str]
        is_config_pending_restart: Optional[bool]
        is_dynamic_config: Optional[bool]
        is_read_only: Optional[bool]
        source: Optional[str]
        unit: Optional[str]
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


    class azure.mgmt.postgresqlflexibleservers.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DEFAULT = "Default"
        GEO_RESTORE = "GeoRestore"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"
        REPLICA = "Replica"
        REVIVE_DROPPED = "ReviveDropped"
        UPDATE = "Update"


    class azure.mgmt.postgresqlflexibleservers.models.CreateModeForPatch(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        UPDATE = "Update"


    class azure.mgmt.postgresqlflexibleservers.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.postgresqlflexibleservers.models.DataEncryption(_Model):
        geo_backup_encryption_key_status: Optional[Union[str, EncryptionKeyStatus]]
        geo_backup_key_uri: Optional[str]
        geo_backup_user_assigned_identity_id: Optional[str]
        primary_encryption_key_status: Optional[Union[str, EncryptionKeyStatus]]
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


    class azure.mgmt.postgresqlflexibleservers.models.DataEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        SYSTEM_MANAGED = "SystemManaged"


    class azure.mgmt.postgresqlflexibleservers.models.Database(ProxyResource):
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


    class azure.mgmt.postgresqlflexibleservers.models.DatabaseMigrationState(_Model):
        applied_changes: Optional[int]
        cdc_delete_counter: Optional[int]
        cdc_insert_counter: Optional[int]
        cdc_update_counter: Optional[int]
        database_name: Optional[str]
        ended_on: Optional[datetime]
        full_load_completed_tables: Optional[int]
        full_load_errored_tables: Optional[int]
        full_load_loading_tables: Optional[int]
        full_load_queued_tables: Optional[int]
        incoming_changes: Optional[int]
        latency: Optional[int]
        message: Optional[str]
        migration_operation: Optional[str]
        migration_state: Optional[Union[str, MigrationDatabaseState]]
        started_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                applied_changes: Optional[int] = ..., 
                cdc_delete_counter: Optional[int] = ..., 
                cdc_insert_counter: Optional[int] = ..., 
                cdc_update_counter: Optional[int] = ..., 
                database_name: Optional[str] = ..., 
                ended_on: Optional[datetime] = ..., 
                full_load_completed_tables: Optional[int] = ..., 
                full_load_errored_tables: Optional[int] = ..., 
                full_load_loading_tables: Optional[int] = ..., 
                full_load_queued_tables: Optional[int] = ..., 
                incoming_changes: Optional[int] = ..., 
                latency: Optional[int] = ..., 
                message: Optional[str] = ..., 
                migration_operation: Optional[str] = ..., 
                migration_state: Optional[Union[str, MigrationDatabaseState]] = ..., 
                started_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.DatabaseProperties(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.DbLevelValidationStatus(_Model):
        database_name: Optional[str]
        ended_on: Optional[datetime]
        started_on: Optional[datetime]
        summary: Optional[list[ValidationSummaryItem]]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                ended_on: Optional[datetime] = ..., 
                started_on: Optional[datetime] = ..., 
                summary: Optional[list[ValidationSummaryItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.DbServerMetadata(_Model):
        location: Optional[str]
        sku: Optional[ServerSku]
        storage_mb: Optional[int]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[ServerSku] = ..., 
                storage_mb: Optional[int] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.DelegatedSubnetUsage(_Model):
        subnet_name: Optional[str]
        usage: Optional[int]


    class azure.mgmt.postgresqlflexibleservers.models.EncryptionKeyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.postgresqlflexibleservers.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.postgresqlflexibleservers.models.FailoverMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCED_FAILOVER = "ForcedFailover"
        FORCED_SWITCHOVER = "ForcedSwitchover"
        PLANNED_FAILOVER = "PlannedFailover"
        PLANNED_SWITCHOVER = "PlannedSwitchover"


    class azure.mgmt.postgresqlflexibleservers.models.FastProvisioningEditionCapability(CapabilityBase):
        reason: str
        server_count: Optional[int]
        status: Union[str, CapabilityStatus]
        supported_server_versions: Optional[str]
        supported_sku: Optional[str]
        supported_storage_gb: Optional[int]
        supported_tier: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.FastProvisioningSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.FeatureStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.FirewallRule(ProxyResource):
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


    class azure.mgmt.postgresqlflexibleservers.models.FirewallRuleProperties(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.GeographicallyRedundantBackup(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.GeographicallyRedundantBackupSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.HighAvailability(_Model):
        mode: Optional[Union[str, PostgreSqlFlexibleServerHighAvailabilityMode]]
        standby_availability_zone: Optional[str]
        state: Optional[Union[str, HighAvailabilityState]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, PostgreSqlFlexibleServerHighAvailabilityMode]] = ..., 
                standby_availability_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.HighAvailabilityForPatch(_Model):
        mode: Optional[Union[str, PostgreSqlFlexibleServerHighAvailabilityMode]]
        standby_availability_zone: Optional[str]
        state: Optional[Union[str, HighAvailabilityState]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, PostgreSqlFlexibleServerHighAvailabilityMode]] = ..., 
                standby_availability_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.HighAvailabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SAME_ZONE = "SameZone"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.postgresqlflexibleservers.models.HighAvailabilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING_STANDBY = "CreatingStandby"
        FAILING_OVER = "FailingOver"
        HEALTHY = "Healthy"
        NOT_ENABLED = "NotEnabled"
        REMOVING_STANDBY = "RemovingStandby"
        REPLICATING_DATA = "ReplicatingData"


    class azure.mgmt.postgresqlflexibleservers.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.postgresqlflexibleservers.models.ImpactRecord(_Model):
        absolute_value: Optional[float]
        dimension_name: Optional[str]
        query_id: Optional[int]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                absolute_value: Optional[float] = ..., 
                dimension_name: Optional[str] = ..., 
                query_id: Optional[int] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.LocationRestricted(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.LogSpecification(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.LogicalReplicationOnSourceServer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.postgresqlflexibleservers.models.LtrBackupOperationResponseProperties(_Model):
        backup_metadata: Optional[str]
        backup_name: Optional[str]
        data_transferred_in_bytes: Optional[int]
        datasource_size_in_bytes: Optional[int]
        end_time: Optional[datetime]
        error_code: Optional[str]
        error_message: Optional[str]
        percent_complete: Optional[float]
        start_time: datetime
        status: Union[str, ExecutionStatus]

        @overload
        def __init__(
                self, 
                *, 
                backup_metadata: Optional[str] = ..., 
                backup_name: Optional[str] = ..., 
                data_transferred_in_bytes: Optional[int] = ..., 
                datasource_size_in_bytes: Optional[int] = ..., 
                end_time: Optional[datetime] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: datetime, 
                status: Union[str, ExecutionStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.LtrPreBackupRequest(BackupRequestBase):
        backup_settings: BackupSettings

        @overload
        def __init__(
                self, 
                *, 
                backup_settings: BackupSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.LtrPreBackupResponse(_Model):
        properties: BackupsLongTermRetentionResponseProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: BackupsLongTermRetentionResponseProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MaintenanceWindow(_Model):
        custom_window: Optional[str]
        day_of_week: Optional[int]
        start_hour: Optional[int]
        start_minute: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                custom_window: Optional[str] = ..., 
                day_of_week: Optional[int] = ..., 
                start_hour: Optional[int] = ..., 
                start_minute: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MaintenanceWindowForPatch(_Model):
        custom_window: Optional[str]
        day_of_week: Optional[int]
        start_hour: Optional[int]
        start_minute: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                custom_window: Optional[str] = ..., 
                day_of_week: Optional[int] = ..., 
                start_hour: Optional[int] = ..., 
                start_minute: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        category: Optional[str]
        display_description: Optional[str]
        display_name: Optional[str]
        name: Optional[str]
        supported_aggregation_types: Optional[list[str]]
        supported_time_grain_types: Optional[list[str]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                category: Optional[str] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MicrosoftEntraAuth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.MigrateNetworkStatus(_Model):
        resource_group_name: Optional[str]
        server_name: Optional[str]
        state: Optional[Union[str, NetworkMigrationState]]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_group_name: Optional[str] = ..., 
                server_name: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrateRolesAndPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.postgresqlflexibleservers.models.Migration(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MigrationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MigrationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationDatabaseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELING = "Canceling"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        WAITING_FOR_CUTOVER_TRIGGER = "WaitingForCutoverTrigger"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationListFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ALL = "All"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFLINE = "Offline"
        ONLINE = "Online"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationNameAvailability(_Model):
        message: Optional[str]
        name: str
        name_available: Optional[bool]
        reason: Optional[Union[str, MigrationNameAvailabilityReason]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIGRATE = "Migrate"
        VALIDATE = "Validate"
        VALIDATE_AND_MIGRATE = "ValidateAndMigrate"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationProperties(_Model):
        cancel: Optional[Union[str, Cancel]]
        current_status: Optional[MigrationStatus]
        dbs_to_cancel_migration_on: Optional[list[str]]
        dbs_to_migrate: Optional[list[str]]
        dbs_to_trigger_cutover_on: Optional[list[str]]
        migrate_roles: Optional[Union[str, MigrateRolesAndPermissions]]
        migration_id: Optional[str]
        migration_instance_resource_id: Optional[str]
        migration_mode: Optional[Union[str, MigrationMode]]
        migration_option: Optional[Union[str, MigrationOption]]
        migration_window_end_time_in_utc: Optional[datetime]
        migration_window_start_time_in_utc: Optional[datetime]
        overwrite_dbs_in_target: Optional[Union[str, OverwriteDatabasesOnTargetServer]]
        secret_parameters: Optional[MigrationSecretParameters]
        setup_logical_replication_on_source_db_if_needed: Optional[Union[str, LogicalReplicationOnSourceServer]]
        source_db_server_fully_qualified_domain_name: Optional[str]
        source_db_server_metadata: Optional[DbServerMetadata]
        source_db_server_resource_id: Optional[str]
        source_type: Optional[Union[str, SourceType]]
        ssl_mode: Optional[Union[str, SslMode]]
        start_data_migration: Optional[Union[str, StartDataMigration]]
        target_db_server_fully_qualified_domain_name: Optional[str]
        target_db_server_metadata: Optional[DbServerMetadata]
        target_db_server_resource_id: Optional[str]
        trigger_cutover: Optional[Union[str, TriggerCutover]]

        @overload
        def __init__(
                self, 
                *, 
                cancel: Optional[Union[str, Cancel]] = ..., 
                dbs_to_cancel_migration_on: Optional[list[str]] = ..., 
                dbs_to_migrate: Optional[list[str]] = ..., 
                dbs_to_trigger_cutover_on: Optional[list[str]] = ..., 
                migrate_roles: Optional[Union[str, MigrateRolesAndPermissions]] = ..., 
                migration_instance_resource_id: Optional[str] = ..., 
                migration_mode: Optional[Union[str, MigrationMode]] = ..., 
                migration_option: Optional[Union[str, MigrationOption]] = ..., 
                migration_window_end_time_in_utc: Optional[datetime] = ..., 
                migration_window_start_time_in_utc: Optional[datetime] = ..., 
                overwrite_dbs_in_target: Optional[Union[str, OverwriteDatabasesOnTargetServer]] = ..., 
                secret_parameters: Optional[MigrationSecretParameters] = ..., 
                setup_logical_replication_on_source_db_if_needed: Optional[Union[str, LogicalReplicationOnSourceServer]] = ..., 
                source_db_server_fully_qualified_domain_name: Optional[str] = ..., 
                source_db_server_resource_id: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceType]] = ..., 
                ssl_mode: Optional[Union[str, SslMode]] = ..., 
                start_data_migration: Optional[Union[str, StartDataMigration]] = ..., 
                target_db_server_fully_qualified_domain_name: Optional[str] = ..., 
                trigger_cutover: Optional[Union[str, TriggerCutover]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationPropertiesForPatch(_Model):
        cancel: Optional[Union[str, Cancel]]
        dbs_to_cancel_migration_on: Optional[list[str]]
        dbs_to_migrate: Optional[list[str]]
        dbs_to_trigger_cutover_on: Optional[list[str]]
        migrate_roles: Optional[Union[str, MigrateRolesAndPermissions]]
        migration_mode: Optional[Union[str, MigrationMode]]
        migration_window_start_time_in_utc: Optional[datetime]
        overwrite_dbs_in_target: Optional[Union[str, OverwriteDatabasesOnTargetServer]]
        secret_parameters: Optional[MigrationSecretParametersForPatch]
        setup_logical_replication_on_source_db_if_needed: Optional[Union[str, LogicalReplicationOnSourceServer]]
        source_db_server_fully_qualified_domain_name: Optional[str]
        source_db_server_resource_id: Optional[str]
        start_data_migration: Optional[Union[str, StartDataMigration]]
        target_db_server_fully_qualified_domain_name: Optional[str]
        trigger_cutover: Optional[Union[str, TriggerCutover]]

        @overload
        def __init__(
                self, 
                *, 
                cancel: Optional[Union[str, Cancel]] = ..., 
                dbs_to_cancel_migration_on: Optional[list[str]] = ..., 
                dbs_to_migrate: Optional[list[str]] = ..., 
                dbs_to_trigger_cutover_on: Optional[list[str]] = ..., 
                migrate_roles: Optional[Union[str, MigrateRolesAndPermissions]] = ..., 
                migration_mode: Optional[Union[str, MigrationMode]] = ..., 
                migration_window_start_time_in_utc: Optional[datetime] = ..., 
                overwrite_dbs_in_target: Optional[Union[str, OverwriteDatabasesOnTargetServer]] = ..., 
                secret_parameters: Optional[MigrationSecretParametersForPatch] = ..., 
                setup_logical_replication_on_source_db_if_needed: Optional[Union[str, LogicalReplicationOnSourceServer]] = ..., 
                source_db_server_fully_qualified_domain_name: Optional[str] = ..., 
                source_db_server_resource_id: Optional[str] = ..., 
                start_data_migration: Optional[Union[str, StartDataMigration]] = ..., 
                target_db_server_fully_qualified_domain_name: Optional[str] = ..., 
                trigger_cutover: Optional[Union[str, TriggerCutover]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationResourceForPatch(_Model):
        properties: Optional[MigrationPropertiesForPatch]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MigrationPropertiesForPatch] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationSecretParameters(_Model):
        admin_credentials: AdminCredentials
        source_server_username: Optional[str]
        target_server_username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_credentials: AdminCredentials, 
                source_server_username: Optional[str] = ..., 
                target_server_username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationSecretParametersForPatch(_Model):
        admin_credentials: Optional[AdminCredentialsForPatch]
        source_server_username: Optional[str]
        target_server_username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_credentials: Optional[AdminCredentialsForPatch] = ..., 
                source_server_username: Optional[str] = ..., 
                target_server_username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.MigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CLEANING_UP = "CleaningUp"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        VALIDATION_FAILED = "ValidationFailed"
        WAITING_FOR_USER_ACTION = "WaitingForUserAction"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationStatus(_Model):
        current_sub_state_details: Optional[MigrationSubstateDetails]
        error: Optional[str]
        state: Optional[Union[str, MigrationState]]


    class azure.mgmt.postgresqlflexibleservers.models.MigrationSubstate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELING_REQUESTED_DB_MIGRATIONS = "CancelingRequestedDBMigrations"
        COMPLETED = "Completed"
        COMPLETING_MIGRATION = "CompletingMigration"
        MIGRATING_DATA = "MigratingData"
        PERFORMING_PRE_REQUISITE_STEPS = "PerformingPreRequisiteSteps"
        VALIDATION_IN_PROGRESS = "ValidationInProgress"
        WAITING_FOR_CUTOVER_TRIGGER = "WaitingForCutoverTrigger"
        WAITING_FOR_DATA_MIGRATION_SCHEDULING = "WaitingForDataMigrationScheduling"
        WAITING_FOR_DATA_MIGRATION_WINDOW = "WaitingForDataMigrationWindow"
        WAITING_FOR_DBS_TO_MIGRATE_SPECIFICATION = "WaitingForDBsToMigrateSpecification"
        WAITING_FOR_LOGICAL_REPLICATION_SETUP_REQUEST_ON_SOURCE_DB = "WaitingForLogicalReplicationSetupRequestOnSourceDB"
        WAITING_FOR_TARGET_DB_OVERWRITE_CONFIRMATION = "WaitingForTargetDBOverwriteConfirmation"


    class azure.mgmt.postgresqlflexibleservers.models.MigrationSubstateDetails(_Model):
        current_sub_state: Optional[Union[str, MigrationSubstate]]
        db_details: Optional[dict[str, DatabaseMigrationState]]
        validation_details: Optional[ValidationDetails]

        @overload
        def __init__(
                self, 
                *, 
                db_details: Optional[dict[str, DatabaseMigrationState]] = ..., 
                validation_details: Optional[ValidationDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.NameAvailabilityModel(CheckNameAvailabilityResponse):
        message: str
        name: Optional[str]
        name_available: bool
        reason: Union[str, CheckNameAvailabilityReason]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.NameProperty(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.Network(_Model):
        delegated_subnet_resource_id: Optional[str]
        private_dns_zone_arm_resource_id: Optional[str]
        public_network_access: Optional[Union[str, ServerPublicNetworkAccessState]]

        @overload
        def __init__(
                self, 
                *, 
                delegated_subnet_resource_id: Optional[str] = ..., 
                private_dns_zone_arm_resource_id: Optional[str] = ..., 
                public_network_access: Optional[Union[str, ServerPublicNetworkAccessState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.NetworkMigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCEL_IN_PROGRESS = "CancelInProgress"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.postgresqlflexibleservers.models.ObjectRecommendation(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[ObjectRecommendationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ObjectRecommendationDetails(_Model):
        database_name: Optional[str]
        included_columns: Optional[list[str]]
        index_columns: Optional[list[str]]
        index_name: Optional[str]
        index_type: Optional[str]
        schema: Optional[str]
        table: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                included_columns: Optional[list[str]] = ..., 
                index_columns: Optional[list[str]] = ..., 
                index_name: Optional[str] = ..., 
                index_type: Optional[str] = ..., 
                schema: Optional[str] = ..., 
                table: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ObjectRecommendationProperties(_Model):
        analyzed_workload: Optional[ObjectRecommendationPropertiesAnalyzedWorkload]
        current_state: Optional[str]
        details: Optional[ObjectRecommendationDetails]
        estimated_impact: Optional[list[ImpactRecord]]
        implementation_details: Optional[ObjectRecommendationPropertiesImplementationDetails]
        improved_query_ids: Optional[list[int]]
        initial_recommended_time: Optional[datetime]
        last_recommended_time: Optional[datetime]
        recommendation_reason: Optional[str]
        recommendation_type: Optional[Union[str, RecommendationTypeEnum]]
        times_recommended: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                analyzed_workload: Optional[ObjectRecommendationPropertiesAnalyzedWorkload] = ..., 
                current_state: Optional[str] = ..., 
                implementation_details: Optional[ObjectRecommendationPropertiesImplementationDetails] = ..., 
                improved_query_ids: Optional[list[int]] = ..., 
                initial_recommended_time: Optional[datetime] = ..., 
                last_recommended_time: Optional[datetime] = ..., 
                recommendation_reason: Optional[str] = ..., 
                recommendation_type: Optional[Union[str, RecommendationTypeEnum]] = ..., 
                times_recommended: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ObjectRecommendationPropertiesAnalyzedWorkload(_Model):
        end_time: Optional[datetime]
        query_count: Optional[int]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                query_count: Optional[int] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ObjectRecommendationPropertiesImplementationDetails(_Model):
        method: Optional[str]
        script: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                method: Optional[str] = ..., 
                script: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.OnlineStorageResizeSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, OperationOrigin]]
        properties: Optional[OperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                is_data_action: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM = "system"
        USER = "user"


    class azure.mgmt.postgresqlflexibleservers.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.OverwriteDatabasesOnTargetServer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.postgresqlflexibleservers.models.PasswordBasedAuth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.PostgreSqlFlexibleServerHighAvailabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        SAME_ZONE = "SameZone"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.postgresqlflexibleservers.models.PostgresMajorVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EIGHTEEN = "18"
        ELEVEN = "11"
        FIFTEEN = "15"
        FOURTEEN = "14"
        SEVENTEEN = "17"
        SIXTEEN = "16"
        THIRTEEN = "13"
        TWELVE = "12"


    class azure.mgmt.postgresqlflexibleservers.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.postgresqlflexibleservers.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.postgresqlflexibleservers.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.postgresqlflexibleservers.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.postgresqlflexibleservers.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.postgresqlflexibleservers.models.QuotaUsage(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[NameProperty]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[NameProperty] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ReadReplicaPromoteMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDALONE = "Standalone"
        SWITCHOVER = "Switchover"


    class azure.mgmt.postgresqlflexibleservers.models.ReadReplicaPromoteOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCED = "Forced"
        PLANNED = "Planned"


    class azure.mgmt.postgresqlflexibleservers.models.RecommendationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYZE_TABLE = "AnalyzeTable"
        CREATE_INDEX = "CreateIndex"
        DROP_INDEX = "DropIndex"
        RE_INDEX = "ReIndex"
        VACUUM_TABLE = "VacuumTable"


    class azure.mgmt.postgresqlflexibleservers.models.RecommendationTypeParameterEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYZE_TABLE = "AnalyzeTable"
        CREATE_INDEX = "CreateIndex"
        DROP_INDEX = "DropIndex"
        RE_INDEX = "ReIndex"
        VACUUM_TABLE = "VacuumTable"


    class azure.mgmt.postgresqlflexibleservers.models.Replica(_Model):
        capacity: Optional[int]
        promote_mode: Optional[Union[str, ReadReplicaPromoteMode]]
        promote_option: Optional[Union[str, ReadReplicaPromoteOption]]
        replication_state: Optional[Union[str, ReplicationState]]
        role: Optional[Union[str, ReplicationRole]]

        @overload
        def __init__(
                self, 
                *, 
                promote_mode: Optional[Union[str, ReadReplicaPromoteMode]] = ..., 
                promote_option: Optional[Union[str, ReadReplicaPromoteOption]] = ..., 
                role: Optional[Union[str, ReplicationRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNC_REPLICA = "AsyncReplica"
        GEO_ASYNC_REPLICA = "GeoAsyncReplica"
        NONE = "None"
        PRIMARY = "Primary"


    class azure.mgmt.postgresqlflexibleservers.models.ReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        BROKEN = "Broken"
        CATCHUP = "Catchup"
        PROVISIONING = "Provisioning"
        RECONFIGURING = "Reconfiguring"
        UPDATING = "Updating"


    class azure.mgmt.postgresqlflexibleservers.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.RestartParameter(_Model):
        failover_mode: Optional[Union[str, FailoverMode]]
        restart_with_failover: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                failover_mode: Optional[Union[str, FailoverMode]] = ..., 
                restart_with_failover: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.Server(TrackedResource):
        id: str
        identity: Optional[UserAssignedIdentity]
        location: str
        name: str
        properties: Optional[ServerProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedIdentity] = ..., 
                location: str, 
                properties: Optional[ServerProperties] = ..., 
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


    class azure.mgmt.postgresqlflexibleservers.models.ServerEditionCapability(CapabilityBase):
        default_sku_name: Optional[str]
        name: Optional[str]
        reason: str
        status: Union[str, CapabilityStatus]
        supported_server_skus: Optional[list[ServerSkuCapability]]
        supported_storage_editions: Optional[list[StorageEditionCapability]]


    class azure.mgmt.postgresqlflexibleservers.models.ServerForPatch(_Model):
        identity: Optional[UserAssignedIdentity]
        properties: Optional[ServerPropertiesForPatch]
        sku: Optional[SkuForPatch]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedIdentity] = ..., 
                properties: Optional[ServerPropertiesForPatch] = ..., 
                sku: Optional[SkuForPatch] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ServerProperties(_Model):
        administrator_login: Optional[str]
        administrator_login_password: Optional[str]
        auth_config: Optional[AuthConfig]
        availability_zone: Optional[str]
        backup: Optional[Backup]
        cluster: Optional[Cluster]
        create_mode: Optional[Union[str, CreateMode]]
        data_encryption: Optional[DataEncryption]
        fully_qualified_domain_name: Optional[str]
        high_availability: Optional[HighAvailability]
        maintenance_window: Optional[MaintenanceWindow]
        minor_version: Optional[str]
        network: Optional[Network]
        point_in_time_utc: Optional[datetime]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        replica: Optional[Replica]
        replica_capacity: Optional[int]
        replication_role: Optional[Union[str, ReplicationRole]]
        source_server_resource_id: Optional[str]
        state: Optional[Union[str, ServerState]]
        storage: Optional[Storage]
        version: Optional[Union[str, PostgresMajorVersion]]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login: Optional[str] = ..., 
                administrator_login_password: Optional[str] = ..., 
                auth_config: Optional[AuthConfig] = ..., 
                availability_zone: Optional[str] = ..., 
                backup: Optional[Backup] = ..., 
                cluster: Optional[Cluster] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                data_encryption: Optional[DataEncryption] = ..., 
                high_availability: Optional[HighAvailability] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                network: Optional[Network] = ..., 
                point_in_time_utc: Optional[datetime] = ..., 
                replica: Optional[Replica] = ..., 
                replication_role: Optional[Union[str, ReplicationRole]] = ..., 
                source_server_resource_id: Optional[str] = ..., 
                storage: Optional[Storage] = ..., 
                version: Optional[Union[str, PostgresMajorVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ServerPropertiesForPatch(_Model):
        administrator_login: Optional[str]
        administrator_login_password: Optional[str]
        auth_config: Optional[AuthConfigForPatch]
        availability_zone: Optional[str]
        backup: Optional[BackupForPatch]
        cluster: Optional[Cluster]
        create_mode: Optional[Union[str, CreateModeForPatch]]
        data_encryption: Optional[DataEncryption]
        high_availability: Optional[HighAvailabilityForPatch]
        maintenance_window: Optional[MaintenanceWindowForPatch]
        network: Optional[Network]
        replica: Optional[Replica]
        replication_role: Optional[Union[str, ReplicationRole]]
        storage: Optional[Storage]
        version: Optional[Union[str, PostgresMajorVersion]]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                auth_config: Optional[AuthConfigForPatch] = ..., 
                availability_zone: Optional[str] = ..., 
                backup: Optional[BackupForPatch] = ..., 
                cluster: Optional[Cluster] = ..., 
                create_mode: Optional[Union[str, CreateModeForPatch]] = ..., 
                data_encryption: Optional[DataEncryption] = ..., 
                high_availability: Optional[HighAvailabilityForPatch] = ..., 
                maintenance_window: Optional[MaintenanceWindowForPatch] = ..., 
                network: Optional[Network] = ..., 
                replica: Optional[Replica] = ..., 
                replication_role: Optional[Union[str, ReplicationRole]] = ..., 
                storage: Optional[Storage] = ..., 
                version: Optional[Union[str, PostgresMajorVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ServerPublicNetworkAccessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.ServerSku(_Model):
        name: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ServerSkuCapability(CapabilityBase):
        name: Optional[str]
        reason: str
        security_profile: Optional[str]
        status: Union[str, CapabilityStatus]
        supported_features: Optional[list[SupportedFeature]]
        supported_ha_mode: Optional[list[Union[str, HighAvailabilityMode]]]
        supported_iops: Optional[int]
        supported_memory_per_vcore_mb: Optional[int]
        supported_zones: Optional[list[str]]
        v_cores: Optional[int]


    class azure.mgmt.postgresqlflexibleservers.models.ServerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DROPPING = "Dropping"
        INACCESSIBLE = "Inaccessible"
        PROVISIONING = "Provisioning"
        READY = "Ready"
        RESTARTING = "Restarting"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UPDATING = "Updating"


    class azure.mgmt.postgresqlflexibleservers.models.ServerVersionCapability(CapabilityBase):
        name: Optional[str]
        reason: str
        status: Union[str, CapabilityStatus]
        supported_features: Optional[list[SupportedFeature]]
        supported_versions_to_upgrade: Optional[list[str]]


    class azure.mgmt.postgresqlflexibleservers.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]


    class azure.mgmt.postgresqlflexibleservers.models.Sku(_Model):
        name: str
        tier: Union[str, SkuTier]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tier: Union[str, SkuTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.SkuForPatch(_Model):
        name: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BURSTABLE = "Burstable"
        GENERAL_PURPOSE = "GeneralPurpose"
        MEMORY_OPTIMIZED = "MemoryOptimized"


    class azure.mgmt.postgresqlflexibleservers.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APSARA_DB_RDS = "ApsaraDB_RDS"
        AWS = "AWS"
        AWS_AURORA = "AWS_AURORA"
        AWS_EC2 = "AWS_EC2"
        AWS_RDS = "AWS_RDS"
        AZURE_VM = "AzureVM"
        CRUNCHY_POSTGRE_SQL = "Crunchy_PostgreSQL"
        DIGITAL_OCEAN_DROPLETS = "Digital_Ocean_Droplets"
        DIGITAL_OCEAN_POSTGRE_SQL = "Digital_Ocean_PostgreSQL"
        EDB = "EDB"
        EDB_ORACLE_SERVER = "EDB_Oracle_Server"
        EDB_POSTGRE_SQL = "EDB_PostgreSQL"
        GCP = "GCP"
        GCP_ALLOY_DB = "GCP_AlloyDB"
        GCP_CLOUD_SQL = "GCP_CloudSQL"
        GCP_COMPUTE = "GCP_Compute"
        HEROKU_POSTGRE_SQL = "Heroku_PostgreSQL"
        HUAWEI_COMPUTE = "Huawei_Compute"
        HUAWEI_RDS = "Huawei_RDS"
        ON_PREMISES = "OnPremises"
        POSTGRE_SQL_COSMOS_DB = "PostgreSQLCosmosDB"
        POSTGRE_SQL_FLEXIBLE_SERVER = "PostgreSQLFlexibleServer"
        POSTGRE_SQL_SINGLE_SERVER = "PostgreSQLSingleServer"
        SUPABASE_POSTGRE_SQL = "Supabase_PostgreSQL"


    class azure.mgmt.postgresqlflexibleservers.models.SslMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREFER = "Prefer"
        REQUIRE = "Require"
        VERIFY_CA = "VerifyCA"
        VERIFY_FULL = "VerifyFull"


    class azure.mgmt.postgresqlflexibleservers.models.StartDataMigration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.postgresqlflexibleservers.models.Storage(_Model):
        auto_grow: Optional[Union[str, StorageAutoGrow]]
        iops: Optional[int]
        storage_size_gb: Optional[int]
        throughput: Optional[int]
        tier: Optional[Union[str, AzureManagedDiskPerformanceTier]]
        type: Optional[Union[str, StorageType]]

        @overload
        def __init__(
                self, 
                *, 
                auto_grow: Optional[Union[str, StorageAutoGrow]] = ..., 
                iops: Optional[int] = ..., 
                storage_size_gb: Optional[int] = ..., 
                throughput: Optional[int] = ..., 
                tier: Optional[Union[str, AzureManagedDiskPerformanceTier]] = ..., 
                type: Optional[Union[str, StorageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.StorageAutoGrow(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.StorageAutoGrowthSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.StorageEditionCapability(CapabilityBase):
        default_storage_size_mb: Optional[int]
        name: Optional[str]
        reason: str
        status: Union[str, CapabilityStatus]
        supported_storage_mb: Optional[list[StorageMbCapability]]


    class azure.mgmt.postgresqlflexibleservers.models.StorageMbCapability(CapabilityBase):
        default_iops_tier: Optional[str]
        maximum_storage_size_mb: Optional[int]
        reason: str
        status: Union[str, CapabilityStatus]
        storage_size_mb: Optional[int]
        supported_iops: Optional[int]
        supported_iops_tiers: Optional[list[StorageTierCapability]]
        supported_maximum_iops: Optional[int]
        supported_maximum_throughput: Optional[int]
        supported_throughput: Optional[int]


    class azure.mgmt.postgresqlflexibleservers.models.StorageTierCapability(CapabilityBase):
        iops: Optional[int]
        name: Optional[str]
        reason: str
        status: Union[str, CapabilityStatus]


    class azure.mgmt.postgresqlflexibleservers.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.postgresqlflexibleservers.models.SupportedFeature(_Model):
        name: Optional[str]
        status: Optional[Union[str, FeatureStatus]]


    class azure.mgmt.postgresqlflexibleservers.models.SystemData(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.ThreatProtectionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.postgresqlflexibleservers.models.ThreatProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.TrackedResource(Resource):
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


    class azure.mgmt.postgresqlflexibleservers.models.TriggerCutover(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.postgresqlflexibleservers.models.TuningOptionParameterEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDEX = "index"
        TABLE = "table"


    class azure.mgmt.postgresqlflexibleservers.models.TuningOptions(ProxyResource):
        id: str
        name: str
        properties: Optional[TuningOptionsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TuningOptionsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.TuningOptionsProperties(_Model):
        state: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.UserAssignedIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, UserIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.UserIdentity(_Model):
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


    class azure.mgmt.postgresqlflexibleservers.models.ValidationDetails(_Model):
        db_level_validation_details: Optional[list[DbLevelValidationStatus]]
        server_level_validation_details: Optional[list[ValidationSummaryItem]]
        status: Optional[Union[str, ValidationState]]
        validation_end_time_in_utc: Optional[datetime]
        validation_start_time_in_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                db_level_validation_details: Optional[list[DbLevelValidationStatus]] = ..., 
                server_level_validation_details: Optional[list[ValidationSummaryItem]] = ..., 
                status: Optional[Union[str, ValidationState]] = ..., 
                validation_end_time_in_utc: Optional[datetime] = ..., 
                validation_start_time_in_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ValidationMessage(_Model):
        message: Optional[str]
        state: Optional[Union[str, ValidationState]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                state: Optional[Union[str, ValidationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        WARNING = "Warning"


    class azure.mgmt.postgresqlflexibleservers.models.ValidationSummaryItem(_Model):
        messages: Optional[list[ValidationMessage]]
        state: Optional[Union[str, ValidationState]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                messages: Optional[list[ValidationMessage]] = ..., 
                state: Optional[Union[str, ValidationState]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.VirtualEndpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[VirtualEndpointResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualEndpointResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.VirtualEndpointResourceForPatch(_Model):
        properties: Optional[VirtualEndpointResourceProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualEndpointResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.VirtualEndpointResourceProperties(_Model):
        endpoint_type: Optional[Union[str, VirtualEndpointType]]
        members: Optional[list[str]]
        virtual_endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_type: Optional[Union[str, VirtualEndpointType]] = ..., 
                members: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.VirtualEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_WRITE = "ReadWrite"


    class azure.mgmt.postgresqlflexibleservers.models.VirtualNetworkSubnetUsageModel(_Model):
        delegated_subnets_usage: Optional[list[DelegatedSubnetUsage]]
        location: Optional[str]
        subscription_id: Optional[str]


    class azure.mgmt.postgresqlflexibleservers.models.VirtualNetworkSubnetUsageParameter(_Model):
        virtual_network_arm_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                virtual_network_arm_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.postgresqlflexibleservers.models.ZoneRedundantHighAvailabilityAndGeographicallyRedundantBackupSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.postgresqlflexibleservers.models.ZoneRedundantHighAvailabilitySupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


namespace azure.mgmt.postgresqlflexibleservers.operations

    class azure.mgmt.postgresqlflexibleservers.operations.AdministratorsMicrosoftEntraOperations:

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
                object_id: str, 
                parameters: AdministratorMicrosoftEntraAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdministratorMicrosoftEntra]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdministratorMicrosoftEntra]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdministratorMicrosoftEntra]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> AdministratorMicrosoftEntra: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AdministratorMicrosoftEntra]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.AdvancedThreatProtectionSettingsOperations:

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
                threat_protection_name: Union[str, ThreatProtectionName], 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSettingsModel: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AdvancedThreatProtectionSettingsModel]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.BackupsAutomaticAndOnDemandOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> LROPoller[BackupAutomaticAndOnDemand]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> BackupAutomaticAndOnDemand: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupAutomaticAndOnDemand]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.BackupsLongTermRetentionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: BackupsLongTermRetentionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupsLongTermRetentionResponse]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupsLongTermRetentionResponse]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupsLongTermRetentionResponse]: ...

        @overload
        def check_prerequisites(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: LtrPreBackupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LtrPreBackupResponse: ...

        @overload
        def check_prerequisites(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LtrPreBackupResponse: ...

        @overload
        def check_prerequisites(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LtrPreBackupResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> BackupsLongTermRetentionOperation: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupsLongTermRetentionOperation]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.CapabilitiesByLocationOperations:

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
            ) -> ItemPaged[Capability]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.CapabilitiesByServerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Capability]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.CapturedLogsOperations:

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
            ) -> ItemPaged[CapturedLog]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: ConfigurationForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Configuration]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                server_name: str, 
                configuration_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Configuration]: ...

        @overload
        def begin_put(
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
                parameters: ConfigurationForUpdate, 
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
                parameters: JSON, 
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
                **kwargs: Any
            ) -> ItemPaged[Configuration]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.DatabasesOperations:

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
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_create(
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


    class azure.mgmt.postgresqlflexibleservers.operations.FirewallRulesOperations:

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
                parameters: JSON, 
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


    class azure.mgmt.postgresqlflexibleservers.operations.MigrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> Optional[Migration]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: MigrationNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationNameAvailability: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationNameAvailability: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationNameAvailability: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: Migration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> Migration: ...

        @distributed_trace
        def list_by_target_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                *, 
                migration_list_filter: Optional[Union[str, MigrationListFilter]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Migration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: MigrationResourceForPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Migration: ...


    class azure.mgmt.postgresqlflexibleservers.operations.NameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_globally(
                self, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        def check_globally(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        def check_globally(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        def check_with_location(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        def check_with_location(
                self, 
                location_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...

        @overload
        def check_with_location(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityModel: ...


    class azure.mgmt.postgresqlflexibleservers.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.PrivateDnsZoneSuffixOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> str: ...


    class azure.mgmt.postgresqlflexibleservers.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
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
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
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
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.PrivateLinkResourcesOperations:

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


    class azure.mgmt.postgresqlflexibleservers.operations.QuotaUsagesOperations:

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
            ) -> ItemPaged[QuotaUsage]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.ReplicasOperations:

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


    class azure.mgmt.postgresqlflexibleservers.operations.ServerThreatProtectionSettingsOperations:

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
                threat_protection_name: Union[str, ThreatProtectionName], 
                parameters: AdvancedThreatProtectionSettingsModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtectionSettingsModel]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                threat_protection_name: Union[str, ThreatProtectionName], 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtectionSettingsModel]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                threat_protection_name: Union[str, ThreatProtectionName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AdvancedThreatProtectionSettingsModel]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.ServersOperations:

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
                parameters: Server, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @overload
        def begin_create_or_update(
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

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'server_name', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def begin_migrate_network_mode(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> LROPoller[MigrateNetworkStatus]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Optional[RestartParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: Optional[IO[bytes]] = None, 
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
                parameters: ServerForPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Server]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                parameters: JSON, 
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
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Server]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Server]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.TuningOptionsOperations:

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
                tuning_option: Union[str, TuningOptionParameterEnum], 
                **kwargs: Any
            ) -> TuningOptions: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TuningOptions]: ...

        @distributed_trace
        def list_recommendations(
                self, 
                resource_group_name: str, 
                server_name: str, 
                tuning_option: Union[str, TuningOptionParameterEnum], 
                *, 
                recommendation_type: Optional[Union[str, RecommendationTypeParameterEnum]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ObjectRecommendation]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.VirtualEndpointsOperations:

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
                virtual_endpoint_name: str, 
                parameters: VirtualEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: VirtualEndpointResourceForPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                server_name: str, 
                virtual_endpoint_name: str, 
                **kwargs: Any
            ) -> VirtualEndpoint: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualEndpoint]: ...


    class azure.mgmt.postgresqlflexibleservers.operations.VirtualNetworkSubnetUsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list(
                self, 
                location_name: str, 
                parameters: VirtualNetworkSubnetUsageParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageModel: ...

        @overload
        def list(
                self, 
                location_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageModel: ...

        @overload
        def list(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetworkSubnetUsageModel: ...


```