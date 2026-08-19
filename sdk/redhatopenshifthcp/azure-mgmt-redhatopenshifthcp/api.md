```py
namespace azure.mgmt.redhatopenshifthcp

    class azure.mgmt.redhatopenshifthcp.RedHatOpenShiftClient: implements ContextManager 
        external_auths: ExternalAuthsOperations
        hcp_open_shift_clusters: HcpOpenShiftClustersOperations
        hcp_open_shift_versions: HcpOpenShiftVersionsOperations
        hcp_operator_identity_role_sets: HcpOperatorIdentityRoleSetsOperations
        node_pools: NodePoolsOperations
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


namespace azure.mgmt.redhatopenshifthcp.aio

    class azure.mgmt.redhatopenshifthcp.aio.RedHatOpenShiftClient: implements AsyncContextManager 
        external_auths: ExternalAuthsOperations
        hcp_open_shift_clusters: HcpOpenShiftClustersOperations
        hcp_open_shift_versions: HcpOpenShiftVersionsOperations
        hcp_operator_identity_role_sets: HcpOperatorIdentityRoleSetsOperations
        node_pools: NodePoolsOperations
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


namespace azure.mgmt.redhatopenshifthcp.aio.operations

    class azure.mgmt.redhatopenshifthcp.aio.operations.ExternalAuthsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                resource: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalAuth]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                resource: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalAuth]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalAuth]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                properties: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalAuth]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                properties: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalAuth]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalAuth]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                **kwargs: Any
            ) -> ExternalAuth: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExternalAuth]: ...


    class azure.mgmt.redhatopenshifthcp.aio.operations.HcpOpenShiftClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                resource: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                resource: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_request_admin_credential(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                body: HcpOpenShiftClusterAdminCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftClusterAdminCredential]: ...

        @overload
        async def begin_request_admin_credential(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                body: HcpOpenShiftClusterAdminCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftClusterAdminCredential]: ...

        @overload
        async def begin_request_admin_credential(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftClusterAdminCredential]: ...

        @distributed_trace_async
        async def begin_revoke_credentials(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                properties: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                properties: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HcpOpenShiftCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> HcpOpenShiftCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HcpOpenShiftCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[HcpOpenShiftCluster]: ...


    class azure.mgmt.redhatopenshifthcp.aio.operations.HcpOpenShiftVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                hcp_open_shift_version_name: str, 
                **kwargs: Any
            ) -> HcpOpenShiftVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HcpOpenShiftVersion]: ...


    class azure.mgmt.redhatopenshifthcp.aio.operations.HcpOperatorIdentityRoleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                hcp_operator_identity_role_set_name: str, 
                **kwargs: Any
            ) -> HcpOperatorIdentityRoleSet: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HcpOperatorIdentityRoleSet]: ...


    class azure.mgmt.redhatopenshifthcp.aio.operations.NodePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> NodePool: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodePool]: ...


    class azure.mgmt.redhatopenshifthcp.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.redhatopenshifthcp.models

    class azure.mgmt.redhatopenshifthcp.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.redhatopenshifthcp.models.ApiProfile(_Model):
        authorized_cid_rs: Optional[list[str]]
        url: str
        visibility: Optional[Union[str, Visibility]]

        @overload
        def __init__(
                self, 
                *, 
                authorized_cid_rs: Optional[list[str]] = ..., 
                visibility: Optional[Union[str, Visibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ClusterAutoscalingProfile(_Model):
        max_node_provision_time_seconds: Optional[int]
        max_nodes_total: Optional[int]
        max_pod_grace_period_seconds: Optional[int]
        pod_priority_threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_node_provision_time_seconds: Optional[int] = ..., 
                max_nodes_total: Optional[int] = ..., 
                max_pod_grace_period_seconds: Optional[int] = ..., 
                pod_priority_threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ClusterImageRegistryProfile(_Model):
        state: Optional[Union[str, ClusterImageRegistryState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, ClusterImageRegistryState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ClusterImageRegistryState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redhatopenshifthcp.models.Condition(_Model):
        last_transition_time: datetime
        message: str
        reason: str
        status: Union[str, StatusType]
        type: Union[str, ConditionType]


    class azure.mgmt.redhatopenshifthcp.models.ConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        PROGRESSING = "Progressing"


    class azure.mgmt.redhatopenshifthcp.models.ConsoleProfile(_Model):
        url: str


    class azure.mgmt.redhatopenshifthcp.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.redhatopenshifthcp.models.CryptoRestrictions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIPS = "FIPS"
        NONE = "None"


    class azure.mgmt.redhatopenshifthcp.models.CustomerManagedEncryptionProfile(_Model):
        encryption_type: Optional[Union[str, CustomerManagedEncryptionType]]
        kms: Optional[KmsEncryptionProfile]

        @overload
        def __init__(
                self, 
                *, 
                encryption_type: Optional[Union[str, CustomerManagedEncryptionType]] = ..., 
                kms: Optional[KmsEncryptionProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.CustomerManagedEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KMS = "KMS"


    class azure.mgmt.redhatopenshifthcp.models.DiskStorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"


    class azure.mgmt.redhatopenshifthcp.models.DnsProfile(_Model):
        base_domain: Optional[str]
        base_domain_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_domain_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.Effect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_EXECUTE = "NoExecute"
        NO_SCHEDULE = "NoSchedule"
        PREFER_NO_SCHEDULE = "PreferNoSchedule"


    class azure.mgmt.redhatopenshifthcp.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.redhatopenshifthcp.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.redhatopenshifthcp.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.EtcdDataEncryptionKeyManagementModeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"


    class azure.mgmt.redhatopenshifthcp.models.EtcdDataEncryptionProfile(_Model):
        customer_managed: Optional[CustomerManagedEncryptionProfile]
        key_management_mode: Union[str, EtcdDataEncryptionKeyManagementModeType]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed: Optional[CustomerManagedEncryptionProfile] = ..., 
                key_management_mode: Union[str, EtcdDataEncryptionKeyManagementModeType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.EtcdProfile(_Model):
        data_encryption: Optional[EtcdDataEncryptionProfile]

        @overload
        def __init__(
                self, 
                *, 
                data_encryption: Optional[EtcdDataEncryptionProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuth(ProxyResource):
        id: str
        name: str
        properties: Optional[ExternalAuthProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExternalAuthProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuthClaimProfile(_Model):
        mappings: TokenClaimMappingsProfile
        validation_rules: Optional[list[TokenClaimValidationRule]]

        @overload
        def __init__(
                self, 
                *, 
                mappings: TokenClaimMappingsProfile, 
                validation_rules: Optional[list[TokenClaimValidationRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuthClientComponentProfile(_Model):
        auth_client_namespace: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                auth_client_namespace: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuthClientProfile(_Model):
        client_id: str
        component: ExternalAuthClientComponentProfile
        extra_scopes: Optional[list[str]]
        type: Union[str, ExternalAuthClientType]

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                component: ExternalAuthClientComponentProfile, 
                extra_scopes: Optional[list[str]] = ..., 
                type: Union[str, ExternalAuthClientType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuthClientType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL = "Confidential"
        PUBLIC = "Public"


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuthProperties(_Model):
        claim: ExternalAuthClaimProfile
        clients: Optional[list[ExternalAuthClientProfile]]
        issuer: TokenIssuerProfile
        provisioning_state: Optional[Union[str, ExternalAuthProvisioningState]]
        status: Optional[ResourceStatus]

        @overload
        def __init__(
                self, 
                *, 
                claim: ExternalAuthClaimProfile, 
                clients: Optional[list[ExternalAuthClientProfile]] = ..., 
                issuer: TokenIssuerProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ExternalAuthProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        AWAITING_SECRET = "AwaitingSecret"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.redhatopenshifthcp.models.GroupClaimProfile(_Model):
        claim: str
        prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                claim: str, 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOpenShiftCluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[HcpOpenShiftClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[HcpOpenShiftClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOpenShiftClusterAdminCredential(_Model):
        expiration_timestamp: datetime
        kubeconfig: str


    class azure.mgmt.redhatopenshifthcp.models.HcpOpenShiftClusterAdminCredentialRequest(_Model):
        certificate_signing_request: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_signing_request: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOpenShiftClusterProperties(_Model):
        api: Optional[ApiProfile]
        autoscaling: Optional[ClusterAutoscalingProfile]
        cluster_image_registry: Optional[ClusterImageRegistryProfile]
        console: Optional[ConsoleProfile]
        crypto_restrictions: Optional[Union[str, CryptoRestrictions]]
        dns: Optional[DnsProfile]
        etcd: Optional[EtcdProfile]
        image_digest_mirrors: Optional[list[ImageDigestMirror]]
        ingress: Optional[IngressProfile]
        network: Optional[NetworkProfile]
        node_drain_timeout_minutes: Optional[int]
        platform: PlatformProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[ResourceStatus]
        version: VersionProfile

        @overload
        def __init__(
                self, 
                *, 
                api: Optional[ApiProfile] = ..., 
                autoscaling: Optional[ClusterAutoscalingProfile] = ..., 
                cluster_image_registry: Optional[ClusterImageRegistryProfile] = ..., 
                crypto_restrictions: Optional[Union[str, CryptoRestrictions]] = ..., 
                dns: Optional[DnsProfile] = ..., 
                etcd: Optional[EtcdProfile] = ..., 
                image_digest_mirrors: Optional[list[ImageDigestMirror]] = ..., 
                ingress: Optional[IngressProfile] = ..., 
                network: Optional[NetworkProfile] = ..., 
                node_drain_timeout_minutes: Optional[int] = ..., 
                platform: PlatformProfile, 
                version: VersionProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOpenShiftVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[HcpOpenShiftVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HcpOpenShiftVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOpenShiftVersionProperties(_Model):
        channel_group: str
        enabled: bool
        end_of_life_timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                channel_group: str, 
                enabled: bool, 
                end_of_life_timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOperatorIdentityRoleSet(ProxyResource):
        id: str
        name: str
        properties: Optional[HcpOperatorIdentityRoleSetProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HcpOperatorIdentityRoleSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.HcpOperatorIdentityRoleSetProperties(_Model):
        control_plane_operators: list[OperatorIdentityRoles]
        data_plane_operators: list[OperatorIdentityRoles]

        @overload
        def __init__(
                self, 
                *, 
                control_plane_operators: list[OperatorIdentityRoles], 
                data_plane_operators: list[OperatorIdentityRoles]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ImageDigestMirror(_Model):
        mirrors: list[str]
        source: str

        @overload
        def __init__(
                self, 
                *, 
                mirrors: list[str], 
                source: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.IngressProfile(_Model):
        type: Optional[Union[str, IngressType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IngressType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.IngressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.redhatopenshifthcp.models.KeyVaultVisibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.redhatopenshifthcp.models.KmsEncryptionProfile(_Model):
        active_key: KmsKey
        vault_name: str
        visibility: Union[str, KeyVaultVisibility]

        @overload
        def __init__(
                self, 
                *, 
                active_key: KmsKey, 
                vault_name: str, 
                visibility: Union[str, KeyVaultVisibility]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.KmsKey(_Model):
        name: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.Label(_Model):
        key: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.redhatopenshifthcp.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.redhatopenshifthcp.models.NetworkProfile(_Model):
        host_prefix: Optional[int]
        machine_cidr: Optional[str]
        network_type: Optional[Union[str, NetworkType]]
        pod_cidr: Optional[str]
        service_cidr: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                host_prefix: Optional[int] = ..., 
                machine_cidr: Optional[str] = ..., 
                network_type: Optional[Union[str, NetworkType]] = ..., 
                pod_cidr: Optional[str] = ..., 
                service_cidr: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.NetworkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "Other"
        OVN_KUBERNETES = "OVNKubernetes"


    class azure.mgmt.redhatopenshifthcp.models.NodePool(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[NodePoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[NodePoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.NodePoolAutoScaling(_Model):
        max: Optional[int]
        min: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max: Optional[int] = ..., 
                min: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.NodePoolPlatformProfile(_Model):
        availability_zone: Optional[str]
        enable_encryption_at_host: Optional[bool]
        os_disk: Optional[OsDiskProfile]
        subnet_id: Optional[str]
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                enable_encryption_at_host: Optional[bool] = ..., 
                os_disk: Optional[OsDiskProfile] = ..., 
                subnet_id: Optional[str] = ..., 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.NodePoolProperties(_Model):
        auto_repair: Optional[bool]
        auto_scaling: Optional[NodePoolAutoScaling]
        labels: Optional[list[Label]]
        node_drain_timeout_minutes: Optional[int]
        platform: NodePoolPlatformProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replicas: Optional[int]
        status: Optional[ResourceStatus]
        taints: Optional[list[Taint]]
        version: Optional[NodePoolVersionProfile]

        @overload
        def __init__(
                self, 
                *, 
                auto_repair: Optional[bool] = ..., 
                auto_scaling: Optional[NodePoolAutoScaling] = ..., 
                labels: Optional[list[Label]] = ..., 
                node_drain_timeout_minutes: Optional[int] = ..., 
                platform: NodePoolPlatformProfile, 
                replicas: Optional[int] = ..., 
                taints: Optional[list[Taint]] = ..., 
                version: Optional[NodePoolVersionProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.NodePoolVersionProfile(_Model):
        channel_group: Optional[str]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                channel_group: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.Operation(_Model):
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


    class azure.mgmt.redhatopenshifthcp.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.redhatopenshifthcp.models.OperatorIdentityRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        ON_ENABLEMENT = "OnEnablement"


    class azure.mgmt.redhatopenshifthcp.models.OperatorIdentityRoles(_Model):
        name: str
        required: Union[str, OperatorIdentityRequired]
        role_definitions: list[RoleDefinition]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                required: Union[str, OperatorIdentityRequired], 
                role_definitions: list[RoleDefinition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.OperatorsAuthenticationProfile(_Model):
        user_assigned_identities: UserAssignedIdentitiesProfile

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identities: UserAssignedIdentitiesProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.redhatopenshifthcp.models.OsDiskProfile(_Model):
        disk_storage_account_type: Optional[Union[str, DiskStorageAccountType]]
        disk_type: Optional[Union[str, OsDiskType]]
        encryption_set_id: Optional[str]
        size_gi_b: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_storage_account_type: Optional[Union[str, DiskStorageAccountType]] = ..., 
                disk_type: Optional[Union[str, OsDiskType]] = ..., 
                encryption_set_id: Optional[str] = ..., 
                size_gi_b: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.OsDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EPHEMERAL = "Ephemeral"
        MANAGED = "Managed"


    class azure.mgmt.redhatopenshifthcp.models.OutboundType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOAD_BALANCER = "LoadBalancer"


    class azure.mgmt.redhatopenshifthcp.models.PlatformProfile(_Model):
        issuer_url: str
        managed_resource_group: Optional[str]
        network_security_group_id: str
        operators_authentication: OperatorsAuthenticationProfile
        outbound_type: Optional[Union[str, OutboundType]]
        subnet_id: str
        vnet_integration_subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                managed_resource_group: Optional[str] = ..., 
                network_security_group_id: str, 
                operators_authentication: OperatorsAuthenticationProfile, 
                outbound_type: Optional[Union[str, OutboundType]] = ..., 
                subnet_id: str, 
                vnet_integration_subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.redhatopenshifthcp.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.redhatopenshifthcp.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.redhatopenshifthcp.models.ResourceStatus(_Model):
        conditions: Optional[list[Condition]]


    class azure.mgmt.redhatopenshifthcp.models.RoleDefinition(_Model):
        name: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.StatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"
        UNKNOWN = "Unknown"


    class azure.mgmt.redhatopenshifthcp.models.SystemData(_Model):
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


    class azure.mgmt.redhatopenshifthcp.models.Taint(_Model):
        effect: Union[str, Effect]
        key: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                effect: Union[str, Effect], 
                key: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.TokenClaimMappingsProfile(_Model):
        groups: Optional[GroupClaimProfile]
        username: UsernameClaimProfile

        @overload
        def __init__(
                self, 
                *, 
                groups: Optional[GroupClaimProfile] = ..., 
                username: UsernameClaimProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.TokenClaimValidationRule(_Model):
        required_claim: Optional[TokenRequiredClaim]
        type: Optional[Union[str, TokenValidationRuleType]]

        @overload
        def __init__(
                self, 
                *, 
                required_claim: Optional[TokenRequiredClaim] = ..., 
                type: Optional[Union[str, TokenValidationRuleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.TokenIssuerProfile(_Model):
        audiences: list[str]
        ca: Optional[str]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                audiences: list[str], 
                ca: Optional[str] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.TokenRequiredClaim(_Model):
        claim: str
        required_value: str

        @overload
        def __init__(
                self, 
                *, 
                claim: str, 
                required_value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.TokenValidationRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUIRED_CLAIM = "RequiredClaim"


    class azure.mgmt.redhatopenshifthcp.models.TrackedResource(Resource):
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


    class azure.mgmt.redhatopenshifthcp.models.UserAssignedIdentitiesProfile(_Model):
        control_plane_operators: dict[str, str]
        data_plane_operators: dict[str, str]
        service_managed_identity: str

        @overload
        def __init__(
                self, 
                *, 
                control_plane_operators: dict[str, str], 
                data_plane_operators: dict[str, str], 
                service_managed_identity: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.redhatopenshifthcp.models.UsernameClaimPrefixPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        NO_PREFIX = "NoPrefix"
        PREFIX = "Prefix"


    class azure.mgmt.redhatopenshifthcp.models.UsernameClaimProfile(_Model):
        claim: str
        prefix: Optional[str]
        prefix_policy: Optional[Union[str, UsernameClaimPrefixPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                claim: str, 
                prefix: Optional[str] = ..., 
                prefix_policy: Optional[Union[str, UsernameClaimPrefixPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.VersionProfile(_Model):
        channel_group: Optional[str]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                channel_group: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshifthcp.models.Visibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


namespace azure.mgmt.redhatopenshifthcp.operations

    class azure.mgmt.redhatopenshifthcp.operations.ExternalAuthsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                resource: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalAuth]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                resource: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalAuth]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalAuth]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                properties: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalAuth]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                properties: ExternalAuth, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalAuth]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalAuth]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                external_auth_name: str, 
                **kwargs: Any
            ) -> ExternalAuth: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExternalAuth]: ...


    class azure.mgmt.redhatopenshifthcp.operations.HcpOpenShiftClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                resource: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                resource: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_request_admin_credential(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                body: HcpOpenShiftClusterAdminCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftClusterAdminCredential]: ...

        @overload
        def begin_request_admin_credential(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                body: HcpOpenShiftClusterAdminCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftClusterAdminCredential]: ...

        @overload
        def begin_request_admin_credential(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftClusterAdminCredential]: ...

        @distributed_trace
        def begin_revoke_credentials(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                properties: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                properties: HcpOpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HcpOpenShiftCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> HcpOpenShiftCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HcpOpenShiftCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[HcpOpenShiftCluster]: ...


    class azure.mgmt.redhatopenshifthcp.operations.HcpOpenShiftVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                hcp_open_shift_version_name: str, 
                **kwargs: Any
            ) -> HcpOpenShiftVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[HcpOpenShiftVersion]: ...


    class azure.mgmt.redhatopenshifthcp.operations.HcpOperatorIdentityRoleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                hcp_operator_identity_role_set_name: str, 
                **kwargs: Any
            ) -> HcpOperatorIdentityRoleSet: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[HcpOperatorIdentityRoleSet]: ...


    class azure.mgmt.redhatopenshifthcp.operations.NodePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> NodePool: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                hcp_open_shift_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NodePool]: ...


    class azure.mgmt.redhatopenshifthcp.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.redhatopenshifthcp.types

    class azure.mgmt.redhatopenshifthcp.types.ApiProfile(TypedDict, total=False):
        key "url": Required[str]
        key "visibility": Union[str, Visibility]
        authorizedCidrs: list[str]
        url: str
        visibility: Union[str, Visibility]


    class azure.mgmt.redhatopenshifthcp.types.ClusterAutoscalingProfile(TypedDict, total=False):
        key "maxNodeProvisionTimeSeconds": int
        key "maxNodesTotal": int
        key "maxPodGracePeriodSeconds": int
        key "podPriorityThreshold": int
        maxNodeProvisionTimeSeconds: int
        maxNodesTotal: int
        maxPodGracePeriodSeconds: int
        podPriorityThreshold: int


    class azure.mgmt.redhatopenshifthcp.types.ClusterImageRegistryProfile(TypedDict, total=False):
        key "state": Union[str, ClusterImageRegistryState]
        state: Union[str, ClusterImageRegistryState]


    class azure.mgmt.redhatopenshifthcp.types.Condition(TypedDict, total=False):
        key "lastTransitionTime": Required[str]
        key "message": Required[str]
        key "reason": Required[str]
        key "status": Required[Union[str, StatusType]]
        key "type": Required[Union[str, ConditionType]]
        lastTransitionTime: str
        message: str
        reason: str
        status: Union[str, StatusType]
        type: Union[str, ConditionType]


    class azure.mgmt.redhatopenshifthcp.types.ConsoleProfile(TypedDict, total=False):
        key "url": Required[str]
        url: str


    class azure.mgmt.redhatopenshifthcp.types.CustomerManagedEncryptionProfile(TypedDict, total=False):
        key "encryptionType": Union[str, CustomerManagedEncryptionType]
        key "kms": ForwardRef('KmsEncryptionProfile', module='types')
        encryptionType: Union[str, CustomerManagedEncryptionType]
        kms: KmsEncryptionProfile


    class azure.mgmt.redhatopenshifthcp.types.DnsProfile(TypedDict, total=False):
        key "baseDomain": str
        key "baseDomainPrefix": str
        baseDomain: str
        baseDomainPrefix: str


    class azure.mgmt.redhatopenshifthcp.types.EtcdDataEncryptionProfile(TypedDict, total=False):
        key "customerManaged": ForwardRef('CustomerManagedEncryptionProfile', module='types')
        key "keyManagementMode": Required[Union[str, EtcdDataEncryptionKeyManagementModeType]]
        customerManaged: CustomerManagedEncryptionProfile
        keyManagementMode: Union[str, EtcdDataEncryptionKeyManagementModeType]


    class azure.mgmt.redhatopenshifthcp.types.EtcdProfile(TypedDict, total=False):
        key "dataEncryption": ForwardRef('EtcdDataEncryptionProfile', module='types')
        dataEncryption: EtcdDataEncryptionProfile


    class azure.mgmt.redhatopenshifthcp.types.ExternalAuth(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ExternalAuthProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ExternalAuthProperties
        systemData: SystemData
        type: str


    class azure.mgmt.redhatopenshifthcp.types.ExternalAuthClaimProfile(TypedDict, total=False):
        key "mappings": Required[TokenClaimMappingsProfile]
        mappings: TokenClaimMappingsProfile
        validationRules: list[TokenClaimValidationRule]


    class azure.mgmt.redhatopenshifthcp.types.ExternalAuthClientComponentProfile(TypedDict, total=False):
        key "authClientNamespace": Required[str]
        key "name": Required[str]
        authClientNamespace: str
        name: str


    class azure.mgmt.redhatopenshifthcp.types.ExternalAuthClientProfile(TypedDict, total=False):
        key "clientId": Required[str]
        key "component": Required[ExternalAuthClientComponentProfile]
        key "type": Required[Union[str, ExternalAuthClientType]]
        clientId: str
        component: ExternalAuthClientComponentProfile
        extraScopes: list[str]
        type: Union[str, ExternalAuthClientType]


    class azure.mgmt.redhatopenshifthcp.types.ExternalAuthProperties(TypedDict, total=False):
        key "claim": Required[ExternalAuthClaimProfile]
        key "issuer": Required[TokenIssuerProfile]
        key "provisioningState": Union[str, ExternalAuthProvisioningState]
        key "status": ForwardRef('ResourceStatus', module='types')
        claim: ExternalAuthClaimProfile
        clients: list[ExternalAuthClientProfile]
        issuer: TokenIssuerProfile
        provisioningState: Union[str, ExternalAuthProvisioningState]
        status: ResourceStatus


    class azure.mgmt.redhatopenshifthcp.types.GroupClaimProfile(TypedDict, total=False):
        key "claim": Required[str]
        key "prefix": str
        claim: str
        prefix: str


    class azure.mgmt.redhatopenshifthcp.types.HcpOpenShiftCluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('HcpOpenShiftClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: HcpOpenShiftClusterProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.redhatopenshifthcp.types.HcpOpenShiftClusterAdminCredentialRequest(TypedDict, total=False):
        key "certificateSigningRequest": str
        certificateSigningRequest: str


    class azure.mgmt.redhatopenshifthcp.types.HcpOpenShiftClusterProperties(TypedDict, total=False):
        key "api": ForwardRef('ApiProfile', module='types')
        key "autoscaling": ForwardRef('ClusterAutoscalingProfile', module='types')
        key "clusterImageRegistry": ForwardRef('ClusterImageRegistryProfile', module='types')
        key "console": ForwardRef('ConsoleProfile', module='types')
        key "cryptoRestrictions": Union[str, CryptoRestrictions]
        key "dns": ForwardRef('DnsProfile', module='types')
        key "etcd": ForwardRef('EtcdProfile', module='types')
        key "ingress": ForwardRef('IngressProfile', module='types')
        key "network": ForwardRef('NetworkProfile', module='types')
        key "nodeDrainTimeoutMinutes": int
        key "platform": Required[PlatformProfile]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('ResourceStatus', module='types')
        key "version": Required[VersionProfile]
        api: ApiProfile
        autoscaling: ClusterAutoscalingProfile
        clusterImageRegistry: ClusterImageRegistryProfile
        console: ConsoleProfile
        cryptoRestrictions: Union[str, CryptoRestrictions]
        dns: DnsProfile
        etcd: EtcdProfile
        imageDigestMirrors: list[ImageDigestMirror]
        ingress: IngressProfile
        network: NetworkProfile
        nodeDrainTimeoutMinutes: int
        platform: PlatformProfile
        provisioningState: Union[str, ProvisioningState]
        status: ResourceStatus
        version: VersionProfile


    class azure.mgmt.redhatopenshifthcp.types.ImageDigestMirror(TypedDict, total=False):
        key "mirrors": Required[list[str]]
        key "source": Required[str]
        mirrors: list[str]
        source: str


    class azure.mgmt.redhatopenshifthcp.types.IngressProfile(TypedDict, total=False):
        key "type": Union[str, IngressType]
        type: Union[str, IngressType]


    class azure.mgmt.redhatopenshifthcp.types.KmsEncryptionProfile(TypedDict, total=False):
        key "activeKey": Required[KmsKey]
        key "vaultName": Required[str]
        key "visibility": Required[Union[str, KeyVaultVisibility]]
        activeKey: KmsKey
        vaultName: str
        visibility: Union[str, KeyVaultVisibility]


    class azure.mgmt.redhatopenshifthcp.types.KmsKey(TypedDict, total=False):
        key "name": Required[str]
        key "version": Required[str]
        name: str
        version: str


    class azure.mgmt.redhatopenshifthcp.types.Label(TypedDict, total=False):
        key "key": Required[str]
        key "value": str
        key: str
        value: str


    class azure.mgmt.redhatopenshifthcp.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.redhatopenshifthcp.types.NetworkProfile(TypedDict, total=False):
        key "hostPrefix": int
        key "machineCidr": str
        key "networkType": Union[str, NetworkType]
        key "podCidr": str
        key "serviceCidr": str
        hostPrefix: int
        machineCidr: str
        networkType: Union[str, NetworkType]
        podCidr: str
        serviceCidr: str


    class azure.mgmt.redhatopenshifthcp.types.NodePool(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NodePoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NodePoolProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.redhatopenshifthcp.types.NodePoolAutoScaling(TypedDict, total=False):
        key "max": int
        key "min": int
        max: int
        min: int


    class azure.mgmt.redhatopenshifthcp.types.NodePoolPlatformProfile(TypedDict, total=False):
        key "availabilityZone": str
        key "enableEncryptionAtHost": bool
        key "osDisk": ForwardRef('OsDiskProfile', module='types')
        key "subnetId": str
        key "vmSize": Required[str]
        availabilityZone: str
        enableEncryptionAtHost: bool
        osDisk: OsDiskProfile
        subnetId: str
        vmSize: str


    class azure.mgmt.redhatopenshifthcp.types.NodePoolProperties(TypedDict, total=False):
        key "autoRepair": bool
        key "autoScaling": ForwardRef('NodePoolAutoScaling', module='types')
        key "nodeDrainTimeoutMinutes": int
        key "platform": Required[NodePoolPlatformProfile]
        key "provisioningState": Union[str, ProvisioningState]
        key "replicas": int
        key "status": ForwardRef('ResourceStatus', module='types')
        key "version": ForwardRef('NodePoolVersionProfile', module='types')
        autoRepair: bool
        autoScaling: NodePoolAutoScaling
        labels: list[Label]
        nodeDrainTimeoutMinutes: int
        platform: NodePoolPlatformProfile
        provisioningState: Union[str, ProvisioningState]
        replicas: int
        status: ResourceStatus
        taints: list[Taint]
        version: NodePoolVersionProfile


    class azure.mgmt.redhatopenshifthcp.types.NodePoolVersionProfile(TypedDict, total=False):
        key "channelGroup": str
        key "id": Required[str]
        channelGroup: str
        id: str


    class azure.mgmt.redhatopenshifthcp.types.OperatorsAuthenticationProfile(TypedDict, total=False):
        key "userAssignedIdentities": Required[UserAssignedIdentitiesProfile]
        userAssignedIdentities: UserAssignedIdentitiesProfile


    class azure.mgmt.redhatopenshifthcp.types.OsDiskProfile(TypedDict, total=False):
        key "diskStorageAccountType": Union[str, DiskStorageAccountType]
        key "diskType": Union[str, OsDiskType]
        key "encryptionSetId": str
        key "sizeGiB": int
        diskStorageAccountType: Union[str, DiskStorageAccountType]
        diskType: Union[str, OsDiskType]
        encryptionSetId: str
        sizeGiB: int


    class azure.mgmt.redhatopenshifthcp.types.PlatformProfile(TypedDict, total=False):
        key "issuerUrl": Required[str]
        key "managedResourceGroup": str
        key "networkSecurityGroupId": Required[str]
        key "operatorsAuthentication": Required[OperatorsAuthenticationProfile]
        key "outboundType": Union[str, OutboundType]
        key "subnetId": Required[str]
        key "vnetIntegrationSubnetId": Required[str]
        issuerUrl: str
        managedResourceGroup: str
        networkSecurityGroupId: str
        operatorsAuthentication: OperatorsAuthenticationProfile
        outboundType: Union[str, OutboundType]
        subnetId: str
        vnetIntegrationSubnetId: str


    class azure.mgmt.redhatopenshifthcp.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.redhatopenshifthcp.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.redhatopenshifthcp.types.ResourceStatus(TypedDict, total=False):
        conditions: list[Condition]


    class azure.mgmt.redhatopenshifthcp.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.redhatopenshifthcp.types.Taint(TypedDict, total=False):
        key "effect": Required[Union[str, Effect]]
        key "key": Required[str]
        key "value": str
        effect: Union[str, Effect]
        key: str
        value: str


    class azure.mgmt.redhatopenshifthcp.types.TokenClaimMappingsProfile(TypedDict, total=False):
        key "groups": ForwardRef('GroupClaimProfile', module='types')
        key "username": Required[UsernameClaimProfile]
        groups: GroupClaimProfile
        username: UsernameClaimProfile


    class azure.mgmt.redhatopenshifthcp.types.TokenClaimValidationRule(TypedDict, total=False):
        key "requiredClaim": ForwardRef('TokenRequiredClaim', module='types')
        key "type": Union[str, TokenValidationRuleType]
        requiredClaim: TokenRequiredClaim
        type: Union[str, TokenValidationRuleType]


    class azure.mgmt.redhatopenshifthcp.types.TokenIssuerProfile(TypedDict, total=False):
        key "audiences": Required[list[str]]
        key "ca": str
        key "url": Required[str]
        audiences: list[str]
        ca: str
        url: str


    class azure.mgmt.redhatopenshifthcp.types.TokenRequiredClaim(TypedDict, total=False):
        key "claim": Required[str]
        key "requiredValue": Required[str]
        claim: str
        requiredValue: str


    class azure.mgmt.redhatopenshifthcp.types.TrackedResource(Resource):
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


    class azure.mgmt.redhatopenshifthcp.types.UserAssignedIdentitiesProfile(TypedDict, total=False):
        key "controlPlaneOperators": Required[dict[str, str]]
        key "dataPlaneOperators": Required[dict[str, str]]
        key "serviceManagedIdentity": Required[str]
        controlPlaneOperators: dict[str, str]
        dataPlaneOperators: dict[str, str]
        serviceManagedIdentity: str


    class azure.mgmt.redhatopenshifthcp.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.redhatopenshifthcp.types.UsernameClaimProfile(TypedDict, total=False):
        key "claim": Required[str]
        key "prefix": str
        key "prefixPolicy": Union[str, UsernameClaimPrefixPolicy]
        claim: str
        prefix: str
        prefixPolicy: Union[str, UsernameClaimPrefixPolicy]


    class azure.mgmt.redhatopenshifthcp.types.VersionProfile(TypedDict, total=False):
        key "channelGroup": str
        key "id": Required[str]
        channelGroup: str
        id: str


```