```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.redhatopenshift

    class azure.mgmt.redhatopenshift.AzureRedHatOpenShiftClient: implements ContextManager 
        open_shift_clusters: OpenShiftClustersOperations
        open_shift_versions: OpenShiftVersionsOperations
        operations: Operations
        platform_workload_identity_role_set: PlatformWorkloadIdentityRoleSetOperations
        platform_workload_identity_role_sets: PlatformWorkloadIdentityRoleSetsOperations

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


namespace azure.mgmt.redhatopenshift.aio

    class azure.mgmt.redhatopenshift.aio.AzureRedHatOpenShiftClient: implements AsyncContextManager 
        open_shift_clusters: OpenShiftClustersOperations
        open_shift_versions: OpenShiftVersionsOperations
        operations: Operations
        platform_workload_identity_role_set: PlatformWorkloadIdentityRoleSetOperations
        platform_workload_identity_role_sets: PlatformWorkloadIdentityRoleSetsOperations

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


namespace azure.mgmt.redhatopenshift.aio.operations

    class azure.mgmt.redhatopenshift.aio.operations.OpenShiftClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: OpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OpenShiftCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OpenShiftCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: OpenShiftClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OpenShiftCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OpenShiftCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> OpenShiftCluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OpenShiftCluster]: ...

        @distributed_trace_async
        async def list_admin_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> OpenShiftClusterAdminKubeconfig: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OpenShiftCluster]: ...

        @distributed_trace_async
        async def list_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> OpenShiftClusterCredentials: ...


    class azure.mgmt.redhatopenshift.aio.operations.OpenShiftVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                open_shift_version: str, 
                **kwargs: Any
            ) -> OpenShiftVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OpenShiftVersion]: ...


    class azure.mgmt.redhatopenshift.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.redhatopenshift.aio.operations.PlatformWorkloadIdentityRoleSetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                open_shift_minor_version: str, 
                **kwargs: Any
            ) -> PlatformWorkloadIdentityRoleSet: ...


    class azure.mgmt.redhatopenshift.aio.operations.PlatformWorkloadIdentityRoleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PlatformWorkloadIdentityRoleSet]: ...


namespace azure.mgmt.redhatopenshift.models

    class azure.mgmt.redhatopenshift.models.APIServerProfile(Model):
        ip: str
        url: str
        visibility: Union[str, Visibility]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                visibility: Optional[Union[str, Visibility]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.ClusterProfile(Model):
        domain: str
        fips_validated_modules: Union[str, FipsValidatedModules]
        oidc_issuer: str
        pull_secret: str
        resource_group_id: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain: Optional[str] = ..., 
                fips_validated_modules: Optional[Union[str, FipsValidatedModules]] = ..., 
                pull_secret: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.ConsoleProfile(Model):
        url: str

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


    class azure.mgmt.redhatopenshift.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.redhatopenshift.models.Display(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.EffectiveOutboundIP(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.EncryptionAtHost(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redhatopenshift.models.FipsValidatedModules(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redhatopenshift.models.IngressProfile(Model):
        ip: str
        name: str
        visibility: Union[str, Visibility]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                visibility: Optional[Union[str, Visibility]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.LoadBalancerProfile(Model):
        effective_outbound_ips: list[EffectiveOutboundIP]
        managed_outbound_ips: ManagedOutboundIPs

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_outbound_ips: Optional[ManagedOutboundIPs] = ..., 
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


    class azure.mgmt.redhatopenshift.models.ManagedOutboundIPs(Model):
        count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
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


    class azure.mgmt.redhatopenshift.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
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


    class azure.mgmt.redhatopenshift.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.redhatopenshift.models.MasterProfile(Model):
        disk_encryption_set_id: str
        encryption_at_host: Union[str, EncryptionAtHost]
        subnet_id: str
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                encryption_at_host: Optional[Union[str, EncryptionAtHost]] = ..., 
                subnet_id: Optional[str] = ..., 
                vm_size: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.NetworkProfile(Model):
        load_balancer_profile: LoadBalancerProfile
        outbound_type: Union[str, OutboundType]
        pod_cidr: str
        preconfigured_nsg: Union[str, PreconfiguredNSG]
        service_cidr: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                load_balancer_profile: Optional[LoadBalancerProfile] = ..., 
                outbound_type: Optional[Union[str, OutboundType]] = ..., 
                pod_cidr: Optional[str] = ..., 
                preconfigured_nsg: Optional[Union[str, PreconfiguredNSG]] = ..., 
                service_cidr: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftCluster(TrackedResource):
        apiserver_profile: APIServerProfile
        cluster_profile: ClusterProfile
        console_profile: ConsoleProfile
        id: str
        identity: ManagedServiceIdentity
        ingress_profiles: list[IngressProfile]
        location: str
        master_profile: MasterProfile
        name: str
        network_profile: NetworkProfile
        platform_workload_identity_profile: PlatformWorkloadIdentityProfile
        provisioning_state: Union[str, ProvisioningState]
        service_principal_profile: ServicePrincipalProfile
        system_data: SystemData
        tags: dict[str, str]
        type: str
        worker_profiles: list[WorkerProfile]
        worker_profiles_status: list[WorkerProfile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                apiserver_profile: Optional[APIServerProfile] = ..., 
                cluster_profile: Optional[ClusterProfile] = ..., 
                console_profile: Optional[ConsoleProfile] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                ingress_profiles: Optional[list[IngressProfile]] = ..., 
                location: str, 
                master_profile: Optional[MasterProfile] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                platform_workload_identity_profile: Optional[PlatformWorkloadIdentityProfile] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                service_principal_profile: Optional[ServicePrincipalProfile] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                worker_profiles: Optional[list[WorkerProfile]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterAdminKubeconfig(Model):
        kubeconfig: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kubeconfig: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterCredentials(Model):
        kubeadmin_password: str
        kubeadmin_username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kubeadmin_password: Optional[str] = ..., 
                kubeadmin_username: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterList(Model):
        next_link: str
        value: list[OpenShiftCluster]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[OpenShiftCluster]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterUpdate(Model):
        apiserver_profile: APIServerProfile
        cluster_profile: ClusterProfile
        console_profile: ConsoleProfile
        identity: ManagedServiceIdentity
        ingress_profiles: list[IngressProfile]
        master_profile: MasterProfile
        network_profile: NetworkProfile
        platform_workload_identity_profile: PlatformWorkloadIdentityProfile
        provisioning_state: Union[str, ProvisioningState]
        service_principal_profile: ServicePrincipalProfile
        tags: dict[str, str]
        worker_profiles: list[WorkerProfile]
        worker_profiles_status: list[WorkerProfile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                apiserver_profile: Optional[APIServerProfile] = ..., 
                cluster_profile: Optional[ClusterProfile] = ..., 
                console_profile: Optional[ConsoleProfile] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                ingress_profiles: Optional[list[IngressProfile]] = ..., 
                master_profile: Optional[MasterProfile] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                platform_workload_identity_profile: Optional[PlatformWorkloadIdentityProfile] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                service_principal_profile: Optional[ServicePrincipalProfile] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                worker_profiles: Optional[list[WorkerProfile]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftVersion(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                version: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OpenShiftVersionList(Model):
        next_link: str
        value: list[OpenShiftVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[OpenShiftVersion]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.Operation(Model):
        display: Display
        name: str
        origin: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[Display] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.OperationList(Model):
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


    class azure.mgmt.redhatopenshift.models.OutboundType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOADBALANCER = "Loadbalancer"
        USER_DEFINED_ROUTING = "UserDefinedRouting"


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentity(Model):
        client_id: str
        object_id: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityProfile(Model):
        platform_workload_identities: dict[str, PlatformWorkloadIdentity]
        upgradeable_to: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                platform_workload_identities: Optional[dict[str, PlatformWorkloadIdentity]] = ..., 
                upgradeable_to: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityRole(Model):
        operator_name: str
        role_definition_id: str
        role_definition_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operator_name: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                role_definition_name: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityRoleSet(ProxyResource):
        id: str
        name: str
        open_shift_version: str
        platform_workload_identity_roles: list[PlatformWorkloadIdentityRole]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                open_shift_version: Optional[str] = ..., 
                platform_workload_identity_roles: Optional[list[PlatformWorkloadIdentityRole]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityRoleSetList(Model):
        next_link: str
        value: list[PlatformWorkloadIdentityRoleSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[PlatformWorkloadIdentityRoleSet]] = ..., 
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


    class azure.mgmt.redhatopenshift.models.PreconfiguredNSG(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redhatopenshift.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN_UPDATING = "AdminUpdating"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.redhatopenshift.models.ProxyResource(Resource):
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


    class azure.mgmt.redhatopenshift.models.Resource(Model):
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


    class azure.mgmt.redhatopenshift.models.ServicePrincipalProfile(Model):
        client_id: str
        client_secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
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


    class azure.mgmt.redhatopenshift.models.SystemData(Model):
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


    class azure.mgmt.redhatopenshift.models.TrackedResource(Resource):
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


    class azure.mgmt.redhatopenshift.models.UserAssignedIdentity(Model):
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


    class azure.mgmt.redhatopenshift.models.Visibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.redhatopenshift.models.WorkerProfile(Model):
        count: int
        disk_encryption_set_id: str
        disk_size_gb: int
        encryption_at_host: Union[str, EncryptionAtHost]
        name: str
        subnet_id: str
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption_at_host: Optional[Union[str, EncryptionAtHost]] = ..., 
                name: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                vm_size: Optional[str] = ..., 
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


namespace azure.mgmt.redhatopenshift.operations

    class azure.mgmt.redhatopenshift.operations.OpenShiftClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: OpenShiftCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OpenShiftCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OpenShiftCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: OpenShiftClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OpenShiftCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OpenShiftCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> OpenShiftCluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OpenShiftCluster]: ...

        @distributed_trace
        def list_admin_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> OpenShiftClusterAdminKubeconfig: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OpenShiftCluster]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> OpenShiftClusterCredentials: ...


    class azure.mgmt.redhatopenshift.operations.OpenShiftVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                open_shift_version: str, 
                **kwargs: Any
            ) -> OpenShiftVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[OpenShiftVersion]: ...


    class azure.mgmt.redhatopenshift.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.redhatopenshift.operations.PlatformWorkloadIdentityRoleSetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                open_shift_minor_version: str, 
                **kwargs: Any
            ) -> PlatformWorkloadIdentityRoleSet: ...


    class azure.mgmt.redhatopenshift.operations.PlatformWorkloadIdentityRoleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[PlatformWorkloadIdentityRoleSet]: ...


```