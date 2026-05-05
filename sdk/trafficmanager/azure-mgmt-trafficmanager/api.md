```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
        async def get_default(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> TrafficManagerGeographicHierarchy: ...


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
                top_left: Optional[List[float]] = None, 
                bot_right: Optional[List[float]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                heat_map_type: str = ..., 
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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Profile]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Profile]: ...

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
                parameters: IO, 
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
        async def create_or_update(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> UserMetricsModel: ...

        @distributed_trace_async
        async def delete(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DeleteOperationResult: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> UserMetricsModel: ...


namespace azure.mgmt.trafficmanager.models

    class azure.mgmt.trafficmanager.models.AllowedEndpointRecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        DOMAIN_NAME = "DomainName"
        I_PV4_ADDRESS = "IPv4Address"
        I_PV6_ADDRESS = "IPv6Address"


    class azure.mgmt.trafficmanager.models.AlwaysServe(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.CheckTrafficManagerRelativeDnsNameAvailabilityParameters(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.DeleteOperationResult(Model):
        operation_result: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.DnsConfig(Model):
        fqdn: str
        relative_name: str
        ttl: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                relative_name: Optional[str] = ..., 
                ttl: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.Endpoint(ProxyResource):
        always_serve: Union[str, AlwaysServe]
        custom_headers: list[EndpointPropertiesCustomHeadersItem]
        endpoint_location: str
        endpoint_monitor_status: Union[str, EndpointMonitorStatus]
        endpoint_status: Union[str, EndpointStatus]
        geo_mapping: list[str]
        id: str
        min_child_endpoints: int
        min_child_endpoints_i_pv4: int
        min_child_endpoints_i_pv6: int
        name: str
        priority: int
        subnets: list[EndpointPropertiesSubnetsItem]
        target: str
        target_resource_id: str
        type: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                always_serve: Optional[Union[str, AlwaysServe]] = ..., 
                custom_headers: Optional[List[EndpointPropertiesCustomHeadersItem]] = ..., 
                endpoint_location: Optional[str] = ..., 
                endpoint_monitor_status: Optional[Union[str, EndpointMonitorStatus]] = ..., 
                endpoint_status: Optional[Union[str, EndpointStatus]] = ..., 
                geo_mapping: Optional[List[str]] = ..., 
                id: Optional[str] = ..., 
                min_child_endpoints: Optional[int] = ..., 
                min_child_endpoints_i_pv4: Optional[int] = ..., 
                min_child_endpoints_i_pv6: Optional[int] = ..., 
                name: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                subnets: Optional[List[EndpointPropertiesSubnetsItem]] = ..., 
                target: Optional[str] = ..., 
                target_resource_id: Optional[str] = ..., 
                type: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.EndpointMonitorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHECKING_ENDPOINT = "CheckingEndpoint"
        DEGRADED = "Degraded"
        DISABLED = "Disabled"
        INACTIVE = "Inactive"
        ONLINE = "Online"
        STOPPED = "Stopped"
        UNMONITORED = "Unmonitored"


    class azure.mgmt.trafficmanager.models.EndpointPropertiesCustomHeadersItem(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.EndpointPropertiesSubnetsItem(Model):
        first: str
        last: str
        scope: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                first: Optional[str] = ..., 
                last: Optional[str] = ..., 
                scope: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.EndpointStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ENDPOINTS = "AzureEndpoints"
        EXTERNAL_ENDPOINTS = "ExternalEndpoints"
        NESTED_ENDPOINTS = "NestedEndpoints"


    class azure.mgmt.trafficmanager.models.HeatMapEndpoint(Model):
        endpoint_id: int
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_id: Optional[int] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.HeatMapModel(ProxyResource):
        end_time: datetime
        endpoints: list[HeatMapEndpoint]
        id: str
        name: str
        start_time: datetime
        traffic_flows: list[TrafficFlow]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                endpoints: Optional[List[HeatMapEndpoint]] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                traffic_flows: Optional[List[TrafficFlow]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.MonitorConfig(Model):
        custom_headers: list[MonitorConfigCustomHeadersItem]
        expected_status_code_ranges: list[MonitorConfigExpectedStatusCodeRangesItem]
        interval_in_seconds: int
        path: str
        port: int
        profile_monitor_status: Union[str, ProfileMonitorStatus]
        protocol: Union[str, MonitorProtocol]
        timeout_in_seconds: int
        tolerated_number_of_failures: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_headers: Optional[List[MonitorConfigCustomHeadersItem]] = ..., 
                expected_status_code_ranges: Optional[List[MonitorConfigExpectedStatusCodeRangesItem]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                path: Optional[str] = ..., 
                port: Optional[int] = ..., 
                profile_monitor_status: Optional[Union[str, ProfileMonitorStatus]] = ..., 
                protocol: Optional[Union[str, MonitorProtocol]] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                tolerated_number_of_failures: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.MonitorConfigCustomHeadersItem(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.MonitorConfigExpectedStatusCodeRangesItem(Model):
        max: int
        min: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max: Optional[int] = ..., 
                min: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.MonitorProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "HTTP"
        HTTPS = "HTTPS"
        TCP = "TCP"


    class azure.mgmt.trafficmanager.models.Profile(TrackedResource):
        allowed_endpoint_record_types: Union[list[str, AllowedEndpointRecordType]]
        dns_config: DnsConfig
        endpoints: list[Endpoint]
        id: str
        location: str
        max_return: int
        monitor_config: MonitorConfig
        name: str
        profile_status: Union[str, ProfileStatus]
        tags: dict[str, str]
        traffic_routing_method: Union[str, TrafficRoutingMethod]
        traffic_view_enrollment_status: Union[str, TrafficViewEnrollmentStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_endpoint_record_types: Optional[List[Union[str, AllowedEndpointRecordType]]] = ..., 
                dns_config: Optional[DnsConfig] = ..., 
                endpoints: Optional[List[Endpoint]] = ..., 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                max_return: Optional[int] = ..., 
                monitor_config: Optional[MonitorConfig] = ..., 
                name: Optional[str] = ..., 
                profile_status: Optional[Union[str, ProfileStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                traffic_routing_method: Optional[Union[str, TrafficRoutingMethod]] = ..., 
                traffic_view_enrollment_status: Optional[Union[str, TrafficViewEnrollmentStatus]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.ProfileListResult(Model):
        value: list[Profile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Profile]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.ProfileMonitorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHECKING_ENDPOINTS = "CheckingEndpoints"
        DEGRADED = "Degraded"
        DISABLED = "Disabled"
        INACTIVE = "Inactive"
        ONLINE = "Online"


    class azure.mgmt.trafficmanager.models.ProfileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.trafficmanager.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.QueryExperience(Model):
        endpoint_id: int
        latency: float
        query_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_id: int, 
                latency: Optional[float] = ..., 
                query_count: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.Region(Model):
        code: str
        name: str
        regions: list[Region]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                name: Optional[str] = ..., 
                regions: Optional[List[Region]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.TrafficFlow(Model):
        latitude: float
        longitude: float
        query_experiences: list[QueryExperience]
        source_ip: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                latitude: Optional[float] = ..., 
                longitude: Optional[float] = ..., 
                query_experiences: Optional[List[QueryExperience]] = ..., 
                source_ip: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.TrafficManagerGeographicHierarchy(ProxyResource):
        geographic_hierarchy: Region
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                geographic_hierarchy: Optional[Region] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.trafficmanager.models.TrafficManagerNameAvailability(Model):
        message: str
        name: str
        name_available: bool
        reason: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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
        key: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                key: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.trafficmanager.operations

    class azure.mgmt.trafficmanager.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...


    class azure.mgmt.trafficmanager.operations.GeographicHierarchiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_default(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> TrafficManagerGeographicHierarchy: ...


    class azure.mgmt.trafficmanager.operations.HeatMapOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                top_left: Optional[List[float]] = None, 
                bot_right: Optional[List[float]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                heat_map_type: str = ..., 
                **kwargs: Any
            ) -> HeatMapModel: ...


    class azure.mgmt.trafficmanager.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                parameters: IO, 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[DeleteOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Profile]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Profile]: ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Profile: ...


    class azure.mgmt.trafficmanager.operations.TrafficManagerUserMetricsKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def create_or_update(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> UserMetricsModel: ...

        @distributed_trace
        def delete(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DeleteOperationResult: ...

        @distributed_trace
        def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> UserMetricsModel: ...


```