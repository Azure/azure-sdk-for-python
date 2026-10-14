```py
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


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

    class azure.mgmt.redhatopenshift.models.APIServerProfile(_Model):
        ip: Optional[str]
        url: Optional[str]
        visibility: Optional[Union[str, Visibility]]

        @overload
        def __init__(
                self, 
                *, 
                visibility: Optional[Union[str, Visibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.ClusterProfile(_Model):
        domain: Optional[str]
        fips_validated_modules: Optional[Union[str, FipsValidatedModules]]
        oidc_issuer: Optional[str]
        pull_secret: Optional[str]
        resource_group_id: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domain: Optional[str] = ..., 
                fips_validated_modules: Optional[Union[str, FipsValidatedModules]] = ..., 
                pull_secret: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.ConsoleProfile(_Model):
        url: Optional[str]


    class azure.mgmt.redhatopenshift.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.redhatopenshift.models.Display(_Model):
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


    class azure.mgmt.redhatopenshift.models.EffectiveOutboundIP(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.EncryptionAtHost(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redhatopenshift.models.FipsValidatedModules(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.redhatopenshift.models.IngressProfile(_Model):
        ip: Optional[str]
        name: Optional[str]
        visibility: Optional[Union[str, Visibility]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                visibility: Optional[Union[str, Visibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.LoadBalancerProfile(_Model):
        effective_outbound_ips: Optional[list[EffectiveOutboundIP]]
        managed_outbound_ips: Optional[ManagedOutboundIPs]

        @overload
        def __init__(
                self, 
                *, 
                managed_outbound_ips: Optional[ManagedOutboundIPs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.ManagedOutboundIPs(_Model):
        count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.redhatopenshift.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.redhatopenshift.models.MasterProfile(_Model):
        disk_encryption_set_id: Optional[str]
        encryption_at_host: Optional[Union[str, EncryptionAtHost]]
        subnet_id: Optional[str]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                encryption_at_host: Optional[Union[str, EncryptionAtHost]] = ..., 
                subnet_id: Optional[str] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.NetworkProfile(_Model):
        load_balancer_profile: Optional[LoadBalancerProfile]
        outbound_type: Optional[Union[str, OutboundType]]
        pod_cidr: Optional[str]
        preconfigured_nsg: Optional[Union[str, PreconfiguredNSG]]
        service_cidr: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                load_balancer_profile: Optional[LoadBalancerProfile] = ..., 
                outbound_type: Optional[Union[str, OutboundType]] = ..., 
                pod_cidr: Optional[str] = ..., 
                preconfigured_nsg: Optional[Union[str, PreconfiguredNSG]] = ..., 
                service_cidr: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftCluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[OpenShiftClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[OpenShiftClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterAdminKubeconfig(_Model):
        kubeconfig: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kubeconfig: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterCredentials(_Model):
        kubeadmin_password: Optional[str]
        kubeadmin_username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kubeadmin_password: Optional[str] = ..., 
                kubeadmin_username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterProperties(_Model):
        apiserver_profile: Optional[APIServerProfile]
        cluster_profile: Optional[ClusterProfile]
        console_profile: Optional[ConsoleProfile]
        ingress_profiles: Optional[list[IngressProfile]]
        master_profile: Optional[MasterProfile]
        network_profile: Optional[NetworkProfile]
        platform_workload_identity_profile: Optional[PlatformWorkloadIdentityProfile]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_principal_profile: Optional[ServicePrincipalProfile]
        worker_profiles: Optional[list[WorkerProfile]]
        worker_profiles_status: Optional[list[WorkerProfile]]

        @overload
        def __init__(
                self, 
                *, 
                apiserver_profile: Optional[APIServerProfile] = ..., 
                cluster_profile: Optional[ClusterProfile] = ..., 
                console_profile: Optional[ConsoleProfile] = ..., 
                ingress_profiles: Optional[list[IngressProfile]] = ..., 
                master_profile: Optional[MasterProfile] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                platform_workload_identity_profile: Optional[PlatformWorkloadIdentityProfile] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                service_principal_profile: Optional[ServicePrincipalProfile] = ..., 
                worker_profiles: Optional[list[WorkerProfile]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftClusterUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[OpenShiftClusterProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[OpenShiftClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[OpenShiftVersionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OpenShiftVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redhatopenshift.models.OpenShiftVersionProperties(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.Operation(_Model):
        display: Optional[Display]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[Display] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.OutboundType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOADBALANCER = "Loadbalancer"
        USER_DEFINED_ROUTING = "UserDefinedRouting"


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentity(_Model):
        client_id: Optional[str]
        object_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityProfile(_Model):
        platform_workload_identities: Optional[dict[str, PlatformWorkloadIdentity]]
        upgradeable_to: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                platform_workload_identities: Optional[dict[str, PlatformWorkloadIdentity]] = ..., 
                upgradeable_to: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityRole(_Model):
        operator_name: Optional[str]
        role_definition_id: Optional[str]
        role_definition_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                operator_name: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                role_definition_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityRoleSet(ProxyResource):
        id: str
        name: str
        properties: Optional[PlatformWorkloadIdentityRoleSetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlatformWorkloadIdentityRoleSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.redhatopenshift.models.PlatformWorkloadIdentityRoleSetProperties(_Model):
        open_shift_version: Optional[str]
        platform_workload_identity_roles: Optional[list[PlatformWorkloadIdentityRole]]

        @overload
        def __init__(
                self, 
                *, 
                open_shift_version: Optional[str] = ..., 
                platform_workload_identity_roles: Optional[list[PlatformWorkloadIdentityRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.redhatopenshift.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.redhatopenshift.models.ServicePrincipalProfile(_Model):
        client_id: Optional[str]
        client_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.redhatopenshift.models.SystemData(_Model):
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


    class azure.mgmt.redhatopenshift.models.TrackedResource(Resource):
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


    class azure.mgmt.redhatopenshift.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.redhatopenshift.models.Visibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.redhatopenshift.models.WorkerProfile(_Model):
        count: Optional[int]
        disk_encryption_set_id: Optional[str]
        disk_size_gb: Optional[int]
        encryption_at_host: Optional[Union[str, EncryptionAtHost]]
        name: Optional[str]
        subnet_id: Optional[str]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption_at_host: Optional[Union[str, EncryptionAtHost]] = ..., 
                name: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


namespace azure.mgmt.redhatopenshift.types

    class azure.mgmt.redhatopenshift.types.APIServerProfile(TypedDict, total=False):
        key "ip": str
        key "url": str
        key "visibility": Union[str, Visibility]
        ip: str
        url: str
        visibility: Union[str, Visibility]


    class azure.mgmt.redhatopenshift.types.ClusterProfile(TypedDict, total=False):
        key "domain": str
        key "fipsValidatedModules": Union[str, FipsValidatedModules]
        key "oidcIssuer": str
        key "pullSecret": str
        key "resourceGroupId": str
        key "version": str
        domain: str
        fips_validated_modules: Union[str, FipsValidatedModules]
        oidc_issuer: str
        pull_secret: str
        resource_group_id: str
        version: str


    class azure.mgmt.redhatopenshift.types.ConsoleProfile(TypedDict, total=False):
        key "url": str
        url: str


    class azure.mgmt.redhatopenshift.types.EffectiveOutboundIP(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.redhatopenshift.types.IngressProfile(TypedDict, total=False):
        key "ip": str
        key "name": str
        key "visibility": Union[str, Visibility]
        ip: str
        name: str
        visibility: Union[str, Visibility]


    class azure.mgmt.redhatopenshift.types.LoadBalancerProfile(TypedDict, total=False):
        key "managedOutboundIps": ForwardRef('ManagedOutboundIPs', module='types')
        effectiveOutboundIps: list[EffectiveOutboundIP]
        effective_outbound_ips: list[EffectiveOutboundIP]
        managed_outbound_ips: ManagedOutboundIPs


    class azure.mgmt.redhatopenshift.types.ManagedOutboundIPs(TypedDict, total=False):
        key "count": int
        count: int


    class azure.mgmt.redhatopenshift.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.redhatopenshift.types.MasterProfile(TypedDict, total=False):
        key "diskEncryptionSetId": str
        key "encryptionAtHost": Union[str, EncryptionAtHost]
        key "subnetId": str
        key "vmSize": str
        disk_encryption_set_id: str
        encryption_at_host: Union[str, EncryptionAtHost]
        subnet_id: str
        vm_size: str


    class azure.mgmt.redhatopenshift.types.NetworkProfile(TypedDict, total=False):
        key "loadBalancerProfile": ForwardRef('LoadBalancerProfile', module='types')
        key "outboundType": Union[str, OutboundType]
        key "podCidr": str
        key "preconfiguredNSG": Union[str, PreconfiguredNSG]
        key "serviceCidr": str
        load_balancer_profile: LoadBalancerProfile
        outbound_type: Union[str, OutboundType]
        pod_cidr: str
        preconfigured_nsg: Union[str, PreconfiguredNSG]
        service_cidr: str


    class azure.mgmt.redhatopenshift.types.OpenShiftCluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('OpenShiftClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: OpenShiftClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.redhatopenshift.types.OpenShiftClusterProperties(TypedDict, total=False):
        key "apiserverProfile": ForwardRef('APIServerProfile', module='types')
        key "clusterProfile": ForwardRef('ClusterProfile', module='types')
        key "consoleProfile": ForwardRef('ConsoleProfile', module='types')
        key "masterProfile": ForwardRef('MasterProfile', module='types')
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "platformWorkloadIdentityProfile": ForwardRef('PlatformWorkloadIdentityProfile', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "servicePrincipalProfile": ForwardRef('ServicePrincipalProfile', module='types')
        apiserver_profile: APIServerProfile
        cluster_profile: ClusterProfile
        console_profile: ConsoleProfile
        ingressProfiles: list[IngressProfile]
        ingress_profiles: list[IngressProfile]
        master_profile: MasterProfile
        network_profile: NetworkProfile
        platform_workload_identity_profile: PlatformWorkloadIdentityProfile
        provisioning_state: Union[str, ProvisioningState]
        service_principal_profile: ServicePrincipalProfile
        workerProfiles: list[WorkerProfile]
        workerProfilesStatus: list[WorkerProfile]
        worker_profiles: list[WorkerProfile]
        worker_profiles_status: list[WorkerProfile]


    class azure.mgmt.redhatopenshift.types.OpenShiftClusterUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('OpenShiftClusterProperties', module='types')
        identity: ManagedServiceIdentity
        properties: OpenShiftClusterProperties
        tags: dict[str, str]


    class azure.mgmt.redhatopenshift.types.PlatformWorkloadIdentity(TypedDict, total=False):
        key "clientId": str
        key "objectId": str
        key "resourceId": str
        client_id: str
        object_id: str
        resource_id: str


    class azure.mgmt.redhatopenshift.types.PlatformWorkloadIdentityProfile(TypedDict, total=False):
        key "upgradeableTo": str
        platformWorkloadIdentities: dict[str, PlatformWorkloadIdentity]
        platform_workload_identities: dict[str, PlatformWorkloadIdentity]
        upgradeable_to: str


    class azure.mgmt.redhatopenshift.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.redhatopenshift.types.ServicePrincipalProfile(TypedDict, total=False):
        key "clientId": str
        key "clientSecret": str
        client_id: str
        client_secret: str


    class azure.mgmt.redhatopenshift.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.redhatopenshift.types.TrackedResource(Resource):
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


    class azure.mgmt.redhatopenshift.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.redhatopenshift.types.WorkerProfile(TypedDict, total=False):
        key "count": int
        key "diskEncryptionSetId": str
        key "diskSizeGB": int
        key "encryptionAtHost": Union[str, EncryptionAtHost]
        key "name": str
        key "subnetId": str
        key "vmSize": str
        count: int
        disk_encryption_set_id: str
        disk_size_gb: int
        encryption_at_host: Union[str, EncryptionAtHost]
        name: str
        subnet_id: str
        vm_size: str


```