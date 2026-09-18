```py
namespace azure.mgmt.containerinstance

    class azure.mgmt.containerinstance.ContainerInstanceManagementClient: implements ContextManager 
        ai_agents_groups: AiAgentsGroupsOperations
        cg_profile: CGProfileOperations
        cg_profiles: CGProfilesOperations
        container_groups: ContainerGroupsOperations
        containers: ContainersOperations
        location: LocationOperations
        ngroups: NGroupsOperations
        operations: Operations
        subnet_service_association_link: SubnetServiceAssociationLinkOperations

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


namespace azure.mgmt.containerinstance.aio

    class azure.mgmt.containerinstance.aio.ContainerInstanceManagementClient: implements AsyncContextManager 
        ai_agents_groups: AiAgentsGroupsOperations
        cg_profile: CGProfileOperations
        cg_profiles: CGProfilesOperations
        container_groups: ContainerGroupsOperations
        containers: ContainersOperations
        location: LocationOperations
        ngroups: NGroupsOperations
        operations: Operations
        subnet_service_association_link: SubnetServiceAssociationLinkOperations

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


namespace azure.mgmt.containerinstance.aio.operations

    class azure.mgmt.containerinstance.aio.operations.AiAgentsGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                resource: AiAgentsGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiAgentsGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                resource: AiAgentsGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiAgentsGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiAgentsGroup]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_agents_group_name']}, api_versions_list=['2026-08-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                properties: AiAgentsGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiAgentsGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                properties: AiAgentsGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiAgentsGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiAgentsGroup]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_agents_group_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        async def connect(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                **kwargs: Any
            ) -> AiAgentsGroupAccessToken: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_agents_group_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                **kwargs: Any
            ) -> AiAgentsGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiAgentsGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AiAgentsGroup]: ...


    class azure.mgmt.containerinstance.aio.operations.CGProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: ContainerGroupProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: ContainerGroupProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace_async
        async def get_by_revision_number(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                revision_number: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def list_all_revisions(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerGroupProfile]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: ContainerGroupProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: ContainerGroupProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...


    class azure.mgmt.containerinstance.aio.operations.CGProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerGroupProfile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ContainerGroupProfile]: ...


    class azure.mgmt.containerinstance.aio.operations.ContainerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: ContainerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: ContainerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @distributed_trace_async
        async def get_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> List[str]: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ContainerGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerGroup]: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: Resource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: Resource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...


    class azure.mgmt.containerinstance.aio.operations.ContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def attach(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ContainerAttachResponse: ...

        @overload
        async def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: ContainerExecRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @overload
        async def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: ContainerExecRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @overload
        async def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @distributed_trace_async
        async def list_logs(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                *, 
                tail: Optional[int] = ..., 
                timestamps: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Logs: ...


    class azure.mgmt.containerinstance.aio.operations.LocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_cached_images(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CachedImages]: ...

        @distributed_trace
        def list_capabilities(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Capabilities]: ...

        @distributed_trace
        def list_usage(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.containerinstance.aio.operations.NGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> NGroup: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[NGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NGroup]: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.containerinstance.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.containerinstance.aio.operations.SubnetServiceAssociationLinkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


namespace azure.mgmt.containerinstance.models

    class azure.mgmt.containerinstance.models.AiAgentsGroup(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AiAgentsGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AiAgentsGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.AiAgentsGroupAccessToken(_Model):
        access_token: str
        endpoint: str
        not_after: datetime

        @overload
        def __init__(
                self, 
                *, 
                access_token: str, 
                endpoint: str, 
                not_after: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.AiAgentsGroupNetworkProfile(_Model):
        subnets: Optional[list[SubnetReference]]

        @overload
        def __init__(
                self, 
                *, 
                subnets: Optional[list[SubnetReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.AiAgentsGroupProperties(_Model):
        management_resource_group_id: Optional[str]
        network_profile: Optional[AiAgentsGroupNetworkProfile]
        provisioning_state: Optional[Union[str, AiAgentsGroupProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                network_profile: Optional[AiAgentsGroupNetworkProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.AiAgentsGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerinstance.models.AiAgentsGroupTagsUpdate(_Model):
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


    class azure.mgmt.containerinstance.models.ApiEntityReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ApplicationGateway(_Model):
        backend_address_pools: Optional[list[ApplicationGatewayBackendAddressPool]]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backend_address_pools: Optional[list[ApplicationGatewayBackendAddressPool]] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ApplicationGatewayBackendAddressPool(_Model):
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ArmResource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerinstance.models.AzureFileShareAccessTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COOL = "Cool"
        HOT = "Hot"
        PREMIUM = "Premium"
        TRANSACTION_OPTIMIZED = "TransactionOptimized"


    class azure.mgmt.containerinstance.models.AzureFileShareAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUSIVE = "Exclusive"
        SHARED = "Shared"


    class azure.mgmt.containerinstance.models.AzureFileVolume(_Model):
        read_only: Optional[bool]
        share_name: str
        storage_account_key: Optional[str]
        storage_account_key_reference: Optional[str]
        storage_account_name: str
        user_assigned_identity_client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                read_only: Optional[bool] = ..., 
                share_name: str, 
                storage_account_key: Optional[str] = ..., 
                storage_account_key_reference: Optional[str] = ..., 
                storage_account_name: str, 
                user_assigned_identity_client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.CachedImages(_Model):
        image: str
        os_type: str

        @overload
        def __init__(
                self, 
                *, 
                image: str, 
                os_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.Capabilities(_Model):
        capabilities: Optional[CapabilitiesCapabilities]
        gpu: Optional[str]
        ip_address_type: Optional[str]
        location: Optional[str]
        os_type: Optional[str]
        resource_type: Optional[str]


    class azure.mgmt.containerinstance.models.CapabilitiesCapabilities(_Model):
        max_cpu: Optional[float]
        max_gpu_count: Optional[float]
        max_memory_in_gb: Optional[float]


    class azure.mgmt.containerinstance.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.CloudErrorBody(_Model):
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


    class azure.mgmt.containerinstance.models.ConfidentialComputeProperties(_Model):
        cce_policy: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cce_policy: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ConfigMap(_Model):
        key_value_pairs: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                key_value_pairs: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.Container(_Model):
        name: str
        properties: ContainerProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: ContainerProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerAttachResponse(_Model):
        password: Optional[str]
        web_socket_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                web_socket_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerExec(_Model):
        command: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerExecRequest(_Model):
        command: Optional[str]
        terminal_size: Optional[ContainerExecRequestTerminalSize]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[str] = ..., 
                terminal_size: Optional[ContainerExecRequestTerminalSize] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerExecRequestTerminalSize(_Model):
        cols: Optional[int]
        rows: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cols: Optional[int] = ..., 
                rows: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerExecResponse(_Model):
        password: Optional[str]
        web_socket_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                web_socket_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroup(ProxyResource):
        id: str
        identity: Optional[ContainerGroupIdentity]
        location: Optional[str]
        name: str
        properties: ContainerGroupProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ContainerGroupIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: ContainerGroupProperties, 
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


    class azure.mgmt.containerinstance.models.ContainerGroupDiagnostics(_Model):
        log_analytics: Optional[LogAnalytics]

        @overload
        def __init__(
                self, 
                *, 
                log_analytics: Optional[LogAnalytics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentities]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentities]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupIpAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.containerinstance.models.ContainerGroupNetworkProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.containerinstance.models.ContainerGroupPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.containerinstance.models.ContainerGroupProfile(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ContainerGroupProfileProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ContainerGroupProfileProperties] = ..., 
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


    class azure.mgmt.containerinstance.models.ContainerGroupProfilePatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProfileProperties(_Model):
        confidential_compute_properties: Optional[ConfidentialComputeProperties]
        containers: list[Container]
        diagnostics: Optional[ContainerGroupDiagnostics]
        encryption_properties: Optional[EncryptionProperties]
        extensions: Optional[list[DeploymentExtensionSpec]]
        image_registry_credentials: Optional[list[ImageRegistryCredential]]
        init_containers: Optional[list[InitContainerDefinition]]
        ip_address: Optional[IpAddress]
        os_type: Union[str, OperatingSystemTypes]
        priority: Optional[Union[str, ContainerGroupPriority]]
        registered_revisions: Optional[list[int]]
        restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]]
        revision: Optional[int]
        security_context: Optional[SecurityContextDefinition]
        shutdown_grace_period: Optional[datetime]
        sku: Optional[Union[str, ContainerGroupSku]]
        time_to_live: Optional[datetime]
        use_krypton: Optional[bool]
        volumes: Optional[list[Volume]]

        @overload
        def __init__(
                self, 
                *, 
                confidential_compute_properties: Optional[ConfidentialComputeProperties] = ..., 
                containers: list[Container], 
                diagnostics: Optional[ContainerGroupDiagnostics] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                extensions: Optional[list[DeploymentExtensionSpec]] = ..., 
                image_registry_credentials: Optional[list[ImageRegistryCredential]] = ..., 
                init_containers: Optional[list[InitContainerDefinition]] = ..., 
                ip_address: Optional[IpAddress] = ..., 
                os_type: Union[str, OperatingSystemTypes], 
                priority: Optional[Union[str, ContainerGroupPriority]] = ..., 
                restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]] = ..., 
                security_context: Optional[SecurityContextDefinition] = ..., 
                shutdown_grace_period: Optional[datetime] = ..., 
                sku: Optional[Union[str, ContainerGroupSku]] = ..., 
                time_to_live: Optional[datetime] = ..., 
                use_krypton: Optional[bool] = ..., 
                volumes: Optional[list[Volume]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProfileReferenceDefinition(_Model):
        id: Optional[str]
        revision: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                revision: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProfileStub(_Model):
        container_group_properties: Optional[NGroupContainerGroupProperties]
        network_profile: Optional[NetworkProfile]
        resource: Optional[ApiEntityReference]
        revision: Optional[int]
        storage_profile: Optional[StorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                container_group_properties: Optional[NGroupContainerGroupProperties] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                resource: Optional[ApiEntityReference] = ..., 
                revision: Optional[int] = ..., 
                storage_profile: Optional[StorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProperties(_Model):
        confidential_compute_properties: Optional[ConfidentialComputeProperties]
        container_group_profile: Optional[ContainerGroupProfileReferenceDefinition]
        containers: list[Container]
        diagnostics: Optional[ContainerGroupDiagnostics]
        dns_config: Optional[DnsConfiguration]
        encryption_properties: Optional[EncryptionProperties]
        extensions: Optional[list[DeploymentExtensionSpec]]
        identity_acls: Optional[IdentityAcls]
        image_registry_credentials: Optional[list[ImageRegistryCredential]]
        init_containers: Optional[list[InitContainerDefinition]]
        instance_view: Optional[ContainerGroupPropertiesInstanceView]
        ip_address: Optional[IpAddress]
        is_created_from_standby_pool: Optional[bool]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        priority: Optional[Union[str, ContainerGroupPriority]]
        provisioning_state: Optional[str]
        restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]]
        secret_references: Optional[list[SecretReference]]
        sku: Optional[Union[str, ContainerGroupSku]]
        standby_pool_profile: Optional[StandbyPoolProfileDefinition]
        subnet_ids: Optional[list[ContainerGroupSubnetId]]
        volumes: Optional[list[Volume]]

        @overload
        def __init__(
                self, 
                *, 
                confidential_compute_properties: Optional[ConfidentialComputeProperties] = ..., 
                container_group_profile: Optional[ContainerGroupProfileReferenceDefinition] = ..., 
                containers: list[Container], 
                diagnostics: Optional[ContainerGroupDiagnostics] = ..., 
                dns_config: Optional[DnsConfiguration] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                extensions: Optional[list[DeploymentExtensionSpec]] = ..., 
                identity_acls: Optional[IdentityAcls] = ..., 
                image_registry_credentials: Optional[list[ImageRegistryCredential]] = ..., 
                init_containers: Optional[list[InitContainerDefinition]] = ..., 
                ip_address: Optional[IpAddress] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                priority: Optional[Union[str, ContainerGroupPriority]] = ..., 
                restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]] = ..., 
                secret_references: Optional[list[SecretReference]] = ..., 
                sku: Optional[Union[str, ContainerGroupSku]] = ..., 
                standby_pool_profile: Optional[StandbyPoolProfileDefinition] = ..., 
                subnet_ids: Optional[list[ContainerGroupSubnetId]] = ..., 
                volumes: Optional[list[Volume]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerGroupPropertiesInstanceView(_Model):
        events: Optional[list[Event]]
        state: Optional[str]


    class azure.mgmt.containerinstance.models.ContainerGroupRestartPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        NEVER = "Never"
        ON_FAILURE = "OnFailure"


    class azure.mgmt.containerinstance.models.ContainerGroupSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL = "Confidential"
        DEDICATED = "Dedicated"
        NOT_SPECIFIED = "NotSpecified"
        STANDARD = "Standard"


    class azure.mgmt.containerinstance.models.ContainerGroupSubnetId(_Model):
        id: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerHttpGet(_Model):
        http_headers: Optional[list[HttpHeader]]
        path: Optional[str]
        port: int
        scheme: Optional[Union[str, Scheme]]

        @overload
        def __init__(
                self, 
                *, 
                http_headers: Optional[list[HttpHeader]] = ..., 
                path: Optional[str] = ..., 
                port: int, 
                scheme: Optional[Union[str, Scheme]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerInstanceOperationsOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.containerinstance.models.ContainerNetworkProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.containerinstance.models.ContainerPort(_Model):
        port: int
        protocol: Optional[Union[str, ContainerNetworkProtocol]]

        @overload
        def __init__(
                self, 
                *, 
                port: int, 
                protocol: Optional[Union[str, ContainerNetworkProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerProbe(_Model):
        exec_property: Optional[ContainerExec]
        failure_threshold: Optional[int]
        http_get: Optional[ContainerHttpGet]
        initial_delay_seconds: Optional[int]
        period_seconds: Optional[int]
        success_threshold: Optional[int]
        timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                exec_property: Optional[ContainerExec] = ..., 
                failure_threshold: Optional[int] = ..., 
                http_get: Optional[ContainerHttpGet] = ..., 
                initial_delay_seconds: Optional[int] = ..., 
                period_seconds: Optional[int] = ..., 
                success_threshold: Optional[int] = ..., 
                timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerProperties(_Model):
        command: Optional[list[str]]
        config_map: Optional[ConfigMap]
        environment_variables: Optional[list[EnvironmentVariable]]
        image: Optional[str]
        instance_view: Optional[ContainerPropertiesInstanceView]
        liveness_probe: Optional[ContainerProbe]
        ports: Optional[list[ContainerPort]]
        readiness_probe: Optional[ContainerProbe]
        resources: Optional[ResourceRequirements]
        security_context: Optional[SecurityContextDefinition]
        volume_mounts: Optional[list[VolumeMount]]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[list[str]] = ..., 
                config_map: Optional[ConfigMap] = ..., 
                environment_variables: Optional[list[EnvironmentVariable]] = ..., 
                image: Optional[str] = ..., 
                liveness_probe: Optional[ContainerProbe] = ..., 
                ports: Optional[list[ContainerPort]] = ..., 
                readiness_probe: Optional[ContainerProbe] = ..., 
                resources: Optional[ResourceRequirements] = ..., 
                security_context: Optional[SecurityContextDefinition] = ..., 
                volume_mounts: Optional[list[VolumeMount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ContainerPropertiesInstanceView(_Model):
        current_state: Optional[ContainerState]
        events: Optional[list[Event]]
        previous_state: Optional[ContainerState]
        restart_count: Optional[int]


    class azure.mgmt.containerinstance.models.ContainerState(_Model):
        detail_status: Optional[str]
        exit_code: Optional[int]
        finish_time: Optional[datetime]
        start_time: Optional[datetime]
        state: Optional[str]


    class azure.mgmt.containerinstance.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerinstance.models.DeploymentExtensionSpec(_Model):
        name: str
        properties: Optional[DeploymentExtensionSpecProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[DeploymentExtensionSpecProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerinstance.models.DeploymentExtensionSpecProperties(_Model):
        extension_type: str
        protected_settings: Optional[Any]
        settings: Optional[Any]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                extension_type: str, 
                protected_settings: Optional[Any] = ..., 
                settings: Optional[Any] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.DnsConfiguration(_Model):
        name_servers: list[str]
        options: Optional[str]
        search_domains: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name_servers: list[str], 
                options: Optional[str] = ..., 
                search_domains: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.DnsNameLabelReusePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOREUSE = "Noreuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"
        UNSECURE = "Unsecure"


    class azure.mgmt.containerinstance.models.ElasticProfile(_Model):
        container_group_naming_policy: Optional[ElasticProfileContainerGroupNamingPolicy]
        desired_count: Optional[int]
        maintain_desired_count: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                container_group_naming_policy: Optional[ElasticProfileContainerGroupNamingPolicy] = ..., 
                desired_count: Optional[int] = ..., 
                maintain_desired_count: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ElasticProfileContainerGroupNamingPolicy(_Model):
        guid_naming_policy: Optional[ElasticProfileContainerGroupNamingPolicyGuidNamingPolicy]

        @overload
        def __init__(
                self, 
                *, 
                guid_naming_policy: Optional[ElasticProfileContainerGroupNamingPolicyGuidNamingPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ElasticProfileContainerGroupNamingPolicyGuidNamingPolicy(_Model):
        prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.EncryptionProperties(_Model):
        identity: Optional[str]
        key_name: str
        key_version: str
        vault_base_url: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                key_name: str, 
                key_version: str, 
                vault_base_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.EnvironmentVariable(_Model):
        name: str
        secure_value: Optional[str]
        secure_value_reference: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                secure_value: Optional[str] = ..., 
                secure_value_reference: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerinstance.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerinstance.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.Event(_Model):
        count: Optional[int]
        first_timestamp: Optional[datetime]
        last_timestamp: Optional[datetime]
        message: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.containerinstance.models.FileShare(_Model):
        name: Optional[str]
        properties: Optional[FileShareProperties]
        resource_group_name: Optional[str]
        storage_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[FileShareProperties] = ..., 
                resource_group_name: Optional[str] = ..., 
                storage_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.FileShareProperties(_Model):
        share_access_tier: Optional[Union[str, AzureFileShareAccessTier]]
        share_access_type: Optional[Union[str, AzureFileShareAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                share_access_tier: Optional[Union[str, AzureFileShareAccessTier]] = ..., 
                share_access_type: Optional[Union[str, AzureFileShareAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.GitRepoVolume(_Model):
        directory: Optional[str]
        repository: str
        revision: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                directory: Optional[str] = ..., 
                repository: str, 
                revision: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.GpuResource(_Model):
        count: int
        sku: Union[str, GpuSku]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                sku: Union[str, GpuSku]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.GpuSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        K80 = "K80"
        P100 = "P100"
        V100 = "V100"


    class azure.mgmt.containerinstance.models.HttpHeader(_Model):
        name: Optional[str]
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


    class azure.mgmt.containerinstance.models.IdentityAccessControl(_Model):
        access: Optional[Union[str, IdentityAccessLevel]]
        identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access: Optional[Union[str, IdentityAccessLevel]] = ..., 
                identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.IdentityAccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.containerinstance.models.IdentityAcls(_Model):
        acls: Optional[list[IdentityAccessControl]]
        default_access: Optional[Union[str, IdentityAccessLevel]]

        @overload
        def __init__(
                self, 
                *, 
                acls: Optional[list[IdentityAccessControl]] = ..., 
                default_access: Optional[Union[str, IdentityAccessLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ImageRegistryCredential(_Model):
        identity: Optional[str]
        identity_url: Optional[str]
        password: Optional[str]
        password_reference: Optional[str]
        server: str
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                identity_url: Optional[str] = ..., 
                password: Optional[str] = ..., 
                password_reference: Optional[str] = ..., 
                server: str, 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.InitContainerDefinition(_Model):
        name: str
        properties: InitContainerPropertiesDefinition

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: InitContainerPropertiesDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerinstance.models.InitContainerPropertiesDefinition(_Model):
        command: Optional[list[str]]
        environment_variables: Optional[list[EnvironmentVariable]]
        image: Optional[str]
        instance_view: Optional[InitContainerPropertiesDefinitionInstanceView]
        security_context: Optional[SecurityContextDefinition]
        volume_mounts: Optional[list[VolumeMount]]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[list[str]] = ..., 
                environment_variables: Optional[list[EnvironmentVariable]] = ..., 
                image: Optional[str] = ..., 
                security_context: Optional[SecurityContextDefinition] = ..., 
                volume_mounts: Optional[list[VolumeMount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.InitContainerPropertiesDefinitionInstanceView(_Model):
        current_state: Optional[ContainerState]
        events: Optional[list[Event]]
        previous_state: Optional[ContainerState]
        restart_count: Optional[int]


    class azure.mgmt.containerinstance.models.IpAddress(_Model):
        auto_generated_domain_name_label_scope: Optional[Union[str, DnsNameLabelReusePolicy]]
        dns_name_label: Optional[str]
        fqdn: Optional[str]
        ip: Optional[str]
        ports: list[Port]
        type: Union[str, ContainerGroupIpAddressType]

        @overload
        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, DnsNameLabelReusePolicy]] = ..., 
                dns_name_label: Optional[str] = ..., 
                ip: Optional[str] = ..., 
                ports: list[Port], 
                type: Union[str, ContainerGroupIpAddressType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.LoadBalancer(_Model):
        backend_address_pools: Optional[list[LoadBalancerBackendAddressPool]]

        @overload
        def __init__(
                self, 
                *, 
                backend_address_pools: Optional[list[LoadBalancerBackendAddressPool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.LoadBalancerBackendAddressPool(_Model):
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.LogAnalytics(_Model):
        log_type: Optional[Union[str, LogAnalyticsLogType]]
        metadata: Optional[dict[str, str]]
        workspace_id: str
        workspace_key: str
        workspace_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                log_type: Optional[Union[str, LogAnalyticsLogType]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                workspace_id: str, 
                workspace_key: str, 
                workspace_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.LogAnalyticsLogType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_INSIGHTS = "ContainerInsights"
        CONTAINER_INSTANCE_LOGS = "ContainerInstanceLogs"


    class azure.mgmt.containerinstance.models.Logs(_Model):
        content: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.containerinstance.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerinstance.models.NGroup(ProxyResource):
        id: str
        identity: Optional[NGroupIdentity]
        location: Optional[str]
        name: str
        properties: Optional[NGroupProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[NGroupIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[NGroupProperties] = ..., 
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


    class azure.mgmt.containerinstance.models.NGroupCGPropertyContainer(_Model):
        name: Optional[str]
        properties: Optional[NGroupCGPropertyContainerProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[NGroupCGPropertyContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.NGroupCGPropertyContainerProperties(_Model):
        volume_mounts: Optional[list[VolumeMount]]

        @overload
        def __init__(
                self, 
                *, 
                volume_mounts: Optional[list[VolumeMount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.NGroupCGPropertyVolume(_Model):
        azure_file: Optional[AzureFileVolume]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                azure_file: Optional[AzureFileVolume] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.NGroupContainerGroupProperties(_Model):
        containers: Optional[list[NGroupCGPropertyContainer]]
        subnet_ids: Optional[list[ContainerGroupSubnetId]]
        volumes: Optional[list[NGroupCGPropertyVolume]]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[NGroupCGPropertyContainer]] = ..., 
                subnet_ids: Optional[list[ContainerGroupSubnetId]] = ..., 
                volumes: Optional[list[NGroupCGPropertyVolume]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.NGroupIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentities]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentities]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.NGroupPatch(_Model):
        identity: Optional[NGroupIdentity]
        properties: Optional[NGroupProperties]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[NGroupIdentity] = ..., 
                properties: Optional[NGroupProperties] = ..., 
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


    class azure.mgmt.containerinstance.models.NGroupProperties(_Model):
        container_group_profiles: Optional[list[ContainerGroupProfileStub]]
        elastic_profile: Optional[ElasticProfile]
        placement_profile: Optional[PlacementProfile]
        provisioning_state: Optional[Union[str, NGroupProvisioningState]]
        update_profile: Optional[UpdateProfile]

        @overload
        def __init__(
                self, 
                *, 
                container_group_profiles: Optional[list[ContainerGroupProfileStub]] = ..., 
                elastic_profile: Optional[ElasticProfile] = ..., 
                placement_profile: Optional[PlacementProfile] = ..., 
                update_profile: Optional[UpdateProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.NGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MIGRATING = "Migrating"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerinstance.models.NGroupUpdateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        ROLLING = "Rolling"


    class azure.mgmt.containerinstance.models.NetworkProfile(_Model):
        application_gateway: Optional[ApplicationGateway]
        load_balancer: Optional[LoadBalancer]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway: Optional[ApplicationGateway] = ..., 
                load_balancer: Optional[LoadBalancer] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.containerinstance.models.Operation(_Model):
        display: OperationDisplay
        name: str
        origin: Optional[Union[str, ContainerInstanceOperationsOrigin]]
        properties: Optional[Any]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: OperationDisplay, 
                name: str, 
                origin: Optional[Union[str, ContainerInstanceOperationsOrigin]] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerinstance.models.OperationDisplay(_Model):
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


    class azure.mgmt.containerinstance.models.PlacementProfile(_Model):
        fault_domain_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                fault_domain_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.Port(_Model):
        port: int
        protocol: Optional[Union[str, ContainerGroupNetworkProtocol]]

        @overload
        def __init__(
                self, 
                *, 
                port: int, 
                protocol: Optional[Union[str, ContainerGroupNetworkProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ProxyResource(ArmResource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerinstance.models.Resource(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerinstance.models.ResourceLimits(_Model):
        cpu: Optional[float]
        gpu: Optional[GpuResource]
        memory_in_gb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[float] = ..., 
                gpu: Optional[GpuResource] = ..., 
                memory_in_gb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ResourceRequests(_Model):
        cpu: float
        gpu: Optional[GpuResource]
        memory_in_gb: float

        @overload
        def __init__(
                self, 
                *, 
                cpu: float, 
                gpu: Optional[GpuResource] = ..., 
                memory_in_gb: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.ResourceRequirements(_Model):
        limits: Optional[ResourceLimits]
        requests: ResourceRequests

        @overload
        def __init__(
                self, 
                *, 
                limits: Optional[ResourceLimits] = ..., 
                requests: ResourceRequests
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.Scheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        HTTPS = "https"


    class azure.mgmt.containerinstance.models.SecretReference(_Model):
        identity: str
        name: str
        secret_reference_uri: str

        @overload
        def __init__(
                self, 
                *, 
                identity: str, 
                name: str, 
                secret_reference_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.SecurityContextCapabilitiesDefinition(_Model):
        add: Optional[list[str]]
        drop: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                add: Optional[list[str]] = ..., 
                drop: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.SecurityContextDefinition(_Model):
        allow_privilege_escalation: Optional[bool]
        capabilities: Optional[SecurityContextCapabilitiesDefinition]
        privileged: Optional[bool]
        run_as_group: Optional[int]
        run_as_user: Optional[int]
        seccomp_profile: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_privilege_escalation: Optional[bool] = ..., 
                capabilities: Optional[SecurityContextCapabilitiesDefinition] = ..., 
                privileged: Optional[bool] = ..., 
                run_as_group: Optional[int] = ..., 
                run_as_user: Optional[int] = ..., 
                seccomp_profile: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.StandbyPoolProfileDefinition(_Model):
        fail_container_group_create_on_reuse_failure: Optional[bool]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                fail_container_group_create_on_reuse_failure: Optional[bool] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.StorageProfile(_Model):
        file_shares: Optional[list[FileShare]]

        @overload
        def __init__(
                self, 
                *, 
                file_shares: Optional[list[FileShare]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.SubnetReference(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.SystemData(_Model):
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


    class azure.mgmt.containerinstance.models.TrackedResource(ArmResource):
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


    class azure.mgmt.containerinstance.models.UpdateProfile(_Model):
        rolling_update_profile: Optional[UpdateProfileRollingUpdateProfile]
        update_mode: Optional[Union[str, NGroupUpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                rolling_update_profile: Optional[UpdateProfileRollingUpdateProfile] = ..., 
                update_mode: Optional[Union[str, NGroupUpdateMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.UpdateProfileRollingUpdateProfile(_Model):
        in_place_update: Optional[bool]
        max_batch_percent: Optional[int]
        max_unhealthy_percent: Optional[int]
        pause_time_between_batches: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                in_place_update: Optional[bool] = ..., 
                max_batch_percent: Optional[int] = ..., 
                max_unhealthy_percent: Optional[int] = ..., 
                pause_time_between_batches: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.Usage(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[UsageName]
        unit: Optional[str]


    class azure.mgmt.containerinstance.models.UsageName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.containerinstance.models.UserAssignedIdentities(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.containerinstance.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.containerinstance.models.Volume(_Model):
        azure_file: Optional[AzureFileVolume]
        empty_dir: Optional[Any]
        git_repo: Optional[GitRepoVolume]
        name: str
        secret: Optional[dict[str, str]]
        secret_reference: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                azure_file: Optional[AzureFileVolume] = ..., 
                empty_dir: Optional[Any] = ..., 
                git_repo: Optional[GitRepoVolume] = ..., 
                name: str, 
                secret: Optional[dict[str, str]] = ..., 
                secret_reference: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerinstance.models.VolumeMount(_Model):
        mount_path: str
        name: str
        read_only: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                mount_path: str, 
                name: str, 
                read_only: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.containerinstance.operations

    class azure.mgmt.containerinstance.operations.AiAgentsGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                resource: AiAgentsGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiAgentsGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                resource: AiAgentsGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiAgentsGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiAgentsGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_agents_group_name']}, api_versions_list=['2026-08-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                properties: AiAgentsGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiAgentsGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                properties: AiAgentsGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiAgentsGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiAgentsGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_agents_group_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def connect(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                **kwargs: Any
            ) -> AiAgentsGroupAccessToken: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_agents_group_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                ai_agents_group_name: str, 
                **kwargs: Any
            ) -> AiAgentsGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiAgentsGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AiAgentsGroup]: ...


    class azure.mgmt.containerinstance.operations.CGProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: ContainerGroupProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: ContainerGroupProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def get_by_revision_number(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                revision_number: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def list_all_revisions(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerGroupProfile]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: ContainerGroupProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: ContainerGroupProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...


    class azure.mgmt.containerinstance.operations.CGProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerGroupProfile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ContainerGroupProfile]: ...


    class azure.mgmt.containerinstance.operations.ContainerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: ContainerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: ContainerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @distributed_trace
        def get_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> List[str]: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ContainerGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerGroup]: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: Resource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: Resource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...


    class azure.mgmt.containerinstance.operations.ContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def attach(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ContainerAttachResponse: ...

        @overload
        def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: ContainerExecRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @overload
        def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: ContainerExecRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @overload
        def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @distributed_trace
        def list_logs(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                *, 
                tail: Optional[int] = ..., 
                timestamps: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Logs: ...


    class azure.mgmt.containerinstance.operations.LocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_cached_images(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[CachedImages]: ...

        @distributed_trace
        def list_capabilities(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Capabilities]: ...

        @distributed_trace
        def list_usage(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.containerinstance.operations.NGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: NGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                n_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> NGroup: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[NGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NGroup]: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                ngroups_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.containerinstance.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.containerinstance.operations.SubnetServiceAssociationLinkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


namespace azure.mgmt.containerinstance.types

    class azure.mgmt.containerinstance.types.AiAgentsGroup(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AiAgentsGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AiAgentsGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerinstance.types.AiAgentsGroupNetworkProfile(TypedDict, total=False):
        subnets: list[SubnetReference]


    class azure.mgmt.containerinstance.types.AiAgentsGroupProperties(TypedDict, total=False):
        key "managementResourceGroupId": str
        key "networkProfile": ForwardRef('AiAgentsGroupNetworkProfile', module='types')
        key "provisioningState": Union[str, AiAgentsGroupProvisioningState]
        management_resource_group_id: str
        network_profile: AiAgentsGroupNetworkProfile
        provisioning_state: Union[str, AiAgentsGroupProvisioningState]


    class azure.mgmt.containerinstance.types.AiAgentsGroupTagsUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.containerinstance.types.ApiEntityReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.containerinstance.types.ApplicationGateway(TypedDict, total=False):
        key "resource": str
        backendAddressPools: list[ApplicationGatewayBackendAddressPool]
        backend_address_pools: list[ApplicationGatewayBackendAddressPool]
        resource: str


    class azure.mgmt.containerinstance.types.ApplicationGatewayBackendAddressPool(TypedDict, total=False):
        key "resource": str
        resource: str


    class azure.mgmt.containerinstance.types.ArmResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerinstance.types.AzureFileVolume(TypedDict, total=False):
        key "readOnly": bool
        key "shareName": Required[str]
        key "storageAccountKey": str
        key "storageAccountKeyReference": str
        key "storageAccountName": Required[str]
        key "userAssignedIdentityClientId": str
        read_only: bool
        share_name: str
        storage_account_key: str
        storage_account_key_reference: str
        storage_account_name: str
        user_assigned_identity_client_id: str


    class azure.mgmt.containerinstance.types.ConfidentialComputeProperties(TypedDict, total=False):
        key "ccePolicy": str
        cce_policy: str


    class azure.mgmt.containerinstance.types.ConfigMap(TypedDict, total=False):
        keyValuePairs: dict[str, str]
        key_value_pairs: dict[str, str]


    class azure.mgmt.containerinstance.types.Container(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[ContainerProperties]
        name: str
        properties: ContainerProperties


    class azure.mgmt.containerinstance.types.ContainerExec(TypedDict, total=False):
        command: list[str]


    class azure.mgmt.containerinstance.types.ContainerExecRequest(TypedDict, total=False):
        key "command": str
        key "terminalSize": ForwardRef('ContainerExecRequestTerminalSize', module='types')
        command: str
        terminal_size: ContainerExecRequestTerminalSize


    class azure.mgmt.containerinstance.types.ContainerExecRequestTerminalSize(TypedDict, total=False):
        key "cols": int
        key "rows": int
        cols: int
        rows: int


    class azure.mgmt.containerinstance.types.ContainerGroup(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ContainerGroupIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[ContainerGroupProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ContainerGroupIdentity
        location: str
        name: str
        properties: ContainerGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.containerinstance.types.ContainerGroupDiagnostics(TypedDict, total=False):
        key "logAnalytics": ForwardRef('LogAnalytics', module='types')
        log_analytics: LogAnalytics


    class azure.mgmt.containerinstance.types.ContainerGroupIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentities]
        user_assigned_identities: dict[str, UserAssignedIdentities]


    class azure.mgmt.containerinstance.types.ContainerGroupProfile(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ContainerGroupProfileProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ContainerGroupProfileProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.containerinstance.types.ContainerGroupProfilePatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.containerinstance.types.ContainerGroupProfileProperties(TypedDict, total=False):
        key "confidentialComputeProperties": ForwardRef('ConfidentialComputeProperties', module='types')
        key "containers": Required[list[Container]]
        key "diagnostics": ForwardRef('ContainerGroupDiagnostics', module='types')
        key "encryptionProperties": ForwardRef('EncryptionProperties', module='types')
        key "ipAddress": ForwardRef('IpAddress', module='types')
        key "osType": Required[Union[str, OperatingSystemTypes]]
        key "priority": Union[str, ContainerGroupPriority]
        key "restartPolicy": Union[str, ContainerGroupRestartPolicy]
        key "revision": int
        key "securityContext": ForwardRef('SecurityContextDefinition', module='types')
        key "shutdownGracePeriod": str
        key "sku": Union[str, ContainerGroupSku]
        key "timeToLive": str
        key "useKrypton": bool
        confidential_compute_properties: ConfidentialComputeProperties
        containers: list[Container]
        diagnostics: ContainerGroupDiagnostics
        encryption_properties: EncryptionProperties
        extensions: list[DeploymentExtensionSpec]
        imageRegistryCredentials: list[ImageRegistryCredential]
        image_registry_credentials: list[ImageRegistryCredential]
        initContainers: list[InitContainerDefinition]
        init_containers: list[InitContainerDefinition]
        ip_address: IpAddress
        os_type: Union[str, OperatingSystemTypes]
        priority: Union[str, ContainerGroupPriority]
        registeredRevisions: list[int]
        registered_revisions: list[int]
        restart_policy: Union[str, ContainerGroupRestartPolicy]
        revision: int
        security_context: SecurityContextDefinition
        shutdown_grace_period: str
        sku: Union[str, ContainerGroupSku]
        time_to_live: str
        use_krypton: bool
        volumes: list[Volume]


    class azure.mgmt.containerinstance.types.ContainerGroupProfileReferenceDefinition(TypedDict, total=False):
        key "id": str
        key "revision": int
        id: str
        revision: int


    class azure.mgmt.containerinstance.types.ContainerGroupProfileStub(TypedDict, total=False):
        key "containerGroupProperties": ForwardRef('NGroupContainerGroupProperties', module='types')
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "resource": ForwardRef('ApiEntityReference', module='types')
        key "revision": int
        key "storageProfile": ForwardRef('StorageProfile', module='types')
        container_group_properties: NGroupContainerGroupProperties
        network_profile: NetworkProfile
        resource: ApiEntityReference
        revision: int
        storage_profile: StorageProfile


    class azure.mgmt.containerinstance.types.ContainerGroupProperties(TypedDict, total=False):
        key "confidentialComputeProperties": ForwardRef('ConfidentialComputeProperties', module='types')
        key "containerGroupProfile": ForwardRef('ContainerGroupProfileReferenceDefinition', module='types')
        key "containers": Required[list[Container]]
        key "diagnostics": ForwardRef('ContainerGroupDiagnostics', module='types')
        key "dnsConfig": ForwardRef('DnsConfiguration', module='types')
        key "encryptionProperties": ForwardRef('EncryptionProperties', module='types')
        key "identityAcls": ForwardRef('IdentityAcls', module='types')
        key "instanceView": ForwardRef('ContainerGroupPropertiesInstanceView', module='types')
        key "ipAddress": ForwardRef('IpAddress', module='types')
        key "isCreatedFromStandbyPool": bool
        key "osType": Union[str, OperatingSystemTypes]
        key "priority": Union[str, ContainerGroupPriority]
        key "provisioningState": str
        key "restartPolicy": Union[str, ContainerGroupRestartPolicy]
        key "sku": Union[str, ContainerGroupSku]
        key "standbyPoolProfile": ForwardRef('StandbyPoolProfileDefinition', module='types')
        confidential_compute_properties: ConfidentialComputeProperties
        container_group_profile: ContainerGroupProfileReferenceDefinition
        containers: list[Container]
        diagnostics: ContainerGroupDiagnostics
        dns_config: DnsConfiguration
        encryption_properties: EncryptionProperties
        extensions: list[DeploymentExtensionSpec]
        identity_acls: IdentityAcls
        imageRegistryCredentials: list[ImageRegistryCredential]
        image_registry_credentials: list[ImageRegistryCredential]
        initContainers: list[InitContainerDefinition]
        init_containers: list[InitContainerDefinition]
        instance_view: ContainerGroupPropertiesInstanceView
        ip_address: IpAddress
        is_created_from_standby_pool: bool
        os_type: Union[str, OperatingSystemTypes]
        priority: Union[str, ContainerGroupPriority]
        provisioning_state: str
        restart_policy: Union[str, ContainerGroupRestartPolicy]
        secretReferences: list[SecretReference]
        secret_references: list[SecretReference]
        sku: Union[str, ContainerGroupSku]
        standby_pool_profile: StandbyPoolProfileDefinition
        subnetIds: list[ContainerGroupSubnetId]
        subnet_ids: list[ContainerGroupSubnetId]
        volumes: list[Volume]


    class azure.mgmt.containerinstance.types.ContainerGroupPropertiesInstanceView(TypedDict, total=False):
        key "state": str
        events: list[Event]
        state: str


    class azure.mgmt.containerinstance.types.ContainerGroupSubnetId(TypedDict, total=False):
        key "id": Required[str]
        key "name": str
        id: str
        name: str


    class azure.mgmt.containerinstance.types.ContainerHttpGet(TypedDict, total=False):
        key "path": str
        key "port": Required[int]
        key "scheme": Union[str, Scheme]
        httpHeaders: list[HttpHeader]
        http_headers: list[HttpHeader]
        path: str
        port: int
        scheme: Union[str, Scheme]


    class azure.mgmt.containerinstance.types.ContainerPort(TypedDict, total=False):
        key "port": Required[int]
        key "protocol": Union[str, ContainerNetworkProtocol]
        port: int
        protocol: Union[str, ContainerNetworkProtocol]


    class azure.mgmt.containerinstance.types.ContainerProbe(TypedDict, total=False):
        key "exec": ForwardRef('ContainerExec', module='types')
        key "failureThreshold": int
        key "httpGet": ForwardRef('ContainerHttpGet', module='types')
        key "initialDelaySeconds": int
        key "periodSeconds": int
        key "successThreshold": int
        key "timeoutSeconds": int
        exec_property: ContainerExec
        failure_threshold: int
        http_get: ContainerHttpGet
        initial_delay_seconds: int
        period_seconds: int
        success_threshold: int
        timeout_seconds: int


    class azure.mgmt.containerinstance.types.ContainerProperties(TypedDict, total=False):
        key "configMap": ForwardRef('ConfigMap', module='types')
        key "image": str
        key "instanceView": ForwardRef('ContainerPropertiesInstanceView', module='types')
        key "livenessProbe": ForwardRef('ContainerProbe', module='types')
        key "readinessProbe": ForwardRef('ContainerProbe', module='types')
        key "resources": ForwardRef('ResourceRequirements', module='types')
        key "securityContext": ForwardRef('SecurityContextDefinition', module='types')
        command: list[str]
        config_map: ConfigMap
        environmentVariables: list[EnvironmentVariable]
        environment_variables: list[EnvironmentVariable]
        image: str
        instance_view: ContainerPropertiesInstanceView
        liveness_probe: ContainerProbe
        ports: list[ContainerPort]
        readiness_probe: ContainerProbe
        resources: ResourceRequirements
        security_context: SecurityContextDefinition
        volumeMounts: list[VolumeMount]
        volume_mounts: list[VolumeMount]


    class azure.mgmt.containerinstance.types.ContainerPropertiesInstanceView(TypedDict, total=False):
        key "currentState": ForwardRef('ContainerState', module='types')
        key "previousState": ForwardRef('ContainerState', module='types')
        key "restartCount": int
        current_state: ContainerState
        events: list[Event]
        previous_state: ContainerState
        restart_count: int


    class azure.mgmt.containerinstance.types.ContainerState(TypedDict, total=False):
        key "detailStatus": str
        key "exitCode": int
        key "finishTime": str
        key "startTime": str
        key "state": str
        detail_status: str
        exit_code: int
        finish_time: str
        start_time: str
        state: str


    class azure.mgmt.containerinstance.types.DeploymentExtensionSpec(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('DeploymentExtensionSpecProperties', module='types')
        name: str
        properties: DeploymentExtensionSpecProperties


    class azure.mgmt.containerinstance.types.DeploymentExtensionSpecProperties(TypedDict, total=False):
        key "extensionType": Required[str]
        key "protectedSettings": Any
        key "settings": Any
        key "version": Required[str]
        extension_type: str
        protected_settings: Any
        settings: Any
        version: str


    class azure.mgmt.containerinstance.types.DnsConfiguration(TypedDict, total=False):
        key "nameServers": Required[list[str]]
        key "options": str
        key "searchDomains": str
        name_servers: list[str]
        options: str
        search_domains: str


    class azure.mgmt.containerinstance.types.ElasticProfile(TypedDict, total=False):
        key "containerGroupNamingPolicy": ForwardRef('ElasticProfileContainerGroupNamingPolicy', module='types')
        key "desiredCount": int
        key "maintainDesiredCount": bool
        container_group_naming_policy: ElasticProfileContainerGroupNamingPolicy
        desired_count: int
        maintain_desired_count: bool


    class azure.mgmt.containerinstance.types.ElasticProfileContainerGroupNamingPolicy(TypedDict, total=False):
        key "guidNamingPolicy": ForwardRef('ElasticProfileContainerGroupNamingPolicyGuidNamingPolicy', module='types')
        guid_naming_policy: ElasticProfileContainerGroupNamingPolicyGuidNamingPolicy


    class azure.mgmt.containerinstance.types.ElasticProfileContainerGroupNamingPolicyGuidNamingPolicy(TypedDict, total=False):
        key "prefix": str
        prefix: str


    class azure.mgmt.containerinstance.types.EncryptionProperties(TypedDict, total=False):
        key "identity": str
        key "keyName": Required[str]
        key "keyVersion": Required[str]
        key "vaultBaseUrl": Required[str]
        identity: str
        key_name: str
        key_version: str
        vault_base_url: str


    class azure.mgmt.containerinstance.types.EnvironmentVariable(TypedDict, total=False):
        key "name": Required[str]
        key "secureValue": str
        key "secureValueReference": str
        key "value": str
        name: str
        secure_value: str
        secure_value_reference: str
        value: str


    class azure.mgmt.containerinstance.types.Event(TypedDict, total=False):
        key "count": int
        key "firstTimestamp": str
        key "lastTimestamp": str
        key "message": str
        key "name": str
        key "type": str
        count: int
        first_timestamp: str
        last_timestamp: str
        message: str
        name: str
        type: str


    class azure.mgmt.containerinstance.types.FileShare(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('FileShareProperties', module='types')
        key "resourceGroupName": str
        key "storageAccountName": str
        name: str
        properties: FileShareProperties
        resource_group_name: str
        storage_account_name: str


    class azure.mgmt.containerinstance.types.FileShareProperties(TypedDict, total=False):
        key "shareAccessTier": Union[str, AzureFileShareAccessTier]
        key "shareAccessType": Union[str, AzureFileShareAccessType]
        share_access_tier: Union[str, AzureFileShareAccessTier]
        share_access_type: Union[str, AzureFileShareAccessType]


    class azure.mgmt.containerinstance.types.GitRepoVolume(TypedDict, total=False):
        key "directory": str
        key "repository": Required[str]
        key "revision": str
        directory: str
        repository: str
        revision: str


    class azure.mgmt.containerinstance.types.GpuResource(TypedDict, total=False):
        key "count": Required[int]
        key "sku": Required[Union[str, GpuSku]]
        count: int
        sku: Union[str, GpuSku]


    class azure.mgmt.containerinstance.types.HttpHeader(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.containerinstance.types.IdentityAccessControl(TypedDict, total=False):
        key "access": Union[str, IdentityAccessLevel]
        key "identity": str
        access: Union[str, IdentityAccessLevel]
        identity: str


    class azure.mgmt.containerinstance.types.IdentityAcls(TypedDict, total=False):
        key "defaultAccess": Union[str, IdentityAccessLevel]
        acls: list[IdentityAccessControl]
        default_access: Union[str, IdentityAccessLevel]


    class azure.mgmt.containerinstance.types.ImageRegistryCredential(TypedDict, total=False):
        key "identity": str
        key "identityUrl": str
        key "password": str
        key "passwordReference": str
        key "server": Required[str]
        key "username": str
        identity: str
        identity_url: str
        password: str
        password_reference: str
        server: str
        username: str


    class azure.mgmt.containerinstance.types.InitContainerDefinition(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[InitContainerPropertiesDefinition]
        name: str
        properties: InitContainerPropertiesDefinition


    class azure.mgmt.containerinstance.types.InitContainerPropertiesDefinition(TypedDict, total=False):
        key "image": str
        key "instanceView": ForwardRef('InitContainerPropertiesDefinitionInstanceView', module='types')
        key "securityContext": ForwardRef('SecurityContextDefinition', module='types')
        command: list[str]
        environmentVariables: list[EnvironmentVariable]
        environment_variables: list[EnvironmentVariable]
        image: str
        instance_view: InitContainerPropertiesDefinitionInstanceView
        security_context: SecurityContextDefinition
        volumeMounts: list[VolumeMount]
        volume_mounts: list[VolumeMount]


    class azure.mgmt.containerinstance.types.InitContainerPropertiesDefinitionInstanceView(TypedDict, total=False):
        key "currentState": ForwardRef('ContainerState', module='types')
        key "previousState": ForwardRef('ContainerState', module='types')
        key "restartCount": int
        current_state: ContainerState
        events: list[Event]
        previous_state: ContainerState
        restart_count: int


    class azure.mgmt.containerinstance.types.IpAddress(TypedDict, total=False):
        key "autoGeneratedDomainNameLabelScope": Union[str, DnsNameLabelReusePolicy]
        key "dnsNameLabel": str
        key "fqdn": str
        key "ip": str
        key "ports": Required[list[Port]]
        key "type": Required[Union[str, ContainerGroupIpAddressType]]
        auto_generated_domain_name_label_scope: Union[str, DnsNameLabelReusePolicy]
        dns_name_label: str
        fqdn: str
        ip: str
        ports: list[Port]
        type: Union[str, ContainerGroupIpAddressType]


    class azure.mgmt.containerinstance.types.LoadBalancer(TypedDict, total=False):
        backendAddressPools: list[LoadBalancerBackendAddressPool]
        backend_address_pools: list[LoadBalancerBackendAddressPool]


    class azure.mgmt.containerinstance.types.LoadBalancerBackendAddressPool(TypedDict, total=False):
        key "resource": str
        resource: str


    class azure.mgmt.containerinstance.types.LogAnalytics(TypedDict, total=False):
        key "logType": Union[str, LogAnalyticsLogType]
        key "workspaceId": Required[str]
        key "workspaceKey": Required[str]
        key "workspaceResourceId": str
        log_type: Union[str, LogAnalyticsLogType]
        metadata: dict[str, str]
        workspace_id: str
        workspace_key: str
        workspace_resource_id: str


    class azure.mgmt.containerinstance.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.containerinstance.types.NGroup(ProxyResource):
        key "id": str
        key "identity": ForwardRef('NGroupIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('NGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: NGroupIdentity
        location: str
        name: str
        properties: NGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.containerinstance.types.NGroupCGPropertyContainer(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('NGroupCGPropertyContainerProperties', module='types')
        name: str
        properties: NGroupCGPropertyContainerProperties


    class azure.mgmt.containerinstance.types.NGroupCGPropertyContainerProperties(TypedDict, total=False):
        volumeMounts: list[VolumeMount]
        volume_mounts: list[VolumeMount]


    class azure.mgmt.containerinstance.types.NGroupCGPropertyVolume(TypedDict, total=False):
        key "azureFile": ForwardRef('AzureFileVolume', module='types')
        key "name": Required[str]
        azure_file: AzureFileVolume
        name: str


    class azure.mgmt.containerinstance.types.NGroupContainerGroupProperties(TypedDict, total=False):
        containers: list[NGroupCGPropertyContainer]
        subnetIds: list[ContainerGroupSubnetId]
        subnet_ids: list[ContainerGroupSubnetId]
        volumes: list[NGroupCGPropertyVolume]


    class azure.mgmt.containerinstance.types.NGroupIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentities]
        user_assigned_identities: dict[str, UserAssignedIdentities]


    class azure.mgmt.containerinstance.types.NGroupPatch(TypedDict, total=False):
        key "identity": ForwardRef('NGroupIdentity', module='types')
        key "properties": ForwardRef('NGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        identity: NGroupIdentity
        properties: NGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        zones: list[str]


    class azure.mgmt.containerinstance.types.NGroupProperties(TypedDict, total=False):
        key "elasticProfile": ForwardRef('ElasticProfile', module='types')
        key "placementProfile": ForwardRef('PlacementProfile', module='types')
        key "provisioningState": Union[str, NGroupProvisioningState]
        key "updateProfile": ForwardRef('UpdateProfile', module='types')
        containerGroupProfiles: list[ContainerGroupProfileStub]
        container_group_profiles: list[ContainerGroupProfileStub]
        elastic_profile: ElasticProfile
        placement_profile: PlacementProfile
        provisioning_state: Union[str, NGroupProvisioningState]
        update_profile: UpdateProfile


    class azure.mgmt.containerinstance.types.NetworkProfile(TypedDict, total=False):
        key "applicationGateway": ForwardRef('ApplicationGateway', module='types')
        key "loadBalancer": ForwardRef('LoadBalancer', module='types')
        application_gateway: ApplicationGateway
        load_balancer: LoadBalancer


    class azure.mgmt.containerinstance.types.PlacementProfile(TypedDict, total=False):
        key "faultDomainCount": int
        fault_domain_count: int


    class azure.mgmt.containerinstance.types.Port(TypedDict, total=False):
        key "port": Required[int]
        key "protocol": Union[str, ContainerGroupNetworkProtocol]
        port: int
        protocol: Union[str, ContainerGroupNetworkProtocol]


    class azure.mgmt.containerinstance.types.ProxyResource(ArmResource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerinstance.types.Resource(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.containerinstance.types.ResourceLimits(TypedDict, total=False):
        key "cpu": float
        key "gpu": ForwardRef('GpuResource', module='types')
        key "memoryInGB": float
        cpu: float
        gpu: GpuResource
        memory_in_gb: float


    class azure.mgmt.containerinstance.types.ResourceRequests(TypedDict, total=False):
        key "cpu": Required[float]
        key "gpu": ForwardRef('GpuResource', module='types')
        key "memoryInGB": Required[float]
        cpu: float
        gpu: GpuResource
        memory_in_gb: float


    class azure.mgmt.containerinstance.types.ResourceRequirements(TypedDict, total=False):
        key "limits": ForwardRef('ResourceLimits', module='types')
        key "requests": Required[ResourceRequests]
        limits: ResourceLimits
        requests: ResourceRequests


    class azure.mgmt.containerinstance.types.SecretReference(TypedDict, total=False):
        key "identity": Required[str]
        key "name": Required[str]
        key "secretReferenceUri": Required[str]
        identity: str
        name: str
        secret_reference_uri: str


    class azure.mgmt.containerinstance.types.SecurityContextCapabilitiesDefinition(TypedDict, total=False):
        add: list[str]
        drop: list[str]


    class azure.mgmt.containerinstance.types.SecurityContextDefinition(TypedDict, total=False):
        key "allowPrivilegeEscalation": bool
        key "capabilities": ForwardRef('SecurityContextCapabilitiesDefinition', module='types')
        key "privileged": bool
        key "runAsGroup": int
        key "runAsUser": int
        key "seccompProfile": str
        allow_privilege_escalation: bool
        capabilities: SecurityContextCapabilitiesDefinition
        privileged: bool
        run_as_group: int
        run_as_user: int
        seccomp_profile: str


    class azure.mgmt.containerinstance.types.StandbyPoolProfileDefinition(TypedDict, total=False):
        key "failContainerGroupCreateOnReuseFailure": bool
        key "id": str
        fail_container_group_create_on_reuse_failure: bool
        id: str


    class azure.mgmt.containerinstance.types.StorageProfile(TypedDict, total=False):
        fileShares: list[FileShare]
        file_shares: list[FileShare]


    class azure.mgmt.containerinstance.types.SubnetReference(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.containerinstance.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.containerinstance.types.TrackedResource(ArmResource):
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


    class azure.mgmt.containerinstance.types.UpdateProfile(TypedDict, total=False):
        key "rollingUpdateProfile": ForwardRef('UpdateProfileRollingUpdateProfile', module='types')
        key "updateMode": Union[str, NGroupUpdateMode]
        rolling_update_profile: UpdateProfileRollingUpdateProfile
        update_mode: Union[str, NGroupUpdateMode]


    class azure.mgmt.containerinstance.types.UpdateProfileRollingUpdateProfile(TypedDict, total=False):
        key "inPlaceUpdate": bool
        key "maxBatchPercent": int
        key "maxUnhealthyPercent": int
        key "pauseTimeBetweenBatches": str
        in_place_update: bool
        max_batch_percent: int
        max_unhealthy_percent: int
        pause_time_between_batches: str


    class azure.mgmt.containerinstance.types.UserAssignedIdentities(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.containerinstance.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.containerinstance.types.Volume(TypedDict, total=False):
        key "azureFile": ForwardRef('AzureFileVolume', module='types')
        key "emptyDir": Any
        key "gitRepo": ForwardRef('GitRepoVolume', module='types')
        key "name": Required[str]
        azure_file: AzureFileVolume
        empty_dir: Any
        git_repo: GitRepoVolume
        name: str
        secret: dict[str, str]
        secretReference: dict[str, str]
        secret_reference: dict[str, str]


    class azure.mgmt.containerinstance.types.VolumeMount(TypedDict, total=False):
        key "mountPath": Required[str]
        key "name": Required[str]
        key "readOnly": bool
        mount_path: str
        name: str
        read_only: bool


```