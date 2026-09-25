```py
namespace azure.mgmt.computeworkloadmanager

    class azure.mgmt.computeworkloadmanager.WorkloadManagerClient: implements ContextManager 
        capabilities: CapabilitiesOperations
        runtime_bindings: RuntimeBindingsOperations
        runtime_links: RuntimeLinksOperations
        workload_spaces: WorkloadSpacesOperations

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


namespace azure.mgmt.computeworkloadmanager.aio

    class azure.mgmt.computeworkloadmanager.aio.WorkloadManagerClient: implements AsyncContextManager 
        capabilities: CapabilitiesOperations
        runtime_bindings: RuntimeBindingsOperations
        runtime_links: RuntimeLinksOperations
        workload_spaces: WorkloadSpacesOperations

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


namespace azure.mgmt.computeworkloadmanager.aio.operations

    class azure.mgmt.computeworkloadmanager.aio.operations.CapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Capability]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Capability]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Capability]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                properties: CapabilityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Capability]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                properties: CapabilityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Capability]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Capability]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list_by_workload_space(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Capability]: ...


    class azure.mgmt.computeworkloadmanager.aio.operations.RuntimeBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                resource: RuntimeBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                resource: RuntimeBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeBinding]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                properties: RuntimeBindingUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeBinding]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                properties: RuntimeBindingUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeBinding]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeBinding]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                **kwargs: Any
            ) -> RuntimeBinding: ...

        @distributed_trace
        def list_by_workload_space(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RuntimeBinding]: ...


    class azure.mgmt.computeworkloadmanager.aio.operations.RuntimeLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                resource: RuntimeLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                resource: RuntimeLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                properties: RuntimeLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                properties: RuntimeLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuntimeLink]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                **kwargs: Any
            ) -> RuntimeLink: ...

        @distributed_trace
        def list_by_workload_space(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RuntimeLink]: ...


    class azure.mgmt.computeworkloadmanager.aio.operations.WorkloadSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                resource: WorkloadSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                resource: WorkloadSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadSpace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                properties: WorkloadSpaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadSpace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                properties: WorkloadSpaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadSpace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadSpace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> WorkloadSpace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadSpace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[WorkloadSpace]: ...


namespace azure.mgmt.computeworkloadmanager.models

    class azure.mgmt.computeworkloadmanager.models.Capability(TrackedResource):
        id: str
        kind: Optional[Union[str, CapabilityKind]]
        location: str
        name: str
        properties: Optional[CapabilityProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, CapabilityKind]] = ..., 
                location: str, 
                properties: Optional[CapabilityProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.CapabilityKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_SANDBOX = "AgentSandbox"


    class azure.mgmt.computeworkloadmanager.models.CapabilityProperties(_Model):
        effective_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version_policy: Union[str, VersionPolicy]

        @overload
        def __init__(
                self, 
                *, 
                version_policy: Union[str, VersionPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.CapabilityUpdate(_Model):
        properties: Optional[CapabilityUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilityUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.CapabilityUpdateProperties(_Model):
        version_policy: Optional[Union[str, VersionPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                version_policy: Optional[Union[str, VersionPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.CapacityProfile(_Model):
        maximum_nodes: int
        minimum_nodes: int

        @overload
        def __init__(
                self, 
                *, 
                maximum_nodes: int, 
                minimum_nodes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.CapacityProfileUpdate(_Model):
        maximum_nodes: Optional[int]
        minimum_nodes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                maximum_nodes: Optional[int] = ..., 
                minimum_nodes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computeworkloadmanager.models.EgressMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"


    class azure.mgmt.computeworkloadmanager.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computeworkloadmanager.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computeworkloadmanager.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ExecutionIdentity(_Model):
        provisioning_mode: str
        scope: Union[str, ExecutionIdentityScope]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_mode: str, 
                scope: Union[str, ExecutionIdentityScope]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ExecutionIdentityProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REFERENCED = "Referenced"
        SERVICE_MANAGED = "ServiceManaged"


    class azure.mgmt.computeworkloadmanager.models.ExecutionIdentityScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SANDBOX_GROUP = "SandboxGroup"


    class azure.mgmt.computeworkloadmanager.models.ExecutionIdentityUpdate(_Model):
        scope: Optional[Union[str, ExecutionIdentityScope]]

        @overload
        def __init__(
                self, 
                *, 
                scope: Optional[Union[str, ExecutionIdentityScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ManagedRuntimeBindingProperties(RuntimeBindingProperties, discriminator='Managed'):
        identity_profile: RuntimeIdentityProfile
        managed_profile: ManagedRuntimeProfile
        network_profile: RuntimeNetworkProfile
        provider_resource_id: str
        provisioning_mode: Literal[RuntimeBindingProvisioningMode.MANAGED]
        provisioning_state: Union[str, ProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                identity_profile: Optional[RuntimeIdentityProfile] = ..., 
                managed_profile: ManagedRuntimeProfile, 
                network_profile: Optional[RuntimeNetworkProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ManagedRuntimeProfile(_Model):
        offering: Optional[str]
        provider: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offering: Optional[str] = ..., 
                provider: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.computeworkloadmanager.models.ReferencedExecutionIdentity(ExecutionIdentity, discriminator='Referenced'):
        provisioning_mode: Literal[ExecutionIdentityProvisioningMode.REFERENCED]
        scope: Union[str, ExecutionIdentityScope]
        user_assigned_identity_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                scope: Union[str, ExecutionIdentityScope], 
                user_assigned_identity_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ReferencedRuntimeBindingProperties(RuntimeBindingProperties, discriminator='Referenced'):
        identity_profile: RuntimeIdentityProfile
        network_profile: RuntimeNetworkProfile
        provider_resource_id: str
        provisioning_mode: Literal[RuntimeBindingProvisioningMode.REFERENCED]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                identity_profile: Optional[RuntimeIdentityProfile] = ..., 
                network_profile: Optional[RuntimeNetworkProfile] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computeworkloadmanager.models.RuntimeBinding(TrackedResource):
        id: str
        kind: Optional[Union[str, RuntimeBindingKind]]
        location: str
        name: str
        properties: Optional[RuntimeBindingProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, RuntimeBindingKind]] = ..., 
                location: str, 
                properties: Optional[RuntimeBindingProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeBindingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KUBERNETES = "Kubernetes"
        SERVERLESS_CONTAINERS = "ServerlessContainers"


    class azure.mgmt.computeworkloadmanager.models.RuntimeBindingProperties(_Model):
        identity_profile: Optional[RuntimeIdentityProfile]
        network_profile: Optional[RuntimeNetworkProfile]
        provider_resource_id: Optional[str]
        provisioning_mode: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                identity_profile: Optional[RuntimeIdentityProfile] = ..., 
                network_profile: Optional[RuntimeNetworkProfile] = ..., 
                provisioning_mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeBindingProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        REFERENCED = "Referenced"


    class azure.mgmt.computeworkloadmanager.models.RuntimeBindingUpdate(_Model):
        properties: Optional[RuntimeBindingUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuntimeBindingUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeBindingUpdateProperties(_Model):
        identity_profile: Optional[RuntimeIdentityProfileUpdate]
        network_profile: Optional[RuntimeNetworkProfile]

        @overload
        def __init__(
                self, 
                *, 
                identity_profile: Optional[RuntimeIdentityProfileUpdate] = ..., 
                network_profile: Optional[RuntimeNetworkProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeIdentityProfile(_Model):
        execution_identity: Optional[ExecutionIdentity]

        @overload
        def __init__(
                self, 
                *, 
                execution_identity: Optional[ExecutionIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeIdentityProfileUpdate(_Model):
        execution_identity: Optional[ExecutionIdentityUpdate]

        @overload
        def __init__(
                self, 
                *, 
                execution_identity: Optional[ExecutionIdentityUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeLink(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[RuntimeLinkProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[RuntimeLinkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeLinkIntegrationProfile(_Model):
        managed_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                managed_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeLinkProperties(_Model):
        capacity_profile: Optional[CapacityProfile]
        execution_binding_resource_id: Optional[str]
        integration_profile: Optional[RuntimeLinkIntegrationProfile]
        orchestrator_binding_resource_id: str
        provider_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_profile: Optional[CapacityProfile] = ..., 
                execution_binding_resource_id: Optional[str] = ..., 
                integration_profile: Optional[RuntimeLinkIntegrationProfile] = ..., 
                orchestrator_binding_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeLinkUpdate(_Model):
        properties: Optional[RuntimeLinkUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuntimeLinkUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeLinkUpdateProperties(_Model):
        capacity_profile: Optional[CapacityProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                capacity_profile: Optional[CapacityProfileUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.RuntimeNetworkProfile(_Model):
        egress_mode: Optional[Union[str, EgressMode]]
        subnet_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                egress_mode: Optional[Union[str, EgressMode]] = ..., 
                subnet_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.ServiceManagedExecutionIdentity(ExecutionIdentity, discriminator='ServiceManaged'):
        provisioning_mode: Literal[ExecutionIdentityProvisioningMode.SERVICE_MANAGED]
        scope: Union[str, ExecutionIdentityScope]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                scope: Union[str, ExecutionIdentityScope]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.SystemData(_Model):
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


    class azure.mgmt.computeworkloadmanager.models.TrackedResource(Resource):
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


    class azure.mgmt.computeworkloadmanager.models.VersionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_MANAGED = "ServiceManaged"


    class azure.mgmt.computeworkloadmanager.models.WorkloadSpace(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[WorkloadSpaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WorkloadSpaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeworkloadmanager.models.WorkloadSpaceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.computeworkloadmanager.models.WorkloadSpaceUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.computeworkloadmanager.operations

    class azure.mgmt.computeworkloadmanager.operations.CapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Capability]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Capability]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Capability]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                properties: CapabilityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Capability]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                properties: CapabilityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Capability]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Capability]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list_by_workload_space(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Capability]: ...


    class azure.mgmt.computeworkloadmanager.operations.RuntimeBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                resource: RuntimeBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                resource: RuntimeBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeBinding]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                properties: RuntimeBindingUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeBinding]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                properties: RuntimeBindingUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeBinding]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeBinding]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                binding_name: str, 
                **kwargs: Any
            ) -> RuntimeBinding: ...

        @distributed_trace
        def list_by_workload_space(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RuntimeBinding]: ...


    class azure.mgmt.computeworkloadmanager.operations.RuntimeLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                resource: RuntimeLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                resource: RuntimeLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                properties: RuntimeLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                properties: RuntimeLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuntimeLink]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                link_name: str, 
                **kwargs: Any
            ) -> RuntimeLink: ...

        @distributed_trace
        def list_by_workload_space(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RuntimeLink]: ...


    class azure.mgmt.computeworkloadmanager.operations.WorkloadSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                resource: WorkloadSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                resource: WorkloadSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadSpace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                properties: WorkloadSpaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadSpace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                properties: WorkloadSpaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadSpace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                space_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadSpace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                space_name: str, 
                **kwargs: Any
            ) -> WorkloadSpace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadSpace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[WorkloadSpace]: ...


namespace azure.mgmt.computeworkloadmanager.types

    class azure.mgmt.computeworkloadmanager.types.Capability(TrackedResource):
        key "id": str
        key "kind": Union[str, CapabilityKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CapabilityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, CapabilityKind]
        location: str
        name: str
        properties: CapabilityProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.computeworkloadmanager.types.CapabilityProperties(TypedDict, total=False):
        key "effectiveVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "versionPolicy": Required[Union[str, VersionPolicy]]
        effectiveVersion: str
        provisioningState: Union[str, ProvisioningState]
        versionPolicy: Union[str, VersionPolicy]


    class azure.mgmt.computeworkloadmanager.types.CapabilityUpdate(TypedDict, total=False):
        key "properties": ForwardRef('CapabilityUpdateProperties', module='types')
        properties: CapabilityUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.computeworkloadmanager.types.CapabilityUpdateProperties(TypedDict, total=False):
        key "versionPolicy": Union[str, VersionPolicy]
        versionPolicy: Union[str, VersionPolicy]


    class azure.mgmt.computeworkloadmanager.types.CapacityProfile(TypedDict, total=False):
        key "maximumNodes": Required[int]
        key "minimumNodes": Required[int]
        maximumNodes: int
        minimumNodes: int


    class azure.mgmt.computeworkloadmanager.types.CapacityProfileUpdate(TypedDict, total=False):
        key "maximumNodes": int
        key "minimumNodes": int
        maximumNodes: int
        minimumNodes: int


    class azure.mgmt.computeworkloadmanager.types.ExecutionIdentityProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REFERENCED = "Referenced"
        SERVICE_MANAGED = "ServiceManaged"


    class azure.mgmt.computeworkloadmanager.types.ExecutionIdentityUpdate(TypedDict, total=False):
        key "scope": Union[str, ExecutionIdentityScope]
        scope: Union[str, ExecutionIdentityScope]


    class azure.mgmt.computeworkloadmanager.types.ManagedRuntimeBindingProperties(TypedDict, total=False):
        key "identityProfile": ForwardRef('RuntimeIdentityProfile', module='types')
        key "managedProfile": Required[ManagedRuntimeProfile]
        key "networkProfile": ForwardRef('RuntimeNetworkProfile', module='types')
        key "providerResourceId": str
        key "provisioningMode": Required[Literal[RuntimeBindingProvisioningMode.MANAGED]]
        key "provisioningState": Union[str, ProvisioningState]
        identityProfile: RuntimeIdentityProfile
        managedProfile: ManagedRuntimeProfile
        networkProfile: RuntimeNetworkProfile
        providerResourceId: str
        provisioningMode: Literal[RuntimeBindingProvisioningMode.MANAGED]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.computeworkloadmanager.types.ManagedRuntimeProfile(TypedDict, total=False):
        key "offering": str
        key "provider": str
        offering: str
        provider: str


    class azure.mgmt.computeworkloadmanager.types.ReferencedExecutionIdentity(TypedDict, total=False):
        key "provisioningMode": Required[Literal[ExecutionIdentityProvisioningMode.REFERENCED]]
        key "scope": Required[Union[str, ExecutionIdentityScope]]
        key "userAssignedIdentityResourceId": Required[str]
        provisioningMode: Literal[ExecutionIdentityProvisioningMode.REFERENCED]
        scope: Union[str, ExecutionIdentityScope]
        userAssignedIdentityResourceId: str


    class azure.mgmt.computeworkloadmanager.types.ReferencedRuntimeBindingProperties(TypedDict, total=False):
        key "identityProfile": ForwardRef('RuntimeIdentityProfile', module='types')
        key "networkProfile": ForwardRef('RuntimeNetworkProfile', module='types')
        key "providerResourceId": str
        key "provisioningMode": Required[Literal[RuntimeBindingProvisioningMode.REFERENCED]]
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceId": Required[str]
        identityProfile: RuntimeIdentityProfile
        networkProfile: RuntimeNetworkProfile
        providerResourceId: str
        provisioningMode: Literal[RuntimeBindingProvisioningMode.REFERENCED]
        provisioningState: Union[str, ProvisioningState]
        resourceId: str


    class azure.mgmt.computeworkloadmanager.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.computeworkloadmanager.types.RuntimeBinding(TrackedResource):
        key "id": str
        key "kind": Union[str, RuntimeBindingKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('RuntimeBindingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, RuntimeBindingKind]
        location: str
        name: str
        properties: RuntimeBindingProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.computeworkloadmanager.types.RuntimeBindingProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        REFERENCED = "Referenced"


    class azure.mgmt.computeworkloadmanager.types.RuntimeBindingUpdate(TypedDict, total=False):
        key "properties": ForwardRef('RuntimeBindingUpdateProperties', module='types')
        properties: RuntimeBindingUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.computeworkloadmanager.types.RuntimeBindingUpdateProperties(TypedDict, total=False):
        key "identityProfile": ForwardRef('RuntimeIdentityProfileUpdate', module='types')
        key "networkProfile": ForwardRef('RuntimeNetworkProfile', module='types')
        identityProfile: RuntimeIdentityProfileUpdate
        networkProfile: RuntimeNetworkProfile


    class azure.mgmt.computeworkloadmanager.types.RuntimeIdentityProfile(TypedDict, total=False):
        key "executionIdentity": ForwardRef('ExecutionIdentity', module='types')
        executionIdentity: ExecutionIdentity


    class azure.mgmt.computeworkloadmanager.types.RuntimeIdentityProfileUpdate(TypedDict, total=False):
        key "executionIdentity": ForwardRef('ExecutionIdentityUpdate', module='types')
        executionIdentity: ExecutionIdentityUpdate


    class azure.mgmt.computeworkloadmanager.types.RuntimeLink(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('RuntimeLinkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: RuntimeLinkProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.computeworkloadmanager.types.RuntimeLinkIntegrationProfile(TypedDict, total=False):
        key "managedIdentityResourceId": str
        managedIdentityResourceId: str


    class azure.mgmt.computeworkloadmanager.types.RuntimeLinkProperties(TypedDict, total=False):
        key "capacityProfile": ForwardRef('CapacityProfile', module='types')
        key "executionBindingResourceId": str
        key "integrationProfile": ForwardRef('RuntimeLinkIntegrationProfile', module='types')
        key "orchestratorBindingResourceId": Required[str]
        key "providerResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        capacityProfile: CapacityProfile
        executionBindingResourceId: str
        integrationProfile: RuntimeLinkIntegrationProfile
        orchestratorBindingResourceId: str
        providerResourceId: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.computeworkloadmanager.types.RuntimeLinkUpdate(TypedDict, total=False):
        key "properties": ForwardRef('RuntimeLinkUpdateProperties', module='types')
        properties: RuntimeLinkUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.computeworkloadmanager.types.RuntimeLinkUpdateProperties(TypedDict, total=False):
        key "capacityProfile": ForwardRef('CapacityProfileUpdate', module='types')
        capacityProfile: CapacityProfileUpdate


    class azure.mgmt.computeworkloadmanager.types.RuntimeNetworkProfile(TypedDict, total=False):
        key "egressMode": Union[str, EgressMode]
        key "subnetResourceId": str
        egressMode: Union[str, EgressMode]
        subnetResourceId: str


    class azure.mgmt.computeworkloadmanager.types.ServiceManagedExecutionIdentity(TypedDict, total=False):
        key "provisioningMode": Required[Literal[ExecutionIdentityProvisioningMode.SERVICE_MANAGED]]
        key "scope": Required[Union[str, ExecutionIdentityScope]]
        key "userAssignedIdentityResourceId": str
        provisioningMode: Literal[ExecutionIdentityProvisioningMode.SERVICE_MANAGED]
        scope: Union[str, ExecutionIdentityScope]
        userAssignedIdentityResourceId: str


    class azure.mgmt.computeworkloadmanager.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.computeworkloadmanager.types.TrackedResource(Resource):
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


    class azure.mgmt.computeworkloadmanager.types.WorkloadSpace(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WorkloadSpaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: WorkloadSpaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.computeworkloadmanager.types.WorkloadSpaceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.computeworkloadmanager.types.WorkloadSpaceUpdate(TypedDict, total=False):
        tags: dict[str, str]


```