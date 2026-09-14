```py
namespace azure.mgmt.hybridkubernetes

    class azure.mgmt.hybridkubernetes.ConnectedKubernetesClient: implements ContextManager 
        connected_cluster: ConnectedClusterOperations
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


namespace azure.mgmt.hybridkubernetes.aio

    class azure.mgmt.hybridkubernetes.aio.ConnectedKubernetesClient: implements AsyncContextManager 
        connected_cluster: ConnectedClusterOperations
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


namespace azure.mgmt.hybridkubernetes.aio.operations

    class azure.mgmt.hybridkubernetes.aio.operations.ConnectedClusterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster: ConnectedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedCluster]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster: ConnectedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedCluster]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster_patch: ConnectedClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedCluster]: ...

        @overload
        async def begin_update_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster_patch: ConnectedClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedCluster]: ...

        @overload
        async def begin_update_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ConnectedCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectedCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ConnectedCluster]: ...

        @overload
        async def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ListClusterUserCredentialProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        async def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ListClusterUserCredentialProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        async def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CredentialResults: ...


    class azure.mgmt.hybridkubernetes.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.hybridkubernetes.models

    class azure.mgmt.hybridkubernetes.models.AadProfile(_Model):
        admin_group_object_i_ds: Optional[list[str]]
        enable_azure_rbac: Optional[bool]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_group_object_i_ds: Optional[list[str]] = ..., 
                enable_azure_rbac: Optional[bool] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.hybridkubernetes.models.AgentError(_Model):
        component: Optional[str]
        message: Optional[str]
        severity: Optional[str]
        time: Optional[datetime]


    class azure.mgmt.hybridkubernetes.models.ArcAgentProfile(_Model):
        agent_auto_upgrade: Optional[Union[str, AutoUpgradeOptions]]
        agent_errors: Optional[list[AgentError]]
        agent_state: Optional[str]
        desired_agent_version: Optional[str]
        system_components: Optional[list[SystemComponent]]

        @overload
        def __init__(
                self, 
                *, 
                agent_auto_upgrade: Optional[Union[str, AutoUpgradeOptions]] = ..., 
                agent_errors: Optional[list[AgentError]] = ..., 
                desired_agent_version: Optional[str] = ..., 
                system_components: Optional[list[SystemComponent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ArcAgentryConfigurations(_Model):
        feature: Optional[str]
        protected_settings: Optional[dict[str, str]]
        settings: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                feature: Optional[str] = ..., 
                protected_settings: Optional[dict[str, str]] = ..., 
                settings: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.AuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        TOKEN = "Token"


    class azure.mgmt.hybridkubernetes.models.AutoUpgradeOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.hybridkubernetes.models.AzureHybridBenefit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        NOT_APPLICABLE = "NotApplicable"
        TRUE = "True"


    class azure.mgmt.hybridkubernetes.models.ConnectedCluster(TrackedResource):
        id: str
        identity: ConnectedClusterIdentity
        kind: Optional[Union[str, ConnectedClusterKind]]
        location: str
        name: str
        properties: ConnectedClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: ConnectedClusterIdentity, 
                kind: Optional[Union[str, ConnectedClusterKind]] = ..., 
                location: str, 
                properties: ConnectedClusterProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ConnectedClusterIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ResourceIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ResourceIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ConnectedClusterKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVISIONED_CLUSTER = "ProvisionedCluster"


    class azure.mgmt.hybridkubernetes.models.ConnectedClusterPatch(_Model):
        properties: Optional[ConnectedClusterPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectedClusterPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ConnectedClusterPatchProperties(_Model):
        azure_hybrid_benefit: Optional[Union[str, AzureHybridBenefit]]
        distribution: Optional[str]
        distribution_version: Optional[str]
        gateway: Optional[Gateway]

        @overload
        def __init__(
                self, 
                *, 
                azure_hybrid_benefit: Optional[Union[str, AzureHybridBenefit]] = ..., 
                distribution: Optional[str] = ..., 
                distribution_version: Optional[str] = ..., 
                gateway: Optional[Gateway] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ConnectedClusterProperties(_Model):
        aad_profile: Optional[AadProfile]
        agent_public_key_certificate: str
        agent_version: Optional[str]
        arc_agent_profile: Optional[ArcAgentProfile]
        arc_agentry_configurations: Optional[list[ArcAgentryConfigurations]]
        azure_hybrid_benefit: Optional[Union[str, AzureHybridBenefit]]
        connectivity_status: Optional[Union[str, ConnectivityStatus]]
        distribution: Optional[str]
        distribution_version: Optional[str]
        gateway: Optional[Gateway]
        infrastructure: Optional[str]
        kubernetes_version: Optional[str]
        last_connectivity_time: Optional[datetime]
        managed_identity_certificate_expiration_time: Optional[datetime]
        miscellaneous_properties: Optional[dict[str, str]]
        offering: Optional[str]
        oidc_issuer_profile: Optional[OidcIssuerProfile]
        private_link_scope_resource_id: Optional[str]
        private_link_state: Optional[Union[str, PrivateLinkState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        security_profile: Optional[SecurityProfile]
        total_core_count: Optional[int]
        total_node_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                aad_profile: Optional[AadProfile] = ..., 
                agent_public_key_certificate: str, 
                arc_agent_profile: Optional[ArcAgentProfile] = ..., 
                arc_agentry_configurations: Optional[list[ArcAgentryConfigurations]] = ..., 
                azure_hybrid_benefit: Optional[Union[str, AzureHybridBenefit]] = ..., 
                distribution: Optional[str] = ..., 
                distribution_version: Optional[str] = ..., 
                gateway: Optional[Gateway] = ..., 
                infrastructure: Optional[str] = ..., 
                oidc_issuer_profile: Optional[OidcIssuerProfile] = ..., 
                private_link_scope_resource_id: Optional[str] = ..., 
                private_link_state: Optional[Union[str, PrivateLinkState]] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                security_profile: Optional[SecurityProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.ConnectivityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_NOT_INSTALLED = "AgentNotInstalled"
        CONNECTED = "Connected"
        CONNECTING = "Connecting"
        EXPIRED = "Expired"
        OFFLINE = "Offline"


    class azure.mgmt.hybridkubernetes.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.hybridkubernetes.models.CredentialResult(_Model):
        name: Optional[str]
        value: Optional[bytes]


    class azure.mgmt.hybridkubernetes.models.CredentialResults(_Model):
        hybrid_connection_config: Optional[HybridConnectionConfig]
        kubeconfigs: Optional[list[CredentialResult]]


    class azure.mgmt.hybridkubernetes.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.hybridkubernetes.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.hybridkubernetes.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.Gateway(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.HybridConnectionConfig(_Model):
        expiration_time: Optional[int]
        hybrid_connection_name: Optional[str]
        relay: Optional[str]
        relay_tid: Optional[str]
        relay_type: Optional[str]
        token: Optional[str]


    class azure.mgmt.hybridkubernetes.models.ListClusterUserCredentialProperties(_Model):
        authentication_method: Union[str, AuthenticationMethod]
        client_proxy: bool

        @overload
        def __init__(
                self, 
                *, 
                authentication_method: Union[str, AuthenticationMethod], 
                client_proxy: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.OidcIssuerProfile(_Model):
        enabled: Optional[bool]
        issuer_url: Optional[str]
        self_hosted_issuer_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                self_hosted_issuer_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.Operation(_Model):
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


    class azure.mgmt.hybridkubernetes.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.hybridkubernetes.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.hybridkubernetes.models.PrivateLinkState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.hybridkubernetes.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.hybridkubernetes.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.hybridkubernetes.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.hybridkubernetes.models.SecurityProfile(_Model):
        workload_identity: Optional[SecurityProfileWorkloadIdentity]

        @overload
        def __init__(
                self, 
                *, 
                workload_identity: Optional[SecurityProfileWorkloadIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.SecurityProfileWorkloadIdentity(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.SystemComponent(_Model):
        current_version: Optional[str]
        major_version: Optional[int]
        type: Optional[str]
        user_specified_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                major_version: Optional[int] = ..., 
                type: Optional[str] = ..., 
                user_specified_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridkubernetes.models.SystemData(_Model):
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


    class azure.mgmt.hybridkubernetes.models.TrackedResource(Resource):
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


namespace azure.mgmt.hybridkubernetes.operations

    class azure.mgmt.hybridkubernetes.operations.ConnectedClusterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster: ConnectedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedCluster]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster: ConnectedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedCluster]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster_patch: ConnectedClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedCluster]: ...

        @overload
        def begin_update_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster_patch: ConnectedClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedCluster]: ...

        @overload
        def begin_update_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                connected_cluster_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ConnectedCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConnectedCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ConnectedCluster]: ...

        @overload
        def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ListClusterUserCredentialProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ListClusterUserCredentialProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CredentialResults: ...


    class azure.mgmt.hybridkubernetes.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.hybridkubernetes.types

    class azure.mgmt.hybridkubernetes.types.AadProfile(TypedDict, total=False):
        key "enableAzureRBAC": bool
        key "tenantID": str
        adminGroupObjectIDs: list[str]
        admin_group_object_i_ds: list[str]
        enable_azure_rbac: bool
        tenant_id: str


    class azure.mgmt.hybridkubernetes.types.AgentError(TypedDict, total=False):
        key "component": str
        key "message": str
        key "severity": str
        key "time": str
        component: str
        message: str
        severity: str
        time: str


    class azure.mgmt.hybridkubernetes.types.ArcAgentProfile(TypedDict, total=False):
        key "agentAutoUpgrade": Union[str, AutoUpgradeOptions]
        key "agentState": str
        key "desiredAgentVersion": str
        agentErrors: list[AgentError]
        agent_auto_upgrade: Union[str, AutoUpgradeOptions]
        agent_errors: list[AgentError]
        agent_state: str
        desired_agent_version: str
        systemComponents: list[SystemComponent]
        system_components: list[SystemComponent]


    class azure.mgmt.hybridkubernetes.types.ArcAgentryConfigurations(TypedDict, total=False):
        key "feature": str
        key "protectedSettings": Optional[dict[str, str]]
        key "settings": Optional[dict[str, str]]
        feature: str
        protected_settings: dict[str, str]
        settings: dict[str, str]


    class azure.mgmt.hybridkubernetes.types.ConnectedCluster(TrackedResource):
        key "id": str
        key "identity": Required[ConnectedClusterIdentity]
        key "kind": Union[str, ConnectedClusterKind]
        key "location": Required[str]
        key "name": str
        key "properties": Required[ConnectedClusterProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ConnectedClusterIdentity
        kind: Union[str, ConnectedClusterKind]
        location: str
        name: str
        properties: ConnectedClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.hybridkubernetes.types.ConnectedClusterIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ResourceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]


    class azure.mgmt.hybridkubernetes.types.ConnectedClusterPatch(TypedDict, total=False):
        key "properties": ForwardRef('ConnectedClusterPatchProperties', module='types')
        properties: ConnectedClusterPatchProperties
        tags: dict[str, str]


    class azure.mgmt.hybridkubernetes.types.ConnectedClusterPatchProperties(TypedDict, total=False):
        key "azureHybridBenefit": Union[str, AzureHybridBenefit]
        key "distribution": str
        key "distributionVersion": str
        key "gateway": ForwardRef('Gateway', module='types')
        azure_hybrid_benefit: Union[str, AzureHybridBenefit]
        distribution: str
        distribution_version: str
        gateway: Gateway


    class azure.mgmt.hybridkubernetes.types.ConnectedClusterProperties(TypedDict, total=False):
        key "aadProfile": ForwardRef('AadProfile', module='types')
        key "agentPublicKeyCertificate": Required[str]
        key "agentVersion": str
        key "arcAgentProfile": ForwardRef('ArcAgentProfile', module='types')
        key "arcAgentryConfigurations": Optional[list[ArcAgentryConfigurations]]
        key "azureHybridBenefit": Union[str, AzureHybridBenefit]
        key "connectivityStatus": Union[str, ConnectivityStatus]
        key "distribution": str
        key "distributionVersion": str
        key "gateway": Optional[Gateway]
        key "infrastructure": str
        key "kubernetesVersion": str
        key "lastConnectivityTime": str
        key "managedIdentityCertificateExpirationTime": str
        key "offering": str
        key "oidcIssuerProfile": ForwardRef('OidcIssuerProfile', module='types')
        key "privateLinkScopeResourceId": str
        key "privateLinkState": Union[str, PrivateLinkState]
        key "provisioningState": Union[str, ProvisioningState]
        key "securityProfile": ForwardRef('SecurityProfile', module='types')
        key "totalCoreCount": int
        key "totalNodeCount": int
        aad_profile: AadProfile
        agent_public_key_certificate: str
        agent_version: str
        arc_agent_profile: ArcAgentProfile
        arc_agentry_configurations: list[ArcAgentryConfigurations]
        azure_hybrid_benefit: Union[str, AzureHybridBenefit]
        connectivity_status: Union[str, ConnectivityStatus]
        distribution: str
        distribution_version: str
        gateway: Gateway
        infrastructure: str
        kubernetes_version: str
        last_connectivity_time: str
        managed_identity_certificate_expiration_time: str
        miscellaneousProperties: dict[str, str]
        miscellaneous_properties: dict[str, str]
        offering: str
        oidc_issuer_profile: OidcIssuerProfile
        private_link_scope_resource_id: str
        private_link_state: Union[str, PrivateLinkState]
        provisioning_state: Union[str, ProvisioningState]
        security_profile: SecurityProfile
        total_core_count: int
        total_node_count: int


    class azure.mgmt.hybridkubernetes.types.Gateway(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.hybridkubernetes.types.ListClusterUserCredentialProperties(TypedDict, total=False):
        key "authenticationMethod": Required[Union[str, AuthenticationMethod]]
        key "clientProxy": Required[bool]
        authentication_method: Union[str, AuthenticationMethod]
        client_proxy: bool


    class azure.mgmt.hybridkubernetes.types.OidcIssuerProfile(TypedDict, total=False):
        key "enabled": bool
        key "issuerUrl": str
        key "selfHostedIssuerUrl": str
        enabled: bool
        issuer_url: str
        self_hosted_issuer_url: str


    class azure.mgmt.hybridkubernetes.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.hybridkubernetes.types.SecurityProfile(TypedDict, total=False):
        key "workloadIdentity": ForwardRef('SecurityProfileWorkloadIdentity', module='types')
        workload_identity: SecurityProfileWorkloadIdentity


    class azure.mgmt.hybridkubernetes.types.SecurityProfileWorkloadIdentity(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.hybridkubernetes.types.SystemComponent(TypedDict, total=False):
        key "currentVersion": str
        key "majorVersion": int
        key "type": str
        key "userSpecifiedVersion": str
        current_version: str
        major_version: int
        type: str
        user_specified_version: str


    class azure.mgmt.hybridkubernetes.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.hybridkubernetes.types.TrackedResource(Resource):
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


```