```py
namespace azure.mgmt.cosmosdbforpostgresql

    class azure.mgmt.cosmosdbforpostgresql.CosmosdbForPostgresqlMgmtClient: implements ContextManager 
        clusters: ClustersOperations
        configurations: ConfigurationsOperations
        firewall_rules: FirewallRulesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        roles: RolesOperations
        servers: ServersOperations

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


namespace azure.mgmt.cosmosdbforpostgresql.aio

    class azure.mgmt.cosmosdbforpostgresql.aio.CosmosdbForPostgresqlMgmtClient: implements AsyncContextManager 
        clusters: ClustersOperations
        configurations: ConfigurationsOperations
        firewall_rules: FirewallRulesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        roles: RolesOperations
        servers: ServersOperations

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


namespace azure.mgmt.cosmosdbforpostgresql.aio.operations

    class azure.mgmt.cosmosdbforpostgresql.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_promote_read_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                promote_request: Optional[PromoteRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_promote_read_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                promote_request: Optional[PromoteRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_promote_read_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                promote_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_on_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerConfiguration]: ...

        @overload
        async def begin_update_on_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerConfiguration]: ...

        @overload
        async def begin_update_on_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerConfiguration]: ...

        @overload
        async def begin_update_on_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerConfiguration]: ...

        @overload
        async def begin_update_on_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerConfiguration]: ...

        @overload
        async def begin_update_on_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> Configuration: ...

        @distributed_trace_async
        async def get_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> ServerConfiguration: ...

        @distributed_trace_async
        async def get_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> ServerConfiguration: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Configuration]: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ServerConfiguration]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FirewallRule]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.RolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                parameters: Role, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Role]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                parameters: Role, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Role]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Role]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                **kwargs: Any
            ) -> Role: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Role]: ...


    class azure.mgmt.cosmosdbforpostgresql.aio.operations.ServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ClusterServer: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterServer]: ...


namespace azure.mgmt.cosmosdbforpostgresql.models

    class azure.mgmt.cosmosdbforpostgresql.models.AadEnabledEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.cosmosdbforpostgresql.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.cosmosdbforpostgresql.models.ActiveDirectoryAuth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.cosmosdbforpostgresql.models.AuthConfig(_Model):
        active_directory_auth: Optional[Union[str, ActiveDirectoryAuth]]
        password_auth: Optional[Union[str, PasswordAuth]]

        @overload
        def __init__(
                self, 
                *, 
                active_directory_auth: Optional[Union[str, ActiveDirectoryAuth]] = ..., 
                password_auth: Optional[Union[str, PasswordAuth]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.CheckNameAvailabilityResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_DB_FOR_POSTGRESQL_SERVER_GROUPSV2 = "Microsoft.DBforPostgreSQL/serverGroupsv2"


    class azure.mgmt.cosmosdbforpostgresql.models.Cluster(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        location: str
        name: str
        properties: Optional[ClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: str, 
                properties: Optional[ClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ClusterForUpdate(_Model):
        identity: Optional[IdentityProperties]
        properties: Optional[ClusterPropertiesForUpdate]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[ClusterPropertiesForUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ClusterProperties(_Model):
        aad_auth_enabled: Optional[Union[str, AadEnabledEnum]]
        administrator_login: Optional[str]
        administrator_login_password: Optional[str]
        auth_config: Optional[AuthConfig]
        citus_version: Optional[str]
        coordinator_enable_public_ip_access: Optional[bool]
        coordinator_server_edition: Optional[str]
        coordinator_storage_quota_in_mb: Optional[int]
        coordinator_v_cores: Optional[int]
        data_encryption: Optional[DataEncryption]
        database_name: Optional[str]
        earliest_restore_time: Optional[datetime]
        enable_geo_backup: Optional[bool]
        enable_ha: Optional[bool]
        enable_shards_on_coordinator: Optional[bool]
        maintenance_window: Optional[MaintenanceWindow]
        node_count: Optional[int]
        node_enable_public_ip_access: Optional[bool]
        node_server_edition: Optional[str]
        node_storage_quota_in_mb: Optional[int]
        node_v_cores: Optional[int]
        password_enabled: Optional[Union[str, PasswordEnabledEnum]]
        point_in_time_utc: Optional[datetime]
        postgresql_version: Optional[str]
        preferred_primary_zone: Optional[str]
        private_endpoint_connections: Optional[list[SimplePrivateEndpointConnection]]
        provisioning_state: Optional[str]
        read_replicas: Optional[list[str]]
        server_names: Optional[list[ServerNameItem]]
        source_location: Optional[str]
        source_resource_id: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                auth_config: Optional[AuthConfig] = ..., 
                citus_version: Optional[str] = ..., 
                coordinator_enable_public_ip_access: Optional[bool] = ..., 
                coordinator_server_edition: Optional[str] = ..., 
                coordinator_storage_quota_in_mb: Optional[int] = ..., 
                coordinator_v_cores: Optional[int] = ..., 
                data_encryption: Optional[DataEncryption] = ..., 
                database_name: Optional[str] = ..., 
                enable_geo_backup: Optional[bool] = ..., 
                enable_ha: Optional[bool] = ..., 
                enable_shards_on_coordinator: Optional[bool] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                node_count: Optional[int] = ..., 
                node_enable_public_ip_access: Optional[bool] = ..., 
                node_server_edition: Optional[str] = ..., 
                node_storage_quota_in_mb: Optional[int] = ..., 
                node_v_cores: Optional[int] = ..., 
                point_in_time_utc: Optional[datetime] = ..., 
                postgresql_version: Optional[str] = ..., 
                preferred_primary_zone: Optional[str] = ..., 
                source_location: Optional[str] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ClusterPropertiesForUpdate(_Model):
        administrator_login_password: Optional[str]
        citus_version: Optional[str]
        coordinator_enable_public_ip_access: Optional[bool]
        coordinator_server_edition: Optional[str]
        coordinator_storage_quota_in_mb: Optional[int]
        coordinator_v_cores: Optional[int]
        enable_ha: Optional[bool]
        enable_shards_on_coordinator: Optional[bool]
        maintenance_window: Optional[MaintenanceWindow]
        node_count: Optional[int]
        node_enable_public_ip_access: Optional[bool]
        node_server_edition: Optional[str]
        node_storage_quota_in_mb: Optional[int]
        node_v_cores: Optional[int]
        postgresql_version: Optional[str]
        preferred_primary_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                citus_version: Optional[str] = ..., 
                coordinator_enable_public_ip_access: Optional[bool] = ..., 
                coordinator_server_edition: Optional[str] = ..., 
                coordinator_storage_quota_in_mb: Optional[int] = ..., 
                coordinator_v_cores: Optional[int] = ..., 
                enable_ha: Optional[bool] = ..., 
                enable_shards_on_coordinator: Optional[bool] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                node_count: Optional[int] = ..., 
                node_server_edition: Optional[str] = ..., 
                node_storage_quota_in_mb: Optional[int] = ..., 
                node_v_cores: Optional[int] = ..., 
                postgresql_version: Optional[str] = ..., 
                preferred_primary_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ClusterServer(ProxyResource):
        id: str
        name: str
        properties: Optional[ClusterServerProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterServerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ClusterServerProperties(ServerProperties):
        administrator_login: str
        availability_zone: Optional[str]
        citus_version: Optional[str]
        enable_ha: bool
        enable_public_ip_access: bool
        fully_qualified_domain_name: Optional[str]
        ha_state: Optional[str]
        is_read_only: bool
        postgresql_version: Optional[str]
        role: Optional[Union[str, ServerRole]]
        server_edition: str
        state: Optional[str]
        storage_quota_in_mb: int
        v_cores: int

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                citus_version: Optional[str] = ..., 
                enable_ha: Optional[bool] = ..., 
                postgresql_version: Optional[str] = ..., 
                role: Optional[Union[str, ServerRole]] = ..., 
                server_edition: Optional[str] = ..., 
                storage_quota_in_mb: Optional[int] = ..., 
                v_cores: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.Configuration(ProxyResource):
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


    class azure.mgmt.cosmosdbforpostgresql.models.ConfigurationDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Boolean"
        ENUMERATION = "Enumeration"
        INTEGER = "Integer"
        NUMERIC = "Numeric"


    class azure.mgmt.cosmosdbforpostgresql.models.ConfigurationProperties(_Model):
        allowed_values: Optional[str]
        data_type: Optional[Union[str, ConfigurationDataType]]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        requires_restart: Optional[bool]
        server_role_group_configurations: list[ServerRoleGroupConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                requires_restart: Optional[bool] = ..., 
                server_role_group_configurations: list[ServerRoleGroupConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.cosmosdbforpostgresql.models.DataEncryption(_Model):
        primary_key_uri: Optional[str]
        primary_user_assigned_identity_id: Optional[str]
        type: Optional[Union[str, DataEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                primary_key_uri: Optional[str] = ..., 
                primary_user_assigned_identity_id: Optional[str] = ..., 
                type: Optional[Union[str, DataEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.DataEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.cosmosdbforpostgresql.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.cosmosdbforpostgresql.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.cosmosdbforpostgresql.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.FirewallRule(ProxyResource):
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


    class azure.mgmt.cosmosdbforpostgresql.models.FirewallRuleProperties(_Model):
        end_ip_address: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
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


    class azure.mgmt.cosmosdbforpostgresql.models.IdentityProperties(_Model):
        type: Optional[Union[str, IdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cosmosdbforpostgresql.models.MaintenanceWindow(_Model):
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


    class azure.mgmt.cosmosdbforpostgresql.models.NameAvailability(_Model):
        message: Optional[str]
        name: Optional[str]
        name_available: Optional[bool]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.NameAvailabilityRequest(_Model):
        name: str
        type: Union[str, CheckNameAvailabilityResourceType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, CheckNameAvailabilityResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.Operation(_Model):
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


    class azure.mgmt.cosmosdbforpostgresql.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.cosmosdbforpostgresql.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.cosmosdbforpostgresql.models.PasswordAuth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.cosmosdbforpostgresql.models.PasswordEnabledEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.cosmosdbforpostgresql.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "group"
        SERVICE_PRINCIPAL = "servicePrincipal"
        USER = "user"


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpointConnectionSimpleProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpointProperty]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpointProperty(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.cosmosdbforpostgresql.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.cosmosdbforpostgresql.models.PromoteRequest(_Model):
        enable_geo_backup: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_geo_backup: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cosmosdbforpostgresql.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.cosmosdbforpostgresql.models.Role(ProxyResource):
        id: str
        name: str
        properties: RoleProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: RoleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.RoleProperties(_Model):
        external_identity: Optional[RolePropertiesExternalIdentity]
        password: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        role_type: Optional[Union[str, RoleType]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                external_identity: Optional[RolePropertiesExternalIdentity] = ..., 
                password: Optional[str] = ..., 
                role_type: Optional[Union[str, RoleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.RolePropertiesExternalIdentity(_Model):
        object_id: str
        principal_type: Union[str, PrincipalType]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: str, 
                principal_type: Union[str, PrincipalType], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.RoleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "admin"
        USER = "user"


    class azure.mgmt.cosmosdbforpostgresql.models.ServerConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[ServerConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ServerConfigurationProperties(_Model):
        allowed_values: Optional[str]
        data_type: Optional[Union[str, ConfigurationDataType]]
        default_value: Optional[str]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        requires_restart: Optional[bool]
        source: Optional[str]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ServerNameItem(_Model):
        fully_qualified_domain_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ServerProperties(_Model):
        administrator_login: Optional[str]
        enable_ha: Optional[bool]
        enable_public_ip_access: Optional[bool]
        is_read_only: Optional[bool]
        server_edition: Optional[str]
        storage_quota_in_mb: Optional[int]
        v_cores: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enable_ha: Optional[bool] = ..., 
                server_edition: Optional[str] = ..., 
                storage_quota_in_mb: Optional[int] = ..., 
                v_cores: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.ServerRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COORDINATOR = "Coordinator"
        WORKER = "Worker"


    class azure.mgmt.cosmosdbforpostgresql.models.ServerRoleGroupConfiguration(_Model):
        default_value: Optional[str]
        role: Union[str, ServerRole]
        source: Optional[str]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                role: Union[str, ServerRole], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.SimplePrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionSimpleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionSimpleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdbforpostgresql.models.SystemData(_Model):
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


    class azure.mgmt.cosmosdbforpostgresql.models.TrackedResource(Resource):
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


    class azure.mgmt.cosmosdbforpostgresql.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.cosmosdbforpostgresql.operations

    class azure.mgmt.cosmosdbforpostgresql.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_promote_read_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                promote_request: Optional[PromoteRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_promote_read_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                promote_request: Optional[PromoteRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_promote_read_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                promote_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterForUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_request: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_on_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerConfiguration]: ...

        @overload
        def begin_update_on_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerConfiguration]: ...

        @overload
        def begin_update_on_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerConfiguration]: ...

        @overload
        def begin_update_on_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerConfiguration]: ...

        @overload
        def begin_update_on_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: ServerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerConfiguration]: ...

        @overload
        def begin_update_on_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> Configuration: ...

        @distributed_trace
        def get_coordinator(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> ServerConfiguration: ...

        @distributed_trace
        def get_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> ServerConfiguration: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Configuration]: ...

        @distributed_trace
        def list_by_server(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ServerConfiguration]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FirewallRule]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.RolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                parameters: Role, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Role]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                parameters: Role, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Role]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Role]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                role_name: str, 
                **kwargs: Any
            ) -> Role: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Role]: ...


    class azure.mgmt.cosmosdbforpostgresql.operations.ServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                server_name: str, 
                **kwargs: Any
            ) -> ClusterServer: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClusterServer]: ...


namespace azure.mgmt.cosmosdbforpostgresql.types

    class azure.mgmt.cosmosdbforpostgresql.types.AuthConfig(TypedDict, total=False):
        key "activeDirectoryAuth": Union[str, ActiveDirectoryAuth]
        key "passwordAuth": Union[str, PasswordAuth]
        active_directory_auth: Union[str, ActiveDirectoryAuth]
        password_auth: Union[str, PasswordAuth]


    class azure.mgmt.cosmosdbforpostgresql.types.Cluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        location: str
        name: str
        properties: ClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.ClusterForUpdate(TypedDict, total=False):
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "properties": ForwardRef('ClusterPropertiesForUpdate', module='types')
        identity: IdentityProperties
        properties: ClusterPropertiesForUpdate
        tags: dict[str, str]


    class azure.mgmt.cosmosdbforpostgresql.types.ClusterProperties(TypedDict, total=False):
        key "aadAuthEnabled": Union[str, AadEnabledEnum]
        key "administratorLogin": str
        key "administratorLoginPassword": str
        key "authConfig": ForwardRef('AuthConfig', module='types')
        key "citusVersion": str
        key "coordinatorEnablePublicIpAccess": bool
        key "coordinatorServerEdition": str
        key "coordinatorStorageQuotaInMb": int
        key "coordinatorVCores": int
        key "dataEncryption": ForwardRef('DataEncryption', module='types')
        key "databaseName": str
        key "earliestRestoreTime": str
        key "enableGeoBackup": bool
        key "enableHa": bool
        key "enableShardsOnCoordinator": bool
        key "maintenanceWindow": ForwardRef('MaintenanceWindow', module='types')
        key "nodeCount": int
        key "nodeEnablePublicIpAccess": bool
        key "nodeServerEdition": str
        key "nodeStorageQuotaInMb": int
        key "nodeVCores": int
        key "passwordEnabled": Union[str, PasswordEnabledEnum]
        key "pointInTimeUTC": str
        key "postgresqlVersion": str
        key "preferredPrimaryZone": str
        key "provisioningState": str
        key "sourceLocation": str
        key "sourceResourceId": str
        key "state": str
        aad_auth_enabled: Union[str, AadEnabledEnum]
        administrator_login: str
        administrator_login_password: str
        auth_config: AuthConfig
        citus_version: str
        coordinator_enable_public_ip_access: bool
        coordinator_server_edition: str
        coordinator_storage_quota_in_mb: int
        coordinator_v_cores: int
        data_encryption: DataEncryption
        database_name: str
        earliest_restore_time: str
        enable_geo_backup: bool
        enable_ha: bool
        enable_shards_on_coordinator: bool
        maintenance_window: MaintenanceWindow
        node_count: int
        node_enable_public_ip_access: bool
        node_server_edition: str
        node_storage_quota_in_mb: int
        node_v_cores: int
        password_enabled: Union[str, PasswordEnabledEnum]
        point_in_time_utc: str
        postgresql_version: str
        preferred_primary_zone: str
        privateEndpointConnections: list[SimplePrivateEndpointConnection]
        private_endpoint_connections: list[SimplePrivateEndpointConnection]
        provisioning_state: str
        readReplicas: list[str]
        read_replicas: list[str]
        serverNames: list[ServerNameItem]
        server_names: list[ServerNameItem]
        source_location: str
        source_resource_id: str
        state: str


    class azure.mgmt.cosmosdbforpostgresql.types.ClusterPropertiesForUpdate(TypedDict, total=False):
        key "administratorLoginPassword": str
        key "citusVersion": str
        key "coordinatorEnablePublicIpAccess": bool
        key "coordinatorServerEdition": str
        key "coordinatorStorageQuotaInMb": int
        key "coordinatorVCores": int
        key "enableHa": bool
        key "enableShardsOnCoordinator": bool
        key "maintenanceWindow": ForwardRef('MaintenanceWindow', module='types')
        key "nodeCount": int
        key "nodeEnablePublicIpAccess": bool
        key "nodeServerEdition": str
        key "nodeStorageQuotaInMb": int
        key "nodeVCores": int
        key "postgresqlVersion": str
        key "preferredPrimaryZone": str
        administrator_login_password: str
        citus_version: str
        coordinator_enable_public_ip_access: bool
        coordinator_server_edition: str
        coordinator_storage_quota_in_mb: int
        coordinator_v_cores: int
        enable_ha: bool
        enable_shards_on_coordinator: bool
        maintenance_window: MaintenanceWindow
        node_count: int
        node_enable_public_ip_access: bool
        node_server_edition: str
        node_storage_quota_in_mb: int
        node_v_cores: int
        postgresql_version: str
        preferred_primary_zone: str


    class azure.mgmt.cosmosdbforpostgresql.types.ClusterServer(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ClusterServerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ClusterServerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.ClusterServerProperties(ServerProperties):
        key "administratorLogin": str
        key "availabilityZone": str
        key "citusVersion": str
        key "enableHa": bool
        key "enablePublicIpAccess": bool
        key "fullyQualifiedDomainName": str
        key "haState": str
        key "isReadOnly": bool
        key "postgresqlVersion": str
        key "role": Union[str, ServerRole]
        key "serverEdition": str
        key "state": str
        key "storageQuotaInMb": int
        key "vCores": int
        administrator_login: str
        availability_zone: str
        citus_version: str
        enable_ha: bool
        enable_public_ip_access: bool
        fully_qualified_domain_name: str
        ha_state: str
        is_read_only: bool
        postgresql_version: str
        role: Union[str, ServerRole]
        server_edition: str
        state: str
        storage_quota_in_mb: int
        v_cores: int


    class azure.mgmt.cosmosdbforpostgresql.types.Configuration(ProxyResource):
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


    class azure.mgmt.cosmosdbforpostgresql.types.ConfigurationProperties(TypedDict, total=False):
        key "allowedValues": str
        key "dataType": Union[str, ConfigurationDataType]
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        key "requiresRestart": bool
        key "serverRoleGroupConfigurations": Required[list[ServerRoleGroupConfiguration]]
        allowed_values: str
        data_type: Union[str, ConfigurationDataType]
        description: str
        provisioning_state: Union[str, ProvisioningState]
        requires_restart: bool
        server_role_group_configurations: list[ServerRoleGroupConfiguration]


    class azure.mgmt.cosmosdbforpostgresql.types.DataEncryption(TypedDict, total=False):
        key "primaryKeyUri": str
        key "primaryUserAssignedIdentityId": str
        key "type": Union[str, DataEncryptionType]
        primary_key_uri: str
        primary_user_assigned_identity_id: str
        type: Union[str, DataEncryptionType]


    class azure.mgmt.cosmosdbforpostgresql.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.cosmosdbforpostgresql.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.cosmosdbforpostgresql.types.FirewallRule(ProxyResource):
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


    class azure.mgmt.cosmosdbforpostgresql.types.FirewallRuleProperties(TypedDict, total=False):
        key "endIpAddress": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "startIpAddress": Required[str]
        end_ip_address: str
        provisioning_state: Union[str, ProvisioningState]
        start_ip_address: str


    class azure.mgmt.cosmosdbforpostgresql.types.IdentityProperties(TypedDict, total=False):
        key "type": Union[str, IdentityType]
        type: Union[str, IdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.cosmosdbforpostgresql.types.MaintenanceWindow(TypedDict, total=False):
        key "customWindow": str
        key "dayOfWeek": int
        key "startHour": int
        key "startMinute": int
        custom_window: str
        day_of_week: int
        start_hour: int
        start_minute: int


    class azure.mgmt.cosmosdbforpostgresql.types.NameAvailability(TypedDict, total=False):
        key "message": str
        key "name": str
        key "nameAvailable": bool
        key "type": str
        message: str
        name: str
        name_available: bool
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.NameAvailabilityRequest(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, CheckNameAvailabilityResourceType]]
        name: str
        type: Union[str, CheckNameAvailabilityResourceType]


    class azure.mgmt.cosmosdbforpostgresql.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.cosmosdbforpostgresql.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateEndpointConnectionSimpleProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpointProperty', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpointProperty
        private_link_service_connection_state: PrivateLinkServiceConnectionState


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateEndpointProperty(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateLinkResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.cosmosdbforpostgresql.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.cosmosdbforpostgresql.types.PromoteRequest(TypedDict, total=False):
        key "enableGeoBackup": bool
        enable_geo_backup: bool


    class azure.mgmt.cosmosdbforpostgresql.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.Role(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[RoleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RoleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.RoleProperties(TypedDict, total=False):
        key "externalIdentity": ForwardRef('RolePropertiesExternalIdentity', module='types')
        key "password": str
        key "provisioningState": Union[str, ProvisioningState]
        key "roleType": Union[str, RoleType]
        external_identity: RolePropertiesExternalIdentity
        password: str
        provisioning_state: Union[str, ProvisioningState]
        role_type: Union[str, RoleType]


    class azure.mgmt.cosmosdbforpostgresql.types.RolePropertiesExternalIdentity(TypedDict, total=False):
        key "objectId": Required[str]
        key "principalType": Required[Union[str, PrincipalType]]
        key "tenantId": str
        object_id: str
        principal_type: Union[str, PrincipalType]
        tenant_id: str


    class azure.mgmt.cosmosdbforpostgresql.types.ServerConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServerConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServerConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.ServerConfigurationProperties(TypedDict, total=False):
        key "allowedValues": str
        key "dataType": Union[str, ConfigurationDataType]
        key "defaultValue": str
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        key "requiresRestart": bool
        key "source": str
        key "value": Required[str]
        allowed_values: str
        data_type: Union[str, ConfigurationDataType]
        default_value: str
        description: str
        provisioning_state: Union[str, ProvisioningState]
        requires_restart: bool
        source: str
        value: str


    class azure.mgmt.cosmosdbforpostgresql.types.ServerNameItem(TypedDict, total=False):
        key "fullyQualifiedDomainName": str
        key "name": str
        fully_qualified_domain_name: str
        name: str


    class azure.mgmt.cosmosdbforpostgresql.types.ServerProperties(TypedDict, total=False):
        key "administratorLogin": str
        key "enableHa": bool
        key "enablePublicIpAccess": bool
        key "isReadOnly": bool
        key "serverEdition": str
        key "storageQuotaInMb": int
        key "vCores": int
        administrator_login: str
        enable_ha: bool
        enable_public_ip_access: bool
        is_read_only: bool
        server_edition: str
        storage_quota_in_mb: int
        v_cores: int


    class azure.mgmt.cosmosdbforpostgresql.types.ServerRoleGroupConfiguration(TypedDict, total=False):
        key "defaultValue": str
        key "role": Required[Union[str, ServerRole]]
        key "source": str
        key "value": Required[str]
        default_value: str
        role: Union[str, ServerRole]
        source: str
        value: str


    class azure.mgmt.cosmosdbforpostgresql.types.SimplePrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionSimpleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionSimpleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdbforpostgresql.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.cosmosdbforpostgresql.types.TrackedResource(Resource):
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


    class azure.mgmt.cosmosdbforpostgresql.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


```