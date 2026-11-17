```py
namespace azure.mgmt.databricks

    class azure.mgmt.databricks.AzureDatabricksManagementClient: implements ContextManager 
        access_connectors: AccessConnectorsOperations
        operations: Operations
        outbound_network_dependencies_endpoints: OutboundNetworkDependenciesEndpointsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        vnet_peering: VNetPeeringOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.databricks.aio

    class azure.mgmt.databricks.aio.AzureDatabricksManagementClient: implements AsyncContextManager 
        access_connectors: AccessConnectorsOperations
        operations: Operations
        outbound_network_dependencies_endpoints: OutboundNetworkDependenciesEndpointsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        vnet_peering: VNetPeeringOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.databricks.aio.operations

    class azure.mgmt.databricks.aio.operations.AccessConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessConnector]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessConnector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessConnector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessConnector]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AccessConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessConnector]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AccessConnector]: ...


    class azure.mgmt.databricks.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.databricks.aio.operations.OutboundNetworkDependenciesEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> List[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.databricks.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.databricks.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> GroupIdInformation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupIdInformation]: ...


    class azure.mgmt.databricks.aio.operations.VNetPeeringOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                virtual_network_peering_parameters: VirtualNetworkPeering, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkPeering]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                virtual_network_peering_parameters: VirtualNetworkPeering, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkPeering]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                virtual_network_peering_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkPeering]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> Optional[VirtualNetworkPeering]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetworkPeering]: ...


    class azure.mgmt.databricks.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                force_deletion: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Workspace]: ...


namespace azure.mgmt.databricks.models

    class azure.mgmt.databricks.models.AccessConnector(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AccessConnectorProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AccessConnectorProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.AccessConnectorProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        refered_by: Optional[list[str]]


    class azure.mgmt.databricks.models.AccessConnectorUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.AddressSpace(_Model):
        address_prefixes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.AutomaticClusterUpdateDefinition(_Model):
        value: Optional[Union[str, AutomaticClusterUpdateValue]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[Union[str, AutomaticClusterUpdateValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.AutomaticClusterUpdateValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databricks.models.ComplianceSecurityProfileDefinition(_Model):
        compliance_standards: Optional[list[str]]
        value: Optional[Union[str, ComplianceSecurityProfileValue]]

        @overload
        def __init__(
                self, 
                *, 
                compliance_standards: Optional[list[str]] = ..., 
                value: Optional[Union[str, ComplianceSecurityProfileValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.ComplianceSecurityProfileValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databricks.models.ComputeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HYBRID = "Hybrid"
        SERVERLESS = "Serverless"


    class azure.mgmt.databricks.models.CreatedBy(_Model):
        application_id: Optional[str]
        oid: Optional[str]
        puid: Optional[str]


    class azure.mgmt.databricks.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.databricks.models.CustomParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "Bool"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.databricks.models.DefaultCatalogProperties(_Model):
        initial_name: Optional[str]
        initial_type: Optional[Union[str, InitialType]]

        @overload
        def __init__(
                self, 
                *, 
                initial_name: Optional[str] = ..., 
                initial_type: Optional[Union[str, InitialType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.DefaultStorageFirewall(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databricks.models.Encryption(_Model):
        key_name: Optional[str]
        key_source: Optional[Union[str, KeySource]]
        key_vault_uri: Optional[str]
        key_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_source: Optional[Union[str, KeySource]] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EncryptionEntitiesDefinition(_Model):
        managed_disk: Optional[ManagedDiskEncryption]
        managed_services: Optional[EncryptionV2]

        @overload
        def __init__(
                self, 
                *, 
                managed_disk: Optional[ManagedDiskEncryption] = ..., 
                managed_services: Optional[EncryptionV2] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EncryptionKeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEYVAULT = "Microsoft.Keyvault"


    class azure.mgmt.databricks.models.EncryptionV2(_Model):
        key_source: Union[str, EncryptionKeySource]
        key_vault_properties: Optional[EncryptionV2KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Union[str, EncryptionKeySource], 
                key_vault_properties: Optional[EncryptionV2KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EncryptionV2KeyVaultProperties(_Model):
        key_name: str
        key_vault_uri: str
        key_version: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault_uri: str, 
                key_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EndpointDependency(_Model):
        domain_name: Optional[str]
        endpoint_details: Optional[list[EndpointDetail]]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                endpoint_details: Optional[list[EndpointDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EndpointDetail(_Model):
        ip_address: Optional[str]
        is_accessible: Optional[bool]
        latency: Optional[float]
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                is_accessible: Optional[bool] = ..., 
                latency: Optional[float] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EnhancedSecurityComplianceDefinition(_Model):
        automatic_cluster_update: Optional[AutomaticClusterUpdateDefinition]
        compliance_security_profile: Optional[ComplianceSecurityProfileDefinition]
        enhanced_security_monitoring: Optional[EnhancedSecurityMonitoringDefinition]

        @overload
        def __init__(
                self, 
                *, 
                automatic_cluster_update: Optional[AutomaticClusterUpdateDefinition] = ..., 
                compliance_security_profile: Optional[ComplianceSecurityProfileDefinition] = ..., 
                enhanced_security_monitoring: Optional[EnhancedSecurityMonitoringDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EnhancedSecurityMonitoringDefinition(_Model):
        value: Optional[Union[str, EnhancedSecurityMonitoringValue]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[Union[str, EnhancedSecurityMonitoringValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.EnhancedSecurityMonitoringValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databricks.models.ErrorDetail(_Model):
        code: str
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.ErrorInfo(_Model):
        code: str
        details: Optional[list[ErrorDetail]]
        innererror: Optional[str]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[list[ErrorDetail]] = ..., 
                innererror: Optional[str] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.ErrorResponse(_Model):
        error: ErrorInfo

        @overload
        def __init__(
                self, 
                *, 
                error: ErrorInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.GroupIdInformation(ProxyResource):
        id: str
        name: str
        properties: GroupIdInformationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: GroupIdInformationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.GroupIdInformationProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.databricks.models.InitialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIVE_METASTORE = "HiveMetastore"
        UNITY_CATALOG = "UnityCatalog"


    class azure.mgmt.databricks.models.KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        MICROSOFT_KEYVAULT = "Microsoft.Keyvault"


    class azure.mgmt.databricks.models.ManagedDiskEncryption(_Model):
        key_source: Union[str, EncryptionKeySource]
        key_vault_properties: ManagedDiskEncryptionKeyVaultProperties
        rotation_to_latest_key_version_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Union[str, EncryptionKeySource], 
                key_vault_properties: ManagedDiskEncryptionKeyVaultProperties, 
                rotation_to_latest_key_version_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.ManagedDiskEncryptionKeyVaultProperties(_Model):
        key_name: str
        key_vault_uri: str
        key_version: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault_uri: str, 
                key_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.ManagedIdentityConfiguration(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[str]


    class azure.mgmt.databricks.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.databricks.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.databricks.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.OperationDisplay(_Model):
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


    class azure.mgmt.databricks.models.OutboundEnvironmentEndpoint(_Model):
        category: Optional[str]
        endpoints: Optional[list[EndpointDependency]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[list[EndpointDependency]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.PeeringProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.databricks.models.PeeringState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        INITIATED = "Initiated"


    class azure.mgmt.databricks.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.databricks.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: PrivateEndpointConnectionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.databricks.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Union[str, PrivateLinkServiceConnectionStatus]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Union[str, PrivateLinkServiceConnectionStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.databricks.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        READY = "Ready"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.databricks.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databricks.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databricks.models.RequiredNsgRules(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_RULES = "AllRules"
        NO_AZURE_DATABRICKS_RULES = "NoAzureDatabricksRules"
        NO_AZURE_SERVICE_RULES = "NoAzureServiceRules"


    class azure.mgmt.databricks.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.databricks.models.Sku(_Model):
        name: str
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.SystemData(_Model):
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


    class azure.mgmt.databricks.models.TrackedResource(Resource):
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


    class azure.mgmt.databricks.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.databricks.models.VirtualNetworkPeering(ProxyResource):
        id: str
        name: str
        properties: VirtualNetworkPeeringPropertiesFormat
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: VirtualNetworkPeeringPropertiesFormat
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databricks.models.VirtualNetworkPeeringPropertiesFormat(_Model):
        allow_forwarded_traffic: Optional[bool]
        allow_gateway_transit: Optional[bool]
        allow_virtual_network_access: Optional[bool]
        databricks_address_space: Optional[AddressSpace]
        databricks_virtual_network: Optional[VirtualNetworkPeeringPropertiesFormatDatabricksVirtualNetwork]
        peering_state: Optional[Union[str, PeeringState]]
        provisioning_state: Optional[Union[str, PeeringProvisioningState]]
        remote_address_space: Optional[AddressSpace]
        remote_virtual_network: VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork
        use_remote_gateways: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allow_forwarded_traffic: Optional[bool] = ..., 
                allow_gateway_transit: Optional[bool] = ..., 
                allow_virtual_network_access: Optional[bool] = ..., 
                databricks_address_space: Optional[AddressSpace] = ..., 
                databricks_virtual_network: Optional[VirtualNetworkPeeringPropertiesFormatDatabricksVirtualNetwork] = ..., 
                remote_address_space: Optional[AddressSpace] = ..., 
                remote_virtual_network: VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork, 
                use_remote_gateways: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.VirtualNetworkPeeringPropertiesFormatDatabricksVirtualNetwork(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.Workspace(TrackedResource):
        id: str
        location: str
        name: str
        properties: WorkspaceProperties
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: WorkspaceProperties, 
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


    class azure.mgmt.databricks.models.WorkspaceCustomBooleanParameter(_Model):
        type: Optional[Union[str, CustomParameterType]]
        value: bool

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomParameterType]] = ..., 
                value: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceCustomObjectParameter(_Model):
        type: Optional[Union[str, CustomParameterType]]
        value: Any

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomParameterType]] = ..., 
                value: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceCustomParameters(_Model):
        aml_workspace_id: Optional[WorkspaceCustomStringParameter]
        custom_private_subnet_name: Optional[WorkspaceCustomStringParameter]
        custom_public_subnet_name: Optional[WorkspaceCustomStringParameter]
        custom_virtual_network_id: Optional[WorkspaceCustomStringParameter]
        enable_no_public_ip: Optional[WorkspaceNoPublicIPBooleanParameter]
        encryption: Optional[WorkspaceEncryptionParameter]
        load_balancer_backend_pool_name: Optional[WorkspaceCustomStringParameter]
        load_balancer_id: Optional[WorkspaceCustomStringParameter]
        nat_gateway_name: Optional[WorkspaceCustomStringParameter]
        prepare_encryption: Optional[WorkspaceCustomBooleanParameter]
        public_ip_name: Optional[WorkspaceCustomStringParameter]
        require_infrastructure_encryption: Optional[WorkspaceCustomBooleanParameter]
        resource_tags: Optional[WorkspaceCustomObjectParameter]
        storage_account_name: Optional[WorkspaceCustomStringParameter]
        storage_account_sku_name: Optional[WorkspaceCustomStringParameter]
        vnet_address_prefix: Optional[WorkspaceCustomStringParameter]

        @overload
        def __init__(
                self, 
                *, 
                aml_workspace_id: Optional[WorkspaceCustomStringParameter] = ..., 
                custom_private_subnet_name: Optional[WorkspaceCustomStringParameter] = ..., 
                custom_public_subnet_name: Optional[WorkspaceCustomStringParameter] = ..., 
                custom_virtual_network_id: Optional[WorkspaceCustomStringParameter] = ..., 
                enable_no_public_ip: Optional[WorkspaceNoPublicIPBooleanParameter] = ..., 
                encryption: Optional[WorkspaceEncryptionParameter] = ..., 
                load_balancer_backend_pool_name: Optional[WorkspaceCustomStringParameter] = ..., 
                load_balancer_id: Optional[WorkspaceCustomStringParameter] = ..., 
                nat_gateway_name: Optional[WorkspaceCustomStringParameter] = ..., 
                prepare_encryption: Optional[WorkspaceCustomBooleanParameter] = ..., 
                public_ip_name: Optional[WorkspaceCustomStringParameter] = ..., 
                require_infrastructure_encryption: Optional[WorkspaceCustomBooleanParameter] = ..., 
                storage_account_name: Optional[WorkspaceCustomStringParameter] = ..., 
                storage_account_sku_name: Optional[WorkspaceCustomStringParameter] = ..., 
                vnet_address_prefix: Optional[WorkspaceCustomStringParameter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceCustomStringParameter(_Model):
        type: Optional[Union[str, CustomParameterType]]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomParameterType]] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceEncryptionParameter(_Model):
        type: Optional[Union[str, CustomParameterType]]
        value: Optional[Encryption]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomParameterType]] = ..., 
                value: Optional[Encryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceNoPublicIPBooleanParameter(_Model):
        type: Optional[Union[str, CustomParameterType]]
        value: bool

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomParameterType]] = ..., 
                value: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceProperties(_Model):
        access_connector: Optional[WorkspacePropertiesAccessConnector]
        authorizations: Optional[list[WorkspaceProviderAuthorization]]
        compute_mode: Union[str, ComputeMode]
        created_by: Optional[CreatedBy]
        created_date_time: Optional[datetime]
        default_catalog: Optional[DefaultCatalogProperties]
        default_storage_firewall: Optional[Union[str, DefaultStorageFirewall]]
        disk_encryption_set_id: Optional[str]
        encryption: Optional[WorkspacePropertiesEncryption]
        enhanced_security_compliance: Optional[EnhancedSecurityComplianceDefinition]
        is_uc_enabled: Optional[bool]
        managed_disk_identity: Optional[ManagedIdentityConfiguration]
        managed_resource_group_id: Optional[str]
        parameters: Optional[WorkspaceCustomParameters]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        required_nsg_rules: Optional[Union[str, RequiredNsgRules]]
        storage_account_identity: Optional[ManagedIdentityConfiguration]
        ui_definition_uri: Optional[str]
        updated_by: Optional[CreatedBy]
        workspace_id: Optional[str]
        workspace_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_connector: Optional[WorkspacePropertiesAccessConnector] = ..., 
                authorizations: Optional[list[WorkspaceProviderAuthorization]] = ..., 
                compute_mode: Union[str, ComputeMode], 
                created_by: Optional[CreatedBy] = ..., 
                default_catalog: Optional[DefaultCatalogProperties] = ..., 
                default_storage_firewall: Optional[Union[str, DefaultStorageFirewall]] = ..., 
                encryption: Optional[WorkspacePropertiesEncryption] = ..., 
                enhanced_security_compliance: Optional[EnhancedSecurityComplianceDefinition] = ..., 
                managed_disk_identity: Optional[ManagedIdentityConfiguration] = ..., 
                managed_resource_group_id: Optional[str] = ..., 
                parameters: Optional[WorkspaceCustomParameters] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                required_nsg_rules: Optional[Union[str, RequiredNsgRules]] = ..., 
                storage_account_identity: Optional[ManagedIdentityConfiguration] = ..., 
                ui_definition_uri: Optional[str] = ..., 
                updated_by: Optional[CreatedBy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspacePropertiesAccessConnector(_Model):
        id: str
        identity_type: Union[str, IdentityType]
        user_assigned_identity_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                identity_type: Union[str, IdentityType], 
                user_assigned_identity_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspacePropertiesEncryption(_Model):
        entities: EncryptionEntitiesDefinition

        @overload
        def __init__(
                self, 
                *, 
                entities: EncryptionEntitiesDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceProviderAuthorization(_Model):
        principal_id: str
        role_definition_id: str

        @overload
        def __init__(
                self, 
                *, 
                principal_id: str, 
                role_definition_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databricks.models.WorkspaceUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.databricks.operations

    class azure.mgmt.databricks.operations.AccessConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessConnector]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessConnector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: AccessConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessConnector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessConnector]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AccessConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessConnector]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AccessConnector]: ...


    class azure.mgmt.databricks.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.databricks.operations.OutboundNetworkDependenciesEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> List[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.databricks.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.databricks.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> GroupIdInformation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GroupIdInformation]: ...


    class azure.mgmt.databricks.operations.VNetPeeringOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                virtual_network_peering_parameters: VirtualNetworkPeering, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkPeering]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                virtual_network_peering_parameters: VirtualNetworkPeering, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkPeering]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                virtual_network_peering_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkPeering]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> Optional[VirtualNetworkPeering]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetworkPeering]: ...


    class azure.mgmt.databricks.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                force_deletion: bool = False, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Workspace]: ...


namespace azure.mgmt.databricks.types

    class azure.mgmt.databricks.types.AccessConnector(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AccessConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AccessConnectorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.databricks.types.AccessConnectorProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioning_state: Union[str, ProvisioningState]
        referedBy: list[str]
        refered_by: list[str]


    class azure.mgmt.databricks.types.AccessConnectorUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.databricks.types.AddressSpace(TypedDict, total=False):
        addressPrefixes: list[str]
        address_prefixes: list[str]


    class azure.mgmt.databricks.types.AutomaticClusterUpdateDefinition(TypedDict, total=False):
        key "value": Union[str, AutomaticClusterUpdateValue]
        value: Union[str, AutomaticClusterUpdateValue]


    class azure.mgmt.databricks.types.ComplianceSecurityProfileDefinition(TypedDict, total=False):
        key "value": Union[str, ComplianceSecurityProfileValue]
        complianceStandards: list[str]
        compliance_standards: list[str]
        value: Union[str, ComplianceSecurityProfileValue]


    class azure.mgmt.databricks.types.CreatedBy(TypedDict, total=False):
        key "applicationId": str
        key "oid": str
        key "puid": str
        application_id: str
        oid: str
        puid: str


    class azure.mgmt.databricks.types.DefaultCatalogProperties(TypedDict, total=False):
        key "initialName": str
        key "initialType": Union[str, InitialType]
        initial_name: str
        initial_type: Union[str, InitialType]


    class azure.mgmt.databricks.types.Encryption(TypedDict, total=False):
        key "KeyName": str
        key "keySource": Union[str, KeySource]
        key "keyvaulturi": str
        key "keyversion": str
        key_name: str
        key_source: Union[str, KeySource]
        key_vault_uri: str
        key_version: str


    class azure.mgmt.databricks.types.EncryptionEntitiesDefinition(TypedDict, total=False):
        key "managedDisk": ForwardRef('ManagedDiskEncryption', module='types')
        key "managedServices": ForwardRef('EncryptionV2', module='types')
        managed_disk: ManagedDiskEncryption
        managed_services: EncryptionV2


    class azure.mgmt.databricks.types.EncryptionV2(TypedDict, total=False):
        key "keySource": Required[Union[str, EncryptionKeySource]]
        key "keyVaultProperties": ForwardRef('EncryptionV2KeyVaultProperties', module='types')
        key_source: Union[str, EncryptionKeySource]
        key_vault_properties: EncryptionV2KeyVaultProperties


    class azure.mgmt.databricks.types.EncryptionV2KeyVaultProperties(TypedDict, total=False):
        key "keyName": Required[str]
        key "keyVaultUri": Required[str]
        key "keyVersion": Required[str]
        key_name: str
        key_vault_uri: str
        key_version: str


    class azure.mgmt.databricks.types.EnhancedSecurityComplianceDefinition(TypedDict, total=False):
        key "automaticClusterUpdate": ForwardRef('AutomaticClusterUpdateDefinition', module='types')
        key "complianceSecurityProfile": ForwardRef('ComplianceSecurityProfileDefinition', module='types')
        key "enhancedSecurityMonitoring": ForwardRef('EnhancedSecurityMonitoringDefinition', module='types')
        automatic_cluster_update: AutomaticClusterUpdateDefinition
        compliance_security_profile: ComplianceSecurityProfileDefinition
        enhanced_security_monitoring: EnhancedSecurityMonitoringDefinition


    class azure.mgmt.databricks.types.EnhancedSecurityMonitoringDefinition(TypedDict, total=False):
        key "value": Union[str, EnhancedSecurityMonitoringValue]
        value: Union[str, EnhancedSecurityMonitoringValue]


    class azure.mgmt.databricks.types.ManagedDiskEncryption(TypedDict, total=False):
        key "keySource": Required[Union[str, EncryptionKeySource]]
        key "keyVaultProperties": Required[ManagedDiskEncryptionKeyVaultProperties]
        key "rotationToLatestKeyVersionEnabled": bool
        key_source: Union[str, EncryptionKeySource]
        key_vault_properties: ManagedDiskEncryptionKeyVaultProperties
        rotation_to_latest_key_version_enabled: bool


    class azure.mgmt.databricks.types.ManagedDiskEncryptionKeyVaultProperties(TypedDict, total=False):
        key "keyName": Required[str]
        key "keyVaultUri": Required[str]
        key "keyVersion": Required[str]
        key_name: str
        key_vault_uri: str
        key_version: str


    class azure.mgmt.databricks.types.ManagedIdentityConfiguration(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": str
        principal_id: str
        tenant_id: str
        type: str


    class azure.mgmt.databricks.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.databricks.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.databricks.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[PrivateEndpointConnectionProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.databricks.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.databricks.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Required[Union[str, PrivateLinkServiceConnectionStatus]]
        actions_required: str
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]


    class azure.mgmt.databricks.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databricks.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databricks.types.Sku(TypedDict, total=False):
        key "name": Required[str]
        key "tier": str
        name: str
        tier: str


    class azure.mgmt.databricks.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.databricks.types.TrackedResource(Resource):
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


    class azure.mgmt.databricks.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.databricks.types.VirtualNetworkPeering(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[VirtualNetworkPeeringPropertiesFormat]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: VirtualNetworkPeeringPropertiesFormat
        system_data: SystemData
        type: str


    class azure.mgmt.databricks.types.VirtualNetworkPeeringPropertiesFormat(TypedDict, total=False):
        key "allowForwardedTraffic": bool
        key "allowGatewayTransit": bool
        key "allowVirtualNetworkAccess": bool
        key "databricksAddressSpace": ForwardRef('AddressSpace', module='types')
        key "databricksVirtualNetwork": ForwardRef('VirtualNetworkPeeringPropertiesFormatDatabricksVirtualNetwork', module='types')
        key "peeringState": Union[str, PeeringState]
        key "provisioningState": Union[str, PeeringProvisioningState]
        key "remoteAddressSpace": ForwardRef('AddressSpace', module='types')
        key "remoteVirtualNetwork": Required[VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork]
        key "useRemoteGateways": bool
        allow_forwarded_traffic: bool
        allow_gateway_transit: bool
        allow_virtual_network_access: bool
        databricks_address_space: AddressSpace
        databricks_virtual_network: VirtualNetworkPeeringPropertiesFormatDatabricksVirtualNetwork
        peering_state: Union[str, PeeringState]
        provisioning_state: Union[str, PeeringProvisioningState]
        remote_address_space: AddressSpace
        remote_virtual_network: VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork
        use_remote_gateways: bool


    class azure.mgmt.databricks.types.VirtualNetworkPeeringPropertiesFormatDatabricksVirtualNetwork(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.databricks.types.VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.databricks.types.Workspace(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[WorkspaceProperties]
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: WorkspaceProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.databricks.types.WorkspaceCustomBooleanParameter(TypedDict, total=False):
        key "type": Union[str, CustomParameterType]
        key "value": Required[bool]
        type: Union[str, CustomParameterType]
        value: bool


    class azure.mgmt.databricks.types.WorkspaceCustomObjectParameter(TypedDict, total=False):
        key "type": Union[str, CustomParameterType]
        key "value": Required[Any]
        type: Union[str, CustomParameterType]
        value: Any


    class azure.mgmt.databricks.types.WorkspaceCustomParameters(TypedDict, total=False):
        key "amlWorkspaceId": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "customPrivateSubnetName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "customPublicSubnetName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "customVirtualNetworkId": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "enableNoPublicIp": ForwardRef('WorkspaceNoPublicIPBooleanParameter', module='types')
        key "encryption": ForwardRef('WorkspaceEncryptionParameter', module='types')
        key "loadBalancerBackendPoolName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "loadBalancerId": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "natGatewayName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "prepareEncryption": ForwardRef('WorkspaceCustomBooleanParameter', module='types')
        key "publicIpName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "requireInfrastructureEncryption": ForwardRef('WorkspaceCustomBooleanParameter', module='types')
        key "resourceTags": ForwardRef('WorkspaceCustomObjectParameter', module='types')
        key "storageAccountName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "storageAccountSkuName": ForwardRef('WorkspaceCustomStringParameter', module='types')
        key "vnetAddressPrefix": ForwardRef('WorkspaceCustomStringParameter', module='types')
        aml_workspace_id: WorkspaceCustomStringParameter
        custom_private_subnet_name: WorkspaceCustomStringParameter
        custom_public_subnet_name: WorkspaceCustomStringParameter
        custom_virtual_network_id: WorkspaceCustomStringParameter
        enable_no_public_ip: WorkspaceNoPublicIPBooleanParameter
        encryption: WorkspaceEncryptionParameter
        load_balancer_backend_pool_name: WorkspaceCustomStringParameter
        load_balancer_id: WorkspaceCustomStringParameter
        nat_gateway_name: WorkspaceCustomStringParameter
        prepare_encryption: WorkspaceCustomBooleanParameter
        public_ip_name: WorkspaceCustomStringParameter
        require_infrastructure_encryption: WorkspaceCustomBooleanParameter
        resource_tags: WorkspaceCustomObjectParameter
        storage_account_name: WorkspaceCustomStringParameter
        storage_account_sku_name: WorkspaceCustomStringParameter
        vnet_address_prefix: WorkspaceCustomStringParameter


    class azure.mgmt.databricks.types.WorkspaceCustomStringParameter(TypedDict, total=False):
        key "type": Union[str, CustomParameterType]
        key "value": Required[str]
        type: Union[str, CustomParameterType]
        value: str


    class azure.mgmt.databricks.types.WorkspaceEncryptionParameter(TypedDict, total=False):
        key "type": Union[str, CustomParameterType]
        key "value": ForwardRef('Encryption', module='types')
        type: Union[str, CustomParameterType]
        value: Encryption


    class azure.mgmt.databricks.types.WorkspaceNoPublicIPBooleanParameter(TypedDict, total=False):
        key "type": Union[str, CustomParameterType]
        key "value": Required[bool]
        type: Union[str, CustomParameterType]
        value: bool


    class azure.mgmt.databricks.types.WorkspaceProperties(TypedDict, total=False):
        key "accessConnector": ForwardRef('WorkspacePropertiesAccessConnector', module='types')
        key "computeMode": Required[Union[str, ComputeMode]]
        key "createdBy": ForwardRef('CreatedBy', module='types')
        key "createdDateTime": str
        key "defaultCatalog": ForwardRef('DefaultCatalogProperties', module='types')
        key "defaultStorageFirewall": Union[str, DefaultStorageFirewall]
        key "diskEncryptionSetId": str
        key "encryption": ForwardRef('WorkspacePropertiesEncryption', module='types')
        key "enhancedSecurityCompliance": ForwardRef('EnhancedSecurityComplianceDefinition', module='types')
        key "isUcEnabled": bool
        key "managedDiskIdentity": ForwardRef('ManagedIdentityConfiguration', module='types')
        key "managedResourceGroupId": str
        key "parameters": ForwardRef('WorkspaceCustomParameters', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "requiredNsgRules": Union[str, RequiredNsgRules]
        key "storageAccountIdentity": ForwardRef('ManagedIdentityConfiguration', module='types')
        key "uiDefinitionUri": str
        key "updatedBy": ForwardRef('CreatedBy', module='types')
        key "workspaceId": str
        key "workspaceUrl": str
        access_connector: WorkspacePropertiesAccessConnector
        authorizations: list[WorkspaceProviderAuthorization]
        compute_mode: Union[str, ComputeMode]
        created_by: CreatedBy
        created_date_time: str
        default_catalog: DefaultCatalogProperties
        default_storage_firewall: Union[str, DefaultStorageFirewall]
        disk_encryption_set_id: str
        encryption: WorkspacePropertiesEncryption
        enhanced_security_compliance: EnhancedSecurityComplianceDefinition
        is_uc_enabled: bool
        managed_disk_identity: ManagedIdentityConfiguration
        managed_resource_group_id: str
        parameters: WorkspaceCustomParameters
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        required_nsg_rules: Union[str, RequiredNsgRules]
        storage_account_identity: ManagedIdentityConfiguration
        ui_definition_uri: str
        updated_by: CreatedBy
        workspace_id: str
        workspace_url: str


    class azure.mgmt.databricks.types.WorkspacePropertiesAccessConnector(TypedDict, total=False):
        key "id": Required[str]
        key "identityType": Required[Union[str, IdentityType]]
        key "userAssignedIdentityId": str
        id: str
        identity_type: Union[str, IdentityType]
        user_assigned_identity_id: str


    class azure.mgmt.databricks.types.WorkspacePropertiesEncryption(TypedDict, total=False):
        key "entities": Required[EncryptionEntitiesDefinition]
        entities: EncryptionEntitiesDefinition


    class azure.mgmt.databricks.types.WorkspaceProviderAuthorization(TypedDict, total=False):
        key "principalId": Required[str]
        key "roleDefinitionId": Required[str]
        principal_id: str
        role_definition_id: str


    class azure.mgmt.databricks.types.WorkspaceUpdate(TypedDict, total=False):
        tags: dict[str, str]


```