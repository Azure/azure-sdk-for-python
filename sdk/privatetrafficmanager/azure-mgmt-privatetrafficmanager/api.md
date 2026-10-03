```py
namespace azure.mgmt.privatetrafficmanager

    class azure.mgmt.privatetrafficmanager.PrivateTrafficManagerMgmtClient: implements ContextManager 
        endpoints: EndpointsOperations
        health_policies: HealthPoliciesOperations
        operations: Operations
        profile_probing_gateways: ProfileProbingGatewaysOperations
        profiles: ProfilesOperations
        sites: SitesOperations
        topology_maps: TopologyMapsOperations

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


namespace azure.mgmt.privatetrafficmanager.aio

    class azure.mgmt.privatetrafficmanager.aio.PrivateTrafficManagerMgmtClient: implements AsyncContextManager 
        endpoints: EndpointsOperations
        health_policies: HealthPoliciesOperations
        operations: Operations
        profile_probing_gateways: ProfileProbingGatewaysOperations
        profiles: ProfilesOperations
        sites: SitesOperations
        topology_maps: TopologyMapsOperations

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


namespace azure.mgmt.privatetrafficmanager.aio.operations

    class azure.mgmt.privatetrafficmanager.aio.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                resource: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                resource: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                properties: EndpointUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                properties: EndpointUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Endpoint]: ...


    class azure.mgmt.privatetrafficmanager.aio.operations.HealthPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                resource: HealthPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                resource: HealthPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                **kwargs: Any
            ) -> HealthPolicy: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HealthPolicy]: ...


    class azure.mgmt.privatetrafficmanager.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.privatetrafficmanager.aio.operations.ProfileProbingGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                resource: ProfileProbingGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfileProbingGateway]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                resource: ProfileProbingGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfileProbingGateway]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfileProbingGateway]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                properties: ProfileProbingGatewayUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfileProbingGateway]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                properties: ProfileProbingGatewayUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfileProbingGateway]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfileProbingGateway]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                **kwargs: Any
            ) -> ProfileProbingGateway: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProfileProbingGateway]: ...


    class azure.mgmt.privatetrafficmanager.aio.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                resource: PrivateTrafficManagerProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                resource: PrivateTrafficManagerProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateTrafficManagerProfile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                properties: PrivateTrafficManagerProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                properties: PrivateTrafficManagerProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateTrafficManagerProfile]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> PrivateTrafficManagerProfile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateTrafficManagerProfile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PrivateTrafficManagerProfile]: ...


    class azure.mgmt.privatetrafficmanager.aio.operations.SitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Site]: ...


    class azure.mgmt.privatetrafficmanager.aio.operations.TopologyMapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                resource: TopologyMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopologyMap]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                resource: TopologyMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopologyMap]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopologyMap]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                properties: TopologyMapPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopologyMap]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                properties: TopologyMapPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopologyMap]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopologyMap]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                **kwargs: Any
            ) -> TopologyMap: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TopologyMap]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[TopologyMap]: ...


namespace azure.mgmt.privatetrafficmanager.models

    class azure.mgmt.privatetrafficmanager.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.privatetrafficmanager.models.AdministrativeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.privatetrafficmanager.models.AlwaysServe(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.privatetrafficmanager.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.privatetrafficmanager.models.CustomHeader(_Model):
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


    class azure.mgmt.privatetrafficmanager.models.CustomTopologyMapMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.privatetrafficmanager.models.DnsConfig(_Model):
        record_type: Optional[Union[str, RecordType]]
        ttl: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                record_type: Optional[Union[str, RecordType]] = ..., 
                ttl: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.Endpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[EndpointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.EndpointProperties(_Model):
        always_serve: Optional[Union[str, AlwaysServe]]
        endpoint_status: Optional[Union[str, AdministrativeStatus]]
        health_policy_id: Optional[str]
        kind: Optional[Union[str, EndpointsKind]]
        monitoring_target: Optional[str]
        priority: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        target: str
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                always_serve: Optional[Union[str, AlwaysServe]] = ..., 
                endpoint_status: Optional[Union[str, AdministrativeStatus]] = ..., 
                health_policy_id: Optional[str] = ..., 
                kind: Optional[Union[str, EndpointsKind]] = ..., 
                monitoring_target: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                target: str, 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.EndpointUpdate(_Model):
        properties: Optional[EndpointUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EndpointUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.EndpointUpdateProperties(_Model):
        always_serve: Optional[Union[str, AlwaysServe]]
        endpoint_status: Optional[Union[str, AdministrativeStatus]]
        health_policy_id: Optional[str]
        monitoring_target: Optional[str]
        priority: Optional[int]
        target: Optional[str]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                always_serve: Optional[Union[str, AlwaysServe]] = ..., 
                endpoint_status: Optional[Union[str, AdministrativeStatus]] = ..., 
                health_policy_id: Optional[str] = ..., 
                monitoring_target: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                target: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.EndpointsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENDPOINT = "Endpoint"


    class azure.mgmt.privatetrafficmanager.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.privatetrafficmanager.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.privatetrafficmanager.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ExpectedStatusCodeRange(_Model):
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


    class azure.mgmt.privatetrafficmanager.models.HealthPolicy(ProxyResource):
        id: str
        kind: str
        name: str
        properties: Optional[HealthPolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str = ..., 
                properties: Optional[HealthPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.HealthPolicyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROBE = "Probe"


    class azure.mgmt.privatetrafficmanager.models.HealthPolicyProperties(_Model):
        probe_config: Optional[ProbeConfig]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                probe_config: Optional[ProbeConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.Operation(_Model):
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


    class azure.mgmt.privatetrafficmanager.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.privatetrafficmanager.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.privatetrafficmanager.models.PrivateTrafficManagerProfile(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ProfileProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.PrivateTrafficManagerProfileUpdate(_Model):
        properties: Optional[PrivateTrafficManagerProfileUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateTrafficManagerProfileUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.PrivateTrafficManagerProfileUpdateProperties(_Model):
        custom_topology_map_mode: Optional[Union[str, CustomTopologyMapMode]]
        dns_config: Optional[DnsConfig]
        endpoints: Optional[list[ProfileEndpoint]]
        profile_status: Optional[Union[str, ProfileStatus]]
        topology_map_id: Optional[str]
        traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]]

        @overload
        def __init__(
                self, 
                *, 
                custom_topology_map_mode: Optional[Union[str, CustomTopologyMapMode]] = ..., 
                dns_config: Optional[DnsConfig] = ..., 
                endpoints: Optional[list[ProfileEndpoint]] = ..., 
                profile_status: Optional[Union[str, ProfileStatus]] = ..., 
                topology_map_id: Optional[str] = ..., 
                traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProbeConfig(_Model):
        custom_headers: Optional[list[CustomHeader]]
        expected_status_code_ranges: Optional[list[ExpectedStatusCodeRange]]
        interval_in_seconds: Optional[int]
        path: Optional[str]
        port: Optional[int]
        protocol: Optional[Union[str, Protocol]]
        timeout_in_seconds: Optional[int]
        tolerated_number_of_failures: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                custom_headers: Optional[list[CustomHeader]] = ..., 
                expected_status_code_ranges: Optional[list[ExpectedStatusCodeRange]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                path: Optional[str] = ..., 
                port: Optional[int] = ..., 
                protocol: Optional[Union[str, Protocol]] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                tolerated_number_of_failures: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProbeHealthPolicy(HealthPolicy, discriminator='Probe'):
        id: str
        kind: Literal[HealthPolicyKind.PROBE]
        name: str
        properties: HealthPolicyProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HealthPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileEndpoint(_Model):
        always_serve: Optional[Union[str, AlwaysServe]]
        endpoint_status: Optional[Union[str, AdministrativeStatus]]
        health_policy_id: Optional[str]
        kind: Optional[Union[str, EndpointsKind]]
        monitoring_target: Optional[str]
        name: str
        priority: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        target: str
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                always_serve: Optional[Union[str, AlwaysServe]] = ..., 
                endpoint_status: Optional[Union[str, AdministrativeStatus]] = ..., 
                health_policy_id: Optional[str] = ..., 
                kind: Optional[Union[str, EndpointsKind]] = ..., 
                monitoring_target: Optional[str] = ..., 
                name: str, 
                priority: Optional[int] = ..., 
                target: str, 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileProbingGateway(ProxyResource):
        id: str
        name: str
        properties: Optional[ProfileProbingGatewayProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProfileProbingGatewayProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileProbingGatewayProperties(_Model):
        probing_gateway_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                probing_gateway_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileProbingGatewayUpdate(_Model):
        properties: Optional[ProfileProbingGatewayUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProfileProbingGatewayUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileProbingGatewayUpdateProperties(_Model):
        probing_gateway_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                probing_gateway_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileProperties(_Model):
        custom_topology_map_mode: Optional[Union[str, CustomTopologyMapMode]]
        dns_config: Optional[DnsConfig]
        endpoints: Optional[list[ProfileEndpoint]]
        profile_status: Optional[Union[str, ProfileStatus]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        topology_map_id: Optional[str]
        traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]]

        @overload
        def __init__(
                self, 
                *, 
                custom_topology_map_mode: Optional[Union[str, CustomTopologyMapMode]] = ..., 
                dns_config: Optional[DnsConfig] = ..., 
                endpoints: Optional[list[ProfileEndpoint]] = ..., 
                profile_status: Optional[Union[str, ProfileStatus]] = ..., 
                topology_map_id: Optional[str] = ..., 
                traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.ProfileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.privatetrafficmanager.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "HTTP"
        HTTPS = "HTTPS"
        TCP = "TCP"


    class azure.mgmt.privatetrafficmanager.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.privatetrafficmanager.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.models.RecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"
        AAAA = "AAAA"
        CNAME = "CNAME"


    class azure.mgmt.privatetrafficmanager.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.privatetrafficmanager.models.Site(ProxyResource):
        id: str
        name: str
        properties: Optional[SiteProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SiteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.SiteProperties(_Model):
        probing_gateway_ids: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        virtual_network_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                probing_gateway_ids: Optional[list[str]] = ..., 
                virtual_network_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.SiteUpdate(_Model):
        properties: Optional[SiteUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SiteUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.SiteUpdateProperties(_Model):
        probing_gateway_ids: Optional[list[str]]
        virtual_network_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                probing_gateway_ids: Optional[list[str]] = ..., 
                virtual_network_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.SystemData(_Model):
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


    class azure.mgmt.privatetrafficmanager.models.TopologyMap(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[TopologyMapProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[TopologyMapProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.TopologyMapInlineSite(_Model):
        name: str
        properties: Optional[SiteProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[SiteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.TopologyMapPatch(_Model):
        properties: Optional[TopologyMapPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TopologyMapPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.TopologyMapPatchProperties(_Model):
        catch_all_site_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                catch_all_site_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.TopologyMapProperties(_Model):
        catch_all_site_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sites: Optional[list[TopologyMapInlineSite]]

        @overload
        def __init__(
                self, 
                *, 
                catch_all_site_name: Optional[str] = ..., 
                sites: Optional[list[TopologyMapInlineSite]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatetrafficmanager.models.TrackedResource(Resource):
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


    class azure.mgmt.privatetrafficmanager.models.TrafficRoutingMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIORITY = "Priority"
        WEIGHTED = "Weighted"


namespace azure.mgmt.privatetrafficmanager.operations

    class azure.mgmt.privatetrafficmanager.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                resource: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                resource: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                properties: EndpointUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                properties: EndpointUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Endpoint]: ...


    class azure.mgmt.privatetrafficmanager.operations.HealthPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                resource: HealthPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                resource: HealthPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                health_policy_name: str, 
                **kwargs: Any
            ) -> HealthPolicy: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HealthPolicy]: ...


    class azure.mgmt.privatetrafficmanager.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.privatetrafficmanager.operations.ProfileProbingGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                resource: ProfileProbingGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfileProbingGateway]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                resource: ProfileProbingGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfileProbingGateway]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfileProbingGateway]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                properties: ProfileProbingGatewayUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfileProbingGateway]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                properties: ProfileProbingGatewayUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfileProbingGateway]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfileProbingGateway]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                profile_probing_gateway_name: str, 
                **kwargs: Any
            ) -> ProfileProbingGateway: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProfileProbingGateway]: ...


    class azure.mgmt.privatetrafficmanager.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                resource: PrivateTrafficManagerProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                resource: PrivateTrafficManagerProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateTrafficManagerProfile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                properties: PrivateTrafficManagerProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                properties: PrivateTrafficManagerProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateTrafficManagerProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateTrafficManagerProfile]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_traffic_manager_profile_name: str, 
                **kwargs: Any
            ) -> PrivateTrafficManagerProfile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateTrafficManagerProfile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PrivateTrafficManagerProfile]: ...


    class azure.mgmt.privatetrafficmanager.operations.SitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                resource: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                properties: SiteUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                site_name: str, 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Site]: ...


    class azure.mgmt.privatetrafficmanager.operations.TopologyMapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                resource: TopologyMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopologyMap]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                resource: TopologyMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopologyMap]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopologyMap]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                properties: TopologyMapPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopologyMap]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                properties: TopologyMapPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopologyMap]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopologyMap]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                topology_map_name: str, 
                **kwargs: Any
            ) -> TopologyMap: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TopologyMap]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[TopologyMap]: ...


namespace azure.mgmt.privatetrafficmanager.types

    class azure.mgmt.privatetrafficmanager.types.CustomHeader(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.privatetrafficmanager.types.DnsConfig(TypedDict, total=False):
        key "recordType": Union[str, RecordType]
        key "ttl": int
        recordType: Union[str, RecordType]
        ttl: int


    class azure.mgmt.privatetrafficmanager.types.Endpoint(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EndpointProperties
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.EndpointProperties(TypedDict, total=False):
        key "alwaysServe": Union[str, AlwaysServe]
        key "endpointStatus": Union[str, AdministrativeStatus]
        key "healthPolicyId": str
        key "kind": Union[str, EndpointsKind]
        key "monitoringTarget": str
        key "priority": int
        key "provisioningState": Union[str, ProvisioningState]
        key "target": Required[str]
        key "weight": int
        alwaysServe: Union[str, AlwaysServe]
        endpointStatus: Union[str, AdministrativeStatus]
        healthPolicyId: str
        kind: Union[str, EndpointsKind]
        monitoringTarget: str
        priority: int
        provisioningState: Union[str, ProvisioningState]
        target: str
        weight: int


    class azure.mgmt.privatetrafficmanager.types.EndpointUpdate(TypedDict, total=False):
        key "properties": ForwardRef('EndpointUpdateProperties', module='types')
        properties: EndpointUpdateProperties


    class azure.mgmt.privatetrafficmanager.types.EndpointUpdateProperties(TypedDict, total=False):
        key "alwaysServe": Union[str, AlwaysServe]
        key "endpointStatus": Union[str, AdministrativeStatus]
        key "healthPolicyId": str
        key "monitoringTarget": str
        key "priority": int
        key "target": str
        key "weight": int
        alwaysServe: Union[str, AlwaysServe]
        endpointStatus: Union[str, AdministrativeStatus]
        healthPolicyId: str
        monitoringTarget: str
        priority: int
        target: str
        weight: int


    class azure.mgmt.privatetrafficmanager.types.ExpectedStatusCodeRange(TypedDict, total=False):
        key "max": int
        key "min": int
        max: int
        min: int


    class azure.mgmt.privatetrafficmanager.types.HealthPolicy(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[HealthPolicyKind.PROBE]]
        key "name": str
        key "properties": ForwardRef('HealthPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[HealthPolicyKind.PROBE]
        name: str
        properties: HealthPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.HealthPolicyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROBE = "Probe"


    class azure.mgmt.privatetrafficmanager.types.HealthPolicyProperties(TypedDict, total=False):
        key "probeConfig": ForwardRef('ProbeConfig', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        probeConfig: ProbeConfig
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.privatetrafficmanager.types.PrivateTrafficManagerProfile(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProfileProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ProfileProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.privatetrafficmanager.types.PrivateTrafficManagerProfileUpdate(TypedDict, total=False):
        key "properties": ForwardRef('PrivateTrafficManagerProfileUpdateProperties', module='types')
        properties: PrivateTrafficManagerProfileUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.privatetrafficmanager.types.PrivateTrafficManagerProfileUpdateProperties(TypedDict, total=False):
        key "customTopologyMapMode": Union[str, CustomTopologyMapMode]
        key "dnsConfig": ForwardRef('DnsConfig', module='types')
        key "profileStatus": Union[str, ProfileStatus]
        key "topologyMapId": str
        key "trafficRoutingMethod": Union[str, TrafficRoutingMethod]
        customTopologyMapMode: Union[str, CustomTopologyMapMode]
        dnsConfig: DnsConfig
        endpoints: list[ProfileEndpoint]
        profileStatus: Union[str, ProfileStatus]
        topologyMapId: str
        trafficRoutingMethod: Union[str, TrafficRoutingMethod]


    class azure.mgmt.privatetrafficmanager.types.ProbeConfig(TypedDict, total=False):
        key "intervalInSeconds": int
        key "path": str
        key "port": int
        key "protocol": Union[str, Protocol]
        key "timeoutInSeconds": int
        key "toleratedNumberOfFailures": int
        customHeaders: list[CustomHeader]
        expectedStatusCodeRanges: list[ExpectedStatusCodeRange]
        intervalInSeconds: int
        path: str
        port: int
        protocol: Union[str, Protocol]
        timeoutInSeconds: int
        toleratedNumberOfFailures: int


    class azure.mgmt.privatetrafficmanager.types.ProbeHealthPolicy(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[HealthPolicyKind.PROBE]]
        key "name": str
        key "properties": ForwardRef('HealthPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[HealthPolicyKind.PROBE]
        name: str
        properties: HealthPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.ProfileEndpoint(TypedDict, total=False):
        key "alwaysServe": Union[str, AlwaysServe]
        key "endpointStatus": Union[str, AdministrativeStatus]
        key "healthPolicyId": str
        key "kind": Union[str, EndpointsKind]
        key "monitoringTarget": str
        key "name": Required[str]
        key "priority": int
        key "provisioningState": Union[str, ProvisioningState]
        key "target": Required[str]
        key "weight": int
        alwaysServe: Union[str, AlwaysServe]
        endpointStatus: Union[str, AdministrativeStatus]
        healthPolicyId: str
        kind: Union[str, EndpointsKind]
        monitoringTarget: str
        name: str
        priority: int
        provisioningState: Union[str, ProvisioningState]
        target: str
        weight: int


    class azure.mgmt.privatetrafficmanager.types.ProfileProbingGateway(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProfileProbingGatewayProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProfileProbingGatewayProperties
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.ProfileProbingGatewayProperties(TypedDict, total=False):
        key "probingGatewayId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        probingGatewayId: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.privatetrafficmanager.types.ProfileProbingGatewayUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ProfileProbingGatewayUpdateProperties', module='types')
        properties: ProfileProbingGatewayUpdateProperties


    class azure.mgmt.privatetrafficmanager.types.ProfileProbingGatewayUpdateProperties(TypedDict, total=False):
        key "probingGatewayId": str
        probingGatewayId: str


    class azure.mgmt.privatetrafficmanager.types.ProfileProperties(TypedDict, total=False):
        key "customTopologyMapMode": Union[str, CustomTopologyMapMode]
        key "dnsConfig": ForwardRef('DnsConfig', module='types')
        key "profileStatus": Union[str, ProfileStatus]
        key "provisioningState": Union[str, ProvisioningState]
        key "topologyMapId": str
        key "trafficRoutingMethod": Union[str, TrafficRoutingMethod]
        customTopologyMapMode: Union[str, CustomTopologyMapMode]
        dnsConfig: DnsConfig
        endpoints: list[ProfileEndpoint]
        profileStatus: Union[str, ProfileStatus]
        provisioningState: Union[str, ProvisioningState]
        topologyMapId: str
        trafficRoutingMethod: Union[str, TrafficRoutingMethod]


    class azure.mgmt.privatetrafficmanager.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.Site(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SiteProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SiteProperties
        systemData: SystemData
        type: str


    class azure.mgmt.privatetrafficmanager.types.SiteProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        probingGatewayIds: list[str]
        provisioningState: Union[str, ProvisioningState]
        virtualNetworkIds: list[str]


    class azure.mgmt.privatetrafficmanager.types.SiteUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SiteUpdateProperties', module='types')
        properties: SiteUpdateProperties


    class azure.mgmt.privatetrafficmanager.types.SiteUpdateProperties(TypedDict, total=False):
        probingGatewayIds: list[str]
        virtualNetworkIds: list[str]


    class azure.mgmt.privatetrafficmanager.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.privatetrafficmanager.types.TopologyMap(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('TopologyMapProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: TopologyMapProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.privatetrafficmanager.types.TopologyMapInlineSite(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('SiteProperties', module='types')
        name: str
        properties: SiteProperties


    class azure.mgmt.privatetrafficmanager.types.TopologyMapPatch(TypedDict, total=False):
        key "properties": ForwardRef('TopologyMapPatchProperties', module='types')
        properties: TopologyMapPatchProperties
        tags: dict[str, str]


    class azure.mgmt.privatetrafficmanager.types.TopologyMapPatchProperties(TypedDict, total=False):
        key "catchAllSiteName": str
        catchAllSiteName: str


    class azure.mgmt.privatetrafficmanager.types.TopologyMapProperties(TypedDict, total=False):
        key "catchAllSiteName": str
        key "provisioningState": Union[str, ProvisioningState]
        catchAllSiteName: str
        provisioningState: Union[str, ProvisioningState]
        sites: list[TopologyMapInlineSite]


    class azure.mgmt.privatetrafficmanager.types.TrackedResource(Resource):
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


```