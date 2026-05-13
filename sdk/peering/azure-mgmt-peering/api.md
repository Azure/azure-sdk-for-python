```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.peering

    class azure.mgmt.peering.PeeringManagementClient(_PeeringManagementClientOperationsMixin): implements ContextManager 
        cdn_peering_prefixes: CdnPeeringPrefixesOperations
        connection_monitor_tests: ConnectionMonitorTestsOperations
        legacy_peerings: LegacyPeeringsOperations
        looking_glass: LookingGlassOperations
        operations: Operations
        peer_asns: PeerAsnsOperations
        peering_locations: PeeringLocationsOperations
        peering_service_countries: PeeringServiceCountriesOperations
        peering_service_locations: PeeringServiceLocationsOperations
        peering_service_providers: PeeringServiceProvidersOperations
        peering_services: PeeringServicesOperations
        peerings: PeeringsOperations
        prefixes: PrefixesOperations
        received_routes: ReceivedRoutesOperations
        registered_asns: RegisteredAsnsOperations
        registered_prefixes: RegisteredPrefixesOperations
        rp_unbilled_prefixes: RpUnbilledPrefixesOperations

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

        @overload
        def check_service_provider_availability(
                self, 
                check_service_provider_availability_input: CheckServiceProviderAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[str, Enum0]: ...

        @overload
        def check_service_provider_availability(
                self, 
                check_service_provider_availability_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[str, Enum0]: ...

        @overload
        def check_service_provider_availability(
                self, 
                check_service_provider_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[str, Enum0]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.peering.aio

    class azure.mgmt.peering.aio.PeeringManagementClient(_PeeringManagementClientOperationsMixin): implements AsyncContextManager 
        cdn_peering_prefixes: CdnPeeringPrefixesOperations
        connection_monitor_tests: ConnectionMonitorTestsOperations
        legacy_peerings: LegacyPeeringsOperations
        looking_glass: LookingGlassOperations
        operations: Operations
        peer_asns: PeerAsnsOperations
        peering_locations: PeeringLocationsOperations
        peering_service_countries: PeeringServiceCountriesOperations
        peering_service_locations: PeeringServiceLocationsOperations
        peering_service_providers: PeeringServiceProvidersOperations
        peering_services: PeeringServicesOperations
        peerings: PeeringsOperations
        prefixes: PrefixesOperations
        received_routes: ReceivedRoutesOperations
        registered_asns: RegisteredAsnsOperations
        registered_prefixes: RegisteredPrefixesOperations
        rp_unbilled_prefixes: RpUnbilledPrefixesOperations

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

        @overload
        async def check_service_provider_availability(
                self, 
                check_service_provider_availability_input: CheckServiceProviderAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[str, Enum0]: ...

        @overload
        async def check_service_provider_availability(
                self, 
                check_service_provider_availability_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[str, Enum0]: ...

        @overload
        async def check_service_provider_availability(
                self, 
                check_service_provider_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[str, Enum0]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.peering.aio.operations

    class azure.mgmt.peering.aio.operations.CdnPeeringPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                peering_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CdnPeeringPrefix]: ...


    class azure.mgmt.peering.aio.operations.ConnectionMonitorTestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                connection_monitor_test: ConnectionMonitorTest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                connection_monitor_test: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                connection_monitor_test: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @distributed_trace
        def list_by_peering_service(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectionMonitorTest]: ...


    class azure.mgmt.peering.aio.operations.LegacyPeeringsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                asn: Optional[int] = ..., 
                direct_peering_type: Optional[Union[str, DirectPeeringType]] = ..., 
                kind: Union[str, LegacyPeeringsKind], 
                peering_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Peering]: ...


    class azure.mgmt.peering.aio.operations.LookingGlassOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def invoke(
                self, 
                *, 
                command: Union[str, LookingGlassCommand], 
                destination_ip: str, 
                source_location: str, 
                source_type: Union[str, LookingGlassSourceType], 
                **kwargs: Any
            ) -> LookingGlassOutput: ...


    class azure.mgmt.peering.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.peering.aio.operations.PeerAsnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                peer_asn_name: str, 
                peer_asn: PeerAsn, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeerAsn: ...

        @overload
        async def create_or_update(
                self, 
                peer_asn_name: str, 
                peer_asn: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeerAsn: ...

        @overload
        async def create_or_update(
                self, 
                peer_asn_name: str, 
                peer_asn: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeerAsn: ...

        @distributed_trace_async
        async def delete(
                self, 
                peer_asn_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                peer_asn_name: str, 
                **kwargs: Any
            ) -> PeerAsn: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PeerAsn]: ...


    class azure.mgmt.peering.aio.operations.PeeringLocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                direct_peering_type: Optional[Union[str, PeeringLocationsDirectPeeringType]] = ..., 
                kind: Union[str, PeeringLocationsKind], 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringLocation]: ...


    class azure.mgmt.peering.aio.operations.PeeringServiceCountriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[PeeringServiceCountry]: ...


    class azure.mgmt.peering.aio.operations.PeeringServiceLocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                country: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringServiceLocation]: ...


    class azure.mgmt.peering.aio.operations.PeeringServiceProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[PeeringServiceProvider]: ...


    class azure.mgmt.peering.aio.operations.PeeringServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                peering_service: PeeringService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                peering_service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                peering_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                **kwargs: Any
            ) -> PeeringService: ...

        @distributed_trace_async
        async def initialize_connection_monitor(self, **kwargs: Any) -> None: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PeeringService]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                tags: ResourceTags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...


    class azure.mgmt.peering.aio.operations.PeeringsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                peering: Peering, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                peering: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                peering: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> Peering: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Peering]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Peering]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                tags: ResourceTags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...


    class azure.mgmt.peering.aio.operations.PrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                peering_service_prefix: PeeringServicePrefix, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                peering_service_prefix: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                peering_service_prefix: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @distributed_trace
        def list_by_peering_service(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringServicePrefix]: ...


    class azure.mgmt.peering.aio.operations.ReceivedRoutesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_peering(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                *, 
                as_path: Optional[str] = ..., 
                origin_as_validation_state: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                rpki_validation_state: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringReceivedRoute]: ...


    class azure.mgmt.peering.aio.operations.RegisteredAsnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                registered_asn: PeeringRegisteredAsn, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                registered_asn: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                registered_asn: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @distributed_trace
        def list_by_peering(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringRegisteredAsn]: ...


    class azure.mgmt.peering.aio.operations.RegisteredPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                registered_prefix: PeeringRegisteredPrefix, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                registered_prefix: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                registered_prefix: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @distributed_trace
        def list_by_peering(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PeeringRegisteredPrefix]: ...

        @distributed_trace_async
        async def validate(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...


    class azure.mgmt.peering.aio.operations.RpUnbilledPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                *, 
                consolidate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RpUnbilledPrefix]: ...


namespace azure.mgmt.peering.models

    class azure.mgmt.peering.models.BgpSession(_Model):
        max_prefixes_advertised_v4: Optional[int]
        max_prefixes_advertised_v6: Optional[int]
        md5_authentication_key: Optional[str]
        microsoft_session_i_pv4_address: Optional[str]
        microsoft_session_i_pv6_address: Optional[str]
        peer_session_i_pv4_address: Optional[str]
        peer_session_i_pv6_address: Optional[str]
        session_prefix_v4: Optional[str]
        session_prefix_v6: Optional[str]
        session_state_v4: Optional[Union[str, SessionStateV4]]
        session_state_v6: Optional[Union[str, SessionStateV6]]

        @overload
        def __init__(
                self, 
                *, 
                max_prefixes_advertised_v4: Optional[int] = ..., 
                max_prefixes_advertised_v6: Optional[int] = ..., 
                md5_authentication_key: Optional[str] = ..., 
                microsoft_session_i_pv4_address: Optional[str] = ..., 
                microsoft_session_i_pv6_address: Optional[str] = ..., 
                peer_session_i_pv4_address: Optional[str] = ..., 
                peer_session_i_pv6_address: Optional[str] = ..., 
                session_prefix_v4: Optional[str] = ..., 
                session_prefix_v6: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.CdnPeeringPrefix(Resource):
        id: str
        name: str
        properties: Optional[CdnPeeringPrefixProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CdnPeeringPrefixProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.CdnPeeringPrefixProperties(_Model):
        azure_region: Optional[str]
        azure_service: Optional[str]
        bgp_community: Optional[str]
        is_primary_region: Optional[bool]
        prefix: Optional[str]


    class azure.mgmt.peering.models.CheckServiceProviderAvailabilityInput(_Model):
        peering_service_location: Optional[str]
        peering_service_provider: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                peering_service_location: Optional[str] = ..., 
                peering_service_provider: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.Command(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BGP_ROUTE = "BgpRoute"
        PING = "Ping"
        TRACEROUTE = "Traceroute"


    class azure.mgmt.peering.models.ConnectionMonitorTest(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectionMonitorTestProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectionMonitorTestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.ConnectionMonitorTestProperties(_Model):
        destination: Optional[str]
        destination_port: Optional[int]
        is_test_successful: Optional[bool]
        path: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_agent: Optional[str]
        test_frequency_in_sec: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[str] = ..., 
                destination_port: Optional[int] = ..., 
                source_agent: Optional[str] = ..., 
                test_frequency_in_sec: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.ConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        APPROVED = "Approved"
        EXTERNAL_BLOCKER = "ExternalBlocker"
        NONE = "None"
        PENDING_APPROVAL = "PendingApproval"
        PROVISIONING_COMPLETED = "ProvisioningCompleted"
        PROVISIONING_FAILED = "ProvisioningFailed"
        PROVISIONING_STARTED = "ProvisioningStarted"
        TYPE_CHANGE_IN_PROGRESS = "TypeChangeInProgress"
        TYPE_CHANGE_REQUESTED = "TypeChangeRequested"
        VALIDATING = "Validating"


    class azure.mgmt.peering.models.ConnectivityProbe(_Model):
        azure_region: Optional[str]
        endpoint: Optional[str]
        prefixes_to_accesslist: Optional[list[str]]
        protocol: Optional[Union[str, Protocol]]

        @overload
        def __init__(
                self, 
                *, 
                azure_region: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                protocol: Optional[Union[str, Protocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.ContactDetail(_Model):
        email: Optional[str]
        phone: Optional[str]
        role: Optional[Union[str, Role]]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                phone: Optional[str] = ..., 
                role: Optional[Union[str, Role]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.peering.models.DirectConnection(_Model):
        bandwidth_in_mbps: Optional[int]
        bgp_session: Optional[BgpSession]
        connection_identifier: Optional[str]
        connection_state: Optional[Union[str, ConnectionState]]
        error_message: Optional[str]
        microsoft_tracking_id: Optional[str]
        peering_db_facility_id: Optional[int]
        provisioned_bandwidth_in_mbps: Optional[int]
        session_address_provider: Optional[Union[str, SessionAddressProvider]]
        use_for_peering_service: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_in_mbps: Optional[int] = ..., 
                bgp_session: Optional[BgpSession] = ..., 
                connection_identifier: Optional[str] = ..., 
                peering_db_facility_id: Optional[int] = ..., 
                session_address_provider: Optional[Union[str, SessionAddressProvider]] = ..., 
                use_for_peering_service: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.DirectPeeringFacility(_Model):
        address: Optional[str]
        direct_peering_type: Optional[Union[str, DirectPeeringType]]
        peering_db_facility_id: Optional[int]
        peering_db_facility_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                direct_peering_type: Optional[Union[str, DirectPeeringType]] = ..., 
                peering_db_facility_id: Optional[int] = ..., 
                peering_db_facility_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.DirectPeeringType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CDN = "Cdn"
        EDGE = "Edge"
        EDGE_ZONE_FOR_OPERATORS = "EdgeZoneForOperators"
        INTERNAL = "Internal"
        IX = "Ix"
        IX_RS = "IxRs"
        PEER_PROP = "PeerProp"
        TRANSIT = "Transit"
        VOICE = "Voice"


    class azure.mgmt.peering.models.Enum0(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.peering.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.peering.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.peering.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.ExchangeConnection(_Model):
        bgp_session: Optional[BgpSession]
        connection_identifier: Optional[str]
        connection_state: Optional[Union[str, ConnectionState]]
        error_message: Optional[str]
        peering_db_facility_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bgp_session: Optional[BgpSession] = ..., 
                connection_identifier: Optional[str] = ..., 
                peering_db_facility_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.ExchangePeeringFacility(_Model):
        bandwidth_in_mbps: Optional[int]
        exchange_name: Optional[str]
        facility_i_pv4_prefix: Optional[str]
        facility_i_pv6_prefix: Optional[str]
        microsoft_i_pv4_address: Optional[str]
        microsoft_i_pv6_address: Optional[str]
        peering_db_facility_id: Optional[int]
        peering_db_facility_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_in_mbps: Optional[int] = ..., 
                exchange_name: Optional[str] = ..., 
                facility_i_pv4_prefix: Optional[str] = ..., 
                facility_i_pv6_prefix: Optional[str] = ..., 
                microsoft_i_pv4_address: Optional[str] = ..., 
                microsoft_i_pv6_address: Optional[str] = ..., 
                peering_db_facility_id: Optional[int] = ..., 
                peering_db_facility_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.Family(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        EXCHANGE = "Exchange"


    class azure.mgmt.peering.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        EXCHANGE = "Exchange"


    class azure.mgmt.peering.models.LearnedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        VIA_SERVICE_PROVIDER = "ViaServiceProvider"
        VIA_SESSION = "ViaSession"


    class azure.mgmt.peering.models.LegacyPeeringsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        EXCHANGE = "Exchange"


    class azure.mgmt.peering.models.LogAnalyticsWorkspaceProperties(_Model):
        connected_agents: Optional[list[str]]
        key: Optional[str]
        workspace_id: Optional[str]


    class azure.mgmt.peering.models.LookingGlassCommand(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BGP_ROUTE = "BgpRoute"
        PING = "Ping"
        TRACEROUTE = "Traceroute"


    class azure.mgmt.peering.models.LookingGlassOutput(_Model):
        command: Optional[Union[str, Command]]
        output: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[Union[str, Command]] = ..., 
                output: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.LookingGlassSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_REGION = "AzureRegion"
        EDGE_SITE = "EdgeSite"


    class azure.mgmt.peering.models.MetricDimension(_Model):
        display_name: Optional[str]
        name: Optional[str]


    class azure.mgmt.peering.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[MetricDimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        name: Optional[str]
        supported_time_grain_types: Optional[list[str]]
        unit: Optional[str]


    class azure.mgmt.peering.models.Operation(_Model):
        display: Optional[OperationDisplayInfo]
        is_data_action: Optional[bool]
        name: Optional[str]
        properties: Optional[OperationProperties]


    class azure.mgmt.peering.models.OperationDisplayInfo(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.peering.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]


    class azure.mgmt.peering.models.PeerAsn(ProxyResource):
        id: str
        name: str
        properties: Optional[PeerAsnProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PeerAsnProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeerAsnProperties(_Model):
        error_message: Optional[str]
        peer_asn: Optional[int]
        peer_contact_detail: Optional[list[ContactDetail]]
        peer_name: Optional[str]
        validation_state: Optional[Union[str, ValidationState]]

        @overload
        def __init__(
                self, 
                *, 
                peer_asn: Optional[int] = ..., 
                peer_contact_detail: Optional[list[ContactDetail]] = ..., 
                peer_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.Peering(TrackedResource):
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: Optional[PeeringProperties]
        sku: PeeringSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Union[str, Kind], 
                location: str, 
                properties: Optional[PeeringProperties] = ..., 
                sku: PeeringSku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringBandwidthOffer(_Model):
        offer_name: Optional[str]
        value_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                offer_name: Optional[str] = ..., 
                value_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringLocation(Resource):
        id: str
        kind: Optional[Union[str, Kind]]
        name: str
        properties: Optional[PeeringLocationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, Kind]] = ..., 
                properties: Optional[PeeringLocationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringLocationProperties(_Model):
        azure_region: Optional[str]
        country: Optional[str]
        direct: Optional[PeeringLocationPropertiesDirect]
        exchange: Optional[PeeringLocationPropertiesExchange]
        peering_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_region: Optional[str] = ..., 
                country: Optional[str] = ..., 
                direct: Optional[PeeringLocationPropertiesDirect] = ..., 
                exchange: Optional[PeeringLocationPropertiesExchange] = ..., 
                peering_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringLocationPropertiesDirect(_Model):
        bandwidth_offers: Optional[list[PeeringBandwidthOffer]]
        peering_facilities: Optional[list[DirectPeeringFacility]]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_offers: Optional[list[PeeringBandwidthOffer]] = ..., 
                peering_facilities: Optional[list[DirectPeeringFacility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringLocationPropertiesExchange(_Model):
        peering_facilities: Optional[list[ExchangePeeringFacility]]

        @overload
        def __init__(
                self, 
                *, 
                peering_facilities: Optional[list[ExchangePeeringFacility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringLocationsDirectPeeringType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CDN = "Cdn"
        EDGE = "Edge"
        EDGE_ZONE_FOR_OPERATORS = "EdgeZoneForOperators"
        INTERNAL = "Internal"
        IX = "Ix"
        IX_RS = "IxRs"
        PEER_PROP = "PeerProp"
        TRANSIT = "Transit"
        VOICE = "Voice"


    class azure.mgmt.peering.models.PeeringLocationsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        EXCHANGE = "Exchange"


    class azure.mgmt.peering.models.PeeringProperties(_Model):
        connectivity_probes: Optional[list[ConnectivityProbe]]
        direct: Optional[PeeringPropertiesDirect]
        exchange: Optional[PeeringPropertiesExchange]
        peering_location: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                connectivity_probes: Optional[list[ConnectivityProbe]] = ..., 
                direct: Optional[PeeringPropertiesDirect] = ..., 
                exchange: Optional[PeeringPropertiesExchange] = ..., 
                peering_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringPropertiesDirect(_Model):
        connections: Optional[list[DirectConnection]]
        direct_peering_type: Optional[Union[str, DirectPeeringType]]
        peer_asn: Optional[SubResource]
        use_for_peering_service: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                connections: Optional[list[DirectConnection]] = ..., 
                direct_peering_type: Optional[Union[str, DirectPeeringType]] = ..., 
                peer_asn: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringPropertiesExchange(_Model):
        connections: Optional[list[ExchangeConnection]]
        peer_asn: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                connections: Optional[list[ExchangeConnection]] = ..., 
                peer_asn: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringReceivedRoute(_Model):
        as_path: Optional[str]
        next_hop: Optional[str]
        origin_as_validation_state: Optional[str]
        prefix: Optional[str]
        received_timestamp: Optional[str]
        rpki_validation_state: Optional[str]
        trust_anchor: Optional[str]


    class azure.mgmt.peering.models.PeeringRegisteredAsn(ProxyResource):
        id: str
        name: str
        properties: Optional[PeeringRegisteredAsnProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PeeringRegisteredAsnProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringRegisteredAsnProperties(_Model):
        asn: Optional[int]
        peering_service_prefix_key: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                asn: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringRegisteredPrefix(ProxyResource):
        id: str
        name: str
        properties: Optional[PeeringRegisteredPrefixProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PeeringRegisteredPrefixProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringRegisteredPrefixProperties(_Model):
        error_message: Optional[str]
        peering_service_prefix_key: Optional[str]
        prefix: Optional[str]
        prefix_validation_state: Optional[Union[str, PrefixValidationState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringService(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PeeringServiceProperties]
        sku: Optional[PeeringServiceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PeeringServiceProperties] = ..., 
                sku: Optional[PeeringServiceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringServiceCountry(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.peering.models.PeeringServiceLocation(Resource):
        id: str
        name: str
        properties: Optional[PeeringServiceLocationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PeeringServiceLocationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringServiceLocationProperties(_Model):
        azure_region: Optional[str]
        country: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_region: Optional[str] = ..., 
                country: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringServicePrefix(ProxyResource):
        id: str
        name: str
        properties: Optional[PeeringServicePrefixProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PeeringServicePrefixProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringServicePrefixEvent(_Model):
        event_description: Optional[str]
        event_level: Optional[str]
        event_summary: Optional[str]
        event_timestamp: Optional[datetime]
        event_type: Optional[str]


    class azure.mgmt.peering.models.PeeringServicePrefixProperties(_Model):
        error_message: Optional[str]
        events: Optional[list[PeeringServicePrefixEvent]]
        learned_type: Optional[Union[str, LearnedType]]
        peering_service_prefix_key: Optional[str]
        prefix: Optional[str]
        prefix_validation_state: Optional[Union[str, PrefixValidationState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                peering_service_prefix_key: Optional[str] = ..., 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringServiceProperties(_Model):
        log_analytics_workspace_properties: Optional[LogAnalyticsWorkspaceProperties]
        peering_service_location: Optional[str]
        peering_service_provider: Optional[str]
        provider_backup_peering_location: Optional[str]
        provider_primary_peering_location: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                log_analytics_workspace_properties: Optional[LogAnalyticsWorkspaceProperties] = ..., 
                peering_service_location: Optional[str] = ..., 
                peering_service_provider: Optional[str] = ..., 
                provider_backup_peering_location: Optional[str] = ..., 
                provider_primary_peering_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringServiceProvider(Resource):
        id: str
        name: str
        properties: Optional[PeeringServiceProviderProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PeeringServiceProviderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.peering.models.PeeringServiceProviderProperties(_Model):
        peering_locations: Optional[list[str]]
        service_provider_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                peering_locations: Optional[list[str]] = ..., 
                service_provider_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringServiceSku(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PeeringSku(_Model):
        family: Optional[Union[str, Family]]
        name: Optional[str]
        size: Optional[Union[str, Size]]
        tier: Optional[Union[str, Tier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.PrefixValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INVALID = "Invalid"
        NONE = "None"
        PENDING = "Pending"
        UNKNOWN = "Unknown"
        VERIFIED = "Verified"
        WARNING = "Warning"


    class azure.mgmt.peering.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ICMP = "ICMP"
        NONE = "None"
        TCP = "TCP"


    class azure.mgmt.peering.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.peering.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.peering.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.peering.models.ResourceTags(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.Role(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ESCALATION = "Escalation"
        NOC = "Noc"
        OTHER = "Other"
        POLICY = "Policy"
        SERVICE = "Service"
        TECHNICAL = "Technical"


    class azure.mgmt.peering.models.RpUnbilledPrefix(_Model):
        azure_region: Optional[str]
        peer_asn: Optional[int]
        prefix: Optional[str]


    class azure.mgmt.peering.models.ServiceSpecification(_Model):
        metric_specifications: Optional[list[MetricSpecification]]


    class azure.mgmt.peering.models.SessionAddressProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT = "Microsoft"
        PEER = "Peer"


    class azure.mgmt.peering.models.SessionStateV4(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CONNECT = "Connect"
        ESTABLISHED = "Established"
        IDLE = "Idle"
        NONE = "None"
        OPEN_CONFIRM = "OpenConfirm"
        OPEN_RECEIVED = "OpenReceived"
        OPEN_SENT = "OpenSent"
        PENDING_ADD = "PendingAdd"
        PENDING_REMOVE = "PendingRemove"
        PENDING_UPDATE = "PendingUpdate"


    class azure.mgmt.peering.models.SessionStateV6(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CONNECT = "Connect"
        ESTABLISHED = "Established"
        IDLE = "Idle"
        NONE = "None"
        OPEN_CONFIRM = "OpenConfirm"
        OPEN_RECEIVED = "OpenReceived"
        OPEN_SENT = "OpenSent"
        PENDING_ADD = "PendingAdd"
        PENDING_REMOVE = "PendingRemove"
        PENDING_UPDATE = "PendingUpdate"


    class azure.mgmt.peering.models.Size(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        METERED = "Metered"
        UNLIMITED = "Unlimited"


    class azure.mgmt.peering.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.peering.models.SystemData(_Model):
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


    class azure.mgmt.peering.models.Tier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"


    class azure.mgmt.peering.models.TrackedResource(Resource):
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


    class azure.mgmt.peering.models.ValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        FAILED = "Failed"
        NONE = "None"
        PENDING = "Pending"


namespace azure.mgmt.peering.operations

    class azure.mgmt.peering.operations.CdnPeeringPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                peering_location: str, 
                **kwargs: Any
            ) -> ItemPaged[CdnPeeringPrefix]: ...


    class azure.mgmt.peering.operations.ConnectionMonitorTestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                connection_monitor_test: ConnectionMonitorTest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                connection_monitor_test: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                connection_monitor_test: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                connection_monitor_test_name: str, 
                **kwargs: Any
            ) -> ConnectionMonitorTest: ...

        @distributed_trace
        def list_by_peering_service(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConnectionMonitorTest]: ...


    class azure.mgmt.peering.operations.LegacyPeeringsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                asn: Optional[int] = ..., 
                direct_peering_type: Optional[Union[str, DirectPeeringType]] = ..., 
                kind: Union[str, LegacyPeeringsKind], 
                peering_location: str, 
                **kwargs: Any
            ) -> ItemPaged[Peering]: ...


    class azure.mgmt.peering.operations.LookingGlassOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def invoke(
                self, 
                *, 
                command: Union[str, LookingGlassCommand], 
                destination_ip: str, 
                source_location: str, 
                source_type: Union[str, LookingGlassSourceType], 
                **kwargs: Any
            ) -> LookingGlassOutput: ...


    class azure.mgmt.peering.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.peering.operations.PeerAsnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                peer_asn_name: str, 
                peer_asn: PeerAsn, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeerAsn: ...

        @overload
        def create_or_update(
                self, 
                peer_asn_name: str, 
                peer_asn: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeerAsn: ...

        @overload
        def create_or_update(
                self, 
                peer_asn_name: str, 
                peer_asn: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeerAsn: ...

        @distributed_trace
        def delete(
                self, 
                peer_asn_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                peer_asn_name: str, 
                **kwargs: Any
            ) -> PeerAsn: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PeerAsn]: ...


    class azure.mgmt.peering.operations.PeeringLocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                direct_peering_type: Optional[Union[str, PeeringLocationsDirectPeeringType]] = ..., 
                kind: Union[str, PeeringLocationsKind], 
                **kwargs: Any
            ) -> ItemPaged[PeeringLocation]: ...


    class azure.mgmt.peering.operations.PeeringServiceCountriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[PeeringServiceCountry]: ...


    class azure.mgmt.peering.operations.PeeringServiceLocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                country: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PeeringServiceLocation]: ...


    class azure.mgmt.peering.operations.PeeringServiceProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[PeeringServiceProvider]: ...


    class azure.mgmt.peering.operations.PeeringServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                peering_service: PeeringService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                peering_service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                peering_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                **kwargs: Any
            ) -> PeeringService: ...

        @distributed_trace
        def initialize_connection_monitor(self, **kwargs: Any) -> None: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PeeringService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PeeringService]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                tags: ResourceTags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringService: ...


    class azure.mgmt.peering.operations.PeeringsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                peering: Peering, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                peering: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                peering: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> Peering: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Peering]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Peering]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                tags: ResourceTags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Peering: ...


    class azure.mgmt.peering.operations.PrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                peering_service_prefix: PeeringServicePrefix, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                peering_service_prefix: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                peering_service_prefix: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                prefix_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PeeringServicePrefix: ...

        @distributed_trace
        def list_by_peering_service(
                self, 
                resource_group_name: str, 
                peering_service_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PeeringServicePrefix]: ...


    class azure.mgmt.peering.operations.ReceivedRoutesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_peering(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                *, 
                as_path: Optional[str] = ..., 
                origin_as_validation_state: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                rpki_validation_state: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PeeringReceivedRoute]: ...


    class azure.mgmt.peering.operations.RegisteredAsnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                registered_asn: PeeringRegisteredAsn, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                registered_asn: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                registered_asn: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_asn_name: str, 
                **kwargs: Any
            ) -> PeeringRegisteredAsn: ...

        @distributed_trace
        def list_by_peering(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PeeringRegisteredAsn]: ...


    class azure.mgmt.peering.operations.RegisteredPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                registered_prefix: PeeringRegisteredPrefix, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                registered_prefix: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                registered_prefix: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...

        @distributed_trace
        def list_by_peering(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PeeringRegisteredPrefix]: ...

        @distributed_trace
        def validate(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                registered_prefix_name: str, 
                **kwargs: Any
            ) -> PeeringRegisteredPrefix: ...


    class azure.mgmt.peering.operations.RpUnbilledPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                peering_name: str, 
                *, 
                consolidate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RpUnbilledPrefix]: ...


```