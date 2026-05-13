```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.mongocluster

    class azure.mgmt.mongocluster.MongoClusterMgmtClient: implements ContextManager 
        firewall_rules: FirewallRulesOperations
        mongo_clusters: MongoClustersOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_links: PrivateLinksOperations
        replicas: ReplicasOperations
        users: UsersOperations

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


namespace azure.mgmt.mongocluster.aio

    class azure.mgmt.mongocluster.aio.MongoClusterMgmtClient: implements AsyncContextManager 
        firewall_rules: FirewallRulesOperations
        mongo_clusters: MongoClustersOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_links: PrivateLinksOperations
        replicas: ReplicasOperations
        users: UsersOperations

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


namespace azure.mgmt.mongocluster.aio.operations

    class azure.mgmt.mongocluster.aio.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                resource: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FirewallRule]: ...


    class azure.mgmt.mongocluster.aio.operations.MongoClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                resource: MongoCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_promote(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                body: PromoteReplicaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_promote(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_promote(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                properties: MongoClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoCluster]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> MongoCluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[MongoCluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoCluster]: ...

        @distributed_trace_async
        async def list_connection_strings(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ListConnectionStringsResult: ...


    class azure.mgmt.mongocluster.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.mongocluster.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnectionResource]: ...


    class azure.mgmt.mongocluster.aio.operations.PrivateLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.mongocluster.aio.operations.ReplicasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-01-preview', params_added_on={'2024-06-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'accept']}, api_versions_list=['2024-06-01-preview', '2024-07-01', '2024-10-01-preview', '2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Replica]: ...


    class azure.mgmt.mongocluster.aio.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                resource: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'user_name']}, api_versions_list=['2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'user_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[User]: ...


namespace azure.mgmt.mongocluster.models

    class azure.mgmt.mongocluster.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.mongocluster.models.AdministratorProperties(_Model):
        password: Optional[str]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.AuthConfigProperties(_Model):
        allowed_modes: Optional[list[Union[str, AuthenticationMode]]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_modes: Optional[list[Union[str, AuthenticationMode]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.AuthenticationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_ENTRA_ID = "MicrosoftEntraID"
        NATIVE_AUTH = "NativeAuth"


    class azure.mgmt.mongocluster.models.BackupProperties(_Model):
        earliest_restore_time: Optional[str]


    class azure.mgmt.mongocluster.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.mongocluster.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.mongocluster.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.mongocluster.models.ComputeProperties(_Model):
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.ConnectionString(_Model):
        connection_string: Optional[str]
        description: Optional[str]
        name: Optional[str]


    class azure.mgmt.mongocluster.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        GEO_REPLICA = "GeoReplica"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"
        REPLICA = "Replica"


    class azure.mgmt.mongocluster.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.mongocluster.models.CustomerManagedKeyEncryptionProperties(_Model):
        key_encryption_key_identity: Optional[KeyEncryptionKeyIdentity]
        key_encryption_key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key_identity: Optional[KeyEncryptionKeyIdentity] = ..., 
                key_encryption_key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.DataApiMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mongocluster.models.DataApiProperties(_Model):
        mode: Optional[Union[str, DataApiMode]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, DataApiMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.DatabaseRole(_Model):
        db: str
        role: Union[str, UserRole]

        @overload
        def __init__(
                self, 
                *, 
                db: str, 
                role: Union[str, UserRole]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.EncryptionProperties(_Model):
        customer_managed_key_encryption: Optional[CustomerManagedKeyEncryptionProperties]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: Optional[CustomerManagedKeyEncryptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.EntraIdentityProvider(IdentityProvider, discriminator='MicrosoftEntraID'):
        properties: EntraIdentityProviderProperties
        type: Literal[IdentityProviderType.MICROSOFT_ENTRA_ID]

        @overload
        def __init__(
                self, 
                *, 
                properties: EntraIdentityProviderProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.EntraIdentityProviderProperties(_Model):
        principal_type: Union[str, EntraPrincipalType]

        @overload
        def __init__(
                self, 
                *, 
                principal_type: Union[str, EntraPrincipalType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.EntraPrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_PRINCIPAL = "servicePrincipal"
        USER = "user"


    class azure.mgmt.mongocluster.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.mongocluster.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.mongocluster.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.FirewallRule(ProxyResource):
        id: str
        name: str
        properties: Optional[FirewallRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FirewallRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.FirewallRuleProperties(_Model):
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


    class azure.mgmt.mongocluster.models.HighAvailabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        SAME_ZONE = "SameZone"
        ZONE_REDUNDANT_PREFERRED = "ZoneRedundantPreferred"


    class azure.mgmt.mongocluster.models.HighAvailabilityProperties(_Model):
        target_mode: Optional[Union[str, HighAvailabilityMode]]

        @overload
        def __init__(
                self, 
                *, 
                target_mode: Optional[Union[str, HighAvailabilityMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.IdentityProvider(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.IdentityProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_ENTRA_ID = "MicrosoftEntraID"


    class azure.mgmt.mongocluster.models.KeyEncryptionKeyIdentity(_Model):
        identity_type: Optional[Union[str, KeyEncryptionKeyIdentityType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_type: Optional[Union[str, KeyEncryptionKeyIdentityType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.KeyEncryptionKeyIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER_ASSIGNED_IDENTITY = "UserAssignedIdentity"


    class azure.mgmt.mongocluster.models.ListConnectionStringsResult(_Model):
        connection_strings: Optional[list[ConnectionString]]


    class azure.mgmt.mongocluster.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.mongocluster.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.mongocluster.models.MongoCluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[MongoClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[MongoClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.MongoClusterProperties(_Model):
        administrator: Optional[AdministratorProperties]
        auth_config: Optional[AuthConfigProperties]
        backup: Optional[BackupProperties]
        cluster_status: Optional[Union[str, MongoClusterStatus]]
        compute: Optional[ComputeProperties]
        connection_string: Optional[str]
        create_mode: Optional[Union[str, CreateMode]]
        data_api: Optional[DataApiProperties]
        encryption: Optional[EncryptionProperties]
        high_availability: Optional[HighAvailabilityProperties]
        infrastructure_version: Optional[str]
        preview_features: Optional[list[Union[str, PreviewFeature]]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        replica: Optional[ReplicationProperties]
        replica_parameters: Optional[MongoClusterReplicaParameters]
        restore_parameters: Optional[MongoClusterRestoreParameters]
        server_version: Optional[str]
        sharding: Optional[ShardingProperties]
        storage: Optional[StorageProperties]

        @overload
        def __init__(
                self, 
                *, 
                administrator: Optional[AdministratorProperties] = ..., 
                auth_config: Optional[AuthConfigProperties] = ..., 
                backup: Optional[BackupProperties] = ..., 
                compute: Optional[ComputeProperties] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                data_api: Optional[DataApiProperties] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                high_availability: Optional[HighAvailabilityProperties] = ..., 
                preview_features: Optional[list[Union[str, PreviewFeature]]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                replica_parameters: Optional[MongoClusterReplicaParameters] = ..., 
                restore_parameters: Optional[MongoClusterRestoreParameters] = ..., 
                server_version: Optional[str] = ..., 
                sharding: Optional[ShardingProperties] = ..., 
                storage: Optional[StorageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.MongoClusterReplicaParameters(_Model):
        source_location: str
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                source_location: str, 
                source_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.MongoClusterRestoreParameters(_Model):
        point_in_time_utc: Optional[datetime]
        source_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                point_in_time_utc: Optional[datetime] = ..., 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.MongoClusterStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DROPPING = "Dropping"
        PROVISIONING = "Provisioning"
        READY = "Ready"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UPDATING = "Updating"


    class azure.mgmt.mongocluster.models.MongoClusterUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[MongoClusterUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[MongoClusterUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.MongoClusterUpdateProperties(_Model):
        administrator: Optional[AdministratorProperties]
        auth_config: Optional[AuthConfigProperties]
        backup: Optional[BackupProperties]
        compute: Optional[ComputeProperties]
        data_api: Optional[DataApiProperties]
        encryption: Optional[EncryptionProperties]
        high_availability: Optional[HighAvailabilityProperties]
        preview_features: Optional[list[Union[str, PreviewFeature]]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        server_version: Optional[str]
        sharding: Optional[ShardingProperties]
        storage: Optional[StorageProperties]

        @overload
        def __init__(
                self, 
                *, 
                administrator: Optional[AdministratorProperties] = ..., 
                auth_config: Optional[AuthConfigProperties] = ..., 
                backup: Optional[BackupProperties] = ..., 
                compute: Optional[ComputeProperties] = ..., 
                data_api: Optional[DataApiProperties] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                high_availability: Optional[HighAvailabilityProperties] = ..., 
                preview_features: Optional[list[Union[str, PreviewFeature]]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                server_version: Optional[str] = ..., 
                sharding: Optional[ShardingProperties] = ..., 
                storage: Optional[StorageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.Operation(_Model):
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


    class azure.mgmt.mongocluster.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.mongocluster.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.mongocluster.models.PreviewFeature(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_REPLICAS = "GeoReplicas"


    class azure.mgmt.mongocluster.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.mongocluster.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.mongocluster.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.mongocluster.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.mongocluster.models.PrivateEndpointConnectionResource(ProxyResource):
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


    class azure.mgmt.mongocluster.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.mongocluster.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.mongocluster.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.mongocluster.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.mongocluster.models.PromoteMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SWITCHOVER = "Switchover"


    class azure.mgmt.mongocluster.models.PromoteOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCED = "Forced"


    class azure.mgmt.mongocluster.models.PromoteReplicaRequest(_Model):
        mode: Optional[Union[str, PromoteMode]]
        promote_option: Union[str, PromoteOption]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, PromoteMode]] = ..., 
                promote_option: Union[str, PromoteOption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DROPPING = "Dropping"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.mongocluster.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.mongocluster.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.mongocluster.models.Replica(ProxyResource):
        id: str
        name: str
        properties: Optional[MongoClusterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoClusterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.ReplicationProperties(_Model):
        replication_state: Optional[Union[str, ReplicationState]]
        role: Optional[Union[str, ReplicationRole]]
        source_resource_id: Optional[str]


    class azure.mgmt.mongocluster.models.ReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNC_REPLICA = "AsyncReplica"
        GEO_ASYNC_REPLICA = "GeoAsyncReplica"
        PRIMARY = "Primary"


    class azure.mgmt.mongocluster.models.ReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        BROKEN = "Broken"
        CATCHUP = "Catchup"
        PROVISIONING = "Provisioning"
        RECONFIGURING = "Reconfiguring"
        UPDATING = "Updating"


    class azure.mgmt.mongocluster.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.mongocluster.models.ShardingProperties(_Model):
        shard_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                shard_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.StorageProperties(_Model):
        size_gb: Optional[int]
        type: Optional[Union[str, StorageType]]

        @overload
        def __init__(
                self, 
                *, 
                size_gb: Optional[int] = ..., 
                type: Optional[Union[str, StorageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_SSD = "PremiumSSD"
        PREMIUM_SS_DV2 = "PremiumSSDv2"


    class azure.mgmt.mongocluster.models.SystemData(_Model):
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


    class azure.mgmt.mongocluster.models.TrackedResource(Resource):
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


    class azure.mgmt.mongocluster.models.User(ProxyResource):
        id: str
        name: str
        properties: Optional[UserProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UserProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.mongocluster.models.UserProperties(_Model):
        identity_provider: Optional[IdentityProvider]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        roles: Optional[list[DatabaseRole]]

        @overload
        def __init__(
                self, 
                *, 
                identity_provider: Optional[IdentityProvider] = ..., 
                roles: Optional[list[DatabaseRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongocluster.models.UserRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ROOT = "root"


namespace azure.mgmt.mongocluster.operations

    class azure.mgmt.mongocluster.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                resource: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FirewallRule]: ...


    class azure.mgmt.mongocluster.operations.MongoClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                resource: MongoCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_promote(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                body: PromoteReplicaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_promote(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_promote(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                properties: MongoClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoCluster]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> MongoCluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[MongoCluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoCluster]: ...

        @distributed_trace
        def list_connection_strings(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ListConnectionStringsResult: ...


    class azure.mgmt.mongocluster.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.mongocluster.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnectionResource]: ...


    class azure.mgmt.mongocluster.operations.PrivateLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.mongocluster.operations.ReplicasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-01-preview', params_added_on={'2024-06-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'accept']}, api_versions_list=['2024-06-01-preview', '2024-07-01', '2024-10-01-preview', '2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Replica]: ...


    class azure.mgmt.mongocluster.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                resource: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'user_name']}, api_versions_list=['2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'user_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                user_name: str, 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'mongo_cluster_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-09-01'])
        def list_by_mongo_cluster(
                self, 
                resource_group_name: str, 
                mongo_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[User]: ...


```