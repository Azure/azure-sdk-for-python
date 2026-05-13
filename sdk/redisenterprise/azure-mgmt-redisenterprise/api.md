```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.redisenterprise

    class azure.mgmt.redisenterprise.RedisEnterpriseManagementClient: implements ContextManager 
        access_policy_assignment: AccessPolicyAssignmentOperations
        databases: DatabasesOperations
        migration: MigrationOperations
        migrations: MigrationsOperations
        operations: Operations
        operations_status: OperationsStatusOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        redis_enterprise: RedisEnterpriseOperations

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


namespace azure.mgmt.redisenterprise.aio

    class azure.mgmt.redisenterprise.aio.RedisEnterpriseManagementClient: implements AsyncContextManager 
        access_policy_assignment: AccessPolicyAssignmentOperations
        databases: DatabasesOperations
        migration: MigrationOperations
        migrations: MigrationsOperations
        operations: Operations
        operations_status: OperationsStatusOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        redis_enterprise: RedisEnterpriseOperations

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


namespace azure.mgmt.redisenterprise.aio.operations

    class azure.mgmt.redisenterprise.aio.operations.AccessPolicyAssignmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                parameters: AccessPolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessPolicyAssignment]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessPolicyAssignment]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessPolicyAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                **kwargs: Any
            ) -> AccessPolicyAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessPolicyAssignment]: ...


    class azure.mgmt.redisenterprise.aio.operations.DatabasesOperations:

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
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ExportClusterParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_flush(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Optional[FlushParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_flush(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_flush(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_force_link_to_replication_group(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ForceLinkParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_force_link_to_replication_group(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_force_link_to_replication_group(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_force_unlink(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ForceUnlinkParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_force_unlink(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_force_unlink(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_method(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ImportClusterParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_method(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_method(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: DatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @distributed_trace_async
        async def begin_upgrade_db_redis_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Database]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.redisenterprise.aio.operations.MigrationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Migration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Migration]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Migration]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Migration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Migration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Migration]: ...


    class azure.mgmt.redisenterprise.aio.operations.MigrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: MigrationValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationValidationResponse: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationValidationResponse: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationValidationResponse: ...


    class azure.mgmt.redisenterprise.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.redisenterprise.aio.operations.OperationsStatusOperations:

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
            ) -> OperationStatus: ...


    class azure.mgmt.redisenterprise.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.redisenterprise.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.redisenterprise.aio.operations.RedisEnterpriseOperations:

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
                parameters: JSON, 
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
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
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

        @distributed_trace_async
        async def list_skus_for_scaling(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> SkuDetailsList: ...


namespace azure.mgmt.redisenterprise.models

    class azure.mgmt.redisenterprise.models.AccessKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.redisenterprise.models.AccessKeys(_Model):
        primary_key: Optional[str]
        secondary_key: Optional[str]


    class azure.mgmt.redisenterprise.models.AccessKeysAuthentication(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redisenterprise.models.AccessPolicyAssignment(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessPolicyAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessPolicyAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redisenterprise.models.AccessPolicyAssignmentProperties(_Model):
        access_policy_name: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        user: AccessPolicyAssignmentPropertiesUser

        @overload
        def __init__(
                self, 
                *, 
                access_policy_name: str, 
                user: AccessPolicyAssignmentPropertiesUser
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.AccessPolicyAssignmentPropertiesUser(_Model):
        object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.redisenterprise.models.AofFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "always"
        ONE_S = "1s"


    class azure.mgmt.redisenterprise.models.AzureCacheForRedisMigrationProperties(MigrationProperties, discriminator='AzureCacheForRedis'):
        creation_time: datetime
        force_migrate: Optional[bool]
        last_modified_time: datetime
        provisioning_state: Union[str, MigrationProvisioningState]
        skip_data_migration: bool
        source_resource_id: str
        source_type: Literal[SourceType.AZURE_CACHE_FOR_REDIS]
        status_details: str
        switch_dns: bool
        target_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                force_migrate: Optional[bool] = ..., 
                skip_data_migration: bool, 
                source_resource_id: str, 
                switch_dns: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.Cluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[Union[str, Kind]]
        location: str
        name: str
        properties: Optional[ClusterCreateProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ClusterCreateProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusterCreateProperties(ClusterProperties):
        encryption: ClusterPropertiesEncryption
        high_availability: Union[str, HighAvailability]
        host_name: str
        maintenance_configuration: MaintenanceConfiguration
        migrated_endpoint: str
        minimum_tls_version: Union[str, TlsVersion]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        redis_version: str
        redundancy_mode: Union[str, RedundancyMode]
        resource_state: Union[str, ResourceState]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[ClusterPropertiesEncryption] = ..., 
                high_availability: Optional[Union[str, HighAvailability]] = ..., 
                maintenance_configuration: Optional[MaintenanceConfiguration] = ..., 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Union[str, PublicNetworkAccess]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusterProperties(_Model):
        encryption: Optional[ClusterPropertiesEncryption]
        high_availability: Optional[Union[str, HighAvailability]]
        host_name: Optional[str]
        maintenance_configuration: Optional[MaintenanceConfiguration]
        migrated_endpoint: Optional[str]
        minimum_tls_version: Optional[Union[str, TlsVersion]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        redis_version: Optional[str]
        redundancy_mode: Optional[Union[str, RedundancyMode]]
        resource_state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[ClusterPropertiesEncryption] = ..., 
                high_availability: Optional[Union[str, HighAvailability]] = ..., 
                maintenance_configuration: Optional[MaintenanceConfiguration] = ..., 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusterPropertiesEncryption(_Model):
        customer_managed_key_encryption: Optional[ClusterPropertiesEncryptionCustomerManagedKeyEncryption]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: Optional[ClusterPropertiesEncryptionCustomerManagedKeyEncryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusterPropertiesEncryptionCustomerManagedKeyEncryption(_Model):
        key_encryption_key_identity: Optional[ClusterPropertiesEncryptionCustomerManagedKeyEncryptionKeyIdentity]
        key_encryption_key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key_identity: Optional[ClusterPropertiesEncryptionCustomerManagedKeyEncryptionKeyIdentity] = ..., 
                key_encryption_key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusterPropertiesEncryptionCustomerManagedKeyEncryptionKeyIdentity(_Model):
        identity_type: Optional[Union[str, CmkIdentityType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_type: Optional[Union[str, CmkIdentityType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusterUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ClusterUpdateProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ClusterUpdateProperties] = ..., 
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


    class azure.mgmt.redisenterprise.models.ClusterUpdateProperties(ClusterProperties):
        encryption: ClusterPropertiesEncryption
        high_availability: Union[str, HighAvailability]
        host_name: str
        maintenance_configuration: MaintenanceConfiguration
        migrated_endpoint: str
        minimum_tls_version: Union[str, TlsVersion]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        redis_version: str
        redundancy_mode: Union[str, RedundancyMode]
        resource_state: Union[str, ResourceState]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[ClusterPropertiesEncryption] = ..., 
                high_availability: Optional[Union[str, HighAvailability]] = ..., 
                maintenance_configuration: Optional[MaintenanceConfiguration] = ..., 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ClusteringPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE_CLUSTER = "EnterpriseCluster"
        NO_CLUSTER = "NoCluster"
        OSS_CLUSTER = "OSSCluster"


    class azure.mgmt.redisenterprise.models.CmkIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.redisenterprise.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.redisenterprise.models.Database(ProxyResource):
        id: str
        name: str
        properties: Optional[DatabaseCreateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseCreateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redisenterprise.models.DatabaseCreateProperties(DatabaseProperties):
        access_keys_authentication: Union[str, AccessKeysAuthentication]
        client_protocol: Union[str, Protocol]
        clustering_policy: Union[str, ClusteringPolicy]
        defer_upgrade: Union[str, DeferUpgradeSetting]
        eviction_policy: Union[str, EvictionPolicy]
        geo_replication: DatabasePropertiesGeoReplication
        modules: list[Module]
        persistence: Persistence
        port: int
        provisioning_state: Union[str, ProvisioningState]
        redis_version: str
        resource_state: Union[str, ResourceState]

        @overload
        def __init__(
                self, 
                *, 
                access_keys_authentication: Optional[Union[str, AccessKeysAuthentication]] = ..., 
                client_protocol: Optional[Union[str, Protocol]] = ..., 
                clustering_policy: Optional[Union[str, ClusteringPolicy]] = ..., 
                defer_upgrade: Optional[Union[str, DeferUpgradeSetting]] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                geo_replication: Optional[DatabasePropertiesGeoReplication] = ..., 
                modules: Optional[list[Module]] = ..., 
                persistence: Optional[Persistence] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.DatabaseProperties(_Model):
        access_keys_authentication: Optional[Union[str, AccessKeysAuthentication]]
        client_protocol: Optional[Union[str, Protocol]]
        clustering_policy: Optional[Union[str, ClusteringPolicy]]
        defer_upgrade: Optional[Union[str, DeferUpgradeSetting]]
        eviction_policy: Optional[Union[str, EvictionPolicy]]
        geo_replication: Optional[DatabasePropertiesGeoReplication]
        modules: Optional[list[Module]]
        persistence: Optional[Persistence]
        port: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        redis_version: Optional[str]
        resource_state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                access_keys_authentication: Optional[Union[str, AccessKeysAuthentication]] = ..., 
                client_protocol: Optional[Union[str, Protocol]] = ..., 
                clustering_policy: Optional[Union[str, ClusteringPolicy]] = ..., 
                defer_upgrade: Optional[Union[str, DeferUpgradeSetting]] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                geo_replication: Optional[DatabasePropertiesGeoReplication] = ..., 
                modules: Optional[list[Module]] = ..., 
                persistence: Optional[Persistence] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.DatabasePropertiesGeoReplication(_Model):
        group_nickname: Optional[str]
        linked_databases: Optional[list[LinkedDatabase]]

        @overload
        def __init__(
                self, 
                *, 
                group_nickname: Optional[str] = ..., 
                linked_databases: Optional[list[LinkedDatabase]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.DatabaseUpdate(_Model):
        properties: Optional[DatabaseUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redisenterprise.models.DatabaseUpdateProperties(DatabaseProperties):
        access_keys_authentication: Union[str, AccessKeysAuthentication]
        client_protocol: Union[str, Protocol]
        clustering_policy: Union[str, ClusteringPolicy]
        defer_upgrade: Union[str, DeferUpgradeSetting]
        eviction_policy: Union[str, EvictionPolicy]
        geo_replication: DatabasePropertiesGeoReplication
        modules: list[Module]
        persistence: Persistence
        port: int
        provisioning_state: Union[str, ProvisioningState]
        redis_version: str
        resource_state: Union[str, ResourceState]

        @overload
        def __init__(
                self, 
                *, 
                access_keys_authentication: Optional[Union[str, AccessKeysAuthentication]] = ..., 
                client_protocol: Optional[Union[str, Protocol]] = ..., 
                clustering_policy: Optional[Union[str, ClusteringPolicy]] = ..., 
                defer_upgrade: Optional[Union[str, DeferUpgradeSetting]] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                geo_replication: Optional[DatabasePropertiesGeoReplication] = ..., 
                modules: Optional[list[Module]] = ..., 
                persistence: Optional[Persistence] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.DeferUpgradeSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFERRED = "Deferred"
        NOT_DEFERRED = "NotDeferred"


    class azure.mgmt.redisenterprise.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.redisenterprise.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.redisenterprise.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.EvictionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_KEYS_LFU = "AllKeysLFU"
        ALL_KEYS_LRU = "AllKeysLRU"
        ALL_KEYS_RANDOM = "AllKeysRandom"
        NO_EVICTION = "NoEviction"
        VOLATILE_LFU = "VolatileLFU"
        VOLATILE_LRU = "VolatileLRU"
        VOLATILE_RANDOM = "VolatileRandom"
        VOLATILE_TTL = "VolatileTTL"


    class azure.mgmt.redisenterprise.models.ExportClusterParameters(_Model):
        sas_uri: str

        @overload
        def __init__(
                self, 
                *, 
                sas_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.FlushParameters(_Model):
        ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ForceLinkParameters(_Model):
        geo_replication: ForceLinkParametersGeoReplication

        @overload
        def __init__(
                self, 
                *, 
                geo_replication: ForceLinkParametersGeoReplication
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ForceLinkParametersGeoReplication(_Model):
        group_nickname: Optional[str]
        linked_databases: Optional[list[LinkedDatabase]]

        @overload
        def __init__(
                self, 
                *, 
                group_nickname: Optional[str] = ..., 
                linked_databases: Optional[list[LinkedDatabase]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ForceUnlinkParameters(_Model):
        ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.HighAvailability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redisenterprise.models.ImportClusterParameters(_Model):
        sas_uris: list[str]

        @overload
        def __init__(
                self, 
                *, 
                sas_uris: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "v1"
        V2 = "v2"


    class azure.mgmt.redisenterprise.models.LinkState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINKED = "Linked"
        LINKING = "Linking"
        LINK_FAILED = "LinkFailed"
        UNLINKING = "Unlinking"
        UNLINK_FAILED = "UnlinkFailed"


    class azure.mgmt.redisenterprise.models.LinkedDatabase(_Model):
        id: Optional[str]
        state: Optional[Union[str, LinkState]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MaintenanceConfiguration(_Model):
        maintenance_windows: Optional[list[MaintenanceWindow]]

        @overload
        def __init__(
                self, 
                *, 
                maintenance_windows: Optional[list[MaintenanceWindow]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MaintenanceDayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.redisenterprise.models.MaintenanceWindow(_Model):
        duration: str
        schedule: MaintenanceWindowSchedule
        start_hour_utc: int
        type: Union[str, MaintenanceWindowType]

        @overload
        def __init__(
                self, 
                *, 
                duration: str, 
                schedule: MaintenanceWindowSchedule, 
                start_hour_utc: int, 
                type: Union[str, MaintenanceWindowType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MaintenanceWindowSchedule(_Model):
        day_of_week: Optional[Union[str, MaintenanceDayOfWeek]]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, MaintenanceDayOfWeek]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MaintenanceWindowType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEEKLY = "Weekly"


    class azure.mgmt.redisenterprise.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.redisenterprise.models.Migration(ProxyResource):
        id: str
        name: str
        properties: Optional[MigrationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MigrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MigrationProperties(_Model):
        creation_time: Optional[datetime]
        last_modified_time: Optional[datetime]
        provisioning_state: Optional[Union[str, MigrationProvisioningState]]
        source_type: str
        status_details: Optional[str]
        target_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MigrationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELLATION_FAILED = "CancellationFailed"
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        READY_FOR_DNS_SWITCH = "ReadyForDnsSwitch"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.redisenterprise.models.MigrationValidationDisparity(_Model):
        category: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MigrationValidationError(_Model):
        disparities: list[MigrationValidationDisparity]

        @overload
        def __init__(
                self, 
                *, 
                disparities: list[MigrationValidationDisparity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MigrationValidationRequest(_Model):
        force_migrate: Optional[bool]
        skip_data_migration: Optional[bool]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                force_migrate: Optional[bool] = ..., 
                skip_data_migration: Optional[bool] = ..., 
                source_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MigrationValidationResponse(_Model):
        errors: Optional[list[MigrationValidationError]]
        is_valid: bool
        warnings: Optional[list[MigrationValidationWarning]]

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[MigrationValidationError]] = ..., 
                is_valid: bool, 
                warnings: Optional[list[MigrationValidationWarning]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.MigrationValidationWarning(_Model):
        disparities: list[MigrationValidationDisparity]

        @overload
        def __init__(
                self, 
                *, 
                disparities: list[MigrationValidationDisparity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.Module(_Model):
        args: Optional[str]
        name: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                args: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.Operation(_Model):
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


    class azure.mgmt.redisenterprise.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.redisenterprise.models.OperationStatus(_Model):
        end_time: Optional[str]
        error: Optional[ErrorResponse]
        id: Optional[str]
        name: Optional[str]
        start_time: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                error: Optional[ErrorResponse] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.redisenterprise.models.Persistence(_Model):
        aof_enabled: Optional[bool]
        aof_frequency: Optional[Union[str, AofFrequency]]
        rdb_enabled: Optional[bool]
        rdb_frequency: Optional[Union[str, RdbFrequency]]

        @overload
        def __init__(
                self, 
                *, 
                aof_enabled: Optional[bool] = ..., 
                aof_frequency: Optional[Union[str, AofFrequency]] = ..., 
                rdb_enabled: Optional[bool] = ..., 
                rdb_frequency: Optional[Union[str, RdbFrequency]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.redisenterprise.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.redisenterprise.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.redisenterprise.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.redisenterprise.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.redisenterprise.models.PrivateLinkResource(Resource):
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


    class azure.mgmt.redisenterprise.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.redisenterprise.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.redisenterprise.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENCRYPTED = "Encrypted"
        PLAINTEXT = "Plaintext"


    class azure.mgmt.redisenterprise.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.redisenterprise.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.redisenterprise.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redisenterprise.models.RdbFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_H = "1h"
        SIX_H = "6h"
        TWELVE_H = "12h"


    class azure.mgmt.redisenterprise.models.RedundancyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LR = "LR"
        NONE = "None"
        ZR = "ZR"


    class azure.mgmt.redisenterprise.models.RegenerateKeyParameters(_Model):
        key_type: Union[str, AccessKeyType]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Union[str, AccessKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.redisenterprise.models.ResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        DISABLE_FAILED = "DisableFailed"
        DISABLING = "Disabling"
        ENABLE_FAILED = "EnableFailed"
        ENABLING = "Enabling"
        MOVING = "Moving"
        RUNNING = "Running"
        SCALING = "Scaling"
        SCALING_FAILED = "ScalingFailed"
        UPDATE_FAILED = "UpdateFailed"
        UPDATING = "Updating"


    class azure.mgmt.redisenterprise.models.Sku(_Model):
        capacity: Optional[int]
        name: Union[str, SkuName]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.SkuDetails(_Model):
        name: Optional[str]
        size_in_gb: Optional[float]


    class azure.mgmt.redisenterprise.models.SkuDetailsList(_Model):
        skus: Optional[list[SkuDetails]]

        @overload
        def __init__(
                self, 
                *, 
                skus: Optional[list[SkuDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redisenterprise.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BALANCED_B0 = "Balanced_B0"
        BALANCED_B1 = "Balanced_B1"
        BALANCED_B10 = "Balanced_B10"
        BALANCED_B100 = "Balanced_B100"
        BALANCED_B1000 = "Balanced_B1000"
        BALANCED_B150 = "Balanced_B150"
        BALANCED_B20 = "Balanced_B20"
        BALANCED_B250 = "Balanced_B250"
        BALANCED_B3 = "Balanced_B3"
        BALANCED_B350 = "Balanced_B350"
        BALANCED_B5 = "Balanced_B5"
        BALANCED_B50 = "Balanced_B50"
        BALANCED_B500 = "Balanced_B500"
        BALANCED_B700 = "Balanced_B700"
        COMPUTE_OPTIMIZED_X10 = "ComputeOptimized_X10"
        COMPUTE_OPTIMIZED_X100 = "ComputeOptimized_X100"
        COMPUTE_OPTIMIZED_X150 = "ComputeOptimized_X150"
        COMPUTE_OPTIMIZED_X20 = "ComputeOptimized_X20"
        COMPUTE_OPTIMIZED_X250 = "ComputeOptimized_X250"
        COMPUTE_OPTIMIZED_X3 = "ComputeOptimized_X3"
        COMPUTE_OPTIMIZED_X350 = "ComputeOptimized_X350"
        COMPUTE_OPTIMIZED_X5 = "ComputeOptimized_X5"
        COMPUTE_OPTIMIZED_X50 = "ComputeOptimized_X50"
        COMPUTE_OPTIMIZED_X500 = "ComputeOptimized_X500"
        COMPUTE_OPTIMIZED_X700 = "ComputeOptimized_X700"
        ENTERPRISE_E1 = "Enterprise_E1"
        ENTERPRISE_E10 = "Enterprise_E10"
        ENTERPRISE_E100 = "Enterprise_E100"
        ENTERPRISE_E20 = "Enterprise_E20"
        ENTERPRISE_E200 = "Enterprise_E200"
        ENTERPRISE_E400 = "Enterprise_E400"
        ENTERPRISE_E5 = "Enterprise_E5"
        ENTERPRISE_E50 = "Enterprise_E50"
        ENTERPRISE_FLASH_F1500 = "EnterpriseFlash_F1500"
        ENTERPRISE_FLASH_F300 = "EnterpriseFlash_F300"
        ENTERPRISE_FLASH_F700 = "EnterpriseFlash_F700"
        FLASH_OPTIMIZED_A1000 = "FlashOptimized_A1000"
        FLASH_OPTIMIZED_A1500 = "FlashOptimized_A1500"
        FLASH_OPTIMIZED_A2000 = "FlashOptimized_A2000"
        FLASH_OPTIMIZED_A250 = "FlashOptimized_A250"
        FLASH_OPTIMIZED_A4500 = "FlashOptimized_A4500"
        FLASH_OPTIMIZED_A500 = "FlashOptimized_A500"
        FLASH_OPTIMIZED_A700 = "FlashOptimized_A700"
        MEMORY_OPTIMIZED_M10 = "MemoryOptimized_M10"
        MEMORY_OPTIMIZED_M100 = "MemoryOptimized_M100"
        MEMORY_OPTIMIZED_M1000 = "MemoryOptimized_M1000"
        MEMORY_OPTIMIZED_M150 = "MemoryOptimized_M150"
        MEMORY_OPTIMIZED_M1500 = "MemoryOptimized_M1500"
        MEMORY_OPTIMIZED_M20 = "MemoryOptimized_M20"
        MEMORY_OPTIMIZED_M2000 = "MemoryOptimized_M2000"
        MEMORY_OPTIMIZED_M250 = "MemoryOptimized_M250"
        MEMORY_OPTIMIZED_M350 = "MemoryOptimized_M350"
        MEMORY_OPTIMIZED_M50 = "MemoryOptimized_M50"
        MEMORY_OPTIMIZED_M500 = "MemoryOptimized_M500"
        MEMORY_OPTIMIZED_M700 = "MemoryOptimized_M700"


    class azure.mgmt.redisenterprise.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CACHE_FOR_REDIS = "AzureCacheForRedis"


    class azure.mgmt.redisenterprise.models.SystemData(_Model):
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


    class azure.mgmt.redisenterprise.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"


    class azure.mgmt.redisenterprise.models.TrackedResource(Resource):
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


    class azure.mgmt.redisenterprise.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.redisenterprise.operations

    class azure.mgmt.redisenterprise.operations.AccessPolicyAssignmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                parameters: AccessPolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessPolicyAssignment]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessPolicyAssignment]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessPolicyAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                access_policy_assignment_name: str, 
                **kwargs: Any
            ) -> AccessPolicyAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessPolicyAssignment]: ...


    class azure.mgmt.redisenterprise.operations.DatabasesOperations:

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
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ExportClusterParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_flush(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Optional[FlushParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_flush(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_flush(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_force_link_to_replication_group(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ForceLinkParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_force_link_to_replication_group(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_force_link_to_replication_group(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_force_unlink(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ForceUnlinkParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_force_unlink(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_force_unlink(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_method(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: ImportClusterParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_method(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_method(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: DatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @distributed_trace
        def begin_upgrade_db_redis_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Database]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.redisenterprise.operations.MigrationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Migration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Migration]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Migration]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Migration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Migration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Migration]: ...


    class azure.mgmt.redisenterprise.operations.MigrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: MigrationValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationValidationResponse: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationValidationResponse: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MigrationValidationResponse: ...


    class azure.mgmt.redisenterprise.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.redisenterprise.operations.OperationsStatusOperations:

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
            ) -> OperationStatus: ...


    class azure.mgmt.redisenterprise.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.redisenterprise.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.redisenterprise.operations.RedisEnterpriseOperations:

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
                parameters: JSON, 
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
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
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

        @distributed_trace
        def list_skus_for_scaling(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> SkuDetailsList: ...


```