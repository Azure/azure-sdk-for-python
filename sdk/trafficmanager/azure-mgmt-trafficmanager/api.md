```py
namespace azure.mgmt.trafficmanager

    class azure.mgmt.trafficmanager.TrafficManagerManagementClient: implements ContextManager 
        endpoints: EndpointsOperations
        geographic_hierarchies: GeographicHierarchiesOperations
        heat_map: HeatMapOperations
        profiles: ProfilesOperations
        traffic_manager_user_metrics_keys: TrafficManagerUserMetricsKeysOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.trafficmanager.aio

    class azure.mgmt.trafficmanager.aio.TrafficManagerManagementClient: implements AsyncContextManager 
        endpoints: EndpointsOperations
        geographic_hierarchies: GeographicHierarchiesOperations
        heat_map: HeatMapOperations
        profiles: ProfilesOperations
        traffic_manager_user_metrics_keys: TrafficManagerUserMetricsKeysOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.trafficmanager.aio.operations

    class azure.mgmt.trafficmanager.aio.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...


    class azure.mgmt.trafficmanager.aio.operations.GeographicHierarchiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_default(self, **kwargs: Any) -> TrafficManagerGeographicHierarchy: ...


    class azure.mgmt.trafficmanager.aio.operations.HeatMapOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                heat_map_type: Union[str, HeatMapType], 
                *, 
                bot_right: Optional[list[float]] = ..., 
                top_left: Optional[list[float]] = ..., 
                **kwargs: Any
            ) -> HeatMapModel: ...


    class azure.mgmt.trafficmanager.aio.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_traffic_manager_name_availability_v2(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        async def check_traffic_manager_name_availability_v2(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        async def check_traffic_manager_name_availability_v2(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        async def check_traffic_manager_relative_dns_name_availability(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        async def check_traffic_manager_relative_dns_name_availability(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        async def check_traffic_manager_relative_dns_name_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Profile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Profile]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...


    class azure.mgmt.trafficmanager.aio.operations.TrafficManagerUserMetricsKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create_or_update(self, **kwargs: Any) -> UserMetricsModel: ...

        @distributed_trace_async
        async def delete(self, **kwargs: Any) -> DeleteOperationResult: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> UserMetricsModel: ...


namespace azure.mgmt.trafficmanager.models

    class azure.mgmt.trafficmanager.models.AllowedEndpointRecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        DOMAIN_NAME = "DomainName"
        I_PV4_ADDRESS = "IPv4Address"
        I_PV6_ADDRESS = "IPv6Address"


    class azure.mgmt.trafficmanager.models.AlwaysServe(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.CheckTrafficManagerRelativeDnsNameAvailabilityParameters(_Model):
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


    class azure.mgmt.trafficmanager.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.CloudErrorBody(_Model):
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


    class azure.mgmt.trafficmanager.models.DeleteOperationResult(_Model):
        operation_result: Optional[bool]


    class azure.mgmt.trafficmanager.models.DnsConfig(_Model):
        fqdn: Optional[str]
        relative_name: Optional[str]
        ttl: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                relative_name: Optional[str] = ..., 
                ttl: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.Endpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[EndpointProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[EndpointProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.trafficmanager.models.EndpointMonitorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHECKING_ENDPOINT = "CheckingEndpoint"
        DEGRADED = "Degraded"
        DISABLED = "Disabled"
        INACTIVE = "Inactive"
        ONLINE = "Online"
        STOPPED = "Stopped"
        UNMONITORED = "Unmonitored"


    class azure.mgmt.trafficmanager.models.EndpointProperties(_Model):
        always_serve: Optional[Union[str, AlwaysServe]]
        custom_headers: Optional[list[EndpointPropertiesCustomHeadersItem]]
        endpoint_location: Optional[str]
        endpoint_monitor_status: Optional[Union[str, EndpointMonitorStatus]]
        endpoint_status: Optional[Union[str, EndpointStatus]]
        geo_mapping: Optional[list[str]]
        min_child_endpoints: Optional[int]
        min_child_endpoints_i_pv4: Optional[int]
        min_child_endpoints_i_pv6: Optional[int]
        priority: Optional[int]
        subnets: Optional[list[EndpointPropertiesSubnetsItem]]
        target: Optional[str]
        target_resource_id: Optional[str]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                always_serve: Optional[Union[str, AlwaysServe]] = ..., 
                custom_headers: Optional[list[EndpointPropertiesCustomHeadersItem]] = ..., 
                endpoint_location: Optional[str] = ..., 
                endpoint_monitor_status: Optional[Union[str, EndpointMonitorStatus]] = ..., 
                endpoint_status: Optional[Union[str, EndpointStatus]] = ..., 
                geo_mapping: Optional[list[str]] = ..., 
                min_child_endpoints: Optional[int] = ..., 
                min_child_endpoints_i_pv4: Optional[int] = ..., 
                min_child_endpoints_i_pv6: Optional[int] = ..., 
                priority: Optional[int] = ..., 
                subnets: Optional[list[EndpointPropertiesSubnetsItem]] = ..., 
                target: Optional[str] = ..., 
                target_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.EndpointPropertiesCustomHeadersItem(_Model):
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


    class azure.mgmt.trafficmanager.models.EndpointPropertiesSubnetsItem(_Model):
        first: Optional[str]
        last: Optional[str]
        scope: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                first: Optional[str] = ..., 
                last: Optional[str] = ..., 
                scope: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.EndpointStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ENDPOINTS = "AzureEndpoints"
        EXTERNAL_ENDPOINTS = "ExternalEndpoints"
        NESTED_ENDPOINTS = "NestedEndpoints"


    class azure.mgmt.trafficmanager.models.GeographicHierarchyProperties(_Model):
        geographic_hierarchy: Optional[Region]

        @overload
        def __init__(
                self, 
                *, 
                geographic_hierarchy: Optional[Region] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.HeatMapEndpoint(_Model):
        endpoint_id: Optional[int]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_id: Optional[int] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.HeatMapModel(ProxyResource):
        id: str
        name: str
        properties: Optional[HeatMapProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[HeatMapProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.trafficmanager.models.HeatMapProperties(_Model):
        end_time: Optional[datetime]
        endpoints: Optional[list[HeatMapEndpoint]]
        start_time: Optional[datetime]
        traffic_flows: Optional[list[TrafficFlow]]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                endpoints: Optional[list[HeatMapEndpoint]] = ..., 
                start_time: Optional[datetime] = ..., 
                traffic_flows: Optional[list[TrafficFlow]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.HeatMapType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.trafficmanager.models.MonitorConfig(_Model):
        custom_headers: Optional[list[MonitorConfigCustomHeadersItem]]
        expected_status_code_ranges: Optional[list[MonitorConfigExpectedStatusCodeRangesItem]]
        interval_in_seconds: Optional[int]
        path: Optional[str]
        port: Optional[int]
        profile_monitor_status: Optional[Union[str, ProfileMonitorStatus]]
        protocol: Optional[Union[str, MonitorProtocol]]
        timeout_in_seconds: Optional[int]
        tolerated_number_of_failures: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                custom_headers: Optional[list[MonitorConfigCustomHeadersItem]] = ..., 
                expected_status_code_ranges: Optional[list[MonitorConfigExpectedStatusCodeRangesItem]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                path: Optional[str] = ..., 
                port: Optional[int] = ..., 
                profile_monitor_status: Optional[Union[str, ProfileMonitorStatus]] = ..., 
                protocol: Optional[Union[str, MonitorProtocol]] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                tolerated_number_of_failures: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.MonitorConfigCustomHeadersItem(_Model):
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


    class azure.mgmt.trafficmanager.models.MonitorConfigExpectedStatusCodeRangesItem(_Model):
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


    class azure.mgmt.trafficmanager.models.MonitorProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "HTTP"
        HTTPS = "HTTPS"
        TCP = "TCP"


    class azure.mgmt.trafficmanager.models.Profile(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ProfileProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.trafficmanager.models.ProfileMonitorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHECKING_ENDPOINTS = "CheckingEndpoints"
        DEGRADED = "Degraded"
        DISABLED = "Disabled"
        INACTIVE = "Inactive"
        ONLINE = "Online"


    class azure.mgmt.trafficmanager.models.ProfileProperties(_Model):
        allowed_endpoint_record_types: Optional[list[Union[str, AllowedEndpointRecordType]]]
        dns_config: Optional[DnsConfig]
        endpoints: Optional[list[Endpoint]]
        max_return: Optional[int]
        monitor_config: Optional[MonitorConfig]
        profile_status: Optional[Union[str, ProfileStatus]]
        record_type: Optional[Union[str, RecordType]]
        traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]]
        traffic_view_enrollment_status: Optional[Union[str, TrafficViewEnrollmentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_endpoint_record_types: Optional[list[Union[str, AllowedEndpointRecordType]]] = ..., 
                dns_config: Optional[DnsConfig] = ..., 
                endpoints: Optional[list[Endpoint]] = ..., 
                max_return: Optional[int] = ..., 
                monitor_config: Optional[MonitorConfig] = ..., 
                profile_status: Optional[Union[str, ProfileStatus]] = ..., 
                record_type: Optional[Union[str, RecordType]] = ..., 
                traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]] = ..., 
                traffic_view_enrollment_status: Optional[Union[str, TrafficViewEnrollmentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.ProfileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.QueryExperience(_Model):
        endpoint_id: int
        latency: Optional[float]
        query_count: int

        @overload
        def __init__(
                self, 
                *, 
                endpoint_id: int, 
                latency: Optional[float] = ..., 
                query_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.RecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"
        AAAA = "AAAA"
        CNAME = "CNAME"


    class azure.mgmt.trafficmanager.models.Region(_Model):
        code: Optional[str]
        name: Optional[str]
        regions: Optional[list[Region]]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                name: Optional[str] = ..., 
                regions: Optional[list[Region]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.TrackedResource(Resource):
        id: str
        location: Optional[str]
        name: str
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.TrafficFlow(_Model):
        latitude: Optional[float]
        longitude: Optional[float]
        query_experiences: Optional[list[QueryExperience]]
        source_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                latitude: Optional[float] = ..., 
                longitude: Optional[float] = ..., 
                query_experiences: Optional[list[QueryExperience]] = ..., 
                source_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.TrafficManagerGeographicHierarchy(ProxyResource):
        id: str
        name: str
        properties: Optional[GeographicHierarchyProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[GeographicHierarchyProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.trafficmanager.models.TrafficManagerNameAvailability(_Model):
        message: Optional[str]
        name: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.trafficmanager.models.TrafficRoutingMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEOGRAPHIC = "Geographic"
        MULTI_VALUE = "MultiValue"
        PERFORMANCE = "Performance"
        PRIORITY = "Priority"
        SUBNET = "Subnet"
        WEIGHTED = "Weighted"


    class azure.mgmt.trafficmanager.models.TrafficViewEnrollmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.UserMetricsModel(ProxyResource):
        id: str
        name: str
        properties: Optional[UserMetricsProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[UserMetricsProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.trafficmanager.models.UserMetricsProperties(_Model):
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.trafficmanager.operations

    class azure.mgmt.trafficmanager.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...


    class azure.mgmt.trafficmanager.operations.GeographicHierarchiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_default(self, **kwargs: Any) -> TrafficManagerGeographicHierarchy: ...


    class azure.mgmt.trafficmanager.operations.HeatMapOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                heat_map_type: Union[str, HeatMapType], 
                *, 
                bot_right: Optional[list[float]] = ..., 
                top_left: Optional[list[float]] = ..., 
                **kwargs: Any
            ) -> HeatMapModel: ...


    class azure.mgmt.trafficmanager.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_traffic_manager_name_availability_v2(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        def check_traffic_manager_name_availability_v2(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        def check_traffic_manager_name_availability_v2(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        def check_traffic_manager_relative_dns_name_availability(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        def check_traffic_manager_relative_dns_name_availability(
                self, 
                parameters: CheckTrafficManagerRelativeDnsNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        def check_traffic_manager_relative_dns_name_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficManagerNameAvailability: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Profile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Profile]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...


    class azure.mgmt.trafficmanager.operations.TrafficManagerUserMetricsKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create_or_update(self, **kwargs: Any) -> UserMetricsModel: ...

        @distributed_trace
        def delete(self, **kwargs: Any) -> DeleteOperationResult: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> UserMetricsModel: ...


namespace azure.mgmt.trafficmanager.types

    class azure.mgmt.trafficmanager.types.CheckTrafficManagerRelativeDnsNameAvailabilityParameters(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.trafficmanager.types.DnsConfig(TypedDict, total=False):
        key "fqdn": str
        key "relativeName": str
        key "ttl": int
        fqdn: str
        relativeName: str
        ttl: int


    class azure.mgmt.trafficmanager.types.Endpoint(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EndpointProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: EndpointProperties
        type: str


    class azure.mgmt.trafficmanager.types.EndpointProperties(TypedDict, total=False):
        key "alwaysServe": Union[str, AlwaysServe]
        key "endpointLocation": str
        key "endpointMonitorStatus": Union[str, EndpointMonitorStatus]
        key "endpointStatus": Union[str, EndpointStatus]
        key "minChildEndpoints": int
        key "minChildEndpointsIPv4": int
        key "minChildEndpointsIPv6": int
        key "priority": int
        key "target": str
        key "targetResourceId": str
        key "weight": int
        alwaysServe: Union[str, AlwaysServe]
        customHeaders: list[EndpointPropertiesCustomHeadersItem]
        endpointLocation: str
        endpointMonitorStatus: Union[str, EndpointMonitorStatus]
        endpointStatus: Union[str, EndpointStatus]
        geoMapping: list[str]
        minChildEndpoints: int
        minChildEndpointsIPv4: int
        minChildEndpointsIPv6: int
        priority: int
        subnets: list[EndpointPropertiesSubnetsItem]
        target: str
        targetResourceId: str
        weight: int


    class azure.mgmt.trafficmanager.types.EndpointPropertiesCustomHeadersItem(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.trafficmanager.types.EndpointPropertiesSubnetsItem(TypedDict, total=False):
        key "first": str
        key "last": str
        key "scope": int
        first: str
        last: str
        scope: int


    class azure.mgmt.trafficmanager.types.MonitorConfig(TypedDict, total=False):
        key "intervalInSeconds": int
        key "path": str
        key "port": int
        key "profileMonitorStatus": Union[str, ProfileMonitorStatus]
        key "protocol": Union[str, MonitorProtocol]
        key "timeoutInSeconds": int
        key "toleratedNumberOfFailures": int
        customHeaders: list[MonitorConfigCustomHeadersItem]
        expectedStatusCodeRanges: list[MonitorConfigExpectedStatusCodeRangesItem]
        intervalInSeconds: int
        path: str
        port: int
        profileMonitorStatus: Union[str, ProfileMonitorStatus]
        protocol: Union[str, MonitorProtocol]
        timeoutInSeconds: int
        toleratedNumberOfFailures: int


    class azure.mgmt.trafficmanager.types.MonitorConfigCustomHeadersItem(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.trafficmanager.types.MonitorConfigExpectedStatusCodeRangesItem(TypedDict, total=False):
        key "max": int
        key "min": int
        max: int
        min: int


    class azure.mgmt.trafficmanager.types.Profile(TrackedResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ProfileProperties', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ProfileProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.trafficmanager.types.ProfileProperties(TypedDict, total=False):
        key "dnsConfig": ForwardRef('DnsConfig', module='types')
        key "maxReturn": int
        key "monitorConfig": ForwardRef('MonitorConfig', module='types')
        key "profileStatus": Union[str, ProfileStatus]
        key "recordType": Union[str, RecordType]
        key "trafficRoutingMethod": Union[str, TrafficRoutingMethod]
        key "trafficViewEnrollmentStatus": Union[str, TrafficViewEnrollmentStatus]
        allowedEndpointRecordTypes: list[Union[str, AllowedEndpointRecordType]]
        dnsConfig: DnsConfig
        endpoints: list[Endpoint]
        maxReturn: int
        monitorConfig: MonitorConfig
        profileStatus: Union[str, ProfileStatus]
        recordType: Union[str, RecordType]
        trafficRoutingMethod: Union[str, TrafficRoutingMethod]
        trafficViewEnrollmentStatus: Union[str, TrafficViewEnrollmentStatus]


    class azure.mgmt.trafficmanager.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.trafficmanager.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.trafficmanager.types.TrackedResource(Resource):
        key "id": str
        key "location": str
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str


```