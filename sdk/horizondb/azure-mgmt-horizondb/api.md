```py
namespace azure.mgmt.horizondb

    class azure.mgmt.horizondb.HorizonDBMgmtClient: implements ContextManager 
        horizon_db_administrators: HorizonDbAdministratorsOperations
        horizon_db_clusters: HorizonDbClustersOperations
        horizon_db_firewall_rules: HorizonDbFirewallRulesOperations
        horizon_db_parameter_groups: HorizonDbParameterGroupsOperations
        horizon_db_pools: HorizonDbPoolsOperations
        horizon_db_private_endpoint_connections: HorizonDbPrivateEndpointConnectionsOperations
        horizon_db_private_link_resources: HorizonDbPrivateLinkResourcesOperations
        horizon_db_replicas: HorizonDbReplicasOperations
        operations: Operations

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


namespace azure.mgmt.horizondb.aio

    class azure.mgmt.horizondb.aio.HorizonDBMgmtClient: implements AsyncContextManager 
        horizon_db_administrators: HorizonDbAdministratorsOperations
        horizon_db_clusters: HorizonDbClustersOperations
        horizon_db_firewall_rules: HorizonDbFirewallRulesOperations
        horizon_db_parameter_groups: HorizonDbParameterGroupsOperations
        horizon_db_pools: HorizonDbPoolsOperations
        horizon_db_private_endpoint_connections: HorizonDbPrivateEndpointConnectionsOperations
        horizon_db_private_link_resources: HorizonDbPrivateLinkResourcesOperations
        horizon_db_replicas: HorizonDbReplicasOperations
        operations: Operations

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


namespace azure.mgmt.horizondb.aio.operations

    class azure.mgmt.horizondb.aio.operations.HorizonDbAdministratorsOperations:

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
                object_id: str, 
                resource: HorizonDbAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbAdministrator]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: HorizonDbAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbAdministrator]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbAdministrator]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'object_id']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'object_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> HorizonDbAdministrator: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbAdministrator]: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbClustersOperations:

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
                resource: HorizonDbCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: HorizonDbCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
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
                properties: HorizonDbClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: HorizonDbClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> HorizonDbCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[HorizonDbCluster]: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbFirewallRulesOperations:

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
                pool_name: str, 
                firewall_rule_name: str, 
                resource: HorizonDbFirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbFirewallRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: HorizonDbFirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbFirewallRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbFirewallRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> HorizonDbFirewallRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbFirewallRule]: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbParameterGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: HorizonDbParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbParameterGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: HorizonDbParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbParameterGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbParameterGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: HorizonDbParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbParameterGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: HorizonDbParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbParameterGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbParameterGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> HorizonDbParameterGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbParameterGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[HorizonDbParameterGroup]: ...

        @distributed_trace
        def list_connections(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbParameterGroupConnectionProperties]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                *, 
                version: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbParameterGroup]: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbPoolsOperations:

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
                pool_name: str, 
                **kwargs: Any
            ) -> HorizonDbPool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbPool]: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbPrivateEndpointConnectionsOperations:

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

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnectionResource]: ...

        @overload
        async def update_status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @overload
        async def update_status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @overload
        async def update_status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbPrivateLinkResourcesOperations:

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
                group_name: str, 
                **kwargs: Any
            ) -> HorizonDbPrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbPrivateLinkResource]: ...


    class azure.mgmt.horizondb.aio.operations.HorizonDbReplicasOperations:

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
                pool_name: str, 
                replica_name: str, 
                resource: HorizonDbReplica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbReplica]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                resource: HorizonDbReplica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbReplica]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbReplica]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                properties: HorizonDbReplicaForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbReplica]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                properties: HorizonDbReplicaForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbReplica]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HorizonDbReplica]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> HorizonDbReplica: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HorizonDbReplica]: ...


    class azure.mgmt.horizondb.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.horizondb.models

    class azure.mgmt.horizondb.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.horizondb.models.AuthenticationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.CreateModeCluster(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"
        UPDATE = "Update"


    class azure.mgmt.horizondb.models.CreateModePool(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        UPDATE = "Update"


    class azure.mgmt.horizondb.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.horizondb.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.horizondb.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.horizondb.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbAdministrator(ProxyResource):
        id: str
        name: str
        properties: Optional[HorizonDbAdministratorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HorizonDbAdministratorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbAdministratorAdd(_Model):
        properties: HorizonDbAdministratorPropertiesForAdd

        @overload
        def __init__(
                self, 
                *, 
                properties: HorizonDbAdministratorPropertiesForAdd
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbAdministratorProperties(_Model):
        object_id: Optional[str]
        principal_name: str
        principal_type: Union[str, PrincipalTypes]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_name: str, 
                principal_type: Union[str, PrincipalTypes], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbAdministratorPropertiesForAdd(_Model):
        principal_name: str
        principal_type: Union[str, PrincipalTypes]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_name: str, 
                principal_type: Union[str, PrincipalTypes], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbCluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[HorizonDbClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[HorizonDbClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterAuthConfig(_Model):
        entra_id_auth: Optional[Union[str, AuthenticationState]]
        password_auth: Optional[Union[str, AuthenticationState]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                entra_id_auth: Optional[Union[str, AuthenticationState]] = ..., 
                password_auth: Optional[Union[str, AuthenticationState]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterForPatchUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[HorizonDbClusterPropertiesForPatchUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[HorizonDbClusterPropertiesForPatchUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterMirroring(_Model):
        database_names: Optional[list[str]]
        user_assigned_identity_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                database_names: Optional[list[str]] = ..., 
                user_assigned_identity_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterParameterGroupConnectionProperties(_Model):
        apply_immediately: Optional[bool]
        id: Optional[str]
        sync_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apply_immediately: Optional[bool] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterProperties(_Model):
        administrator_login: str
        administrator_login_password: Optional[str]
        auth_config: Optional[HorizonDbClusterAuthConfig]
        compute_model: Optional[HorizonDbComputeModel]
        create_mode: Optional[Union[str, CreateModeCluster]]
        fully_qualified_domain_name: Optional[str]
        mirroring: Optional[HorizonDbClusterMirroring]
        network: Optional[Network]
        parameter_group: Optional[HorizonDbClusterParameterGroupConnectionProperties]
        point_in_time_utc: Optional[datetime]
        pool_name: Optional[str]
        processor_type: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        readonly_endpoint: Optional[str]
        replica_count: Optional[int]
        source_cluster_resource_id: Optional[str]
        state: Optional[Union[str, State]]
        v_cores: Optional[int]
        version: Optional[str]
        zone_placement_policy: Optional[Union[str, ZonePlacementPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login: str, 
                administrator_login_password: Optional[str] = ..., 
                auth_config: Optional[HorizonDbClusterAuthConfig] = ..., 
                compute_model: Optional[HorizonDbComputeModel] = ..., 
                create_mode: Optional[Union[str, CreateModeCluster]] = ..., 
                mirroring: Optional[HorizonDbClusterMirroring] = ..., 
                network: Optional[Network] = ..., 
                parameter_group: Optional[HorizonDbClusterParameterGroupConnectionProperties] = ..., 
                point_in_time_utc: Optional[datetime] = ..., 
                pool_name: Optional[str] = ..., 
                processor_type: Optional[str] = ..., 
                replica_count: Optional[int] = ..., 
                source_cluster_resource_id: Optional[str] = ..., 
                v_cores: Optional[int] = ..., 
                version: Optional[str] = ..., 
                zone_placement_policy: Optional[Union[str, ZonePlacementPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterPropertiesForPatchUpdate(_Model):
        administrator_login_password: Optional[str]
        auth_config: Optional[HorizonDbClusterAuthConfig]
        compute_model: Optional[HorizonDbComputeModel]
        mirroring: Optional[HorizonDbClusterMirroring]
        parameter_group: Optional[HorizonDbClusterParameterGroupConnectionProperties]
        v_cores: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                auth_config: Optional[HorizonDbClusterAuthConfig] = ..., 
                compute_model: Optional[HorizonDbComputeModel] = ..., 
                mirroring: Optional[HorizonDbClusterMirroring] = ..., 
                parameter_group: Optional[HorizonDbClusterParameterGroupConnectionProperties] = ..., 
                v_cores: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbComputeModel(_Model):
        maxv_cores: Optional[float]
        minv_cores: Optional[float]
        type: Optional[Union[str, HorizonDbComputeModelType]]
        v_cores: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                maxv_cores: Optional[float] = ..., 
                minv_cores: Optional[float] = ..., 
                type: Optional[Union[str, HorizonDbComputeModelType]] = ..., 
                v_cores: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbComputeModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVISIONED = "Provisioned"
        SERVERLESS = "Serverless"


    class azure.mgmt.horizondb.models.HorizonDbFirewallRule(ProxyResource):
        id: str
        name: str
        properties: Optional[HorizonDbFirewallRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HorizonDbFirewallRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbFirewallRuleProperties(_Model):
        description: Optional[str]
        end_ip_address: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_ip_address: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                end_ip_address: str, 
                start_ip_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbParameterGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[HorizonDbParameterGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[HorizonDbParameterGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbParameterGroupConnectionProperties(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.horizondb.models.HorizonDbParameterGroupForPatchUpdate(_Model):
        properties: Optional[HorizonDbParameterGroupPropertiesForPatchUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HorizonDbParameterGroupPropertiesForPatchUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbParameterGroupProperties(_Model):
        apply_immediately: Optional[bool]
        description: Optional[str]
        parameters: Optional[list[ParameterProperties]]
        pg_version: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                apply_immediately: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                parameters: Optional[list[ParameterProperties]] = ..., 
                pg_version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbParameterGroupPropertiesForPatchUpdate(_Model):
        apply_immediately: Optional[bool]
        description: Optional[str]
        parameters: Optional[list[ParameterProperties]]

        @overload
        def __init__(
                self, 
                *, 
                apply_immediately: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                parameters: Optional[list[ParameterProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbPool(ProxyResource):
        id: str
        name: str
        properties: Optional[HorizonDbPoolProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HorizonDbPoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbPoolProperties(_Model):
        create_mode: Optional[Union[str, CreateModePool]]
        location: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replica_count: Optional[int]
        state: Optional[Union[str, State]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbPrivateLinkResource(ProxyResource):
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


    class azure.mgmt.horizondb.models.HorizonDbReplica(ProxyResource):
        id: str
        name: str
        properties: Optional[HorizonDbReplicaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HorizonDbReplicaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbReplicaForPatchUpdate(_Model):
        properties: Optional[HorizonDbReplicaPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HorizonDbReplicaPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbReplicaProperties(_Model):
        availability_zone: Optional[str]
        fully_qualified_domain_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        role: Optional[Union[str, ReplicaRole]]
        status: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                role: Optional[Union[str, ReplicaRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbReplicaPropertiesForPatchUpdate(_Model):
        role: Optional[Union[str, ReplicaRole]]

        @overload
        def __init__(
                self, 
                *, 
                role: Optional[Union[str, ReplicaRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.horizondb.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.horizondb.models.Network(_Model):
        public_network_access: Optional[Union[str, PublicNetworkAccessState]]


    class azure.mgmt.horizondb.models.Operation(_Model):
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


    class azure.mgmt.horizondb.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.horizondb.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.horizondb.models.ParameterProperties(_Model):
        allowed_values: Optional[str]
        data_type: Optional[str]
        description: Optional[str]
        documentation_link: Optional[str]
        is_dynamic: Optional[bool]
        is_read_only: Optional[bool]
        name: Optional[str]
        unit: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PrincipalTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.horizondb.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.horizondb.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.horizondb.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.horizondb.models.PrivateEndpointConnectionResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.horizondb.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.horizondb.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.horizondb.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.horizondb.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.horizondb.models.PublicNetworkAccessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.ReplicaRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ = "Read"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.horizondb.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.horizondb.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DROPPING = "Dropping"
        HEALTHY = "Healthy"
        READY = "Ready"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"
        UPGRADING = "Upgrading"


    class azure.mgmt.horizondb.models.SystemData(_Model):
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


    class azure.mgmt.horizondb.models.TrackedResource(Resource):
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


    class azure.mgmt.horizondb.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.horizondb.models.ZonePlacementPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_EFFORT = "BestEffort"
        STRICT = "Strict"


namespace azure.mgmt.horizondb.operations

    class azure.mgmt.horizondb.operations.HorizonDbAdministratorsOperations:

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
                object_id: str, 
                resource: HorizonDbAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbAdministrator]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: HorizonDbAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbAdministrator]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbAdministrator]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'object_id']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'object_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> HorizonDbAdministrator: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbAdministrator]: ...


    class azure.mgmt.horizondb.operations.HorizonDbClustersOperations:

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
                resource: HorizonDbCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: HorizonDbCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
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
                properties: HorizonDbClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: HorizonDbClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> HorizonDbCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[HorizonDbCluster]: ...


    class azure.mgmt.horizondb.operations.HorizonDbFirewallRulesOperations:

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
                pool_name: str, 
                firewall_rule_name: str, 
                resource: HorizonDbFirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbFirewallRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: HorizonDbFirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbFirewallRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbFirewallRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> HorizonDbFirewallRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbFirewallRule]: ...


    class azure.mgmt.horizondb.operations.HorizonDbParameterGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: HorizonDbParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbParameterGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: HorizonDbParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbParameterGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbParameterGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: HorizonDbParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbParameterGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: HorizonDbParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbParameterGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbParameterGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> HorizonDbParameterGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbParameterGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[HorizonDbParameterGroup]: ...

        @distributed_trace
        def list_connections(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbParameterGroupConnectionProperties]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                *, 
                version: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbParameterGroup]: ...


    class azure.mgmt.horizondb.operations.HorizonDbPoolsOperations:

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
                pool_name: str, 
                **kwargs: Any
            ) -> HorizonDbPool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbPool]: ...


    class azure.mgmt.horizondb.operations.HorizonDbPrivateEndpointConnectionsOperations:

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

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnectionResource]: ...

        @overload
        def update_status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @overload
        def update_status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @overload
        def update_status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...


    class azure.mgmt.horizondb.operations.HorizonDbPrivateLinkResourcesOperations:

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
                group_name: str, 
                **kwargs: Any
            ) -> HorizonDbPrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbPrivateLinkResource]: ...


    class azure.mgmt.horizondb.operations.HorizonDbReplicasOperations:

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
                pool_name: str, 
                replica_name: str, 
                resource: HorizonDbReplica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbReplica]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                resource: HorizonDbReplica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbReplica]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbReplica]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                properties: HorizonDbReplicaForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbReplica]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                properties: HorizonDbReplicaForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbReplica]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HorizonDbReplica]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> HorizonDbReplica: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HorizonDbReplica]: ...


    class azure.mgmt.horizondb.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.horizondb.types

    class azure.mgmt.horizondb.types.HorizonDbAdministratorAdd(TypedDict, total=False):
        key "properties": Required[HorizonDbAdministratorPropertiesForAdd]
        properties: HorizonDbAdministratorPropertiesForAdd


    class azure.mgmt.horizondb.types.HorizonDbAdministratorPropertiesForAdd(TypedDict, total=False):
        key "principalName": Required[str]
        key "principalType": Required[Union[str, PrincipalTypes]]
        key "tenantId": str
        principalName: str
        principalType: Union[str, PrincipalTypes]
        tenantId: str


    class azure.mgmt.horizondb.types.HorizonDbCluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('HorizonDbClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: HorizonDbClusterProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.horizondb.types.HorizonDbClusterAuthConfig(TypedDict, total=False):
        key "entraIdAuth": Union[str, AuthenticationState]
        key "passwordAuth": Union[str, AuthenticationState]
        key "tenantId": str
        entraIdAuth: Union[str, AuthenticationState]
        passwordAuth: Union[str, AuthenticationState]
        tenantId: str


    class azure.mgmt.horizondb.types.HorizonDbClusterForPatchUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('HorizonDbClusterPropertiesForPatchUpdate', module='types')
        identity: ManagedServiceIdentity
        properties: HorizonDbClusterPropertiesForPatchUpdate
        tags: dict[str, str]


    class azure.mgmt.horizondb.types.HorizonDbClusterMirroring(TypedDict, total=False):
        key "userAssignedIdentityId": str
        databaseNames: list[str]
        userAssignedIdentityId: str


    class azure.mgmt.horizondb.types.HorizonDbClusterParameterGroupConnectionProperties(TypedDict, total=False):
        key "applyImmediately": bool
        key "id": str
        key "syncStatus": str
        applyImmediately: bool
        id: str
        syncStatus: str


    class azure.mgmt.horizondb.types.HorizonDbClusterProperties(TypedDict, total=False):
        key "administratorLogin": Required[str]
        key "administratorLoginPassword": str
        key "authConfig": ForwardRef('HorizonDbClusterAuthConfig', module='types')
        key "computeModel": ForwardRef('HorizonDbComputeModel', module='types')
        key "createMode": Union[str, CreateModeCluster]
        key "fullyQualifiedDomainName": str
        key "mirroring": ForwardRef('HorizonDbClusterMirroring', module='types')
        key "network": ForwardRef('Network', module='types')
        key "parameterGroup": ForwardRef('HorizonDbClusterParameterGroupConnectionProperties', module='types')
        key "pointInTimeUTC": str
        key "poolName": str
        key "processorType": str
        key "provisioningState": Union[str, ProvisioningState]
        key "readonlyEndpoint": str
        key "replicaCount": int
        key "sourceClusterResourceId": str
        key "state": Union[str, State]
        key "vCores": int
        key "version": str
        key "zonePlacementPolicy": Union[str, ZonePlacementPolicy]
        administratorLogin: str
        administratorLoginPassword: str
        authConfig: HorizonDbClusterAuthConfig
        computeModel: HorizonDbComputeModel
        createMode: Union[str, CreateModeCluster]
        fullyQualifiedDomainName: str
        mirroring: HorizonDbClusterMirroring
        network: Network
        parameterGroup: HorizonDbClusterParameterGroupConnectionProperties
        pointInTimeUTC: str
        poolName: str
        processorType: str
        provisioningState: Union[str, ProvisioningState]
        readonlyEndpoint: str
        replicaCount: int
        sourceClusterResourceId: str
        state: Union[str, State]
        vCores: int
        version: str
        zonePlacementPolicy: Union[str, ZonePlacementPolicy]


    class azure.mgmt.horizondb.types.HorizonDbClusterPropertiesForPatchUpdate(TypedDict, total=False):
        key "administratorLoginPassword": str
        key "authConfig": ForwardRef('HorizonDbClusterAuthConfig', module='types')
        key "computeModel": ForwardRef('HorizonDbComputeModel', module='types')
        key "mirroring": ForwardRef('HorizonDbClusterMirroring', module='types')
        key "parameterGroup": ForwardRef('HorizonDbClusterParameterGroupConnectionProperties', module='types')
        key "vCores": int
        administratorLoginPassword: str
        authConfig: HorizonDbClusterAuthConfig
        computeModel: HorizonDbComputeModel
        mirroring: HorizonDbClusterMirroring
        parameterGroup: HorizonDbClusterParameterGroupConnectionProperties
        vCores: int


    class azure.mgmt.horizondb.types.HorizonDbComputeModel(TypedDict, total=False):
        key "maxvCores": float
        key "minvCores": float
        key "type": Union[str, HorizonDbComputeModelType]
        key "vCores": int
        maxvCores: float
        minvCores: float
        type: Union[str, HorizonDbComputeModelType]
        vCores: int


    class azure.mgmt.horizondb.types.HorizonDbFirewallRule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('HorizonDbFirewallRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: HorizonDbFirewallRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.HorizonDbFirewallRuleProperties(TypedDict, total=False):
        key "description": str
        key "endIpAddress": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "startIpAddress": Required[str]
        description: str
        endIpAddress: str
        provisioningState: Union[str, ProvisioningState]
        startIpAddress: str


    class azure.mgmt.horizondb.types.HorizonDbParameterGroup(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('HorizonDbParameterGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: HorizonDbParameterGroupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.horizondb.types.HorizonDbParameterGroupForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('HorizonDbParameterGroupPropertiesForPatchUpdate', module='types')
        properties: HorizonDbParameterGroupPropertiesForPatchUpdate
        tags: dict[str, str]


    class azure.mgmt.horizondb.types.HorizonDbParameterGroupProperties(TypedDict, total=False):
        key "applyImmediately": bool
        key "description": str
        key "pgVersion": int
        key "provisioningState": Union[str, ProvisioningState]
        key "version": int
        applyImmediately: bool
        description: str
        parameters: list[ParameterProperties]
        pgVersion: int
        provisioningState: Union[str, ProvisioningState]
        version: int


    class azure.mgmt.horizondb.types.HorizonDbParameterGroupPropertiesForPatchUpdate(TypedDict, total=False):
        key "applyImmediately": bool
        key "description": str
        applyImmediately: bool
        description: str
        parameters: list[ParameterProperties]


    class azure.mgmt.horizondb.types.HorizonDbReplica(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('HorizonDbReplicaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: HorizonDbReplicaProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.HorizonDbReplicaForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('HorizonDbReplicaPropertiesForPatchUpdate', module='types')
        properties: HorizonDbReplicaPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.HorizonDbReplicaProperties(TypedDict, total=False):
        key "availabilityZone": str
        key "fullyQualifiedDomainName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "role": Union[str, ReplicaRole]
        key "status": Union[str, State]
        availabilityZone: str
        fullyQualifiedDomainName: str
        provisioningState: Union[str, ProvisioningState]
        role: Union[str, ReplicaRole]
        status: Union[str, State]


    class azure.mgmt.horizondb.types.HorizonDbReplicaPropertiesForPatchUpdate(TypedDict, total=False):
        key "role": Union[str, ReplicaRole]
        role: Union[str, ReplicaRole]


    class azure.mgmt.horizondb.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.horizondb.types.Network(TypedDict, total=False):
        key "publicNetworkAccess": Union[str, PublicNetworkAccessState]
        publicNetworkAccess: Union[str, PublicNetworkAccessState]


    class azure.mgmt.horizondb.types.ParameterProperties(TypedDict, total=False):
        key "allowedValues": str
        key "dataType": str
        key "description": str
        key "documentationLink": str
        key "isDynamic": bool
        key "isReadOnly": bool
        key "name": str
        key "unit": str
        key "value": str
        allowedValues: str
        dataType: str
        description: str
        documentationLink: str
        isDynamic: bool
        isReadOnly: bool
        name: str
        unit: str
        value: str


    class azure.mgmt.horizondb.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.horizondb.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.horizondb.types.PrivateEndpointConnectionResource(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.horizondb.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.horizondb.types.TrackedResource(Resource):
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


    class azure.mgmt.horizondb.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```