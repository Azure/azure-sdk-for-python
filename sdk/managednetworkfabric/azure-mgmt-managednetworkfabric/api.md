```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.managednetworkfabric

    class azure.mgmt.managednetworkfabric.ManagedNetworkFabricMgmtClient: implements ContextManager 
        access_control_lists: AccessControlListsOperations
        external_networks: ExternalNetworksOperations
        internal_networks: InternalNetworksOperations
        internet_gateway_rules: InternetGatewayRulesOperations
        internet_gateways: InternetGatewaysOperations
        ip_communities: IpCommunitiesOperations
        ip_extended_communities: IpExtendedCommunitiesOperations
        ip_prefixes: IpPrefixesOperations
        l2_isolation_domains: L2IsolationDomainsOperations
        l3_isolation_domains: L3IsolationDomainsOperations
        neighbor_groups: NeighborGroupsOperations
        network_device_skus: NetworkDeviceSkusOperations
        network_devices: NetworkDevicesOperations
        network_fabric_controllers: NetworkFabricControllersOperations
        network_fabric_skus: NetworkFabricSkusOperations
        network_fabrics: NetworkFabricsOperations
        network_interfaces: NetworkInterfacesOperations
        network_packet_brokers: NetworkPacketBrokersOperations
        network_racks: NetworkRacksOperations
        network_tap_rules: NetworkTapRulesOperations
        network_taps: NetworkTapsOperations
        network_to_network_interconnects: NetworkToNetworkInterconnectsOperations
        operations: Operations
        route_policies: RoutePoliciesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.managednetworkfabric.aio

    class azure.mgmt.managednetworkfabric.aio.ManagedNetworkFabricMgmtClient: implements AsyncContextManager 
        access_control_lists: AccessControlListsOperations
        external_networks: ExternalNetworksOperations
        internal_networks: InternalNetworksOperations
        internet_gateway_rules: InternetGatewayRulesOperations
        internet_gateways: InternetGatewaysOperations
        ip_communities: IpCommunitiesOperations
        ip_extended_communities: IpExtendedCommunitiesOperations
        ip_prefixes: IpPrefixesOperations
        l2_isolation_domains: L2IsolationDomainsOperations
        l3_isolation_domains: L3IsolationDomainsOperations
        neighbor_groups: NeighborGroupsOperations
        network_device_skus: NetworkDeviceSkusOperations
        network_devices: NetworkDevicesOperations
        network_fabric_controllers: NetworkFabricControllersOperations
        network_fabric_skus: NetworkFabricSkusOperations
        network_fabrics: NetworkFabricsOperations
        network_interfaces: NetworkInterfacesOperations
        network_packet_brokers: NetworkPacketBrokersOperations
        network_racks: NetworkRacksOperations
        network_tap_rules: NetworkTapRulesOperations
        network_taps: NetworkTapsOperations
        network_to_network_interconnects: NetworkToNetworkInterconnectsOperations
        operations: Operations
        route_policies: RoutePoliciesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.managednetworkfabric.aio.operations

    class azure.mgmt.managednetworkfabric.aio.operations.AccessControlListsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: AccessControlList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessControlList]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessControlList]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resync(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: AccessControlListPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessControlList]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessControlList]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AccessControlList: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AccessControlList]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AccessControlList]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.ExternalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetwork]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetworkPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetwork]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ExternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.InternalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetwork]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetwork]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[InternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.InternetGatewayRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: InternetGatewayRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGatewayRule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGatewayRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: InternetGatewayRulePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGatewayRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGatewayRule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InternetGatewayRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[InternetGatewayRule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[InternetGatewayRule]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.InternetGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: InternetGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGateway]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGateway]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: InternetGatewayPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGateway]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGateway]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InternetGateway: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[InternetGateway]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[InternetGateway]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.IpCommunitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IpCommunity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpCommunity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpCommunity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IpCommunityPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpCommunity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpCommunity]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpCommunity]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpCommunity]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.IpExtendedCommunitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IpExtendedCommunity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpExtendedCommunity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpExtendedCommunity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IpExtendedCommunityPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpExtendedCommunity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpExtendedCommunity]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpExtendedCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpExtendedCommunity]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpExtendedCommunity]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.IpPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IpPrefix, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpPrefix]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpPrefix]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IpPrefixPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpPrefix]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpPrefix]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpPrefix: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpPrefix]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpPrefix]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.L2IsolationDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: L2IsolationDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L2IsolationDomain]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L2IsolationDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: L2IsolationDomainPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L2IsolationDomain]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L2IsolationDomain]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> L2IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[L2IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[L2IsolationDomain]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.L3IsolationDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: L3IsolationDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L3IsolationDomain]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L3IsolationDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: L3IsolationDomainPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L3IsolationDomain]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L3IsolationDomain]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> L3IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[L3IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[L3IsolationDomain]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NeighborGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: NeighborGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: NeighborGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NeighborGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NeighborGroup]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NeighborGroup]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkDeviceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                network_device_sku_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkDeviceSku: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkDeviceSku]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDevice]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDevice]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: RebootProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDevicePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDevice]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkDevice: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkDevice]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkDevice]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkFabricControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: NetworkFabricController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricController]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricController]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: NetworkFabricControllerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricController]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricController]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFabricController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFabricController]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFabricController]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkFabricSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                network_fabric_sku_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFabricSku: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFabricSku]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabric]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_deprovision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        async def begin_get_topology(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def begin_provision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabricPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabric]: ...

        @overload
        async def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: ValidateConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @overload
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFabric: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFabric]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFabric]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: NetworkInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: NetworkInterfacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkInterface: ...

        @distributed_trace
        def list_by_network_device(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkInterface]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkPacketBrokersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: NetworkPacketBroker, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkPacketBroker]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkPacketBroker]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: NetworkPacketBrokerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkPacketBroker]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkPacketBroker]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkPacketBroker: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkPacketBroker]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkPacketBroker]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkRacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: NetworkRack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: TagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkRack: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkRack]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkRack]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkTapRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: NetworkTapRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapRule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: NetworkTapRulePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapRule]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkTapRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkTapRule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkTapRule]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkTapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: NetworkTap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTap]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTap]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: NetworkTapPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTap]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTap]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkTap: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkTap]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkTap]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkToNetworkInterconnectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NetworkToNetworkInterconnect, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkToNetworkInterconnect]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkToNetworkInterconnect]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NetworkToNetworkInterconnectPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkToNetworkInterconnect]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkToNetworkInterconnect]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_npb_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_npb_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkToNetworkInterconnect: ...

        @distributed_trace
        def list_by_network_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkToNetworkInterconnect]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.RoutePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: RoutePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RoutePolicy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RoutePolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: RoutePolicyPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RoutePolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RoutePolicy]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RoutePolicy: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RoutePolicy]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RoutePolicy]: ...


namespace azure.mgmt.managednetworkfabric.models

    class azure.mgmt.managednetworkfabric.models.AccessControlList(TrackedResource):
        acls_url: str
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        id: str
        last_synced_time: datetime
        location: str
        match_configurations: list[AccessControlListMatchConfiguration]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acls_url: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                location: str, 
                match_configurations: Optional[List[AccessControlListMatchConfiguration]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListAction(Model):
        counter_name: str
        type: Union[str, AclActionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                counter_name: Optional[str] = ..., 
                type: Optional[Union[str, AclActionType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListMatchCondition(CommonMatchConditions):
        dscp_markings: list[str]
        ether_types: list[str]
        fragments: list[str]
        ip_condition: IpMatchCondition
        ip_lengths: list[str]
        port_condition: AccessControlListPortCondition
        protocol_types: list[str]
        ttl_values: list[str]
        vlan_match_condition: VlanMatchCondition

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dscp_markings: Optional[List[str]] = ..., 
                ether_types: Optional[List[str]] = ..., 
                fragments: Optional[List[str]] = ..., 
                ip_condition: Optional[IpMatchCondition] = ..., 
                ip_lengths: Optional[List[str]] = ..., 
                port_condition: Optional[AccessControlListPortCondition] = ..., 
                protocol_types: Optional[List[str]] = ..., 
                ttl_values: Optional[List[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchCondition] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListMatchConfiguration(Model):
        actions: list[AccessControlListAction]
        ip_address_type: Union[str, IPAddressType]
        match_conditions: list[AccessControlListMatchCondition]
        match_configuration_name: str
        sequence_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[AccessControlListAction]] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_conditions: Optional[List[AccessControlListMatchCondition]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListPatch(TagsUpdate):
        acls_url: str
        annotation: str
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        match_configurations: list[AccessControlListMatchConfiguration]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acls_url: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[AccessControlListMatchConfiguration]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListPatchProperties(AccessControlListPatchableProperties, AnnotationResource):
        acls_url: str
        annotation: str
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        match_configurations: list[AccessControlListMatchConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acls_url: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[AccessControlListMatchConfiguration]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListPatchableProperties(Model):
        acls_url: str
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        match_configurations: list[AccessControlListMatchConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acls_url: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[AccessControlListMatchConfiguration]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListPortCondition(PortCondition):
        flags: list[str]
        layer4_protocol: Union[str, Layer4Protocol]
        port_group_names: list[str]
        port_type: Union[str, PortType]
        ports: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                flags: Optional[List[str]] = ..., 
                layer4_protocol: Union[str, Layer4Protocol], 
                port_group_names: Optional[List[str]] = ..., 
                port_type: Optional[Union[str, PortType]] = ..., 
                ports: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListProperties(AnnotationResource, AccessControlListPatchableProperties):
        acls_url: str
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        last_synced_time: datetime
        match_configurations: list[AccessControlListMatchConfiguration]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acls_url: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[AccessControlListMatchConfiguration]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AccessControlListsListResult(Model):
        next_link: str
        value: list[AccessControlList]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AccessControlList]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AclActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"
        DROP = "Drop"
        LOG = "Log"


    class azure.mgmt.managednetworkfabric.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.managednetworkfabric.models.ActionIpCommunityProperties(IpCommunityAddOperationProperties, IpCommunityDeleteOperationProperties, IpCommunitySetOperationProperties):
        add: IpCommunityIdList
        delete: IpCommunityIdList
        set: IpCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add: Optional[IpCommunityIdList] = ..., 
                delete: Optional[IpCommunityIdList] = ..., 
                set: Optional[IpCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ActionIpExtendedCommunityProperties(IpExtendedCommunityAddOperationProperties, IpExtendedCommunityDeleteOperationProperties, IpExtendedCommunitySetOperationProperties):
        add: IpExtendedCommunityIdList
        delete: IpExtendedCommunityIdList
        set: IpExtendedCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add: Optional[IpExtendedCommunityIdList] = ..., 
                delete: Optional[IpExtendedCommunityIdList] = ..., 
                set: Optional[IpExtendedCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.managednetworkfabric.models.AddressFamilyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.managednetworkfabric.models.AdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        MAT = "MAT"
        RMA = "RMA"


    class azure.mgmt.managednetworkfabric.models.AggregateRoute(Model):
        prefix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                prefix: str, 
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


    class azure.mgmt.managednetworkfabric.models.AggregateRouteConfiguration(Model):
        ipv4_routes: list[AggregateRoute]
        ipv6_routes: list[AggregateRoute]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ipv4_routes: Optional[List[AggregateRoute]] = ..., 
                ipv6_routes: Optional[List[AggregateRoute]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.AllowASOverride(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.managednetworkfabric.models.AnnotationResource(Model):
        annotation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.BfdAdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        MAT = "MAT"
        RMA = "RMA"


    class azure.mgmt.managednetworkfabric.models.BfdConfiguration(Model):
        administrative_state: Union[str, BfdAdministrativeState]
        interval_in_milli_seconds: int
        multiplier: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                interval_in_milli_seconds: int = 300, 
                multiplier: int = 5, 
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


    class azure.mgmt.managednetworkfabric.models.BgpConfiguration(AnnotationResource):
        allow_as: int
        allow_as_override: Union[str, AllowASOverride]
        annotation: str
        bfd_configuration: BfdConfiguration
        default_route_originate: Union[str, BooleanEnumProperty]
        fabric_asn: int
        ipv4_listen_range_prefixes: list[str]
        ipv4_neighbor_address: list[NeighborAddress]
        ipv6_listen_range_prefixes: list[str]
        ipv6_neighbor_address: list[NeighborAddress]
        peer_asn: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_as: int = 2, 
                allow_as_override: Optional[Union[str, AllowASOverride]] = ..., 
                annotation: Optional[str] = ..., 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                default_route_originate: Optional[Union[str, BooleanEnumProperty]] = ..., 
                ipv4_listen_range_prefixes: Optional[List[str]] = ..., 
                ipv4_neighbor_address: Optional[List[NeighborAddress]] = ..., 
                ipv6_listen_range_prefixes: Optional[List[str]] = ..., 
                ipv6_neighbor_address: Optional[List[NeighborAddress]] = ..., 
                peer_asn: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.BooleanEnumProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.CommonDynamicMatchConfiguration(Model):
        ip_groups: list[IpGroupProperties]
        port_groups: list[PortGroupProperties]
        vlan_groups: list[VlanGroupProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_groups: Optional[List[IpGroupProperties]] = ..., 
                port_groups: Optional[List[PortGroupProperties]] = ..., 
                vlan_groups: Optional[List[VlanGroupProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.CommonMatchConditions(Model):
        ip_condition: IpMatchCondition
        protocol_types: list[str]
        vlan_match_condition: VlanMatchCondition

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_condition: Optional[IpMatchCondition] = ..., 
                protocol_types: Optional[List[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchCondition] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.CommonPostActionResponseForDeviceUpdate(ErrorResponse):
        configuration_state: Union[str, ConfigurationState]
        error: ErrorDetail
        failed_devices: list[str]
        successful_devices: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                failed_devices: Optional[List[str]] = ..., 
                successful_devices: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.CommonPostActionResponseForStateUpdate(ErrorResponse):
        configuration_state: Union[str, ConfigurationState]
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.CommunityActionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENY = "Deny"
        PERMIT = "Permit"


    class azure.mgmt.managednetworkfabric.models.Condition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL_TO = "EqualTo"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"
        LESSER_THAN_OR_EQUAL_TO = "LesserThanOrEqualTo"
        RANGE = "Range"


    class azure.mgmt.managednetworkfabric.models.ConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        DEFERRED_CONTROL = "DeferredControl"
        DEPROVISIONED = "Deprovisioned"
        DEPROVISIONING = "Deprovisioning"
        ERROR_DEPROVISIONING = "ErrorDeprovisioning"
        ERROR_PROVISIONING = "ErrorProvisioning"
        FAILED = "Failed"
        PROVISIONED = "Provisioned"
        REJECTED = "Rejected"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.managednetworkfabric.models.ConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "File"
        INLINE = "Inline"


    class azure.mgmt.managednetworkfabric.models.ConnectedSubnet(AnnotationResource):
        annotation: str
        prefix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                prefix: str, 
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


    class azure.mgmt.managednetworkfabric.models.ConnectedSubnetRoutePolicy(Model):
        export_route_policy: L3ExportRoutePolicy
        export_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_route_policy: Optional[L3ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ControllerServices(Model):
        ipv4_address_spaces: list[str]
        ipv6_address_spaces: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ipv4_address_spaces: Optional[List[str]] = ..., 
                ipv6_address_spaces: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.managednetworkfabric.models.DestinationProperties(Model):
        destination_id: str
        destination_tap_rule_id: str
        destination_type: Union[str, DestinationType]
        isolation_domain_properties: IsolationDomainProperties
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                destination_tap_rule_id: Optional[str] = ..., 
                destination_type: Optional[Union[str, DestinationType]] = ..., 
                isolation_domain_properties: Optional[IsolationDomainProperties] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.DestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        ISOLATION_DOMAIN = "IsolationDomain"


    class azure.mgmt.managednetworkfabric.models.DeviceAdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRACEFUL_QUARANTINE = "GracefulQuarantine"
        QUARANTINE = "Quarantine"
        RESYNC = "Resync"
        RMA = "RMA"


    class azure.mgmt.managednetworkfabric.models.DeviceInterfaceProperties(Model):
        identifier: str
        interface_type: str
        supported_connector_types: list[SupportedConnectorProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identifier: Optional[str] = ..., 
                interface_type: Optional[str] = ..., 
                supported_connector_types: Optional[List[SupportedConnectorProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.EnableDisableOnResources(Model):
        resource_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_ids: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.EnableDisableState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.managednetworkfabric.models.Encapsulation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRE = "GRE"
        NONE = "None"


    class azure.mgmt.managednetworkfabric.models.EncapsulationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GT_PV1 = "GTPv1"
        NONE = "None"


    class azure.mgmt.managednetworkfabric.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

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


    class azure.mgmt.managednetworkfabric.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.managednetworkfabric.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExportRoutePolicy(Model):
        export_ipv4_route_policy_id: str
        export_ipv6_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExportRoutePolicyInformation(Model):
        export_ipv4_route_policy_id: str
        export_ipv6_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExpressRouteConnectionInformation(Model):
        express_route_authorization_key: str
        express_route_circuit_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                express_route_authorization_key: str, 
                express_route_circuit_id: str, 
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


    class azure.mgmt.managednetworkfabric.models.ExtendedLocation(Model):
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


    class azure.mgmt.managednetworkfabric.models.Extension(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_EXTENSION = "NoExtension"
        NPB = "NPB"


    class azure.mgmt.managednetworkfabric.models.ExtensionEnumProperty(Model):
        extension: Union[str, Extension]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extension: Union[str, Extension] = "NoExtension", 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetwork(ProxyResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        name: str
        network_to_network_interconnect_id: str
        option_a_properties: ExternalNetworkPropertiesOptionAProperties
        option_b_properties: L3OptionBProperties
        peering_option: Union[str, PeeringOption]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                option_a_properties: Optional[ExternalNetworkPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[L3OptionBProperties] = ..., 
                peering_option: Union[str, PeeringOption], 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatch(Model):
        annotation: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        option_a_properties: ExternalNetworkPatchPropertiesOptionAProperties
        option_b_properties: L3OptionBProperties
        peering_option: Union[str, PeeringOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                option_a_properties: Optional[ExternalNetworkPatchPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[L3OptionBProperties] = ..., 
                peering_option: Optional[Union[str, PeeringOption]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatchProperties(AnnotationResource, ExternalNetworkPatchableProperties):
        annotation: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        option_a_properties: ExternalNetworkPatchPropertiesOptionAProperties
        option_b_properties: L3OptionBProperties
        peering_option: Union[str, PeeringOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                option_a_properties: Optional[ExternalNetworkPatchPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[L3OptionBProperties] = ..., 
                peering_option: Optional[Union[str, PeeringOption]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatchPropertiesOptionAProperties(Layer3IpPrefixProperties, L3OptionAProperties):
        bfd_configuration: BfdConfiguration
        egress_acl_id: str
        fabric_asn: int
        ingress_acl_id: str
        mtu: int
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                egress_acl_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                mtu: int = 1500, 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatchableProperties(Model):
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkProperties(AnnotationResource, ExternalNetworkPatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        network_to_network_interconnect_id: str
        option_a_properties: ExternalNetworkPropertiesOptionAProperties
        option_b_properties: L3OptionBProperties
        peering_option: Union[str, PeeringOption]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                option_a_properties: Optional[ExternalNetworkPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[L3OptionBProperties] = ..., 
                peering_option: Union[str, PeeringOption], 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPropertiesOptionAProperties(Layer3IpPrefixProperties, L3OptionAProperties):
        bfd_configuration: BfdConfiguration
        egress_acl_id: str
        fabric_asn: int
        ingress_acl_id: str
        mtu: int
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                egress_acl_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                mtu: int = 1500, 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ExternalNetworksList(Model):
        next_link: str
        value: list[ExternalNetwork]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ExternalNetwork]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.FabricSkuType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_RACK = "MultiRack"
        SINGLE_RACK = "SingleRack"


    class azure.mgmt.managednetworkfabric.models.GatewayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INFRASTRUCTURE = "Infrastructure"
        WORKLOAD = "Workload"


    class azure.mgmt.managednetworkfabric.models.IPAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.managednetworkfabric.models.ImportRoutePolicy(Model):
        import_ipv4_route_policy_id: str
        import_ipv6_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                import_ipv4_route_policy_id: Optional[str] = ..., 
                import_ipv6_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ImportRoutePolicyInformation(Model):
        import_ipv4_route_policy_id: str
        import_ipv6_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                import_ipv4_route_policy_id: Optional[str] = ..., 
                import_ipv6_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InterfaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        MANAGEMENT = "Management"


    class azure.mgmt.managednetworkfabric.models.InternalNetwork(ProxyResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        bgp_configuration: InternalNetworkPropertiesBgpConfiguration
        configuration_state: Union[str, ConfigurationState]
        connected_i_pv4_subnets: list[ConnectedSubnet]
        connected_i_pv6_subnets: list[ConnectedSubnet]
        egress_acl_id: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        extension: Union[str, Extension]
        id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        ingress_acl_id: str
        is_monitoring_enabled: Union[str, IsMonitoringEnabled]
        mtu: int
        name: str
        provisioning_state: Union[str, ProvisioningState]
        static_route_configuration: InternalNetworkPropertiesStaticRouteConfiguration
        system_data: SystemData
        type: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bgp_configuration: Optional[InternalNetworkPropertiesBgpConfiguration] = ..., 
                connected_i_pv4_subnets: Optional[List[ConnectedSubnet]] = ..., 
                connected_i_pv6_subnets: Optional[List[ConnectedSubnet]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                extension: Union[str, Extension] = "NoExtension", 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Union[str, IsMonitoringEnabled] = "False", 
                mtu: int = 1500, 
                static_route_configuration: Optional[InternalNetworkPropertiesStaticRouteConfiguration] = ..., 
                vlan_id: int, 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPatch(Model):
        annotation: str
        bgp_configuration: BgpConfiguration
        connected_i_pv4_subnets: list[ConnectedSubnet]
        connected_i_pv6_subnets: list[ConnectedSubnet]
        egress_acl_id: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        ingress_acl_id: str
        is_monitoring_enabled: Union[str, IsMonitoringEnabled]
        mtu: int
        static_route_configuration: StaticRouteConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bgp_configuration: Optional[BgpConfiguration] = ..., 
                connected_i_pv4_subnets: Optional[List[ConnectedSubnet]] = ..., 
                connected_i_pv6_subnets: Optional[List[ConnectedSubnet]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Union[str, IsMonitoringEnabled] = "False", 
                mtu: int = 1500, 
                static_route_configuration: Optional[StaticRouteConfiguration] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPatchProperties(AnnotationResource, InternalNetworkPatchableProperties):
        annotation: str
        bgp_configuration: BgpConfiguration
        connected_i_pv4_subnets: list[ConnectedSubnet]
        connected_i_pv6_subnets: list[ConnectedSubnet]
        egress_acl_id: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        ingress_acl_id: str
        is_monitoring_enabled: Union[str, IsMonitoringEnabled]
        mtu: int
        static_route_configuration: StaticRouteConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bgp_configuration: Optional[BgpConfiguration] = ..., 
                connected_i_pv4_subnets: Optional[List[ConnectedSubnet]] = ..., 
                connected_i_pv6_subnets: Optional[List[ConnectedSubnet]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Union[str, IsMonitoringEnabled] = "False", 
                mtu: int = 1500, 
                static_route_configuration: Optional[StaticRouteConfiguration] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPatchableProperties(Model):
        connected_i_pv4_subnets: list[ConnectedSubnet]
        connected_i_pv6_subnets: list[ConnectedSubnet]
        egress_acl_id: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        ingress_acl_id: str
        is_monitoring_enabled: Union[str, IsMonitoringEnabled]
        mtu: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connected_i_pv4_subnets: Optional[List[ConnectedSubnet]] = ..., 
                connected_i_pv6_subnets: Optional[List[ConnectedSubnet]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Union[str, IsMonitoringEnabled] = "False", 
                mtu: int = 1500, 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworkProperties(AnnotationResource, InternalNetworkPatchableProperties, ExtensionEnumProperty):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        bgp_configuration: InternalNetworkPropertiesBgpConfiguration
        configuration_state: Union[str, ConfigurationState]
        connected_i_pv4_subnets: list[ConnectedSubnet]
        connected_i_pv6_subnets: list[ConnectedSubnet]
        egress_acl_id: str
        export_route_policy: ExportRoutePolicy
        export_route_policy_id: str
        extension: Union[str, Extension]
        import_route_policy: ImportRoutePolicy
        import_route_policy_id: str
        ingress_acl_id: str
        is_monitoring_enabled: Union[str, IsMonitoringEnabled]
        mtu: int
        provisioning_state: Union[str, ProvisioningState]
        static_route_configuration: InternalNetworkPropertiesStaticRouteConfiguration
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bgp_configuration: Optional[InternalNetworkPropertiesBgpConfiguration] = ..., 
                connected_i_pv4_subnets: Optional[List[ConnectedSubnet]] = ..., 
                connected_i_pv6_subnets: Optional[List[ConnectedSubnet]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                export_route_policy_id: Optional[str] = ..., 
                extension: Union[str, Extension] = "NoExtension", 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                import_route_policy_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Union[str, IsMonitoringEnabled] = "False", 
                mtu: int = 1500, 
                static_route_configuration: Optional[InternalNetworkPropertiesStaticRouteConfiguration] = ..., 
                vlan_id: int, 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPropertiesBgpConfiguration(BgpConfiguration):
        allow_as: int
        allow_as_override: Union[str, AllowASOverride]
        annotation: str
        bfd_configuration: BfdConfiguration
        default_route_originate: Union[str, BooleanEnumProperty]
        fabric_asn: int
        ipv4_listen_range_prefixes: list[str]
        ipv4_neighbor_address: list[NeighborAddress]
        ipv6_listen_range_prefixes: list[str]
        ipv6_neighbor_address: list[NeighborAddress]
        peer_asn: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_as: int = 2, 
                allow_as_override: Optional[Union[str, AllowASOverride]] = ..., 
                annotation: Optional[str] = ..., 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                default_route_originate: Optional[Union[str, BooleanEnumProperty]] = ..., 
                ipv4_listen_range_prefixes: Optional[List[str]] = ..., 
                ipv4_neighbor_address: Optional[List[NeighborAddress]] = ..., 
                ipv6_listen_range_prefixes: Optional[List[str]] = ..., 
                ipv6_neighbor_address: Optional[List[NeighborAddress]] = ..., 
                peer_asn: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPropertiesStaticRouteConfiguration(StaticRouteConfiguration, ExtensionEnumProperty):
        bfd_configuration: BfdConfiguration
        extension: Union[str, Extension]
        ipv4_routes: list[StaticRouteProperties]
        ipv6_routes: list[StaticRouteProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                extension: Union[str, Extension] = "NoExtension", 
                ipv4_routes: Optional[List[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[List[StaticRouteProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternalNetworksList(Model):
        next_link: str
        value: list[InternalNetwork]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[InternalNetwork]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternetGateway(TrackedResource):
        annotation: str
        id: str
        internet_gateway_rule_id: str
        ipv4_address: str
        location: str
        name: str
        network_fabric_controller_id: str
        port: int
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        type_properties_type: Union[str, GatewayType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                internet_gateway_rule_id: Optional[str] = ..., 
                location: str, 
                network_fabric_controller_id: str, 
                tags: Optional[Dict[str, str]] = ..., 
                type_properties_type: Union[str, GatewayType], 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayPatch(TagsUpdate):
        internet_gateway_rule_id: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                internet_gateway_rule_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayPatchableProperties(Model):
        internet_gateway_rule_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                internet_gateway_rule_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayProperties(AnnotationResource, InternetGatewayPatchableProperties):
        annotation: str
        internet_gateway_rule_id: str
        ipv4_address: str
        network_fabric_controller_id: str
        port: int
        provisioning_state: Union[str, ProvisioningState]
        type: Union[str, GatewayType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                internet_gateway_rule_id: Optional[str] = ..., 
                network_fabric_controller_id: str, 
                type: Union[str, GatewayType], 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRule(TrackedResource):
        annotation: str
        id: str
        internet_gateway_ids: list[str]
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        rule_properties: RuleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                location: str, 
                rule_properties: RuleProperties, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRulePatch(TagsUpdate):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRuleProperties(AnnotationResource):
        annotation: str
        internet_gateway_ids: list[str]
        provisioning_state: Union[str, ProvisioningState]
        rule_properties: RuleProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                rule_properties: RuleProperties, 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRulesListResult(Model):
        next_link: str
        value: list[InternetGatewayRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[InternetGatewayRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.InternetGatewaysListResult(Model):
        next_link: str
        value: list[InternetGateway]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[InternetGateway]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunitiesListResult(Model):
        next_link: str
        value: list[IpCommunity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IpCommunity]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunity(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        id: str
        ip_community_rules: list[IpCommunityRule]
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_community_rules: Optional[List[IpCommunityRule]] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityAddOperationProperties(Model):
        add: IpCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add: Optional[IpCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityDeleteOperationProperties(Model):
        delete: IpCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete: Optional[IpCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityIdList(Model):
        ip_community_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_community_ids: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityPatch(TagsUpdate):
        ip_community_rules: list[IpCommunityRule]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_community_rules: Optional[List[IpCommunityRule]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityPatchableProperties(Model):
        ip_community_rules: list[IpCommunityRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_community_rules: Optional[List[IpCommunityRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityProperties(AnnotationResource, IpCommunityPatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        ip_community_rules: list[IpCommunityRule]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_community_rules: Optional[List[IpCommunityRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunityRule(Model):
        action: Union[str, CommunityActionTypes]
        community_members: list[str]
        sequence_number: int
        well_known_communities: Union[list[str, WellKnownCommunities]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, CommunityActionTypes], 
                community_members: List[str], 
                sequence_number: int, 
                well_known_communities: Optional[List[Union[str, WellKnownCommunities]]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpCommunitySetOperationProperties(Model):
        set: IpCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                set: Optional[IpCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunity(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        id: str
        ip_extended_community_rules: list[IpExtendedCommunityRule]
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_extended_community_rules: List[IpExtendedCommunityRule], 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityAddOperationProperties(Model):
        add: IpExtendedCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add: Optional[IpExtendedCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityDeleteOperationProperties(Model):
        delete: IpExtendedCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete: Optional[IpExtendedCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityIdList(Model):
        ip_extended_community_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_extended_community_ids: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityListResult(Model):
        next_link: str
        value: list[IpExtendedCommunity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IpExtendedCommunity]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityPatch(TagsUpdate):
        annotation: str
        ip_extended_community_rules: list[IpExtendedCommunityRule]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_extended_community_rules: Optional[List[IpExtendedCommunityRule]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityPatchProperties(IpExtendedCommunityPatchableProperties, AnnotationResource):
        annotation: str
        ip_extended_community_rules: list[IpExtendedCommunityRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_extended_community_rules: List[IpExtendedCommunityRule], 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityPatchableProperties(Model):
        ip_extended_community_rules: list[IpExtendedCommunityRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_extended_community_rules: List[IpExtendedCommunityRule], 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityProperties(AnnotationResource, IpExtendedCommunityPatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        ip_extended_community_rules: list[IpExtendedCommunityRule]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_extended_community_rules: List[IpExtendedCommunityRule], 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityRule(Model):
        action: Union[str, CommunityActionTypes]
        route_targets: list[str]
        sequence_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, CommunityActionTypes], 
                route_targets: List[str], 
                sequence_number: int, 
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


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunitySetOperationProperties(Model):
        set: IpExtendedCommunityIdList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                set: Optional[IpExtendedCommunityIdList] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpGroupProperties(Model):
        ip_address_type: Union[str, IPAddressType]
        ip_prefixes: list[str]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                ip_prefixes: Optional[List[str]] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpMatchCondition(Model):
        ip_group_names: list[str]
        ip_prefix_values: list[str]
        prefix_type: Union[str, PrefixType]
        type: Union[str, SourceDestinationType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_group_names: Optional[List[str]] = ..., 
                ip_prefix_values: Optional[List[str]] = ..., 
                prefix_type: Optional[Union[str, PrefixType]] = ..., 
                type: Optional[Union[str, SourceDestinationType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefix(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        id: str
        ip_prefix_rules: list[IpPrefixRule]
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_prefix_rules: Optional[List[IpPrefixRule]] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefixPatch(TagsUpdate):
        annotation: str
        ip_prefix_rules: list[IpPrefixRule]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_prefix_rules: Optional[List[IpPrefixRule]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefixPatchProperties(AnnotationResource, IpPrefixPatchableProperties):
        annotation: str
        ip_prefix_rules: list[IpPrefixRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_prefix_rules: Optional[List[IpPrefixRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefixPatchableProperties(Model):
        ip_prefix_rules: list[IpPrefixRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_prefix_rules: Optional[List[IpPrefixRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefixProperties(AnnotationResource, IpPrefixPatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        ip_prefix_rules: list[IpPrefixRule]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_prefix_rules: Optional[List[IpPrefixRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefixRule(Model):
        action: Union[str, CommunityActionTypes]
        condition: Union[str, Condition]
        network_prefix: str
        sequence_number: int
        subnet_mask_length: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, CommunityActionTypes], 
                condition: Optional[Union[str, Condition]] = ..., 
                network_prefix: str, 
                sequence_number: int, 
                subnet_mask_length: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IpPrefixesListResult(Model):
        next_link: str
        value: list[IpPrefix]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IpPrefix]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.IsManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.IsMonitoringEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.IsWorkloadManagementNetworkEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.IsolationDomainProperties(Model):
        encapsulation: Union[str, Encapsulation]
        neighbor_group_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encapsulation: Optional[Union[str, Encapsulation]] = ..., 
                neighbor_group_ids: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomain(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        id: str
        location: str
        mtu: int
        name: str
        network_fabric_id: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                location: str, 
                mtu: int = 1500, 
                network_fabric_id: str, 
                tags: Optional[Dict[str, str]] = ..., 
                vlan_id: int, 
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


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainPatch(TagsUpdate):
        annotation: str
        mtu: int
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                mtu: int = 1500, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainPatchProperties(AnnotationResource):
        annotation: str
        mtu: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                mtu: int = 1500, 
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


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainProperties(AnnotationResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        mtu: int
        network_fabric_id: str
        provisioning_state: Union[str, ProvisioningState]
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                mtu: int = 1500, 
                network_fabric_id: str, 
                vlan_id: int, 
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


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainsListResult(Model):
        next_link: str
        value: list[L2IsolationDomain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[L2IsolationDomain]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L3ExportRoutePolicy(Model):
        export_ipv4_route_policy_id: str
        export_ipv6_route_policy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomain(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        aggregate_route_configuration: AggregateRouteConfiguration
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        connected_subnet_route_policy: ConnectedSubnetRoutePolicy
        id: str
        location: str
        name: str
        network_fabric_id: str
        provisioning_state: Union[str, ProvisioningState]
        redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets]
        redistribute_static_routes: Union[str, RedistributeStaticRoutes]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRouteConfiguration] = ..., 
                annotation: Optional[str] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy] = ..., 
                location: str, 
                network_fabric_id: str, 
                redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets] = "True", 
                redistribute_static_routes: Union[str, RedistributeStaticRoutes] = "False", 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainPatch(TagsUpdate):
        aggregate_route_configuration: AggregateRouteConfiguration
        annotation: str
        connected_subnet_route_policy: ConnectedSubnetRoutePolicy
        redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets]
        redistribute_static_routes: Union[str, RedistributeStaticRoutes]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRouteConfiguration] = ..., 
                annotation: Optional[str] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy] = ..., 
                redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets] = "True", 
                redistribute_static_routes: Union[str, RedistributeStaticRoutes] = "False", 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainPatchProperties(AnnotationResource, L3IsolationDomainPatchableProperties):
        aggregate_route_configuration: AggregateRouteConfiguration
        annotation: str
        connected_subnet_route_policy: ConnectedSubnetRoutePolicy
        redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets]
        redistribute_static_routes: Union[str, RedistributeStaticRoutes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRouteConfiguration] = ..., 
                annotation: Optional[str] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy] = ..., 
                redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets] = "True", 
                redistribute_static_routes: Union[str, RedistributeStaticRoutes] = "False", 
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


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainPatchableProperties(Model):
        aggregate_route_configuration: AggregateRouteConfiguration
        connected_subnet_route_policy: ConnectedSubnetRoutePolicy
        redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets]
        redistribute_static_routes: Union[str, RedistributeStaticRoutes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRouteConfiguration] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy] = ..., 
                redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets] = "True", 
                redistribute_static_routes: Union[str, RedistributeStaticRoutes] = "False", 
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


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainProperties(AnnotationResource, L3IsolationDomainPatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        aggregate_route_configuration: AggregateRouteConfiguration
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        connected_subnet_route_policy: ConnectedSubnetRoutePolicy
        network_fabric_id: str
        provisioning_state: Union[str, ProvisioningState]
        redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets]
        redistribute_static_routes: Union[str, RedistributeStaticRoutes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRouteConfiguration] = ..., 
                annotation: Optional[str] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy] = ..., 
                network_fabric_id: str, 
                redistribute_connected_subnets: Union[str, RedistributeConnectedSubnets] = "True", 
                redistribute_static_routes: Union[str, RedistributeStaticRoutes] = "False", 
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


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainsListResult(Model):
        next_link: str
        value: list[L3IsolationDomain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[L3IsolationDomain]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L3OptionAProperties(Model):
        bfd_configuration: BfdConfiguration
        egress_acl_id: str
        fabric_asn: int
        ingress_acl_id: str
        mtu: int
        peer_asn: int
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                egress_acl_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                mtu: int = 1500, 
                peer_asn: Optional[int] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.L3OptionBProperties(Model):
        export_route_targets: list[str]
        import_route_targets: list[str]
        route_targets: RouteTargetInformation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_route_targets: Optional[List[str]] = ..., 
                import_route_targets: Optional[List[str]] = ..., 
                route_targets: Optional[RouteTargetInformation] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.Layer2Configuration(Model):
        interfaces: list[str]
        mtu: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                interfaces: Optional[List[str]] = ..., 
                mtu: int = 1500, 
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


    class azure.mgmt.managednetworkfabric.models.Layer3IpPrefixProperties(Model):
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.Layer4Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.managednetworkfabric.models.ManagedResourceGroupConfiguration(Model):
        location: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ManagementNetworkConfigurationPatchableProperties(Model):
        infrastructure_vpn_configuration: VpnConfigurationPatchableProperties
        workload_vpn_configuration: VpnConfigurationPatchableProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                infrastructure_vpn_configuration: Optional[VpnConfigurationPatchableProperties] = ..., 
                workload_vpn_configuration: Optional[VpnConfigurationPatchableProperties] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ManagementNetworkConfigurationProperties(Model):
        infrastructure_vpn_configuration: VpnConfigurationProperties
        workload_vpn_configuration: VpnConfigurationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                infrastructure_vpn_configuration: VpnConfigurationProperties, 
                workload_vpn_configuration: VpnConfigurationProperties, 
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


    class azure.mgmt.managednetworkfabric.models.NeighborAddress(Model):
        address: str
        configuration_state: Union[str, ConfigurationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroup(TrackedResource):
        annotation: str
        destination: NeighborGroupDestination
        id: str
        location: str
        name: str
        network_tap_ids: list[str]
        network_tap_rule_ids: list[str]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destination: Optional[NeighborGroupDestination] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroupDestination(Model):
        ipv4_addresses: list[str]
        ipv6_addresses: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ipv4_addresses: Optional[List[str]] = ..., 
                ipv6_addresses: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroupPatch(TagsUpdate):
        annotation: str
        destination: NeighborGroupDestination
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destination: Optional[NeighborGroupDestination] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroupPatchProperties(AnnotationResource, NeighborGroupPatchableProperties):
        annotation: str
        destination: NeighborGroupDestination

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destination: Optional[NeighborGroupDestination] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroupPatchableProperties(Model):
        destination: NeighborGroupDestination

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination: Optional[NeighborGroupDestination] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroupProperties(AnnotationResource, NeighborGroupPatchableProperties):
        annotation: str
        destination: NeighborGroupDestination
        network_tap_ids: list[str]
        network_tap_rule_ids: list[str]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destination: Optional[NeighborGroupDestination] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NeighborGroupsListResult(Model):
        next_link: str
        value: list[NeighborGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NeighborGroup]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDevice(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        host_name: str
        id: str
        location: str
        management_ipv4_address: str
        management_ipv6_address: str
        name: str
        network_device_role: Union[str, NetworkDeviceRole]
        network_device_sku: str
        network_rack_id: str
        provisioning_state: Union[str, ProvisioningState]
        serial_number: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                location: str, 
                network_device_sku: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDevicePatchParameters(TagsUpdate):
        annotation: str
        host_name: str
        serial_number: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDevicePatchParametersProperties(AnnotationResource, NetworkDevicePatchableProperties):
        annotation: str
        host_name: str
        serial_number: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDevicePatchableProperties(Model):
        host_name: str
        serial_number: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_name: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceProperties(AnnotationResource, NetworkDevicePatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        host_name: str
        management_ipv4_address: str
        management_ipv6_address: str
        network_device_role: Union[str, NetworkDeviceRole]
        network_device_sku: str
        network_rack_id: str
        provisioning_state: Union[str, ProvisioningState]
        serial_number: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                network_device_sku: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CE = "CE"
        MANAGEMENT = "Management"
        NPB = "NPB"
        TO_R = "ToR"
        TS = "TS"


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceRoleName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CE = "CE"
        MANAGEMENT = "Management"
        NPB = "NPB"
        TO_R = "ToR"
        TS = "TS"


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceSku(ProxyResource):
        id: str
        interfaces: list[DeviceInterfaceProperties]
        manufacturer: str
        model: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        supported_role_types: Union[list[str, NetworkDeviceRoleName]]
        supported_versions: list[SupportedVersionProperties]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                interfaces: Optional[List[DeviceInterfaceProperties]] = ..., 
                manufacturer: Optional[str] = ..., 
                model: str, 
                supported_role_types: Optional[List[Union[str, NetworkDeviceRoleName]]] = ..., 
                supported_versions: Optional[List[SupportedVersionProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceSkusListResult(Model):
        next_link: str
        value: list[NetworkDeviceSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkDeviceSku]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkDevicesListResult(Model):
        next_link: str
        value: list[NetworkDevice]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkDevice]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabric(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        fabric_asn: int
        fabric_version: str
        id: str
        ipv4_prefix: str
        ipv6_prefix: str
        l2_isolation_domains: list[str]
        l3_isolation_domains: list[str]
        location: str
        management_network_configuration: ManagementNetworkConfigurationProperties
        name: str
        network_fabric_controller_id: str
        network_fabric_sku: str
        provisioning_state: Union[str, ProvisioningState]
        rack_count: int
        racks: list[str]
        router_ids: list[str]
        server_count_per_rack: int
        system_data: SystemData
        tags: dict[str, str]
        terminal_server_configuration: TerminalServerConfiguration
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                fabric_asn: int, 
                ipv4_prefix: str, 
                ipv6_prefix: Optional[str] = ..., 
                location: str, 
                management_network_configuration: ManagementNetworkConfigurationProperties, 
                network_fabric_controller_id: str, 
                network_fabric_sku: str, 
                rack_count: Optional[int] = ..., 
                server_count_per_rack: int, 
                tags: Optional[Dict[str, str]] = ..., 
                terminal_server_configuration: TerminalServerConfiguration, 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricController(TrackedResource):
        annotation: str
        id: str
        infrastructure_express_route_connections: list[ExpressRouteConnectionInformation]
        infrastructure_services: ControllerServices
        ipv4_address_space: str
        ipv6_address_space: str
        is_workload_management_network_enabled: Union[str, IsWorkloadManagementNetworkEnabled]
        location: str
        managed_resource_group_configuration: ManagedResourceGroupConfiguration
        name: str
        network_fabric_ids: list[str]
        nfc_sku: Union[str, NfcSku]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        tenant_internet_gateway_ids: list[str]
        type: str
        workload_express_route_connections: list[ExpressRouteConnectionInformation]
        workload_management_network: bool
        workload_services: ControllerServices

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                infrastructure_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
                ipv4_address_space: str = "10.0.0.0/19", 
                ipv6_address_space: str = "FC00::/59", 
                is_workload_management_network_enabled: Union[str, IsWorkloadManagementNetworkEnabled] = "True", 
                location: str, 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                nfc_sku: Union[str, NfcSku] = "Standard", 
                tags: Optional[Dict[str, str]] = ..., 
                workload_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllerPatch(TagsUpdate):
        infrastructure_express_route_connections: list[ExpressRouteConnectionInformation]
        tags: dict[str, str]
        workload_express_route_connections: list[ExpressRouteConnectionInformation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                infrastructure_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                workload_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllerPatchableProperties(Model):
        infrastructure_express_route_connections: list[ExpressRouteConnectionInformation]
        workload_express_route_connections: list[ExpressRouteConnectionInformation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                infrastructure_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
                workload_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllerProperties(AnnotationResource, NetworkFabricControllerPatchableProperties):
        annotation: str
        infrastructure_express_route_connections: list[ExpressRouteConnectionInformation]
        infrastructure_services: ControllerServices
        ipv4_address_space: str
        ipv6_address_space: str
        is_workload_management_network_enabled: Union[str, IsWorkloadManagementNetworkEnabled]
        managed_resource_group_configuration: ManagedResourceGroupConfiguration
        network_fabric_ids: list[str]
        nfc_sku: Union[str, NfcSku]
        provisioning_state: Union[str, ProvisioningState]
        tenant_internet_gateway_ids: list[str]
        workload_express_route_connections: list[ExpressRouteConnectionInformation]
        workload_management_network: bool
        workload_services: ControllerServices

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                infrastructure_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
                ipv4_address_space: str = "10.0.0.0/19", 
                ipv6_address_space: str = "FC00::/59", 
                is_workload_management_network_enabled: Union[str, IsWorkloadManagementNetworkEnabled] = "True", 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                nfc_sku: Union[str, NfcSku] = "Standard", 
                workload_express_route_connections: Optional[List[ExpressRouteConnectionInformation]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllersListResult(Model):
        next_link: str
        value: list[NetworkFabricController]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkFabricController]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricPatch(TagsUpdate):
        annotation: str
        fabric_asn: int
        ipv4_prefix: str
        ipv6_prefix: str
        management_network_configuration: ManagementNetworkConfigurationPatchableProperties
        rack_count: int
        server_count_per_rack: int
        tags: dict[str, str]
        terminal_server_configuration: NetworkFabricPatchablePropertiesTerminalServerConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                fabric_asn: Optional[int] = ..., 
                ipv4_prefix: Optional[str] = ..., 
                ipv6_prefix: Optional[str] = ..., 
                management_network_configuration: Optional[ManagementNetworkConfigurationPatchableProperties] = ..., 
                rack_count: Optional[int] = ..., 
                server_count_per_rack: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                terminal_server_configuration: Optional[NetworkFabricPatchablePropertiesTerminalServerConfiguration] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricPatchProperties(AnnotationResource, NetworkFabricPatchableProperties):
        annotation: str
        fabric_asn: int
        ipv4_prefix: str
        ipv6_prefix: str
        management_network_configuration: ManagementNetworkConfigurationPatchableProperties
        rack_count: int
        server_count_per_rack: int
        terminal_server_configuration: NetworkFabricPatchablePropertiesTerminalServerConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                fabric_asn: Optional[int] = ..., 
                ipv4_prefix: Optional[str] = ..., 
                ipv6_prefix: Optional[str] = ..., 
                management_network_configuration: Optional[ManagementNetworkConfigurationPatchableProperties] = ..., 
                rack_count: Optional[int] = ..., 
                server_count_per_rack: Optional[int] = ..., 
                terminal_server_configuration: Optional[NetworkFabricPatchablePropertiesTerminalServerConfiguration] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricPatchableProperties(Model):
        fabric_asn: int
        ipv4_prefix: str
        ipv6_prefix: str
        management_network_configuration: ManagementNetworkConfigurationPatchableProperties
        rack_count: int
        server_count_per_rack: int
        terminal_server_configuration: NetworkFabricPatchablePropertiesTerminalServerConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fabric_asn: Optional[int] = ..., 
                ipv4_prefix: Optional[str] = ..., 
                ipv6_prefix: Optional[str] = ..., 
                management_network_configuration: Optional[ManagementNetworkConfigurationPatchableProperties] = ..., 
                rack_count: Optional[int] = ..., 
                server_count_per_rack: Optional[int] = ..., 
                terminal_server_configuration: Optional[NetworkFabricPatchablePropertiesTerminalServerConfiguration] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricPatchablePropertiesTerminalServerConfiguration(TerminalServerPatchableProperties, Layer3IpPrefixProperties):
        password: str
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        serial_number: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                username: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricProperties(AnnotationResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        fabric_asn: int
        fabric_version: str
        ipv4_prefix: str
        ipv6_prefix: str
        l2_isolation_domains: list[str]
        l3_isolation_domains: list[str]
        management_network_configuration: ManagementNetworkConfigurationProperties
        network_fabric_controller_id: str
        network_fabric_sku: str
        provisioning_state: Union[str, ProvisioningState]
        rack_count: int
        racks: list[str]
        router_ids: list[str]
        server_count_per_rack: int
        terminal_server_configuration: TerminalServerConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                fabric_asn: int, 
                ipv4_prefix: str, 
                ipv6_prefix: Optional[str] = ..., 
                management_network_configuration: ManagementNetworkConfigurationProperties, 
                network_fabric_controller_id: str, 
                network_fabric_sku: str, 
                rack_count: Optional[int] = ..., 
                server_count_per_rack: int, 
                terminal_server_configuration: TerminalServerConfiguration, 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricSku(ProxyResource):
        details: str
        id: str
        max_compute_racks: int
        maximum_server_count: int
        name: str
        provisioning_state: Union[str, ProvisioningState]
        supported_versions: list[str]
        system_data: SystemData
        type: str
        type_properties_type: Union[str, FabricSkuType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_compute_racks: Optional[int] = ..., 
                maximum_server_count: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricSkusListResult(Model):
        next_link: str
        value: list[NetworkFabricSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkFabricSku]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkFabricsListResult(Model):
        next_link: str
        value: list[NetworkFabric]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkFabric]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkInterface(ProxyResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        connected_to: str
        id: str
        interface_type: Union[str, InterfaceType]
        ipv4_address: str
        ipv6_address: str
        name: str
        physical_identifier: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkInterfacePatch(Model):
        annotation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkInterfacePatchProperties(AnnotationResource):
        annotation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkInterfaceProperties(AnnotationResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        connected_to: str
        interface_type: Union[str, InterfaceType]
        ipv4_address: str
        ipv6_address: str
        physical_identifier: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkInterfacesList(Model):
        next_link: str
        value: list[NetworkInterface]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkInterface]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBroker(TrackedResource):
        id: str
        location: str
        name: str
        neighbor_group_ids: list[str]
        network_device_ids: list[str]
        network_fabric_id: str
        network_tap_ids: list[str]
        provisioning_state: Union[str, ProvisioningState]
        source_interface_ids: list[str]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                network_fabric_id: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBrokerPatch(TagsUpdate):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBrokersListResult(Model):
        next_link: str
        value: list[NetworkPacketBroker]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkPacketBroker]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkRack(TrackedResource):
        annotation: str
        id: str
        location: str
        name: str
        network_devices: list[str]
        network_fabric_id: str
        network_rack_type: Union[str, NetworkRackType]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                location: str, 
                network_fabric_id: str, 
                network_rack_type: Optional[Union[str, NetworkRackType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkRackProperties(AnnotationResource):
        annotation: str
        network_devices: list[str]
        network_fabric_id: str
        network_rack_type: Union[str, NetworkRackType]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                network_fabric_id: str, 
                network_rack_type: Optional[Union[str, NetworkRackType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkRackType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGGREGATE = "Aggregate"
        COMBINED = "Combined"
        COMPUTE = "Compute"


    class azure.mgmt.managednetworkfabric.models.NetworkRacksListResult(Model):
        next_link: str
        value: list[NetworkRack]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkRack]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTap(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        destinations: list[NetworkTapPropertiesDestinationsItem]
        id: str
        location: str
        name: str
        network_packet_broker_id: str
        polling_type: Union[str, PollingType]
        provisioning_state: Union[str, ProvisioningState]
        source_tap_rule_id: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destinations: List[NetworkTapPropertiesDestinationsItem], 
                location: str, 
                network_packet_broker_id: str, 
                polling_type: Optional[Union[str, PollingType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapPatch(TagsUpdate):
        annotation: str
        destinations: list[NetworkTapPatchableParametersDestinationsItem]
        polling_type: Union[str, PollingType]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destinations: Optional[List[NetworkTapPatchableParametersDestinationsItem]] = ..., 
                polling_type: Optional[Union[str, PollingType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapPatchableParameters(AnnotationResource):
        annotation: str
        destinations: list[NetworkTapPatchableParametersDestinationsItem]
        polling_type: Union[str, PollingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destinations: Optional[List[NetworkTapPatchableParametersDestinationsItem]] = ..., 
                polling_type: Optional[Union[str, PollingType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapPatchableParametersDestinationsItem(DestinationProperties):
        destination_id: str
        destination_tap_rule_id: str
        destination_type: Union[str, DestinationType]
        isolation_domain_properties: IsolationDomainProperties
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                destination_tap_rule_id: Optional[str] = ..., 
                destination_type: Optional[Union[str, DestinationType]] = ..., 
                isolation_domain_properties: Optional[IsolationDomainProperties] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapProperties(AnnotationResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        destinations: list[NetworkTapPropertiesDestinationsItem]
        network_packet_broker_id: str
        polling_type: Union[str, PollingType]
        provisioning_state: Union[str, ProvisioningState]
        source_tap_rule_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destinations: List[NetworkTapPropertiesDestinationsItem], 
                network_packet_broker_id: str, 
                polling_type: Optional[Union[str, PollingType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapPropertiesDestinationsItem(DestinationProperties):
        destination_id: str
        destination_tap_rule_id: str
        destination_type: Union[str, DestinationType]
        isolation_domain_properties: IsolationDomainProperties
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                destination_tap_rule_id: Optional[str] = ..., 
                destination_type: Optional[Union[str, DestinationType]] = ..., 
                isolation_domain_properties: Optional[IsolationDomainProperties] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRule(TrackedResource):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        id: str
        last_synced_time: datetime
        location: str
        match_configurations: list[NetworkTapRuleMatchConfiguration]
        name: str
        network_tap_id: str
        polling_interval_in_seconds: Union[int, PollingIntervalInSeconds]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        tap_rules_url: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                location: str, 
                match_configurations: Optional[List[NetworkTapRuleMatchConfiguration]] = ..., 
                polling_interval_in_seconds: Union[int, PollingIntervalInSeconds] = 30, 
                tags: Optional[Dict[str, str]] = ..., 
                tap_rules_url: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleAction(Model):
        destination_id: str
        is_timestamp_enabled: Union[str, BooleanEnumProperty]
        match_configuration_name: str
        truncate: str
        type: Union[str, TapRuleActionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                is_timestamp_enabled: Optional[Union[str, BooleanEnumProperty]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                truncate: Optional[str] = ..., 
                type: Optional[Union[str, TapRuleActionType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleMatchCondition(CommonMatchConditions):
        encapsulation_type: Union[str, EncapsulationType]
        ip_condition: IpMatchCondition
        port_condition: PortCondition
        protocol_types: list[str]
        vlan_match_condition: VlanMatchCondition

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encapsulation_type: Union[str, EncapsulationType] = None, 
                ip_condition: Optional[IpMatchCondition] = ..., 
                port_condition: Optional[PortCondition] = ..., 
                protocol_types: Optional[List[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchCondition] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleMatchConfiguration(Model):
        actions: list[NetworkTapRuleAction]
        ip_address_type: Union[str, IPAddressType]
        match_conditions: list[NetworkTapRuleMatchCondition]
        match_configuration_name: str
        sequence_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[NetworkTapRuleAction]] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_conditions: Optional[List[NetworkTapRuleMatchCondition]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRulePatch(TagsUpdate):
        annotation: str
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        match_configurations: list[NetworkTapRuleMatchConfiguration]
        tags: dict[str, str]
        tap_rules_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[NetworkTapRuleMatchConfiguration]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                tap_rules_url: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRulePatchProperties(AnnotationResource, NetworkTapRulePatchableProperties):
        annotation: str
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        match_configurations: list[NetworkTapRuleMatchConfiguration]
        tap_rules_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[NetworkTapRuleMatchConfiguration]] = ..., 
                tap_rules_url: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRulePatchableProperties(Model):
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        match_configurations: list[NetworkTapRuleMatchConfiguration]
        tap_rules_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[NetworkTapRuleMatchConfiguration]] = ..., 
                tap_rules_url: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleProperties(AnnotationResource, NetworkTapRulePatchableProperties):
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: list[CommonDynamicMatchConfiguration]
        last_synced_time: datetime
        match_configurations: list[NetworkTapRuleMatchConfiguration]
        network_tap_id: str
        polling_interval_in_seconds: Union[int, PollingIntervalInSeconds]
        provisioning_state: Union[str, ProvisioningState]
        tap_rules_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[List[CommonDynamicMatchConfiguration]] = ..., 
                match_configurations: Optional[List[NetworkTapRuleMatchConfiguration]] = ..., 
                polling_interval_in_seconds: Union[int, PollingIntervalInSeconds] = 30, 
                tap_rules_url: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapRulesListResult(Model):
        next_link: str
        value: list[NetworkTapRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkTapRule]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkTapsListResult(Model):
        next_link: str
        value: list[NetworkTap]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkTap]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnect(ProxyResource):
        administrative_state: Union[str, AdministrativeState]
        configuration_state: Union[str, ConfigurationState]
        egress_acl_id: str
        export_route_policy: ExportRoutePolicyInformation
        id: str
        import_route_policy: ImportRoutePolicyInformation
        ingress_acl_id: str
        is_management_type: Union[str, IsManagementType]
        layer2_configuration: Layer2Configuration
        name: str
        nni_type: Union[str, NniType]
        npb_static_route_configuration: NpbStaticRouteConfiguration
        option_b_layer3_configuration: NetworkToNetworkInterconnectPropertiesOptionBLayer3Configuration
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str
        use_option_b: Union[str, BooleanEnumProperty]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicyInformation] = ..., 
                import_route_policy: Optional[ImportRoutePolicyInformation] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_management_type: Union[str, IsManagementType] = "True", 
                layer2_configuration: Optional[Layer2Configuration] = ..., 
                nni_type: Union[str, NniType] = "CE", 
                npb_static_route_configuration: Optional[NpbStaticRouteConfiguration] = ..., 
                option_b_layer3_configuration: Optional[NetworkToNetworkInterconnectPropertiesOptionBLayer3Configuration] = ..., 
                use_option_b: Union[str, BooleanEnumProperty], 
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


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnectPatch(ProxyResource):
        egress_acl_id: str
        export_route_policy: ExportRoutePolicyInformation
        id: str
        import_route_policy: ImportRoutePolicyInformation
        ingress_acl_id: str
        layer2_configuration: Layer2Configuration
        name: str
        npb_static_route_configuration: NpbStaticRouteConfiguration
        option_b_layer3_configuration: OptionBLayer3Configuration
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicyInformation] = ..., 
                import_route_policy: Optional[ImportRoutePolicyInformation] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                layer2_configuration: Optional[Layer2Configuration] = ..., 
                npb_static_route_configuration: Optional[NpbStaticRouteConfiguration] = ..., 
                option_b_layer3_configuration: Optional[OptionBLayer3Configuration] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnectPropertiesOptionBLayer3Configuration(OptionBLayer3Configuration):
        fabric_asn: int
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnectsList(Model):
        next_link: str
        value: list[NetworkToNetworkInterconnect]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkToNetworkInterconnect]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.NfcSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        HIGH_PERFORMANCE = "HighPerformance"
        STANDARD = "Standard"


    class azure.mgmt.managednetworkfabric.models.NniType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CE = "CE"
        NPB = "NPB"


    class azure.mgmt.managednetworkfabric.models.NpbStaticRouteConfiguration(Model):
        bfd_configuration: BfdConfiguration
        ipv4_routes: list[StaticRouteProperties]
        ipv6_routes: list[StaticRouteProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                ipv4_routes: Optional[List[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[List[StaticRouteProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.managednetworkfabric.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.managednetworkfabric.models.OptionAProperties(Model):
        bfd_configuration: BfdConfiguration
        mtu: int
        peer_asn: int
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                mtu: int = 1500, 
                peer_asn: Optional[int] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.OptionBLayer3Configuration(Layer3IpPrefixProperties):
        fabric_asn: int
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.OptionBProperties(Model):
        export_route_targets: list[str]
        import_route_targets: list[str]
        route_targets: RouteTargetInformation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_route_targets: Optional[List[str]] = ..., 
                import_route_targets: Optional[List[str]] = ..., 
                route_targets: Optional[RouteTargetInformation] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.managednetworkfabric.models.PeeringOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTION_A = "OptionA"
        OPTION_B = "OptionB"


    class azure.mgmt.managednetworkfabric.models.PollingIntervalInSeconds(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        NINETY = 90
        ONE_HUNDRED_TWENTY = 120
        SIXTY = 60
        THIRTY = 30


    class azure.mgmt.managednetworkfabric.models.PollingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PULL = "Pull"
        PUSH = "Push"


    class azure.mgmt.managednetworkfabric.models.PortCondition(Model):
        layer4_protocol: Union[str, Layer4Protocol]
        port_group_names: list[str]
        port_type: Union[str, PortType]
        ports: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                layer4_protocol: Union[str, Layer4Protocol], 
                port_group_names: Optional[List[str]] = ..., 
                port_type: Optional[Union[str, PortType]] = ..., 
                ports: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.PortGroupProperties(Model):
        name: str
        ports: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                ports: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.PortType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESTINATION_PORT = "DestinationPort"
        SOURCE_PORT = "SourcePort"


    class azure.mgmt.managednetworkfabric.models.PrefixType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LONGEST_PREFIX = "LongestPrefix"
        PREFIX = "Prefix"


    class azure.mgmt.managednetworkfabric.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.managednetworkfabric.models.ProxyResource(Resource):
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


    class azure.mgmt.managednetworkfabric.models.RebootProperties(Model):
        reboot_type: Union[str, RebootType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reboot_type: Optional[Union[str, RebootType]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RebootType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRACEFUL_REBOOT_WITHOUT_ZTP = "GracefulRebootWithoutZTP"
        GRACEFUL_REBOOT_WITH_ZTP = "GracefulRebootWithZTP"
        UNGRACEFUL_REBOOT_WITHOUT_ZTP = "UngracefulRebootWithoutZTP"
        UNGRACEFUL_REBOOT_WITH_ZTP = "UngracefulRebootWithZTP"


    class azure.mgmt.managednetworkfabric.models.RedistributeConnectedSubnets(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.RedistributeStaticRoutes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.Resource(Model):
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


    class azure.mgmt.managednetworkfabric.models.RoutePoliciesListResult(Model):
        next_link: str
        value: list[RoutePolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[RoutePolicy]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RoutePolicy(TrackedResource):
        address_family_type: Union[str, AddressFamilyType]
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        id: str
        location: str
        name: str
        network_fabric_id: str
        provisioning_state: Union[str, ProvisioningState]
        statements: list[RoutePolicyStatementProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_family_type: Union[str, AddressFamilyType] = "IPv4", 
                annotation: Optional[str] = ..., 
                location: str, 
                network_fabric_id: str, 
                statements: Optional[List[RoutePolicyStatementProperties]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RoutePolicyActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE = "Continue"
        CONTINUE_ENUM = "Continue"
        DENY = "Deny"
        PERMIT = "Permit"


    class azure.mgmt.managednetworkfabric.models.RoutePolicyConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "And"
        AND_ENUM = "And"
        OR = "Or"
        OR_ENUM = "Or"


    class azure.mgmt.managednetworkfabric.models.RoutePolicyPatch(TagsUpdate):
        statements: list[RoutePolicyStatementProperties]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                statements: Optional[List[RoutePolicyStatementProperties]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RoutePolicyPatchableProperties(Model):
        statements: list[RoutePolicyStatementProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                statements: Optional[List[RoutePolicyStatementProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RoutePolicyProperties(AnnotationResource, RoutePolicyPatchableProperties):
        address_family_type: Union[str, AddressFamilyType]
        administrative_state: Union[str, AdministrativeState]
        annotation: str
        configuration_state: Union[str, ConfigurationState]
        network_fabric_id: str
        provisioning_state: Union[str, ProvisioningState]
        statements: list[RoutePolicyStatementProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_family_type: Union[str, AddressFamilyType] = "IPv4", 
                annotation: Optional[str] = ..., 
                network_fabric_id: str, 
                statements: Optional[List[RoutePolicyStatementProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RoutePolicyStatementProperties(AnnotationResource):
        action: StatementActionProperties
        annotation: str
        condition: StatementConditionProperties
        sequence_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: StatementActionProperties, 
                annotation: Optional[str] = ..., 
                condition: StatementConditionProperties, 
                sequence_number: int, 
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


    class azure.mgmt.managednetworkfabric.models.RouteTargetInformation(Model):
        export_ipv4_route_targets: list[str]
        export_ipv6_route_targets: list[str]
        import_ipv4_route_targets: list[str]
        import_ipv6_route_targets: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                export_ipv4_route_targets: Optional[List[str]] = ..., 
                export_ipv6_route_targets: Optional[List[str]] = ..., 
                import_ipv4_route_targets: Optional[List[str]] = ..., 
                import_ipv6_route_targets: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.RuleProperties(Model):
        action: Union[str, Action]
        address_list: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, Action], 
                address_list: List[str], 
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


    class azure.mgmt.managednetworkfabric.models.SourceDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESTINATION_IP = "DestinationIP"
        SOURCE_IP = "SourceIP"


    class azure.mgmt.managednetworkfabric.models.StatementActionProperties(Model):
        action_type: Union[str, RoutePolicyActionType]
        ip_community_properties: ActionIpCommunityProperties
        ip_extended_community_properties: ActionIpExtendedCommunityProperties
        local_preference: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_type: Union[str, RoutePolicyActionType], 
                ip_community_properties: Optional[ActionIpCommunityProperties] = ..., 
                ip_extended_community_properties: Optional[ActionIpExtendedCommunityProperties] = ..., 
                local_preference: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.StatementConditionProperties(IpCommunityIdList, IpExtendedCommunityIdList):
        ip_community_ids: list[str]
        ip_extended_community_ids: list[str]
        ip_prefix_id: str
        type: Union[str, RoutePolicyConditionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_community_ids: Optional[List[str]] = ..., 
                ip_extended_community_ids: Optional[List[str]] = ..., 
                ip_prefix_id: Optional[str] = ..., 
                type: Union[str, RoutePolicyConditionType] = "Or", 
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


    class azure.mgmt.managednetworkfabric.models.StaticRouteConfiguration(Model):
        bfd_configuration: BfdConfiguration
        ipv4_routes: list[StaticRouteProperties]
        ipv6_routes: list[StaticRouteProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                ipv4_routes: Optional[List[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[List[StaticRouteProperties]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.StaticRouteProperties(Model):
        next_hop: list[str]
        prefix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_hop: List[str], 
                prefix: str, 
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


    class azure.mgmt.managednetworkfabric.models.SupportedConnectorProperties(Model):
        connector_type: str
        max_speed_in_mbps: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connector_type: Optional[str] = ..., 
                max_speed_in_mbps: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.SupportedVersionProperties(Model):
        is_default: Union[str, BooleanEnumProperty]
        vendor_firmware_version: str
        vendor_os_version: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_default: Optional[Union[str, BooleanEnumProperty]] = ..., 
                vendor_firmware_version: Optional[str] = ..., 
                vendor_os_version: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.SystemData(Model):
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


    class azure.mgmt.managednetworkfabric.models.TagsUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.TapRuleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"
        DROP = "Drop"
        GOTO = "Goto"
        LOG = "Log"
        MIRROR = "Mirror"
        REDIRECT = "Redirect"
        REPLICATE = "Replicate"


    class azure.mgmt.managednetworkfabric.models.TerminalServerConfiguration(TerminalServerPatchableProperties, Layer3IpPrefixProperties):
        network_device_id: str
        password: str
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        serial_number: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                username: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.TerminalServerPatchableProperties(Model):
        password: str
        serial_number: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                username: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.TrackedResource(Resource):
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
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.UpdateAdministrativeState(EnableDisableOnResources):
        resource_ids: list[str]
        state: Union[str, EnableDisableState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_ids: Optional[List[str]] = ..., 
                state: Optional[Union[str, EnableDisableState]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.UpdateDeviceAdministrativeState(EnableDisableOnResources):
        resource_ids: list[str]
        state: Union[str, DeviceAdministrativeState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_ids: Optional[List[str]] = ..., 
                state: Optional[Union[str, DeviceAdministrativeState]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.UpdateVersion(Model):
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


    class azure.mgmt.managednetworkfabric.models.ValidateAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CABLING = "Cabling"
        CONFIGURATION = "Configuration"
        CONNECTIVITY = "Connectivity"


    class azure.mgmt.managednetworkfabric.models.ValidateConfigurationProperties(Model):
        validate_action: Union[str, ValidateAction]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                validate_action: Optional[Union[str, ValidateAction]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.ValidateConfigurationResponse(ErrorResponse):
        configuration_state: Union[str, ConfigurationState]
        error: ErrorDetail
        url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                url: Optional[str] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.VlanGroupProperties(Model):
        name: str
        vlans: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                vlans: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.VlanMatchCondition(Model):
        inner_vlans: list[str]
        vlan_group_names: list[str]
        vlans: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inner_vlans: Optional[List[str]] = ..., 
                vlan_group_names: Optional[List[str]] = ..., 
                vlans: Optional[List[str]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.VpnConfigurationPatchableProperties(Model):
        network_to_network_interconnect_id: str
        option_a_properties: VpnConfigurationPatchablePropertiesOptionAProperties
        option_b_properties: OptionBProperties
        peering_option: Union[str, PeeringOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_to_network_interconnect_id: Optional[str] = ..., 
                option_a_properties: Optional[VpnConfigurationPatchablePropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[OptionBProperties] = ..., 
                peering_option: Optional[Union[str, PeeringOption]] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.VpnConfigurationPatchablePropertiesOptionAProperties(OptionAProperties, Layer3IpPrefixProperties):
        bfd_configuration: BfdConfiguration
        mtu: int
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                mtu: int = 1500, 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.VpnConfigurationProperties(Model):
        administrative_state: Union[str, AdministrativeState]
        network_to_network_interconnect_id: str
        option_a_properties: VpnConfigurationPropertiesOptionAProperties
        option_b_properties: OptionBProperties
        peering_option: Union[str, PeeringOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_to_network_interconnect_id: Optional[str] = ..., 
                option_a_properties: Optional[VpnConfigurationPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[OptionBProperties] = ..., 
                peering_option: Union[str, PeeringOption], 
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


    class azure.mgmt.managednetworkfabric.models.VpnConfigurationPropertiesOptionAProperties(OptionAProperties, Layer3IpPrefixProperties):
        bfd_configuration: BfdConfiguration
        mtu: int
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                mtu: int = 1500, 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
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


    class azure.mgmt.managednetworkfabric.models.WellKnownCommunities(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G_SHUT = "GShut"
        INTERNET = "Internet"
        LOCAL_AS = "LocalAS"
        NO_ADVERTISE = "NoAdvertise"
        NO_EXPORT = "NoExport"


namespace azure.mgmt.managednetworkfabric.operations

    class azure.mgmt.managednetworkfabric.operations.AccessControlListsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: AccessControlList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessControlList]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessControlList]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resync(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: AccessControlListPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessControlList]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessControlList]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AccessControlList: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AccessControlList]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AccessControlList]: ...


    class azure.mgmt.managednetworkfabric.operations.ExternalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetwork]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetworkPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetwork]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ExternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.operations.InternalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetwork]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetwork]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[InternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.operations.InternetGatewayRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: InternetGatewayRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGatewayRule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGatewayRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: InternetGatewayRulePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGatewayRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGatewayRule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InternetGatewayRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[InternetGatewayRule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[InternetGatewayRule]: ...


    class azure.mgmt.managednetworkfabric.operations.InternetGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: InternetGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGateway]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGateway]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: InternetGatewayPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGateway]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGateway]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InternetGateway: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[InternetGateway]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[InternetGateway]: ...


    class azure.mgmt.managednetworkfabric.operations.IpCommunitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IpCommunity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpCommunity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpCommunity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IpCommunityPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpCommunity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpCommunity]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpCommunity]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpCommunity]: ...


    class azure.mgmt.managednetworkfabric.operations.IpExtendedCommunitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IpExtendedCommunity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpExtendedCommunity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpExtendedCommunity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IpExtendedCommunityPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpExtendedCommunity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpExtendedCommunity]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpExtendedCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpExtendedCommunity]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpExtendedCommunity]: ...


    class azure.mgmt.managednetworkfabric.operations.IpPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IpPrefix, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpPrefix]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpPrefix]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IpPrefixPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpPrefix]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpPrefix]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpPrefix: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpPrefix]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpPrefix]: ...


    class azure.mgmt.managednetworkfabric.operations.L2IsolationDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: L2IsolationDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L2IsolationDomain]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L2IsolationDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: L2IsolationDomainPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L2IsolationDomain]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L2IsolationDomain]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> L2IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[L2IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[L2IsolationDomain]: ...


    class azure.mgmt.managednetworkfabric.operations.L3IsolationDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: L3IsolationDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L3IsolationDomain]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L3IsolationDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: L3IsolationDomainPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L3IsolationDomain]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L3IsolationDomain]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> L3IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[L3IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[L3IsolationDomain]: ...


    class azure.mgmt.managednetworkfabric.operations.NeighborGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: NeighborGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NeighborGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NeighborGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: NeighborGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NeighborGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NeighborGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NeighborGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NeighborGroup]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NeighborGroup]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkDeviceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                network_device_sku_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkDeviceSku: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkDeviceSku]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDevice]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDevice]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: RebootProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDevicePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDevice]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkDevice: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkDevice]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkDevice]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkFabricControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: NetworkFabricController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricController]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricController]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: NetworkFabricControllerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricController]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricController]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFabricController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFabricController]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFabricController]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkFabricSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                network_fabric_sku_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFabricSku: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFabricSku]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabric]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_deprovision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        def begin_get_topology(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def begin_provision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabricPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabric]: ...

        @overload
        def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: ValidateConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @overload
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFabric: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFabric]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFabric]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: NetworkInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: NetworkInterfacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkInterface: ...

        @distributed_trace
        def list_by_network_device(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkInterface]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkPacketBrokersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: NetworkPacketBroker, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkPacketBroker]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkPacketBroker]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: NetworkPacketBrokerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkPacketBroker]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkPacketBroker]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkPacketBroker: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkPacketBroker]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkPacketBroker]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkRacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: NetworkRack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: TagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkRack: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkRack]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkRack]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkTapRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: NetworkTapRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTapRule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTapRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: NetworkTapRulePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTapRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTapRule]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkTapRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkTapRule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkTapRule]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkTapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: NetworkTap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTap]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTap]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: NetworkTapPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTap]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTap]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkTap: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkTap]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkTap]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkToNetworkInterconnectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NetworkToNetworkInterconnect, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkToNetworkInterconnect]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkToNetworkInterconnect]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NetworkToNetworkInterconnectPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkToNetworkInterconnect]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkToNetworkInterconnect]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_npb_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_npb_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkToNetworkInterconnect: ...

        @distributed_trace
        def list_by_network_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkToNetworkInterconnect]: ...


    class azure.mgmt.managednetworkfabric.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.managednetworkfabric.operations.RoutePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: RoutePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RoutePolicy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RoutePolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: RoutePolicyPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RoutePolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RoutePolicy]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RoutePolicy: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RoutePolicy]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RoutePolicy]: ...


```